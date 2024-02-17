

echo "Starting the cron job"

export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cron.py