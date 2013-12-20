#!/usr/bin/env bash

set -e
if [ "$USE_CYTHON" == "true" ]
then
	pip install cython
	python setup.py build_ext --inplace
	nosetests --with-doctest --doctest-tests
else
	nosetests --with-doctest --doctest-tests --cover-package=freeze --with-coverage --cover-tests --cover-erase --cover-min-percentage=100
fi
cd lib
pylama -l pep8,pyflakes,pylint -i E203,E272,E221,E251,E202,E271,C0302,W0511,F0401
