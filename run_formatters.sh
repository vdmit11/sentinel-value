#!/usr/bin/env sh

set -e
set -x

isort .
black .
