#!/usr/bin/env bash
set -e -o pipefail

docker stop ${DB_NAME} || true
docker rm ${DB_NAME} || true

mkdir -p $(pwd)/tmp/
cid=$(docker run --name ${DB_NAME} -d -p ${DB_PORT}:5432 -e POSTGRES_PASSWORD=${DB_PASSWORD} -v $(pwd)/tmp/postgres-data:/var/lib/postgresql/data postgres:12.5)
sleep 10
docker exec ${cid} bash -c "exec psql -h ${DB_HOST} -U ${DB_USERNAME} -c 'CREATE DATABASE ${DB_NAME}'"
docker logs -f $cid
