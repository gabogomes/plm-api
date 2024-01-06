#!/usr/bin/env bash

docker rm -f $(docker ps -aq)
docker rmi plm-api-plm_api:latest
docker rmi postgres:14-alpine
docker rmi flyway/flyway:9
docker volume rm plm-api_postgres_data