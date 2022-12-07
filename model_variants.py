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


def saveGrades(mydb, model_variant_id, grade_name, grade_name_en, grade_url, number):
    mycursor = mydb.cursor()
    sql = "INSERT INTO grades(model_variant_id,grade_name_jp,grade_name_en,grade_url,number) VALUES (%s, %s, %s, %s, %s)"
    val = (model_variant_id, grade_name, grade_name_en, grade_url, number)
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

# print("Fetching each row using column name")
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
        print("Title :- {}".format(title))
        print("Title in English :- {}".format(title_en))
        print("Image URL :- {}".format(image_url))
        print("Description :- {}".format(description))
        print("Description in English :- {}".format(description_en))

        print("=========================================")
        variant_id = saveVariants(mydb, model_id, title, title_en, image_url, description, description_en)
        product_table = item.find(".bgTop", first=True).find(".grade")
        for data in product_table:
            url = data.xpath("//a/@href", first=True)
            grade_url = "https://www.goo-net.com{}".format(url)
            grade_name = data.text
            grade_name_en = translate(grade_name)
            number = url.split('/')
            number = number[len(number) - 1]
            print("Model Variant Id :- {}".format(variant_id))
            print("Grade Name :- {}".format(grade_name))
            print("Grade Name in English :- {}".format(grade_name_en))
            print("Grade URL :- {}".format(grade_url))
            print("Number :- {}".format(number))
            print("-------------------------")
            saveGrades(mydb, variant_id, grade_name, grade_name_en, grade_url, number)
