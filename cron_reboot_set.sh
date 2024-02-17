

echo "Starting the cron_reboot_set job"

export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python3 lib/cron_reboot_set.py

sleep 120

# python3 lib/cron.py