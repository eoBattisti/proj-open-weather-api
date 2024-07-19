#!/usr/bin/env bash

set -e


echo "Starting FastAPI application as `whoami` in mode $MODE"
uvicorn --reload --host $HOST --port $PORT main:app
