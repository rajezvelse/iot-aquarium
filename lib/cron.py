import aquarium_iot as aiot
from datetime import datetime, timedelta
import math

schedules = [
    (aiot.CO2_ON_TIME, aiot.switch_on_co2, aiot.CO2_OFF_TIME),
    (aiot.CO2_OFF_TIME, aiot.switch_off_co2, 23.59),
    (aiot.LIGHT_ON_TIME, aiot.switch_on_light, aiot.LIGHT_OFF_TIME),
    (aiot.LIGHT_OFF_TIME, aiot.switch_off_light, 23.59),
    (aiot.FEEDING_TIMES[0], aiot.start_food_feed, aiot.FEEDING_TIMES[0] + aiot.FEEDING_BUFFER),
    (aiot.FEEDING_TIMES[1], aiot.start_food_feed, aiot.FEEDING_TIMES[1] + aiot.FEEDING_BUFFER),
]

if __name__ == "__main__":
    
    aiot.log("Starting cron")
    aiot.setup()
    
    try:
        for schedule in schedules:
            t, fn, buffer = schedule
            fn_name = fn.__name__

            now = datetime.now()
            exec_time = aiot.get_dt(t)
            buff_time = aiot.get_dt(buffer)

            in_next_x_mins = now <= exec_time < now + timedelta(minutes=30)
            in_past = exec_time < now

            last_execution_time = aiot.get_previous_state(fn_name)
            already_executed = last_execution_time and exec_time <= last_execution_time < buff_time
            
            if (in_past and already_executed) or (not in_past and not in_next_x_mins):
                continue
            
            aiot.log("Executing " + fn_name)    
            fn()
            aiot.set_previous_state(fn_name, now)

        
        aiot.log("Finished cron")

    except KeyboardInterrupt:
        aiot.log("Interrupted")

        # os.system("sudo reboot")
    finally:
        aiot.clean()
