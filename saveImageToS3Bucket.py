import os
import random
import string
import requests
import configuration
import boto3
from botocore.client import Config
import urllib.request
from slugify import slugify

def saveImageToBucket(image,raw_image_name):
    try:
        image_format = image.split(".")
        image_format_ext = image_format[len(image_format) - 1]
        source_file_name_slug =  slugify(raw_image_name)
        source_file_name = "{}.{}".format(source_file_name_slug,image_format_ext)
        # s3 = boto3.resource(
        #     's3',
        #     aws_access_key_id=configuration.BUCKET_ACCESS_KEY_ID,
        #     aws_secret_access_key=configuration.BUCKET_ACCESS_SECRET_KEY,
        #     config=Config(signature_version='s3v4')
        # )
        # urllib.request.urlretrieve(image, configuration.root_path+source_file_name)
        # s3.Bucket(configuration.BUCKET_NAME).upload_file(configuration.root_path+source_file_name, source_file_name)
        # try:
        #     os.remove(configuration.root_path+source_file_name)
        # except:
        #     pass
        image_aws_url = "https://car-catalogues.s3.ap-northeast-1.amazonaws.com/{}".format(source_file_name)
        return image_aws_url
    except:
        pass



