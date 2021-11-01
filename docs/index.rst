.. currentmodule:: sentinel_value

Overview
========

.. Warning::

   The code is at the early development stage, and may be unstable.

   Use with caution.


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

- better ``repr()``
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


.. rubric:: Other members of the module

.. autosummary::
   sentinel_value_instances
   sentinel_create_lock
   sentinel

.. automodule:: sentinel_value
