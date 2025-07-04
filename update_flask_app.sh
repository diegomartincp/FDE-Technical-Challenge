#!/bin/bash
git pull
docker-compose build --no-cache app
docker-compose up -d app