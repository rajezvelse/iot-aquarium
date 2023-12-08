
import gdrive_lib as glib
from datetime import datetime

logs_dir = glib.config["logs_dir"]
logger = glib.config["logger"]


if __name__ == "__main__":
    logger.info("Starting cron_sync_log")

    try:
        today = datetime.now()
        log_name = "aquarium_iot_%d_%d_%d.log" % (today.year, today.month, today.day)
        file_to_upload = logs_dir.joinpath(log_name)

        glib.upload_file(file_to_upload)

        logger.info("Finished cron_sync_log")

    except Exception as e:
        logger.error("Error: " + str(e))
