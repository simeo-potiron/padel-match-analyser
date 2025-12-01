# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import PACKAGES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Generic Packages
import uuid

# Google Cloud Packages
from google.cloud import storage


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Import GLOBAL VARIABLES    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

from storage import *


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ~~~~~~~~    Define FUNCTIONS    ~~~~~~~~ #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def get_video_from_gcs(video_url):
    """
    Retrieve the video file stored in GCS using its public link
    """
    destination_blob_name = video_url.split("/")[-1]
    client = storage.Client.from_service_account_info(GCP_SERVICE_ACCOUNT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(destination_blob_name)
    data = blob.download_as_bytes()
    return data

def store_video_to_gcs(file):
    """
    Retrieve a video file in GCS and return its public link
    """
    destination_blob_name = f"{uuid.uuid4()}.mp4"
    client = storage.Client.from_service_account_info(GCP_SERVICE_ACCOUNT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file, content_type=file.type)
    blob.make_public()
    return blob.public_url

def delete_video_from_gcs(video_url):
    """
    Delete the video stored in GCS using its public link
    """
    destination_blob_name = video_url.split("/")[-1]
    client = storage.Client.from_service_account_info(GCP_SERVICE_ACCOUNT)
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(destination_blob_name)
    blob.delete()
