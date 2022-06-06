#!/bin/bash

#initialize the test database and run unit tests

dropdb course_catalog_test --if-exists
createdb course_catalog_test
psql course_catalog_test < courseCatalog.psql > /dev/null
python3 test_app.py
