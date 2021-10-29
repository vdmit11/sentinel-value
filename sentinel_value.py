from typing import Dict


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

    def __new__(cls, variable_name, module_name):  # noqa: D103
        qualified_name = cls._compose_qualified_name(variable_name, module_name)

        existing_instance = registered_sentinel_value_instances.get(qualified_name)
        if existing_instance is not None:
            return existing_instance

        new_instance = super().__new__(cls)
        registered_sentinel_value_instances[qualified_name] = new_instance
        return new_instance

    @staticmethod
    def _compose_qualified_name(variable_name: str, module_name: str) -> str:
        return module_name + "." + variable_name

    def __init__(self, variable_name: str, module_name: str) -> None:
        self.short_name = variable_name
        self.qualified_name = self._compose_qualified_name(variable_name, module_name)

        super().__init__()

    def __str__(self):
        return self.short_name

    def __repr__(self):
        return self.qualified_name

    @staticmethod
    def __bool__():
        return False


registered_sentinel_value_instances: Dict[str, SentinelValue] = {}
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
