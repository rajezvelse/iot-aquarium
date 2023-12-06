import aquarium_iot as aiot
from datetime import datetime, timedelta
import math

schedules = [
    (aiot.FEEDING_TIMES[0], aiot.start_food_feed),
    (aiot.FEEDING_TIMES[1], aiot.start_food_feed),
    (aiot.CO2_ON_TIME, aiot.switch_on_co2),
    (aiot.CO2_OFF_TIME, aiot.switch_off_co2),
    (aiot.LIGHT_ON_TIME, aiot.switch_on_light),
    (aiot.LIGHT_OFF_TIME, aiot.switch_off_light),
]

if __name__ == "__main__":
    
    aiot.log("Starting cron")
    aiot.setup()
    
    try:
        for schedule in schedules:
            now = datetime.now()
            m, h = math.modf(schedule[0])
            m = int(m * 100)
            h = int(h)
            time = datetime(now.year, now.month, now.day, h, m, 0)

            if not (now <= time < now + timedelta(minutes=30)):
                continue

            schedule(1)()

        
        aiot.log("Finished cron")

    except KeyboardInterrupt:
        aiot.log("Interrupted")

        # os.system("sudo reboot")
    finally:
        aiot.clean()
