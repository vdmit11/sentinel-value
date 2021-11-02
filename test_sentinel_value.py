from unittest import mock

import pytest

from sentinel_value import SentinelValue, sentinel, sentinel_value_instances


@pytest.fixture(autouse=True)
def cleanup_sentinel_value_instances_after_each_test():
    yield
    sentinel_value_instances.clear()


def test__SentinelValue__str_and_repr():
    MISSING = SentinelValue("MISSING", "some.module2")
    assert str(MISSING) == "<MISSING>"
    assert repr(MISSING) == "<MISSING>"


def test__SentinelValue__is_falsy():
    MISSING = SentinelValue("MISSING", "some.module3")
    assert not bool(MISSING)


def test__SentinelValue_creates_new_instance_only_once_per_name():
    MISSING = SentinelValue("MISSING", "some.module")

    MISSING_duplicate = SentinelValue("MISSING", "some.module")
    assert MISSING is MISSING_duplicate

    MISSING2 = SentinelValue("MISSING2", "some.module")
    assert MISSING is not MISSING2

    MISSING_in_other_module = SentinelValue("MISSING", "some.module2")
    assert MISSING is not MISSING_in_other_module


def test__SentinelValue_can_change_class_on_the_fly():
    MISSING = SentinelValue("MISSING", __name__)
    assert MISSING.__class__ is SentinelValue

    class Missing(SentinelValue):
        pass

    MISSING_redefined = Missing("MISSING", __name__)

    assert MISSING_redefined is MISSING
    assert MISSING_redefined.__class__ is Missing


def test__sentinel__custom_repr():
    MISSING1 = sentinel("MISSING1")
    assert repr(MISSING1) == "<MISSING1>"

    MISSING2 = sentinel("MISSING2", repr="my.module.MISSING2")
    assert repr(MISSING2) == "my.module.MISSING2"


def test__sentinel__can_be_called_multiple_times():
    MISSING = sentinel("MISSING")
    MISSING_duplicate = sentinel("MISSING")

    assert MISSING_duplicate is MISSING


@mock.patch("inspect.currentframe")
def test__sentinel__throws_error_if_call_stack_not_available(currentframe_mock):
    currentframe_mock.return_value = None

    with pytest.raises(AssertionError):
        sentinel("MISSING")


def test__sentinel__creates_subclass_of_SentinelValue():
    MISSING = sentinel("MISSING")
    Missing = MISSING.__class__

    assert Missing is not SentinelValue
    assert issubclass(Missing, SentinelValue)

    MISSING2 = sentinel("MISSING")
    Missing2 = MISSING2.__class__

    assert Missing2 is Missing
