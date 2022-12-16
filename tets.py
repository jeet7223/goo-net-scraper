import csv

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
cursor = mydb.cursor(dictionary=True)

def translate(word):
    try:
        translator = Translator()
        translator.raise_Exception = True
        response = translator.translate(word, dest="en")
        return response.text
    except:
        return word

sql_select_query = "select * from models"

cursor.execute(sql_select_query)
records = cursor.fetchall()
counter = 0
for row in records:
    url = row["model_url"]
    model_name_en = row["model_name_en"]
    supplier_response = session.get(url)
    product = supplier_response.html.find("#main", first=True).find(".box_gradeList")
    grades = []
    for item in product:
        product_table = item.find(".bgTop", first=True).find(".grade")
        counter = counter + 1
        grade = len(product_table)
        grades.append(grade)
    print("Model Name :- {}".format(model_name_en))
    model_variant = len(product)
    print("Model Variant Found :- {}".format(model_variant))
    ans = sum(grades)
    print("Grades Found :- {}".format(ans))
    print("-------------------------------------")

    # with open("data.csv", 'a', newline='', encoding="utf8") as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     csvwriter.writerow([url, model_name_en, model_variant, grades])
    #     print("Models Found :- {}".format(counter))
    #     print()

