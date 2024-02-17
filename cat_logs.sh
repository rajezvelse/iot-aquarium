export APP_DIR=/media/pi/PENDRIVE8GB/iot/
export PYTHONPATH=$APP_DIR
cd "$APP_DIR/logs"

cat /var/log/cron.log 
cat "$(ls -t | head -n 1)" 