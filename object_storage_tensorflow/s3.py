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


def download(bucket, key):
    conn = getConnection()
    # TODO: generate folder structure if required
    path = '/tmp/object_storage_tensorflow/{}/{}'.format(bucket, key)
    # TODO: return errors
    conn.Bucket(bucket).download_file(key, path)
    return path


def upload(bucket, key, data):
    conn = getConnection()
    # TODO: return errors
    conn.Bucket(bucket).put_object(Key=key, Body=data)
    return key
