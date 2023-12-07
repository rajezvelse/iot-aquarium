#!/bin/bash



echo "Starting the script $PWD/feed.py"

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/feed.py