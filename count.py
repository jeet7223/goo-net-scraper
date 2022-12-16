import configuration
import mysql.connector
mydb = mysql.connector.connect(
    host=configuration.host,
    user=configuration.user,
    password=configuration.password,
    database=configuration.database,
    charset=configuration.charset,
    auth_plugin=configuration.auth_plugin
)

mycursor = mydb.cursor()

mycursor.execute("select count(*) from models")
running_result = mycursor.fetchone()
print("Total Models -: {}".format(running_result[0]))

mycursor.execute("select count(*) from makers")
running_result = mycursor.fetchone()
print("Total Makers -: {}".format(running_result[0]))

mycursor.execute("select count(*) from grades")
running_result = mycursor.fetchone()
print("Total Grades -: {}".format(running_result[0]))

mycursor.execute("select count(*) from grades_specification")
running_result = mycursor.fetchone()
print("Total Grades Specification -: {}".format(running_result[0]))

mycursor.execute("select count(*) from grade_color")
running_result = mycursor.fetchone()
print("Total Grades Color -: {}".format(running_result[0]))

mycursor.execute("select count(*) from  grade_images")
running_result = mycursor.fetchone()
print("Total Grades Images -: {}".format(running_result[0]))

mycursor.execute("select count(*) from model_variants")
running_result = mycursor.fetchone()
print("Total Model Variants -: {}".format(running_result[0]))
