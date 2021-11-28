sentinel-value
==============

|pypi badge| |build badge| |docs badge|


``sentinel-value`` is a Python package, that helps to create `Sentinel Values`_ -
special singleton objects, akin to ``None``, ``NotImplemented`` and  ``Ellipsis``.

It implements the ``sentinel()`` function (described by `PEP 661`_),
and for advanced cases it also provides the ``SentinelValue()`` class (not a part of `PEP 661`_).

.. _`Sentinel Values`: https://en.wikipedia.org/wiki/Sentinel_value
.. _`PEP 661`: https://www.python.org/dev/peps/pep-0661


Usage example:

.. code:: python

  from sentinel_value import sentinel

  MISSING = sentinel("MISSING")

  def get_something(default=MISSING):
      ...
      if default is not MISSING:
          return default
      ...


Or, the same thing, but using the ``SentinelValue`` class
(slightly more verbose, but allows to have nice type annotations):

.. code:: python

  from typing import Union
  from sentinel_value import SentinelValue

  class Missing(SentinelValue):
      pass

  MISSING = Missing(__name__, "MISSING")

  def get_something(default: Union[str, Missing] = MISSING):
      ...
      if default is not MISSING:
          return default
      ...


Links
-----

- Read the Docs: https://sentinel-value.readthedocs.io
- GitHub repository: https://github.com/vdmit11/sentinel-value
- Python package: https://pypi.org/project/sentinel-value/


.. |pypi badge| image:: https://img.shields.io/pypi/v/sentinel-value.svg
  :target: https://pypi.org/project/sentinel-value/
  :alt: Python package version

.. |build badge| image:: https://github.com/vdmit11/sentinel-value/actions/workflows/build.yml/badge.svg
  :target: https://github.com/vdmit11/sentinel-value/actions/workflows/build.yml
  :alt: Tests Status

.. |docs badge| image:: https://readthedocs.org/projects/sentinel-value/badge/?version=latest
  :target: https://sentinel-value.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

