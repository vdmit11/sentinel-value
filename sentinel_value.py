import inspect
import sys
import threading
from typing import Dict, Optional, Type


class SentinelValue:
    """Class for special unique placeholder objects, akin to ``None``.

    Useful for distinguishing "value is not set" and "value is set to None" cases
    as shown in this example::

        >>> NOT_SET = SentinelValue("NOT_SET", __name__)

        >>> value = getattr(object, "some_attribute", NOT_SET)
        >>> if value is NOT_SET:
        ...    print('attribute is not set')
        attribute is not set

    If you need a separate type (for use with :mod:`typing` or :func:`functools.singledispatch`),
    then you can create a subclass::

        >>> from typing import Union

        >>> class Missing(SentinelValue):
        ...     pass

        >>> MISSING = Missing("Missing", __name__)

        # Here is how the Missing class can be used for type hinting.
        >>> value: Union[str, None, Missing] = getattr(object, "some_attribute", MISSING)
        >>> if value is MISSING:
        ...    print("value is missing")
        value is missing
    """

    def __new__(cls, instance_name, module_name):  # noqa: D103
        qualified_name = cls._compose_qualified_name(instance_name, module_name)

        with sentinel_create_lock:
            existing_instance = sentinel_value_instances.get(qualified_name)
            if existing_instance is not None:
                return existing_instance

            new_instance = super().__new__(cls)
            sentinel_value_instances[qualified_name] = new_instance
            return new_instance

    @staticmethod
    def _compose_qualified_name(instance_name: str, module_name: str) -> str:
        return module_name + "." + instance_name

    def __init__(self, instance_name: str, module_name: str) -> None:
        self.short_name = instance_name
        self.qualified_name = self._compose_qualified_name(instance_name, module_name)

        super().__init__()

    def __repr__(self):
        return "<" + self.short_name + ">"

    @staticmethod
    def __bool__():
        return False


sentinel_value_instances: Dict[str, SentinelValue] = {}
"""Dictionary that contains all instances of SentinelValue (and its subclasses).

This dictionary looks like this::

  {
      "package1.module1.MISSING": SentinelValue("MISSING", module_name="package1.module1.MISSING"),
      "package2.module2.MISSING": SentinelValue("MISSING", module_name="package2.module2.MISSING"),
      "package2.module2.ABSENT": SentinelValue("ABSENT", module_name="package2.module2.ABSENT"),
  }

When a :class:`SentinelValue` object is instanciated, it registers itself in this dictionary
(and throws an error if already registered). This is needed to ensure that, for each name,
there exists only 1 unique :class:`SentinelValue` object.
"""


sentinel_create_lock = threading.Lock()
"""A lock that prevents race conditions when creating new :class:`SentinelValue` objects.

Problem: when you start multiple threads, they may try to create sentinel objects concurrently.
If you're lucky enough, you get duplicate :class:`SentinelValue` instances,
which is highly undesirable.

This :data:`sentinel_create_lock` helps to protect against such race conditions.

The lock is acquired whenever a new :class:`SentienlValue` object is created.
So, when multiple threads try to create sentinel objects, then they're executed in sequence,
and the 1st thread really creates a new instance, and other threads will get the already
existing instance.
"""


def sentinel(
    instance_name: str,
    repr: Optional[str] = None,
) -> SentinelValue:
    """Create an unique sentinel object.

    Implementation of PEP 661
    https://www.python.org/dev/peps/pep-0661/

        >>> MISSING = sentinel("MISSING")

        >>> value = getattr(object, "value", MISSING)

        >>> if value is MISSING:
        ...     print("value is not set")
        value is not set

    :param instance_name: Name of Python variable that points to the sentinel object.
                          Needed for serialization (like :mod:`pickle`) and also nice :func:`repr`.

    :param repr: Any custom string that will be returned by func:`repr`.
                 By default, composed as ``{module_name}.{instance_name}``.
    """
    # pylint: disable=redefined-builtin

    module_name = _get_caller_module_name()
    assert module_name

    SentinelValueSubclass = _create_sentinel_value_subclass(instance_name, module_name)

    if repr:
        SentinelValueSubclass.__repr__ = lambda self: repr  # type: ignore

    return SentinelValueSubclass(instance_name, module_name)


def _get_caller_module_name() -> Optional[str]:
    # Walk over the call stack, and stop as soon as we leave this (sentinel_value) module.
    frame = inspect.currentframe()
    while frame:
        module_name: str = frame.f_globals["__name__"]

        if module_name != __name__:
            return module_name

        frame = frame.f_back

    # Normally the code should never reach this point.
    # It may be only the case when stack inspectio is not available
    # (on some alternative Python implementation, like maybe Jython)
    return None


def _create_sentinel_value_subclass(instance_name: str, module_name: str) -> Type[SentinelValue]:
    module = sys.modules[module_name]

    # Genarate class name from variable name.
    # E.g.: MISSING -> _sentinel_type_MISSING
    class_name = "_sentinel_type_" + instance_name.replace(".", "_")

    # Class should be created only once, so first check if it was already created.
    if hasattr(module, class_name):
        existing_class: Type[SentinelValue] = getattr(module, class_name)
        assert issubclass(existing_class, SentinelValue)
        return existing_class

    # Create a new subclass of SentinelValue.
    SentinelValueSubclass = type(class_name, (SentinelValue,), {})

    # Bind class with the module.
    # That modifies module's globals, so the class really becomes a member of the module,
    # indistinguishable from classes that you define in the code.
    setattr(module, class_name, SentinelValueSubclass)
    SentinelValueSubclass.__module__ = module_name

    return SentinelValueSubclass
