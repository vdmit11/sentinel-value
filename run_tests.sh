#!/usr/bin/env sh

echo '----------------'

set -e
set -x

pytest --cov=sentinel_value --cov-fail-under=100 $@
