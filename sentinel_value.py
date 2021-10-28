from typing import Set


class Sentinel:
    """A class that allows to create special marker objects.

    Mostly useful for distinguishing "value is not set" and "value is set to None" cases,
    as shown in this example::

        >>> from sentinel_value import Sentinel

        >>> NotSet = Sentinel('NotSet', __name__)

        >>> value = getattr(object, 'some_attribute', NotSet)
        >>> if value is NotSet:
        ...    print('attribute is not set')
        attribute is not set
    """

    registered_names: Set[str] = set()

    def __init__(self, instance_name: str, module_name: str) -> None:
        qualified_name = module_name + "." + instance_name

        if qualified_name in self.registered_names:
            raise AssertionError(f"Sentinel with name `{qualified_name}` is already registered.")
        self.registered_names.add(qualified_name)

        self.short_name = instance_name
        self.qualified_name = qualified_name

        super().__init__()

    def __str__(self):
        return self.short_name

    def __repr__(self):
        return self.qualified_name

    @staticmethod
    def __bool__():
        return False
