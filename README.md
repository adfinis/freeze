Freeze - hash / sort / compare / diff anything
==============================================

[![Build Status](https://travis-ci.org/adfinis-sygroup/freeze.png?branch=master)](https://travis-ci.org/adfinis-sygroup/freeze)

ATTENTION: I now have enough experience to design clean interface for freeze.
So if there is no bugfix version, the next version will break things.

* freeze_fast will become freeze (because only cycle free datastructures can
  truely be frozen
* freeze becomes dump, freeze_stable becomes dump_stable
  * Their purpose is unit-testing or dumping for analysis
  * There will be an option to select unit-test or dump mode

Freeze the state of data-structures and objects for data-analysis or testing (diffing data-structures).

Docs: https://freeze.readthedocs.org/en/latest/

Dev version docs: https://freeze.readthedocs.org/en/dev/

