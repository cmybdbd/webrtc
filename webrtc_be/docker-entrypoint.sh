#!/bin/bash

python server.py
# gunicorn -b 0.0.0.0:80 server
# gunicorn server:app --bind localhost:1111 --worker-class aiohttp.worker.GunicornWebWorker
