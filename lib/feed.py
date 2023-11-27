import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
from threading import Timer, Thread
from aquarium_iot import init_feeding_sequence

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    try:
        init_feeding_sequence()

    finally:
        GPIO.cleanup()