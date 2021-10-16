from factorio_mod_downloader.models import Mod


def test_mod_from_string():
    assert Mod.from_string("foo") == Mod(name="foo", optional=False)
    assert Mod.from_string("? foo") == Mod(name="foo", optional=True)
    assert Mod.from_string("(?) foo") == Mod(name="foo", optional=True)
    assert Mod.from_string("foo >= 1.2.3") == Mod(
        name="foo", optional=False, operator=">=", version="1.2.3"
    )
    assert Mod.from_string("? foo >= 1.2.3") == Mod(
        name="foo", optional=True, operator=">=", version="1.2.3"
    )
