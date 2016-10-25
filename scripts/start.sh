#!/usr/bin/env bash

gunicorn echo.gunicorn_runner:app --bind 0.0.0.0:${PORT} --log-file - --reload --worker-class aiohttp.worker.GunicornWebWorker
