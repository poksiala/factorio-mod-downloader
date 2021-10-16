import logging
from typing import Any, Dict, List, Optional, Set

import requests

from .models import DownloadDetails, Mod, Release

MODS_BASE_URL = "https://mods.factorio.com"


logger = logging.getLogger(__name__)


def parse_modlist(modlist: List[str]) -> Set[Mod]:
    def parse_modlist_item(mod: str) -> Mod:
        split = mod.strip().split("==")
        return Mod(name=split[0], version=split[1] if len(split) == 2 else None)

    return set(parse_modlist_item(mod) for mod in modlist)


def parse_releases_from_response(json_response: Dict[str, Any]) -> List[Release]:
    releases = json_response.get("releases", [])
    return [Release(**release) for release in releases]


def fetch_releases_for_mod(mod: Mod, client: requests.Session) -> List[Release]:
    logging.debug("Fetching releases for mod %s", mod.name)
    url = f"{MODS_BASE_URL}/api/mods/{mod.name}/full"
    response = client.get(url).json()
    return parse_releases_from_response(response)


def find_release(releases: List[Release], version: Optional[str] = None) -> Release:
    # version None return latest
    if version is None:
        return sorted(releases)[-1]
    for release in releases:
        if release.version == version:
            return release
    raise EOFError("Version %s not found", version)


def build_download_info(mod: Mod, release: Release) -> DownloadDetails:
    return DownloadDetails(
        name=mod.name,
        version=release.version,
        download_url=f"{MODS_BASE_URL}{release.download_url}",
        sha1=release.sha1,
        file_name=release.file_name,
    )


def _solve_dependencies(
    mods: Set[Mod], download_details: Set[DownloadDetails], client: requests.Session
):
    resolved_mod_names = set(dd.name for dd in download_details)
    unsolved_mods = (mod for mod in mods if mod.name not in resolved_mod_names)
    new_dependencies: Set[str] = set()

    for mod in unsolved_mods:
        logger.info("resolving mod %s", mod)
        releases = fetch_releases_for_mod(mod, client)
        logger.debug("Found %d releases", len(releases))
        release = find_release(releases, version=mod.version)
        logger.debug("Selected release %s", release)
        download_details.add(build_download_info(mod, release))
        new_dependencies.update(release.dependencies)

    if new_dependencies:
        _solve_dependencies(
            set(Mod(name=dep) for dep in new_dependencies), download_details, client
        )


def solve_dependencies(
    modlist: List[str], client: requests.Session
) -> List[DownloadDetails]:
    mods = parse_modlist(modlist)
    logger.debug("Initial modlist: %s", list(mod.name for mod in mods))
    download_details: Set[DownloadDetails] = set()
    _solve_dependencies(mods, download_details, client)
    return list(download_details)
