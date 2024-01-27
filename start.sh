#!/bin/bash
echo "Starting application..."
exec /usr/bin/supervisord -n
echo "Application started."

