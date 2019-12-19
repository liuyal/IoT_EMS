import os, sys, time, datetime, requests, subprocess
from datetime import date, timedelta
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

# try:
#     connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='nova', password='Airlink_1', auth_plugin='mysql_native_password')
#     cursor = connection.cursor()
#     cursor.execute("USE nova")
#     cursor.execute("SHOW TABLES")
#     tables = cursor.fetchall()
# except mysql.connector.Error as error:
#     print("Failed access table {}".format(error))

req = "http://localhost/php/django_php/show_tables.php"
response = requests.get(req)
data = response.json()["data"]

mac = "BC:DD:C2:2F:47:79"
time = "1576727581"
temp = "21.00"
hum = "46.00"


insert_req = "http://localhost/php/django_php/insert.php?mac=" + mac + "&time=" + time + "&temp=" + temp + "&hum=" + hum


print(insert_req)
