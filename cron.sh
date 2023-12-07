

echo "Starting the cron job"

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cron.py