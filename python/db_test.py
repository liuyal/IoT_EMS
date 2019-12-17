import os, sys, time, datetime, requests, subprocess
from datetime import date, timedelta

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

req = "http://192.168.1.150/php/select_from_table.php?table=data"
response = requests.get(req)
data = response.json()["data"]
list = []
for item in data:
    epoch_time = item["time"]
    time_str = datetime.datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y-%m-%d %H:%M:%S")
    list.append(time_str)
    print(time_str)
 
try:
    connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1', auth_plugin='mysql_native_password')
    cursor = connection.cursor()
    cursor.execute("USE nova")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

except mysql.connector.Error as error:
    print("Failed access table {}".format(error))

