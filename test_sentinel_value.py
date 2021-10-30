from unittest import mock

import pytest

from sentinel_value import SentinelValue, sentinel


def test__Sentinel__str_and_repr():
    MISSING = SentinelValue("MISSING", "some.module2")
    assert str(MISSING) == "MISSING"
    assert repr(MISSING) == "some.module2.MISSING"


def test__Sentinel__is_falsy():
    MISSING = SentinelValue("MISSING", "some.module3")
    assert not bool(MISSING)


def test__sentinel__custom_repr():
    MISSING = sentinel("MISSING", "my.module.MISSING")
    assert repr(MISSING) == "my.module.MISSING"


def test__sentinel__can_be_called_multiple_times():
    MISSING = sentinel("MISSING")
    MISSING_duplicate = sentinel("MISSING")

    assert MISSING_duplicate is MISSING


@mock.patch("inspect.currentframe")
def test__sentinel__throws_error_if_call_stack_not_available(currentframe_mock):
    currentframe_mock.return_value = None

    with pytest.raises(AssertionError):
        sentinel("MISSING")
