#!/usr/bin/env bash

set -e
set -x

echo "Running development tests..."
python3 -m pytest . --disable-warnings --cov --maxfail=1
