import inspect
import sys
import threading
from typing import Dict, Optional, Type


class SentinelValue:
    """Class for special unique placeholder objects, akin to :data:`None` and :data:`Ellipsis`.

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

    def __init__(self, instance_name: str, module_name: str) -> None:
        """Initialize :class:`SentinelValue` object.

        :param instance_name: name of Python variable that points to the sentinel value.
        :param module_name: name of Python module that hosts the sentinel value.
                            In the majority of cases you should pass ``__name__`` here.
        """
        self.instance_name = instance_name
        self.module_name = module_name
        self.qualified_name = self._compose_qualified_name(instance_name, module_name)

        super().__init__()

    def __new__(cls, instance_name, module_name):
        """Create 1 instance of SentinelValue per name.

        Usually, when you call a class, you expect to get a new instance on each call.

        This is not true for the :class:`SentinelValue` class, that overrides :meth:`object.__new__`
        method to alter the way new instances are created.

        The overriden :meth:`SentinelValue.__new__` method constructs 1 unique instance per name,
        then saves it in the global registry called :data:`sentinel_value_instances`,
        and then next time it returns an already existing object.

        That is, if you call :class:`SentinelValue` multiple times with the same arguments,
        you get the *exactly same* instance, check this out::

          >>> MISSING1 = SentinelValue("MISSING", __name__)
          >>> MISSING2 = SentinelValue("MISSING", __name__)

          >>> MISSING1 is MISSING2
          True

        That guarantees that for each name, there is only 1 unique sentinel object.

        This is needed for 2 things:

        1. :mod:`pickle` - when a sentinel value is pickled/un-pickled,
           you get the same instance (not a copy).

        2. Hot code reloading

           Many IDEs can re-load individual modules on the fly, without re-starting
           the whole Python process. So this uniqueness trick allows to avoid duplicate instances
           that would  appear if the module (containing sentinel value definition) is re-loaded.

           This is also nice when working with a Python shell.
           You can re-send ``SentinelValue()`` calls over and over again to the shell,
           and that wouldn't break your code (that already references the instance).

        """
        qualified_name = cls._compose_qualified_name(instance_name, module_name)

        # The create-if-not-exists kind operation has to be protected with a lock.
        #
        # Otherwise, two (or more) concurrent threads will both see that a sentinel value
        # doensn't exist yet, both will create a new instance, and thus you get a duplicate.
        #
        # Well, of course, there is GIL (Global Interpreted Lock), that, in theory,
        # should protect us as long as we're not doing any I/O, but, there are no guarantees
        # about the GIL, and who knows what would # happen in the future.
        #
        # So let's just not rely on GIL, and just use 1 custom lock here,
        # that guarantees that a new object is really created only once.
        with sentinel_create_lock:
            # Check if the instance already exists in the global registry.
            existing_instance = sentinel_value_instances.get(qualified_name)
            if existing_instance is not None:
                # Change class on the fly. This is needed hot live code reloading features.
                # That is, if a subclass of SentinelValue was re-defined,
                # then we want to switch to the new class (but still use the old instance).
                # A bit hacky, but works.
                if existing_instance.__class__ is not cls:
                    existing_instance.__class__ = cls
                return existing_instance

            # Ok, no existing instance.
            # Then create a new one, and put it to the global registry.
            new_instance = super().__new__(cls)
            sentinel_value_instances[qualified_name] = new_instance
            return new_instance

    def __getnewargs__(self):
        # Get arguments for the __new__ method.
        # This is needed for pickle serialization.
        # In combination with magic in the overriden __new__() method above,
        # that allows to avoid constructing duplicates when un-pickling the object.
        return (self.instance_name, self.module_name)

    @staticmethod
    def _compose_qualified_name(instance_name: str, module_name: str) -> str:
        return module_name + "." + instance_name

    def __repr__(self):
        """Provide :func:`repr` for :class:`SentinelValue`.

        By default, looks like this::

            <MISSING>

        You're free to override it in a subclass if you want to customize it.
        """
        return "<" + self.instance_name + ">"

    @staticmethod
    def __bool__():
        """Return False when :class:`SentinelValue` is treated as :func:`bool`.

        Sentinel values are always falsy.

        This is done because most sentinel objects are "no value" kind of objects
        (they're like ``None``, but just not the ``None`` object).

        So it is often handy to do ``if not value`` to check if there is no value
        (like if an attribute is set to ``None``, or not set at all)::

           >>> NOT_SET = SentinelValue("NOT_SET", __name__)

           >>> value = getattr(object, "foobar", NOT_SET)

           # Is the value None, or empty, or not set at all?
           >>> if not value:
           ...    print("no value")
           no value

        If this doesn't fit your case, you can override this method in a subclass.
        """
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
    # E.g.: MISSING -> _sentinel_MISSING
    class_name = "_sentinel_" + instance_name.replace(".", "_")

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
