import pytest

from sentinel_value import SentinelValue


def test__Sentinel__checks_for_duplicate_names():
    SentinelValue("MISSING", "some.module")

    with pytest.raises(AssertionError):
        SentinelValue("MISSING", "some.module")

    SentinelValue("MISSING2", "some.module")
    SentinelValue("MISSING", "some.other.module")


def test__Sentinel__str_and_repr():
    MISSING = SentinelValue("MISSING", "some.module2")
    assert str(MISSING) == "MISSING"
    assert repr(MISSING) == "some.module2.MISSING"


def test__Sentinel__is_falsy():
    MISSING = SentinelValue("MISSING", "some.module3")
    assert not bool(MISSING)
