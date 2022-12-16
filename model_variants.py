from requests_html import HTMLSession

import configuration
import saveImageToS3Bucket

session = HTMLSession()
from translate import translate
import mysql.connector
import boto3
from botocore.client import Config
mydb = mysql.connector.connect(
    host=configuration.host,
    user=configuration.user,
    password=configuration.password,
    database=configuration.database,
    charset=configuration.charset,
    auth_plugin=configuration.auth_plugin
)
cursor = mydb.cursor(dictionary=True)
s3 = boto3.resource(
    's3',
    aws_access_key_id=configuration.BUCKET_ACCESS_KEY_ID,
    aws_secret_access_key=configuration.BUCKET_ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)
def saveVariants(mydb, model_id, title, title_en, image_url, description, description_en):
    mycursor = mydb.cursor()
    sql = "INSERT INTO model_variants(model_id,title_jp,title_en,img_url,description_jp,description_en) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (model_id, title, title_en, image_url, description, description_en)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid


def saveGrades(mydb, model_variant_id, grade_name, grade_name_en, grade_url, number, grade_heading_jp, grade_heading_en, main_img_url, model_jp, model_en, displacement_jp, displacement_en, number_of_doors_jp, number_of_doors_en, shift_jp, shift_en, drive_system_jp, drive_system_en, capacity_jp, capacity_en, fuel_consumption_jp, fuel_consumption_en, new_price, old_price):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grades(model_variant_id,grade_name_jp,grade_name_en,grade_url,number,grade_heading_jp,grade_heading_en,main_img_url,model_jp,model_en,displacement_jp,displacement_en,number_of_doors_jp,number_of_doors_en,shift_jp,shift_en,drive_system_jp,drive_system_en,capacity_jp,capacity_en,fuel_consumption_jp,fuel_consumption_en,new_price,old_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (model_variant_id, grade_name, grade_name_en, grade_url, number, grade_heading_jp, grade_heading_en, main_img_url, model_jp, model_en, displacement_jp, displacement_en, number_of_doors_jp, number_of_doors_en, shift_jp, shift_en, drive_system_jp, drive_system_en, capacity_jp, capacity_en, fuel_consumption_jp, fuel_consumption_en, new_price, old_price)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid
def saveGradeImages(mydb, grade_id, img):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grade_images(grade_id,image_url) VALUES (%s, %s)"
    val = (grade_id, img)
    mycursor.execute(sql, val)
    mydb.commit()

def saveGradeSpecification(mydb, grade_id, heading_jp, heading_en, label_jp, label_en, val_jp, val_en):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grades_specification(grade_id,heading_jp,heading_en,label_jp,label_en,value_jp,value_en) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (grade_id, heading_jp, heading_en, label_jp, label_en, val_jp, val_en)
    mycursor.execute(sql, val)
    mydb.commit()

def saveGradeColor(mydb, grade_id, color_system_jp, color_system_en, manufacturer_standard_jp, manufacturer_standard_en, manufacturer_option_jp, manufacturer_option_en):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grade_color(grade_id,color_system_jp,color_system_en,manufacturer_standard_jp,manufacturer_standard_en,manufacturer_option_jp,manufacturer_option_en) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (grade_id, color_system_jp, color_system_en, manufacturer_standard_jp, manufacturer_standard_en, manufacturer_option_jp, manufacturer_option_en)
    mycursor.execute(sql, val)
    mydb.commit()



def getMakerName(maker_id):
    sql_maker_query = "select * from makers where id ={}".format(maker_id)
    cursor.execute(sql_maker_query)
    maker_data = cursor.fetchone()
    return maker_data['maker_en']

sql_select_query = "select * from models"

cursor.execute(sql_select_query)
records = cursor.fetchall()

model_counter = 1
for row in records:
    url = row["model_url"]
    model_id = row["id"]
    maker_id = row["maker_id"]
    maker_name = getMakerName(maker_id)
    model_name_en = row["model_name_en"]
    supplier_response = session.get(url)
    product = supplier_response.html.find("#main", first=True).find(".box_gradeList")

    for item in product:
        title = item.find("h2", first=True).text
        title_en = translate(title)
        try:
            variant_image_raw_url = item.find(".box_roundWhite", first=True).find(".img", first=True).xpath(
                "//img/@src", first=True)
            variant_image_url = saveImageToS3Bucket.saveImageToBucket(variant_image_raw_url, title_en,s3)
        except:
            variant_image_url = None

        description = item.find(".txt", first=True).text
        description_en = "-"
        variant_id = saveVariants(mydb, model_id, title, title_en, variant_image_url, description, description_en)

        product_table = item.find(".bgTop", first=True).find(".grade")
        grade_table = item.find(".bgTop", first=True).find(".tbl_type03", first=True).find("tr")
        for table_row in grade_table:
            data = table_row.find("td")

            grade_array = []
            url = table_row.xpath("//a/@href", first=True)
            grade_url = "https://www.goo-net.com{}".format(url)
            for grade_data in data:
                grades = grade_data.text
                grade_array.append(grades)

            if len(grade_array) > 0:
                grade_name = grade_array[0]
                grade_name_en = translate(grade_name)
                model_jp = grade_array[1]
                model_en = "-"
                displacement_jp = grade_array[2]
                displacement_en = "-"
                number_of_doors_jp = grade_array[3]
                number_of_doors_en = "-"
                shift_jp = grade_array[4]
                shift_en = "-"
                drive_system_jp = grade_array[5]
                drive_system_en = "-"
                capacity_jp = grade_array[6]
                capacity_en = "-"
                fuel_consumption_jp = grade_array[7]
                fuel_consumption_en = "-"
                new_price = grade_array[8].replace("円", "")
            else:
                continue


            number = url.split('/')[-2]

            get_grade_info = session.get(grade_url)
            grade_heading = get_grade_info.html.find(".tit_first", first=True).find("h2", first=True).text
            grade_heading_en = "-"


            try:
                main_grade_image_raw_url = get_grade_info.html.find("#car_img_main", first=True).xpath("//img/@src",
                                                                                                       first=True)

                main_grade_image_url = saveImageToS3Bucket.saveImageToBucket(main_grade_image_raw_url,
                                                                             "{} {} {} {}".format(maker_name,
                                                                                                  model_name_en,
                                                                                                  grade_name_en,
                                                                                                  number),s3)
            except:
                main_grade_image_url = None
            catalog_information = get_grade_info.html.find(".box_presentSpec", first=True)
            old_price = catalog_information.find(".oldCar .info", first=True).text.replace('中古車価格帯','')

            grade_id = saveGrades(mydb, variant_id, grade_name, grade_name_en, grade_url, number, grade_heading, grade_heading_en, main_grade_image_url, model_jp, model_en, displacement_jp, displacement_en, number_of_doors_jp, number_of_doors_en, shift_jp, shift_en, drive_system_jp, drive_system_en, capacity_jp, capacity_en, fuel_consumption_jp, fuel_consumption_en, new_price, old_price)

            try:
                thumb_images = get_grade_info.html.find(".photo_thumb02", first=True).find("ul", first=True).find("li")
                images = []
                for image in thumb_images:
                    image_url = image.xpath("//img/@src", first=True)
                    images.append(image_url)
                img_counter = 1
                for img in images:
                    sub_image_url = saveImageToS3Bucket.saveImageToBucket(img,
                                                                          "{} {} {} {}_{}".format(maker_name,
                                                                                                  model_name_en,
                                                                                                  grade_name_en,
                                                                                                  number, img_counter),s3 )
                    saveGradeImages(mydb, grade_id, sub_image_url)
                    img_counter = img_counter + 1
            except:
                print("No images uploaded")
                pass

            main = get_grade_info.html.find("#main", first=True).find(".box_roundGray")
            for data in main:
                try:
                    heading_jp = data.find("h2", first=True).text
                    heading_en = "-"
                except:
                    continue

                if "ボディカラー" in heading_jp:
                    body_color = data.find(".box_color", first=True).find("table", first=True).find("tr")
                    for colors in body_color:
                        color_data = colors.find("td")
                        color_datas = []
                        for c_data in color_data:
                            data = c_data.text
                            color_datas.append(data)

                        if len(color_datas) > 0:
                            color_system_jp = color_datas[0]
                            color_system_en = "-"
                            manufacturer_standard_jp = color_datas[1]
                            manufacturer_standard_en = "-"
                            manufacturer_option_jp = color_datas[2]
                            manufacturer_option_en = "-"
                        else:
                            continue

                        saveGradeColor(mydb, grade_id, color_system_jp, color_system_en, manufacturer_standard_jp, manufacturer_standard_en, manufacturer_option_jp, manufacturer_option_en)
                else:
                    car_info = data.find(".column")
                    for table in car_info:
                        row = table.find("tr")
                        for value in row:
                            try:
                                label_jp = value.find("th", first=True).text
                                label_en = "-"
                                val_jp = value.find("td", first=True).text
                                val_en = "-"
                            except:
                                continue

                            saveGradeSpecification(mydb, grade_id, heading_jp, heading_en, label_jp, label_en, val_jp,
                                                   val_en)
            print("Maker - : {} | Model -: {} | Variant -: {} | Grade -: {} | Model Counter -: {}/{}".format(maker_name,model_name_en,title_en,grade_name_en,model_counter,len(records)))
    model_counter = model_counter + 1