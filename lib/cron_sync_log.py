import settings
import gdrive_lib as glib


logs_dir = glib.config["logs_dir"]
logger = glib.config["logger"]


if __name__ == "__main__":
    logger.info("Starting cron_sync_log")

    try:
        file_to_upload = logs_dir.joinpath("test.log")

        glib.upload_file(file_to_upload)

        logger.info("Finished cron_sync_log")

    except Exception as e:
        logger.error("Error: " + str(e))
