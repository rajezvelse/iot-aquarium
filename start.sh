#!/bin/bash


# cd lib

# echo "Starting the scriptaquarium_iot.py"

# cd /home/pi/iot/
# python3 aquarium_iot.py


wait_period=0

. cron_reboot_set.sh

while true
do
    printf "\nTime Now: `date +%H:%M:%S`"

    . cron.sh

    printf "\nSleeping for 30 minutes"
    # Here 300 is 300 seconds i.e. 5 minutes * 60 = 300 sec
    wait_period=$(($wait_period+10))
    if [ $wait_period -gt 300 ];then
       echo "The script successfully ran, exiting now.."
       break
    else
       sleep 1800
    fi
done