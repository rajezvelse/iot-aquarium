from datetime import datetime
import logging
import pathlib

APP_DIR = "/home/pi/iot/"

# ToDO: Remove this
import pathlib
pwd = pathlib.Path(__file__).parents[1].resolve()
APP_DIR = str(pwd) + "/"

GDRIVE_LOGS_FOLDER_ID = "1i-2dL9fP9yg13r-cjfVAhfbEl04qXT8n"

def get_config(log_name):
    today = datetime.now()
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                APP_DIR
                + "logs/"
                + log_name
                + "_%d_%d_%d.log" % (today.year, today.month, today.day)
            ),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger()

    return {
        "logger": logger,
        "app_dir": APP_DIR,
        "logs_dir": pathlib.Path(APP_DIR + "logs"),
    }

