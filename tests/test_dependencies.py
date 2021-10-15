import json

import pytest

from factorio_mod_downloader import __version__
from factorio_mod_downloader.__main__ import (
    Mod,
    parse_modlist,
    parse_releases_from_response,
    find_release,
)
from factorio_mod_downloader.models import Release


from . import test_data


def test_version():
    assert __version__ == "0.1.0"


def test_parse_modlist():
    modlist = ["foo", "bar==0.1.0"]
    expected = {Mod(name="foo", version=None), Mod(name="bar", version="0.1.0")}
    assert parse_modlist(modlist) == expected


def test_parse_releases_from_response_simple():
    data = json.loads(test_data.RESPONSE_NO_DEPS)
    results = parse_releases_from_response(data)
    assert len(results) == 2
    first, second = results
    assert first.version == "0.0.1"
    assert second.version == "0.1.0"
    assert len(first.dependencies) == 0
    assert len(second.dependencies) == 0


def test_parse_releases_from_response_complex():
    data = json.loads(test_data.FULL_RESPONSE)
    results = parse_releases_from_response(data)
    assert len(results) == 24
    first = results[0]
    assert first.version == "0.13.0"
    assert len(first.dependencies) == 1
    assert first.dependencies[0] == "boblibrary"


def test_find_release():
    release_data = dict(
        download_url="/download",
        file_name="file",
        info_json={},
        released_at="monday",
        sha1="123",
    )
    release_1 = Release(version="0.2.0", **release_data)
    release_2 = Release(version="1.0.0", **release_data)

    assert find_release([release_1, release_2]).version == "1.0.0"
    assert find_release([release_2, release_1]).version == "1.0.0"
    assert find_release([release_1, release_2], version="1.0.0").version == "1.0.0"
    assert find_release([release_1, release_2], version="1.0.0").version == "1.0.0"

    with pytest.raises(EOFError):
        find_release([release_1, release_2], version="1.2.3")
