#!/bin/bash

pytest -rx tests_sitl/test_*.py -W ignore::DeprecationWarning --log-level=INFO