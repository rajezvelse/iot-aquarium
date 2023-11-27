import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import multiprocessing
import json
import os

# GPIO PIN config
SWITCH_1 = 17
SWITCH_2 = 27
SWITCH_3 = 22
SWITCH_4 = 23
SERVO_1 = 24

# Schedule times
FEEDING_TIMES = [8, 18]
FEEDING_BUFFER = 2 # Hours
LIGHT_ON_TIME = 13
LIGHT_OFF_TIME = 21

FILTER_SWITCH = SWITCH_1
LIGHT_SWITCH = SWITCH_2
FEEDER_SERVO = SERVO_1

tasks = []

def log(msg):
    now = datetime.now().isoformat()
    print("[%s] %s" % (now, msg))

def setup():
    GPIO.setmode(GPIO.BCM)

def on(pin):
    log("Switching on")
    GPIO.setup(pin, GPIO.OUT)


def off(pin):
    log("Switching off")
    GPIO.setup(pin, GPIO.IN)


def servo_360(pin):
    log("Starting servo 360")
    # Set up pin for PWM
    GPIO.setup(pin, GPIO.OUT)  # Sets up pin to an output (instead of an input)
    p = GPIO.PWM(pin, 50)  # GPIO pin for PWM with 50Hz
    p.start(0)  # Starts running PWM on the pin and sets it to 0

    p.ChangeDutyCycle(7.4)
    sleep(2.1)
    p.stop()


def init_feeding_sequence():
    log("Initiating feeding sequence...")
    log("Power off the Filter")
    on(FILTER_SWITCH)  # Switch off filter (Normaly closed)
    sleep(10)

    log("Starting to feed")
    servo_360(FEEDER_SERVO)
    f = open("status.json", "r+")
    status = json.load(f)
    status['last_feed_time'] = datetime.now().replace(microsecond=0).isoformat()
    json.dump(status, f)
    f.close()

    log("Waiting for the feed consumption (15 mins)")
    sleep(15 * 60)  # minutes

    log("Power on the Filter")
    off(FILTER_SWITCH)

def clean():
    log("Cleaning all GPIO config...")
    GPIO.cleanup()

def delayed_process(interval, target, *args, **kwargs):
    def d_func(**kwargs):
        sleep(interval)
        target(**kwargs)

    return multiprocessing.Process(target=d_func, *args, **kwargs)


def main():
    global tasks
    now = datetime.now()
    current_hour = now.hour
    

    # Manage lighting
    if current_hour >= LIGHT_ON_TIME and current_hour < LIGHT_OFF_TIME:
        log("Switching on light")
        on(LIGHT_SWITCH)
    elif current_hour < LIGHT_ON_TIME:
        log("Scheduling switching on timer for light")
        light_on_time = datetime(now.year, now.month, now.day, LIGHT_ON_TIME, 0, 0) 
        t = delayed_process((light_on_time-now).seconds, target=lambda: on(LIGHT_SWITCH))
        tasks.append(t)
        t.start()


    log("Scheduling switching off timer for light")
    light_off_time = datetime(now.year, now.month, now.day, LIGHT_OFF_TIME, 0, 0) 
    t = delayed_process((light_off_time-now).seconds, target=lambda: off(LIGHT_SWITCH))
    tasks.append(t)
    t.start()

    # Manage feeding
    f = open("status.json", "r")
    status = json.load(f)
    f.close()

    last_feed_time = datetime.strptime(status['last_feed_time'], "%Y-%m-%dT%H:%M:%S")

    for feed_time in FEEDING_TIMES:
        if feed_time > current_hour:
            log("scheduling feeding at hour : %d" % (feed_time,))
            f_time = datetime(now.year, now.month, now.day, feed_time, 0, 0) 
            t = delayed_process((f_time-now).seconds, target=init_feeding_sequence)
            tasks.append(t)
            t.start()
        elif current_hour - feed_time <= FEEDING_BUFFER:
            if current_hour - last_feed_time.hour < 8:
                log("Last feed processed at: %s. Skipping now" % (status['last_feed_time'],))
                continue
            
            log("Starting immediate feeding")
            t = multiprocessing.Process(target=init_feeding_sequence)
            tasks.append(t)
            t.start()

    # Wait to compelete all parallel tasks
    while len(tasks) > 0:
        sleep(60)
        tasks = list(filter(lambda t: t.is_alive(), tasks))
        log("Checked tasks status")

if __name__ == "__main__":
    setup()
    try:
        main()
    except KeyboardInterrupt:
        
        log('Interrupted')
        for t in tasks:
            if t.is_alive():
                t.terminate()
                
        # os.system("sudo reboot")
    finally:
        clean()
