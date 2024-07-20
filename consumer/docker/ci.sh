#!/usr/bin/env bash

set -e
set -x

echo "Installing requirements..."
pip install --quiet -r requirements/ci.txt

echo "Running development tests..."
python3 -m pytest . --disable-warnings --cov --maxfail=1 --cov-report=term-missing
