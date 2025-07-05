#!/bin/bash
git pull
chmod 755 superset_home
chmod 755 dbdata
docker-compose up -d --build app

