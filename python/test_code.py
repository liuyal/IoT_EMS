import os, sys, time, datetime
import requests, subprocess
from datetime import date, timedelta

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


req = "http://192.168.1.150/read_table.php?table=20190918_DATA"
response = requests.get(req)
data = response.json()["data"]
list = []
for item in data:
    epoch_time = item["TIME"]
    time_str = datetime.datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y-%m-%d %H:%M:%S")
    list.append(time_str)
    print(time_str)

print(0)

# a = requests.get('http://192.168.1.150/')
# b = requests.get('http://192.168.1.150/read_all.php')
# c = requests.get('http://192.168.1.150/insert.php?time=25&temp=22.52')
# today = datetime.datetime.now().strftime("%Y%m%d")
# out = str(subprocess.run([r'date --date="1 day ago" +%Y%m%d'],  shell=True, stdout=subprocess.PIPE).stdout)
# req = requests.get('http://192.168.1.150/read_all.php')
# data = req.content
 
try:
    connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1')
    cursor = connection.cursor()
    cursor.execute("USE nova")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

except mysql.connector.Error as error:
    print("Failed access table {}".format(error))

