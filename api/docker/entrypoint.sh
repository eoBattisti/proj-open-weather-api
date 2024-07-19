#!/usr/bin/env bash

set -e

database="$POSTGRES_DATABASE"
host="$POSTGRES_HOST"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -d "$database" -U "$POSTGRES_USER" -c '\q'; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
done

echo "Starting FastAPI application as `whoami` in mode $MODE"
uvicorn --reload --host $HOST --port $PORT main:app
