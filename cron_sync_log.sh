

echo "Starting the cron_sync_log job"

export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cron_sync_log.py