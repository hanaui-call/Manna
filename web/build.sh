#!/usr/bin/env bash
python dockerfile_generator.py
docker-compose build web
docker-compose kill web
docker-compose up -d web