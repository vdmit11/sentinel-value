.. currentmodule:: sentinel_value

Overview
========

.. Warning::

   The code is at the early development stage, and may be unstable.

   Use with caution.


.. contents::


Work In Progress...
===================

.. code-block::

:func:`sentinel` creates 1 instance per name. Check this out::

   >>> from sentinel_value import sentinel

  >>> MISSING1 = sentinel("MISSING1")
  >>> MISSING2 = sentinel("MISSING2")

  >>> MISSING1 is MISSING2
  False

  # Duplicate is done only for demonstration purposes.
  # You should never do this in your code.
  # That gives bad repr(), and also may cause problems with pickling.
  # In your code, you should always have only 1 variable,
  # and its name should match to the argument passed to the sentinel() function.
  >>> MISSING2_duplicate = sentinel("MISSING2")
  
  >>> MISSING2_duplicate is MISSING2
  True
  
That is, on the 2nd call, you get the *exactly same* object.

This is needed for:

1. :mod:`pickle` serialization.

   That is, when you pickle/un-pickle sentinel values,
   you get references to global objects (and not their copies)


2. Reloading parts of your code (without restarting the whole Python process).

   That is, you can send (and re-send) code to IPython shell, and it wouldn't break
   because of some ``MISSING`` object that was replaced with a new instance by an accident.

API reference
=============

.. rubric:: class SentinelValue

.. autosummary::

      SentinelValue


.. rubric:: Other members of the module

.. autosummary::
   sentinel_value_instances


.. automodule:: sentinel_value
