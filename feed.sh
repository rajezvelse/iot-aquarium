#!/bin/bash



echo "Starting the script $PWD/feed.py"

export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python3 lib/feed.py