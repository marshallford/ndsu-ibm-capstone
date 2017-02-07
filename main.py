import boto3
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.load(f)

conn = boto3.resource(
    's3',
    endpoint_url=config['endpoint'],
    aws_access_key_id=config['accessKeyId'],
    aws_secret_access_key=config['secretAccessKey']
)

for bucket in conn.buckets.all():
    print(bucket.name)
    for obj in bucket.objects.all():
        print("  - %s") % obj.key
