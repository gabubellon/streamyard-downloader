import os

import boto3
from loguru import logger

# TODO Transform in a class

#s3_prefix = ""
#s3_bucket = ""


def send_to_s3(sent_file,s3_bucket,s3_prefix):
    key = "{}/{}".format(s3_prefix, os.path.basename(sent_file)) if s3_prefix else os.path.basename(sent_file)
    
    logger.info(f"Sending {sent_file} to bucket {s3_bucket}/{key}")

    s3_client = boto3.client("s3")
    s3_client.upload_file(sent_file, s3_bucket, key)

    os.remove(sent_file)
