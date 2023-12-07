import aquarium_iot as aiot
from datetime import datetime, timedelta
import math

schedules = [
    aiot.switch_on_co2,
    aiot.switch_off_co2,
    aiot.switch_on_light,
    aiot.switch_off_light,
]

if __name__ == "__main__":
    aiot.log("Starting cron_reboot_set")
    aiot.setup()

    try:
        for fn in schedules:
            fn_name = fn.__name__

            now = datetime.now()
            start_of_day = datetime(
                year=now.year, month=now.month, day=now.day, hour=0, second=0
            )

            aiot.set_previous_state(fn_name, start_of_day)

        aiot.log("Finished cron_reboot_set")

    except Exception as e:
        aiot.log("Error: " + str(e), "error")

        # aiot.clean()

        # os.system("sudo reboot")
    # finally:
    # aiot.clean()
