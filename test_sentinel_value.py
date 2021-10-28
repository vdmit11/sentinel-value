import pytest

from sentinel_value import Sentinel


def test__Sentinel__checks_for_duplicate_names():
    Sentinel("MISSING", "some.module")

    with pytest.raises(AssertionError):
        Sentinel("MISSING", "some.module")

    Sentinel("MISSING2", "some.module")
    Sentinel("MISSING", "some.other.module")


def test__Sentinel__str_and_repr():
    MISSING = Sentinel("MISSING", "some.module2")
    assert str(MISSING) == "MISSING"
    assert repr(MISSING) == "some.module2.MISSING"


def test__Sentinel__is_falsy():
    MISSING = Sentinel("MISSING", "some.module3")
    assert not bool(MISSING)
