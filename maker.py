import csv
import pickle

import mysql.connector
import configuration
from selenium.common.exceptions import TimeoutException
import pandas as pd


headless_mode = True

import sys
import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
from selenium.webdriver.common.by import By
import warnings
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
warnings.filterwarnings("ignore")

mydb = mysql.connector.connect(
    host=configuration.host,
    user=configuration.user,
    password=configuration.password,
    database=configuration.database,
    charset=configuration.charset,
    auth_plugin=configuration.auth_plugin
)

cursor = mydb.cursor()

def saveMakers(mydb, country_name_en, country_name, maker_name_en, maker_name, maker_url):
    mycursor = mydb.cursor()
    sql = "INSERT INTO makers(country_en,country_jp,maker_en,maker_jp,maker_url) VALUES (%s, %s, %s, %s, %s)"
    val = (country_name_en, country_name, maker_name_en, maker_name, maker_url)
    mycursor.execute(sql, val)
    mydb.commit()

def translate(word):
    try:
        translator = Translator()
        translator.raise_Exception = True
        response = translator.translate(word, dest="en")
        return response.text
    except IndexError:
        return word

# TO customize Browser Capablities The bellow codes "options"
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("window-size=1920,1080")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('ignore-certificate-errors')
if headless_mode:
    options.add_argument('--headless')
prefs = {"profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs", prefs)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
driver.implicitly_wait(2)
driver.get("https://www.goo-net.com/catalog/")

columns = driver.find_element(By.CLASS_NAME,'box_roundOrangeB').find_elements(By.CLASS_NAME,'column')
cc_item = driver.find_element(By.CLASS_NAME,'box_roundOrangeB').find_elements(By.CLASS_NAME,'column')[1].find_element(By.TAG_NAME,'ul')
driver.execute_script("arguments[0].setAttribute('class','i-dont-want')", cc_item)
time.sleep(2)
for cols in columns:
    makers_data = cols.find_elements(By.TAG_NAME,'ul')
    c_counter = 0
    for mk_items in makers_data:
        mk_class = mk_items.get_attribute('class')
        if mk_class == "i-dont-want":
            continue
        country_name = cols.find_elements(By.CLASS_NAME, 'tit_country')[c_counter].text
        country_name_en = translate(country_name)

        c_counter = c_counter + 1
        li_data = mk_items.find_elements(By.TAG_NAME, 'li')
        for li_item in li_data:
            maker_name = li_item.find_element(By.TAG_NAME, 'a').text
            maker_href = li_item.find_element(By.TAG_NAME, 'a').get_attribute('href')
            maker_url = "{}".format(maker_href)
            maker_name_en = translate(maker_name).title()
            print("Maker Name -: {}".format(maker_name))
            print("Maker Name English -: {}".format(maker_name_en))
            print("Country Name -: {}".format(country_name))
            print("Country Name English -: {}".format(country_name_en))
            print("Maker Url -: {}".format(maker_url))
            print("==============================================")
            saveMakers(mydb, country_name_en, country_name, maker_name_en, maker_name, maker_url)

driver.quit()