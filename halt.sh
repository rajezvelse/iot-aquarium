#!/bin/bash



echo "Starting the script $PWD/cleanup.py"

export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cleanup.py

sudo halt

