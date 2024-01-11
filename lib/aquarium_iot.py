import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import multiprocessing
import json
import os
import math
import logging
import settings


# GPIO PIN config
SWITCH_1 = 17
SWITCH_2 = 27
SWITCH_3 = 22
SWITCH_4 = 23
SERVO_1 = 24

# Schedule times
REBOOT_TIMES = [6, 9, 21.30, 23.30]
FEEDING_TIMES = [8, 18]
FEEDING_BUFFER = 2  # Hours
LIGHT_ON_TIME = 13
LIGHT_OFF_TIME = 20

CO2_ON_TIME = 10
CO2_OFF_TIME = 21

FILTER_SWITCH = SWITCH_1
LIGHT_SWITCH = SWITCH_2
CO2_SWITCH = SWITCH_3
FEEDER_SERVO = SERVO_1
FEEDER_SERVO_SWITCH = SWITCH_4


config = settings.get_config("aquarium_iot")
logger = config["logger"]
APP_DIR = config["app_dir"]


tasks = []


def log(msg, type=None):
    global logger

    if type == "error":
        logger.error(msg)
    elif type == "debug":
        logger.debug(msg)
    else:
        logger.info(msg)


def reboot():
    log("Running reboot")
    os.system("sudo reboot")


def get_dt(t):
    now = datetime.now()
    m, h = math.modf(t)
    m = int(m * 100)
    h = int(h)
    return datetime(now.year, now.month, now.day, h, m, 0)


def get_previous_state(name):
    global APP_DIR
    f = open(APP_DIR + "status.json", "r")
    status = json.load(f)
    f.close()

    if status.get(name, None):
        return datetime.strptime(status[name], "%Y-%m-%dT%H:%M:%S")
    else:
        return None


def set_previous_state(name, t=None):
    log("Updating prev state for: " + name)
    global APP_DIR
    f = open(APP_DIR + "status.json", "r+")
    status = json.load(f)

    if not t:
        t = datetime.now()

    status[name] = t.replace(microsecond=0).isoformat()
    f.seek(0)
    json.dump(status, f)
    f.truncate()
    f.close()


def setup():
    GPIO.setmode(GPIO.BCM)


def on(pin):
    log("Switching on")
    GPIO.setup(pin, GPIO.OUT)
    # GPIO.output(pin, 1)


def off(pin):
    log("Switching off")
    # GPIO.output(pin, 0)
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
    sleep(200 / 1000)  # 100 millisecods
    GPIO.setup(pin, GPIO.IN)


def init_feeding_sequence():
    log("Initiating feeding sequence...")
    log("Power off the Filter")
    on(FILTER_SWITCH)  # Switch off filter (Normaly closed)
    sleep(10)

    log("Starting to feed")
    on(FEEDER_SERVO_SWITCH)
    sleep(1)
    servo_360(FEEDER_SERVO)
    # sleep(5)
    # servo_360(FEEDER_SERVO)
    sleep(500 / 1000)  # 100 millisecods
    off(FEEDER_SERVO_SWITCH)

    set_previous_state("last_feed_time")

    log("Waiting for the feed consumption (15 mins)")
    sleep(15 * 60)  # minutes

    log("Power on the Filter")
    off(FILTER_SWITCH)


def switch_on_co2():
    log("Switching on Co2")
    on(CO2_SWITCH)


def switch_off_co2():
    log("Switching off Co2")
    off(CO2_SWITCH)


def switch_on_light():
    log("Switching on light")
    on(LIGHT_SWITCH)


def switch_off_light():
    log("Switching off light")
    off(LIGHT_SWITCH)


def start_food_feed():
    global APP_DIR
    f = open(APP_DIR + "status.json", "r")
    status = json.load(f)
    f.close()

    log("Last feed processed at: %s" % (status["last_feed_time"],))
    last_feed_time = datetime.strptime(status["last_feed_time"], "%Y-%m-%dT%H:%M:%S")
    now = datetime.now()
    if divmod((now - last_feed_time).total_seconds(), 3600)[0] < 8:
        log("More frequent to feed. skipping now")
        return

    init_feeding_sequence()


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

    # Manage Co2
    co2_on_m, co2_on_h = math.modf(CO2_ON_TIME)
    co2_on_m = int(co2_on_m * 100)
    co2_on_h = int(co2_on_h)
    co2_on_time = datetime(now.year, now.month, now.day, co2_on_h, co2_on_m, 0)

    co2_off_m, co2_off_h = math.modf(CO2_OFF_TIME)
    co2_off_m = int(co2_off_m * 100)
    co2_off_h = int(co2_off_h)
    co2_off_time = datetime(now.year, now.month, now.day, co2_off_h, co2_on_m, 0)
    if now >= co2_on_time and now < co2_off_time:
        switch_on_co2()
    elif now < co2_on_time:
        log("Scheduling switching on timer for Co2")
        t = delayed_process((co2_on_time - now).seconds, target=lambda: on(CO2_SWITCH))
        tasks.append(t)
        t.start()

    log("Scheduling switching off timer for Co2")
    light_off_time = datetime(now.year, now.month, now.day, LIGHT_OFF_TIME, 0, 0)
    t = delayed_process(
        (light_off_time - now).seconds, target=lambda: off(LIGHT_SWITCH)
    )
    tasks.append(t)
    t.start()

    # Manage lighting
    if current_hour >= LIGHT_ON_TIME and current_hour < LIGHT_OFF_TIME:
        log("Switching on light")
        on(LIGHT_SWITCH)
    elif current_hour < LIGHT_ON_TIME:
        log("Scheduling switching on timer for light")
        light_on_time = datetime(now.year, now.month, now.day, LIGHT_ON_TIME, 0, 0)
        t = delayed_process(
            (light_on_time - now).seconds, target=lambda: on(LIGHT_SWITCH)
        )
        tasks.append(t)
        t.start()

    log("Scheduling switching off timer for light")
    light_off_time = datetime(now.year, now.month, now.day, LIGHT_OFF_TIME, 0, 0)
    t = delayed_process(
        (light_off_time - now).seconds, target=lambda: off(LIGHT_SWITCH)
    )
    tasks.append(t)
    t.start()

    # Manage feeding
    global APP_DIR
    f = open(APP_DIR + "status.json", "r")
    status = json.load(f)
    f.close()

    last_feed_time = datetime.strptime(status["last_feed_time"], "%Y-%m-%dT%H:%M:%S")

    for feed_time in FEEDING_TIMES:
        if feed_time > current_hour:
            log("scheduling feeding at hour : %d" % (feed_time,))
            f_time = datetime(now.year, now.month, now.day, feed_time, 0, 0)
            t = delayed_process((f_time - now).seconds, target=init_feeding_sequence)
            tasks.append(t)
            t.start()
        elif current_hour - feed_time <= FEEDING_BUFFER:
            log("Last feed processed at: %s" % (status["last_feed_time"],))
            if divmod((now - last_feed_time).total_seconds(), 3600)[0] < 8:
                log("Skipping now")
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
        log("Interrupted")
        for t in tasks:
            if t.is_alive():
                t.terminate()

        # os.system("sudo reboot")
    finally:
        clean()
