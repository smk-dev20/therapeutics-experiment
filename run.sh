#!/bin/bash
docker compose up -d postgres_db
echo "Postgresql container creation complete..."

docker compose build
echo "build of python application complete"

docker compose up python_app