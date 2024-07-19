#!/usr/bin/env bash

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
echo "MODE: $MODE"
if [ "$MODE" == "ci" ]; then 
  pip install -r requirements/ci.txt
else
  pip install -r requirements/main.txt
fi
