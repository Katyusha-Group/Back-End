#!/bin/bash
source /katyusha_env/bin/activate
cd /app

daphne -b 0.0.0.0 -p 8001 core.asgi:application