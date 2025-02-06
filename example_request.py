# pip install mysql-connector-python
import mysql.connector


mydb = mysql.connector.connect(
    host='sql5.freesqldatabase.com',
    user='sql5761207',
    password='rr6SDyMifr',
    database='sql5761207'

)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM Classes;")

for x in mycursor:
    print(x)