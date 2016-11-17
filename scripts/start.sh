#!/usr/bin/env bash

echo "====================================================="
echo ""
echo " Setup"
echo ""
echo "====================================================="

./echo/main.py

echo "====================================================="
echo ""
echo " Start"
echo ""
echo "====================================================="

gunicorn echo.gunicorn_runner:app --bind 0.0.0.0:${PORT} --log-file - --reload --worker-class aiohttp.worker.GunicornWebWorker
