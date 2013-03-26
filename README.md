Freeze - hash / sort / compare / diff anything
==============================================

[![Build Status](https://travis-ci.org/adfinis-sygroup/freeze.png?branch=master)](https://travis-ci.org/adfinis-sygroup/freeze)

Freeze the state of data-structures and objects for data-analysis or testing (diffing data-structures).

Docs: https://freeze.readthedocs.org/en/latest/

Dev version docs: https://freeze.readthedocs.org/en/dev/

TODO
----

* Would using generators everywhere improve anything? Difflib supports
  generators, so we might save some memory creating diffs?!
* If we used generators, I'd have to find or write a generator stream
  that would be used with pprint.pprint(stream=generator_stream)
