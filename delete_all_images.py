import boto3
from botocore.client import Config
from boto3 import client
import configuration

s3 = boto3.resource(
            's3',
            aws_access_key_id=configuration.BUCKET_ACCESS_KEY_ID,
            aws_secret_access_key=configuration.BUCKET_ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

my_bucket = s3.Bucket(configuration.BUCKET_NAME)

for file in my_bucket.objects.all():
    print(file.key)
    s3.Object(configuration.BUCKET_NAME, file.key).delete()

