from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import pathlib
import settings


SERVICE = None

config = settings.get_config("sync_log")
logger = config["logger"]


def get_service():
    logger.info("Creatig GDrive service")
    global SERVICE

    if SERVICE:
        logger.info("Existing service instance found")
        return SERVICE

    cred_file = pathlib.Path(config["app_dir"]).joinpath("client_secrets.json")

    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = service_account.Credentials.from_service_account_file(
        filename=cred_file, scopes=scope
    )
    SERVICE = build("drive", "v3", credentials=credentials)

    logger.info("New service instance created")

    return SERVICE


def list_files():
    logger.info("Listing files")
    service = get_service()
    # Call the Drive v3 API
    results = (
        service.files()
        .list(
            pageSize=1000,
            fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)",
            q=f"'{settings.GDRIVE_LOGS_FOLDER_ID}' in parents",
        )
        .execute()
    )
    # get the results
    items = results.get("files", [])

    return items


def create_file(file_path):
    logger.info("Creating new file in drive")

    try:
        global LOGS_FOLDER_ID
        file_name = file_path.name

        service = get_service()

        file_metadata = {
            "name": file_name,
            "parents": [settings.GDRIVE_LOGS_FOLDER_ID],
        }
        media = MediaFileUpload(filename=file_path, mimetype="text/plain")

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        logger.info("File created")
    except Exception as e:
        logger.error("Error: " + str(e))


def update_file(file_id, file_path):
    logger.info("Updating file in drive")

    try:
        global LOGS_FOLDER_ID

        service = get_service()

        media = MediaFileUpload(filename=file_path, mimetype="text/plain")

        file = (
            service.files()
            .update(fileId=file_id, media_body=media, fields="id")
            .execute()
        )
        logger.info("File updated")
    except Exception as e:
        logger.error("Error: " + str(e))


def upload_file(file_path):
    logger.info("Starting file upload")

    file_name = file_path.name

    exiting_files = list_files()

    existing_file_id = None

    for f in exiting_files:
        if f["name"] == file_name:
            existing_file_id = f["id"]
            break

    if existing_file_id:
        update_file(existing_file_id, file_path)
    else:
        create_file(file_path)

    logger.info("File upload completed")
