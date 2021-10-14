from __future__ import annotations
from dataclasses import dataclass, field
import packaging.version
from typing import Dict, List, Optional, Set, Union

version_parse = packaging.version.parse


@dataclass
class Mod:
    name: str
    version: Optional[str] = None
    download_url: Optional[str] = None
    dependencies: Optional[Set[str]] = None

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Release:
    download_url: str
    file_name: str
    info_json: Dict[str, Union[List[str], str]]
    released_at: str
    sha1: str
    version: str
    dependencies: List[str] = field(init=False, default_factory=list)

    def __post_init__(self):
        def is_interesting(dep: str) -> bool:
            # Returns false for base mod and optional mods
            return not dep.split(" ")[0] in {"base", "?"}

        _dependencies = self.info_json.get("dependencies")
        if isinstance(_dependencies, list):
            self.dependencies = [
                dep.split(" ")[0] for dep in _dependencies if is_interesting(dep)
            ]

    def __lt__(self, another: Release) -> bool:
        return version_parse(self.version) < version_parse(another.version)
