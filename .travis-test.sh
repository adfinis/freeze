#!/usr/bin/env bash

nosetests --with-doctest --doctest-tests --cover-package=freeze --with-coverage --cover-tests --cover-erase --cover-min-percentage=100
