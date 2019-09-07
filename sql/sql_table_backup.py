import os, sys, time
from datetime import date, timedelta, datetime

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

time.sleep(1)
current_date_stamp = datetime.utcnow().date().strftime('%Y%m%d')
date_stamp = (datetime.utcnow().date()- timedelta(1)).strftime('%Y%m%d')

try:
    # connection = mysql.connector.connect(host='localhost', database='nova', user='nova', password='Airlink_1')
    connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1')
    cursor = connection.cursor()
    cursor.execute("USE nova")

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if len(tables) < 1:
        cursor.execute("CREATE TABLE DATA(ID INT NOT NULL AUTO_INCREMENT, TIME BIGINT, TEMP DECIMAL(18,2), HUM DECIMAL(18,2), PRIMARY KEY (ID));")
        sys.exit("Created DATA Table")

    cursor.execute("SELECT time from DATA;")
    time_list = cursor.fetchall()

    if len(time_list) < 1:
        sys.exit("Empty DATA Table")

    last_epoch_time = time_list[-1][0]
    last_date_time = time.strftime('%Y%m%d', time.gmtime(last_epoch_time))

    if last_date_time == current_date_stamp:
        sys.exit("Same DATE no backup")
    else:
        cursor.execute("ALTER TABLE DATA RENAME TO " + last_date_time + "_DATA;")
        cursor.execute("CREATE TABLE DATA( ID INT NOT NULL AUTO_INCREMENT, TIME BIGINT, TEMP DECIMAL (18, 2), HUM DECIMAL (18, 2), PRIMARY KEY (ID) );")

except mysql.connector.Error as error:
    print("Failed inserting record into python_users table {}".format(error))

# os.system("sudo apt-get clean")

