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
tables = ["grades","grades_specification","grade_color","grade_images","model_variants","models"]
for table in tables:
    query = "truncate {}".format(table)
    mycursor.execute(query)
    mydb.commit()