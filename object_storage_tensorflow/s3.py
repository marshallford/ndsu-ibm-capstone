import boto3
from . import config


def getConnection():
    info = config.get()
    return boto3.resource(
        's3',
        endpoint_url=info['endpoint'],
        aws_access_key_id=info['accessKeyId'],
        aws_secret_access_key=info['secretAccessKey']
    )
