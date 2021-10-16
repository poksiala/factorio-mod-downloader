from __future__ import annotations
from dataclasses import dataclass, field
import packaging.version
from typing import Dict, List, Optional, Union

version_parse = packaging.version.parse


@dataclass(frozen=True)
class Auth:
    username: str
    token: str


@dataclass(frozen=True)
class Dependency:
    name: str
    optional: bool
    version: Optional[str] = None
    operator: Optional[str] = None

    @classmethod
    def from_string(cls, string: str) -> Dependency:
        split = string.strip().split(" ")
        optional = "?" in split[0]
        name = split[1] if optional else split[0]
        operator = split[-2] if len(split) > 2 else None
        version = split[-1] if len(split) > 2 else None
        return cls(name=name, optional=optional, operator=operator, version=version)


@dataclass(frozen=True)
class DownloadDetails:
    name: str
    version: str
    download_url: str
    sha1: str
    file_name: str

    def __hash__(self) -> int:
        return hash(self.name)


@dataclass
class Mod:
    name: str
    optional: bool
    version: Optional[str] = None
    operator: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.name)

    @classmethod
    def from_string(cls, string: str) -> Mod:
        split = string.strip().split(" ")
        optional = "?" in split[0]
        name = split[1] if optional else split[0]
        operator = split[-2] if len(split) > 2 else None
        version = split[-1] if len(split) > 2 else None
        return cls(name=name, optional=optional, operator=operator, version=version)


@dataclass
class Release:
    download_url: str
    file_name: str
    info_json: Dict[str, Union[List[str], str]]
    released_at: str
    sha1: str
    version: str
    dependencies: List[Mod] = field(init=False, default_factory=list)

    def __post_init__(self):
        def is_interesting(dep: str) -> bool:
            # Returns false for base mod
            return not dep.split(" ")[0] in {"base"}

        _dependencies = self.info_json.get("dependencies")
        if isinstance(_dependencies, list):
            self.dependencies = [
                Mod.from_string(dep) for dep in _dependencies if is_interesting(dep)
            ]

    def __lt__(self, another: Release) -> bool:
        return version_parse(self.version) < version_parse(another.version)
