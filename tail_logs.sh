#!/bin/bash

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd "$APP_DIR/logs"

tail  -n 50 -f /var/log/cron.log "$(ls -t | head -n 1)" 