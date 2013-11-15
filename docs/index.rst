
.. freeze documentation master file, created by
   sphinx-quickstart on Fri Mar 22 02:27:13 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Freeze - hash / sort / compare / diff anything
==============================================


ATTENTION: I now have enough experience to design clean interface for freeze.
So if there is no bugfix version, the next version will break things.

* freeze_fast will become freeze (because only cycle free datastructures can
  truely be frozen
* freeze becomes dump, freeze_stable becomes dump_stable
    - Their purpose is unit-testing or dumping for analysis
    - There will be an option to select unit-test or dump mode

.. toctree::
   :maxdepth: 2

.. autosummary::

   
   freeze.freeze
   freeze.freeze_fast
   freeze.freeze_stable
   freeze.tree_diff_assert
   freeze.stable_hash
   freeze.recursive_hash
   freeze.tree_diff
   freeze.flatten
   freeze.frozen_equal_assert
   freeze.vformat
   freeze.transparent_repr
   freeze.traverse_frozen_data
   freeze.TraversalBasedReprCompare

.. automodule:: freeze
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

