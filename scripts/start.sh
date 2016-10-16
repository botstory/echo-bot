#!/usr/bin/env bash

gunicorn echo.main:app --bind 0.0.0.0:8080 --log-file - --reload --worker-class aiohttp.worker.GunicornWebWorker
