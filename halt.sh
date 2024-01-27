#!/bin/bash



echo "Starting the script $PWD/cleanup.py"

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cleanup.py

sudo halt

