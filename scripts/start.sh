#!/usr/bin/env bash

export PYTHONPATH=${PYTHONPATH}:$(pwd)

echo "PYTHONPATH"
echo ${PYTHONPATH}

echo "====================================================="
echo ""
echo " Setup"
echo ""
echo "====================================================="

python ./echo/main.py

echo "====================================================="
echo ""
echo " Start"
echo ""
echo "====================================================="

gunicorn echo.gunicorn_runner:app --bind 0.0.0.0:${PORT} --log-file - --reload --worker-class aiohttp.worker.GunicornWebWorker
