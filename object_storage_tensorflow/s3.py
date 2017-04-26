import boto3
import os
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
    basePath = '/tmp/object_storage_tensorflow/{}'.format(bucket)
    if not os.path.exists(basePath):
        os.makedirs(basePath)
    path = '{}/{}'.format(basePath, key)
    # TODO: return errors
    conn.Bucket(bucket).download_file(key, path)
    return path


def upload(bucket, key, data):
    conn = getConnection()
    # TODO: return errors
    conn.Bucket(bucket).put_object(Key=key, Body=data)
    return key


def downloadFolder(bucket, folder):
    conn = getConnection()
    basePath = '/tmp/object_storage_tensorflow/{}/{}'.format(bucket, folder)
    if not os.path.exists(basePath):
        os.makedirs(basePath)
    prefix = '{}/'.format(folder)
    keys = []
    for obj in conn.Bucket(bucket).objects.filter(Prefix=prefix):
        path = '{}/{}'.format(basePath, obj.key.split('/', 1)[1])
        conn.Bucket(bucket).download_file(obj.key, path)
        keys.append(obj.key)
    return keys


def uploadFolder(bucket, prefix, keys, data):
    fullkeys = []
    for index, key in enumerate(keys):
        fullKey = '{}/{}'.format(prefix, key)
        upload(bucket, fullKey, data[index])
        fullkeys.append(fullKey)
    return fullkeys
