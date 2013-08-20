#!/usr/bin/env bash

set -e
nosetests --with-doctest --doctest-tests --cover-package=freeze --with-coverage --cover-tests --cover-erase --cover-min-percentage=100
cd lib
pylama -l pep8,pyflakes,pylint -i E203,E272,E221,E251,E202,E271,C0302,W0511,F0401
