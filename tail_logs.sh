#!/bin/bash

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd "$APP_DIR/logs"

tail  -n 50 -f /var/log/cron.log "$(ls -t aquarium_iot* | head -n 1)"  "$(ls -t sync_log* | head -n 1)"