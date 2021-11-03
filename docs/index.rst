.. currentmodule:: sentinel_value

Overview
========

.. contents::


``sentinel-value`` is a Python package, that helps to create `Sentinel Values`_ -
special singleton objects, akin to :data:`None`, :data:`NotImplemented` and :data:`Ellipsis`.

It implements the :func:`sentinel` function (described by `PEP 661`_),
and also :class:`SentinelValue` class for advanced cases (not a part of `PEP 661`_).

.. _`Sentinel Values`: https://en.wikipedia.org/wiki/Sentinel_value
.. _`PEP 661`: https://www.python.org/dev/peps/pep-0661


Usage example::

  >>> from sentinel_value import sentinel

  >>> MISSING = sentinel("MISSING")

  >>> def get_something(default=MISSING):
  ...     ...
  ...     if default is not MISSING:
  ...         return default
  ...     ...


why not just object()?
======================

So, why not just ``MISSING = object()``?

Because sentinel values have some benefits:

- better :func:`repr`
- friendly to :mod:`typing`
- friendly to :mod:`pickle`
- friendly to hot code reloading features of IDEs

So this is not radical killer feature, but more a list of small nice-to-have things.


function sentinel()
===================

:func:`sentinel` function is the simple way to create sentinel objects in 1 line::

  >>> MISSING = sentinel("MISSING")

It produces an instance of :class:`SentinelValue`, with all its features
(uniqueness, pickle-ability, etc), and it just works in most cases.

However, there are some cases where it doesn't work well, and you may want to
directly use the underlying class :class:`SentinelValue`, described below.


class SentinelValue()
=====================

A little bit more advanced way to create sentinel objects is to do this::

  >>> from sentinel_value import SentinelValue

  >>> class Missing(SentinelValue):
  ...     pass

  >>> MISSING = Missing("MISSING", __name__)

Such code is slightly more verbose (than using :func:`sentinel`), but, there are some benfits:

- It is portable (while :func:`sentinel()` is not, because it relies on :class:`inspect.currentframe`).
- It is extensible. You can add and override various methods in your class.
- Class definition is obvious. You can immediately find it in your code when you get
  ``AttributeError: 'Missing' object has no attribute '...'``
- Can be used with :func:`functools.singledispatch`
- Friendly to :mod:`typing` on older Python versions, that don't have :data:`typing.Literal`


Type Annotations
================

`PEP 661`_ suggests to use :data:`typing.Literal`, like this::

  from typing import Literal
  from sentinel_value import sentinel

  NOT_GIVEN = sentinel("NOT_GIVEN")

  def foo(value: int | Literal[NOT_GIVEN]) -> None:
  ...     return None


But, there is a problem: `mypy <http://www.mypy-lang.org/>`_ type checker thinks it is an error:

.. code-block:: no-highlight

  mypy main.py

  main.py:6: error: Parameter 1 of Literal[...] is invalid  [misc]
  main.py:6: error: Variable "main.NOT_GIVEN" is not valid as a type  [valid-type]
  main.py:6: note: See https://mypy.readthedocs.io/en/stable/common_issues.html#variables-vs-type-aliases
  Found 2 errors in 1 file (checked 1 source file)

Maybe such :data:`typing.Literal` expressions will be supported in the future,
but at least now (November 2021, mypy v0.910, Python v3.10.0) it is broken,
and you cannot use ``Literal[SENTINEL_VALUE]`` for type hinting.

So, for now, the only way to have proper type annotations is to avoid :func:`sentinel` function
and instead make your own subclasses of :class:`SentinelValue`, like this::

  >>> from typing import Union
  >>> from sentinel_value import SentinelValue

  >>> class NotGiven(SentinelValue):
  ...     pass

  >>> NOT_GIVEN = NotGiven("NOT_GIVEN", __name__)

  >>> def foo(value: Union[int, NotGiven]) -> None:
  ...     return None

This way it works like a charm, and it doesn't even require :data:`typing.Literal`.

Naming Convention
=================

`PEP 661`_ doesn't enforce any naming convention, however, I (the author of this Python package)
would recommend using ``UPPER_CASE`` for sentinel objects, like this::

  >>> NOT_SET = sentinel("NOT_SET")

or, when subclassing :class:`SentinelValue`:

.. code-block::

  >>> class NotSet(SentinelValue):
  ...     pass

  >>> NOT_SET = NotSet("NotSet", __name__)

Why? Because:

- Sentinel values are unique global constants by definition, and constants are ``NAMED_LIKE_THIS``

- This naming scheme gives slightly less cryptic error messages. For example, this::

    AttributeError: 'NotSet' object has no attribute 'foo'

  reads slightly better (at least to my eye) than this::

    AttributeError: 'NotSetType' object has no attribute 'foo'



API reference
=============

.. rubric:: class SentinelValue

.. autosummary::

      SentinelValue
      SentinelValue.__new__
      SentinelValue.__init__
      SentinelValue.__repr__
      SentinelValue.__bool__


.. rubric:: Other members of the module

.. autosummary::
   sentinel_value_instances
   sentinel_create_lock
   sentinel

.. automodule:: sentinel_value

