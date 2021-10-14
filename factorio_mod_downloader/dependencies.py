from typing import Any, Dict, List, Optional, Set

import requests

from .models import Mod, Release


MODS_BASE_URL = "https://mods.factorio.com"


def parse_modlist(modlist: List[str]) -> Set[Mod]:
    def parse_modlist_item(mod: str) -> Mod:
        split = mod.split("==")
        return Mod(name=split[0].strip(), version=split[1] if len(split) == 2 else None)

    return set(parse_modlist_item(mod) for mod in modlist)


def parse_releases_from_response(json_response: Dict[str, Any]) -> List[Release]:
    releases = json_response.get("releases", [])
    return [Release(**release) for release in releases]


def fetch_releases_for_mod(mod: Mod) -> List[Release]:
    url = f"{MODS_BASE_URL}/api/mods/{mod.name}/full"
    response = requests.get(url).json()
    return parse_releases_from_response(response)


def find_release(releases: List[Release], version: Optional[str] = None) -> Release:
    # version None return latest
    if version is None:
        return sorted(releases)[-1]
    for release in releases:
        if release.version == version:
            return release
    raise EOFError("Mathcing version not found")


def fill_mod_details_from_releases(mod: Mod, releases: List[Release]):
    try:
        release = find_release(releases, version=mod.version)
    except EOFError:
        raise EOFError(f"Could not find version {mod.version} of mod {mod.name}")
    except IndexError:
        raise IndexError(f"No releases found for mod {mod.name}")
    mod.version = release.version
    mod.download_url = f"{MODS_BASE_URL}{release.download_url}"
    mod.dependencies = set(release.dependencies)


def _solve_dependencies(mods: Set[Mod]) -> Set[Mod]:
    unsolved_dependencies: Set[Mod] = set()
    unsolved_mods = (mod for mod in mods if mod.download_url is None)

    for mod in unsolved_mods:
        releases = fetch_releases_for_mod(mod)
        fill_mod_details_from_releases(mod, releases)
        deps = mod.dependencies if mod.dependencies is not None else []
        unsolved_dependencies.update(Mod(name=dep) for dep in deps if dep not in mods)
    if unsolved_dependencies:
        return _solve_dependencies(mods.union(unsolved_dependencies))
    return mods


def solve_dependencies(modlist: List[str]) -> List[Mod]:
    mods = parse_modlist(modlist)
    return list(_solve_dependencies(mods))
