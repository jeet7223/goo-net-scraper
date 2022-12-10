from requests_html import HTMLSession

import configuration

session = HTMLSession()
from googletrans import Translator
import mysql.connector

mydb = mysql.connector.connect(
    host=configuration.host,
    user=configuration.user,
    password=configuration.password,
    database=configuration.database,
    charset=configuration.charset,
    auth_plugin=configuration.auth_plugin
)


def saveVariants(mydb, model_id, title, title_en, image_url, description, description_en):
    mycursor = mydb.cursor()
    sql = "INSERT INTO model_variants(model_id,title_jp,title_en,img_url,description_jp,description_en) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (model_id, title, title_en, image_url, description, description_en)
    mycursor.execute(sql, val)
    mydb.commit()
    return mycursor.lastrowid


def saveGrades(mydb, model_variant_id, grade_name, grade_name_en, grade_url, number, grade_heading_jp, grade_heading_en, main_img_url, model, displacement, number_of_doors, shift, drive_system, capacity, fuel_consumption, new_price, old_price):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grades(model_variant_id,grade_name_jp,grade_name_en,grade_url,number,grade_heading_jp,grade_heading_en,main_img_url,model,displacement,number_of_doors,shift,drive_system,capacity,fuel_consumption,new_price,old_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (model_variant_id, grade_name, grade_name_en, grade_url, number, grade_heading_jp, grade_heading_en, main_img_url, model, displacement, number_of_doors, shift, drive_system, capacity, fuel_consumption, new_price, old_price)
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

def translate(word):
    try:
        translator = Translator()
        translator.raise_Exception = True
        response = translator.translate(word, dest="en")
        return response.text
    except:
        return word

sql_select_query = "select * from models"
cursor = mydb.cursor(dictionary=True)
cursor.execute(sql_select_query)
records = cursor.fetchall()

makers = []
for row in records:
    url = row["model_url"]
    model_id = row["id"]
    makers.append(model_id)
    supplier_response = session.get(url)
    product = supplier_response.html.find("#main", first=True).find(".box_gradeList")

    for item in product:
        title = item.find("h2", first=True).text
        title_en = translate(title)
        image_url = item.find(".box_roundWhite", first=True).find(".img", first=True).xpath("//img/@src", first=True)
        description = item.find(".txt", first=True).text
        description_en = translate(description)

        print("Model Id :- {}".format(model_id))
        # print("Title :- {}".format(title))
        print("Title in English :- {}".format(title_en))
        # print("Image URL :- {}".format(image_url))
        # print("Description :- {}".format(description))
        # print("Description in English :- {}".format(description_en))

        print("=========================================")
        variant_id = saveVariants(mydb, model_id, title, title_en, image_url, description, description_en)

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
                model = grade_array[1]
                displacement = grade_array[2]
                number_of_doors = grade_array[3]
                shift = grade_array[4]
                drive_system = grade_array[5]
                capacity = grade_array[6]
                fuel_consumption = grade_array[7]
                new_price = grade_array[8].replace("円", "")
            else:
                continue

            print("Model Variant Id :- {}".format(variant_id))
            print("Grade Name :- {}".format(grade_name))
            print("Grade Name in English :- {}".format(grade_name_en))
            print("Model :- {}".format(model))
            print("Displacement :- {}".format(displacement))
            print("Number Of Doors :- {}".format(number_of_doors))
            print("Shift :- {}".format(shift))
            print("Drive System :- {}".format(drive_system))
            print("Capacity :- {}".format(capacity))
            print("Fuel Consumption :- {}".format(fuel_consumption))
            print("New Price :- {}".format(new_price))
            print("Grade URL :- {}".format(grade_url))

            number = url.split('/')[-2]
            print("Number :- {}".format(number))
            get_grade_info = session.get(grade_url)
            grade_heading = get_grade_info.html.find(".tit_first", first=True).find("h2", first=True).text
            grade_heading_en = translate(grade_heading)
            print("Grade Heading :- {}".format(grade_heading))
            print("Grade Heading in English :- {}".format(grade_heading_en))

            main_img_url = get_grade_info.html.find("#car_img_main", first=True).xpath("//img/@src", first=True)
            print("Main Image :- {}".format(main_img_url))

            catalog_information = get_grade_info.html.find(".box_presentSpec", first=True)
            old_price = catalog_information.find(".oldCar", first=True).find(".price")[1].text
            print("Old Car Price :- {}".format(old_price))
            print("-----------------------------------")
            print()

            grade_id = saveGrades(mydb, variant_id, grade_name, grade_name_en, grade_url, number, grade_heading, grade_heading_en, main_img_url, model, displacement, number_of_doors, shift, drive_system, capacity, fuel_consumption, new_price, old_price)

            thumb_images = get_grade_info.html.find(".photo_thumb02", first=True).find("ul", first=True).find("li")
            images = []
            for image in thumb_images:
                image_url = image.xpath("//img/@src", first=True)
                images.append(image_url)

            for img in images:
                print(img)
                print("----------------------")
                saveGradeImages(mydb, grade_id, img)

            main = get_grade_info.html.find("#main", first=True).find(".box_roundGray")
            for data in main:
                try:
                    heading_jp = data.find("h2", first=True).text
                    heading_en = translate(heading_jp)
                except:
                    heading_jp = None
                    heading_en = None

                car_info = data.find(".column")
                for table in car_info:
                    row = table.find("tr")
                    for value in row:
                        try:
                            label_jp = value.find("th", first=True).text
                            label_en = translate(label_jp)
                            val_jp = value.find("td", first=True).text
                            val_en = translate(val_jp)
                        except:
                            continue

                        print("Grade Id :- {}".format(grade_id))
                        print(heading_jp)
                        print(heading_en)
                        print(label_jp)
                        print(label_en)
                        print(val_jp)
                        print(val_en)
                        print("=============================")
                        saveGradeSpecification(mydb, grade_id, heading_jp, heading_en, label_jp, label_en, val_jp, val_en)