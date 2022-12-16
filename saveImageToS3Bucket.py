

import requests
import configuration
from slugify import slugify

def saveImageToBucket(image,raw_image_name,s3):
    try:
        image_format = image.split(".")
        image_format_ext = image_format[len(image_format) - 1]
        source_file_name_slug =  slugify(raw_image_name)
        source_file_name = "{}.{}".format(source_file_name_slug,image_format_ext)
        r = requests.get(image, stream=True)
        bucket = s3.Bucket(configuration.BUCKET_NAME)
        bucket.upload_fileobj(r.raw, source_file_name)

        image_aws_url = "https://car-catalogues.s3.ap-northeast-1.amazonaws.com/{}".format(source_file_name)
        return image_aws_url
    except:
        pass





