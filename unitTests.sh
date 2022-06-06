#!/bin/bash

# initialize the test database and run unit tests
# please update the tokens for director and instructor in setup.sh before running the test

dropdb course_catalog_test --if-exists
createdb course_catalog_test
psql course_catalog_test < courseCatalog.psql > /dev/null
source setup.sh
python3 test_app.py
