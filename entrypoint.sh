#!/bin/sh

echo "Running migrations"
alembic upgrade head

echo "Starting server"
exec "$@"