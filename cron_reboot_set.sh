

echo "Starting the cron_reboot_set job"

export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd $APP_DIR

python lib/cron_reboot_set.py

sleep 120

# python lib/cron.py