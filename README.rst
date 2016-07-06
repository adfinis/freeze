======================================================
Freeze - dump / hash / sort / compare / diff anything
======================================================

|travis| |coverage| [1]_

.. |travis|  image:: https://travis-ci.org/adfinis-sygroup/freeze.png?branch=master
   :target: https://travis-ci.org/adfinis-sygroup/freeze
.. |coverage| image:: https://img.shields.io/badge/coverage-100%25-brightgreen.svg

.. [1] Coverage enforced by tests (on travis)

`Read the Docs`_

.. _`Read the Docs`: https://docs.adfinis-sygroup.ch/public/freeze/

Freeze the state of data-structures and objects for data-analysis or testing
(diffing data-structures). Frozen data-structures consist of only tuples and
these are comparable/sortable/hashable. The freeze() function can be used for
many purposes for example implement __hash__() for your complex object very
fast. dump() is intended for testing and analysis.

Authors: Jean-Louis Fuchs <ganwell@fangorn.ch> https://github.com/ganwell

Install Debian/Ubuntu
=====================

Sources:

.. code-block:: text

   deb https://aptly.ad-sy.ch/adsy-public/debian wheezy main

   deb https://aptly.ad-sy.ch/adsy-public/debian jessie main

   deb https://aptly.ad-sy.ch/adsy-public/ubuntu trusty main

   deb https://aptly.ad-sy.ch/adsy-public/ubuntu vivid main

   deb https://aptly.ad-sy.ch/adsy-public/ubuntu xenial main

Install:

.. code-block:: bash

   apt-get update
   apt-get install python-freeze
