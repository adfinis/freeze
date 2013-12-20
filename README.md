Freeze - hash / sort / compare / diff anything
==============================================

[![Build Status](https://travis-ci.org/adfinis-sygroup/freeze.png?branch=master)](https://travis-ci.org/adfinis-sygroup/freeze)

This release breaks the API:

* freeze_fast became freeze (because only cycle free datastructures can
  truely be frozen
* freeze_* became dump

Freeze the state of data-structures and objects for data-analysis or testing (diffing data-structures).

Docs: https://freeze.readthedocs.org/en/latest/

Dev version docs: https://freeze.readthedocs.org/en/dev/

