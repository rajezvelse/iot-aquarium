export APP_DIR=/home/pi/iot/
export PYTHONPATH=$APP_DIR
cd "$APP_DIR/logs"

cat /var/log/cron.log 
cat "$(ls -t | head -n 1)" 