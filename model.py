import csv
import mysql.connector
from translate import translate
from requests_html import HTMLSession

import configuration
import saveImageToS3Bucket
import boto3
from botocore.client import Config
session = HTMLSession()


mydb = mysql.connector.connect(
    host=configuration.host,
    user=configuration.user,
    password=configuration.password,
    database=configuration.database,
    charset=configuration.charset,
    auth_plugin=configuration.auth_plugin
)
s3 = boto3.resource(
    's3',
    aws_access_key_id=configuration.BUCKET_ACCESS_KEY_ID,
    aws_secret_access_key=configuration.BUCKET_ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
def saveModels(mydb, maker_id, model_name, model_name_en, model_url, model_img_url):
    mycursor = mydb.cursor()
    sql = "INSERT INTO models(maker_id,model_name_jp,model_name_en,model_url,model_img_url) VALUES (%s, %s, %s, %s, %s)"
    val = (maker_id, model_name, model_name_en, model_url, model_img_url)
    mycursor.execute(sql, val)
    mydb.commit()




sql_select_query = "select * from makers"
cursor = mydb.cursor(dictionary=True)
cursor.execute(sql_select_query)
records = cursor.fetchall()

# print("Fetching each row using column name")

for row in records:
    url = row["maker_url"]
    maker_id = row["id"]
    maker_name = row["maker_en"]

    supplier_response = session.get(url)
    product = supplier_response.html.find(".box_modelSelect", first=True).find(".section_wrap")

    counter = 1
    models_urls = []
    for data in product:
        p = data.find(".cassette")
        for item in p:
            try:
                url = item.xpath("//a/@href", first=True)
                model_url = "https://www.goo-net.com{}".format(url)
                model_name = item.find(".model", first=True).text
                model_name_en = translate(model_name).title()
                model_raw_url = item.find("figure", first=True).xpath("//img/@data-original", first=True)
                model_img_url = saveImageToS3Bucket.saveImageToBucket(model_raw_url,"{} {}".format(maker_name,model_name_en),s3)
                if model_url in models_urls:
                    continue
                else:
                    models_urls.append(model_url)
            except:
                print("Error")
                continue
            print("Maker -: {}  | Model -: {} |  Counter -: {}".format(maker_name,model_name_en,counter))
            counter = counter + 1
            saveModels(mydb, maker_id, model_name, model_name_en, model_url, model_img_url)

