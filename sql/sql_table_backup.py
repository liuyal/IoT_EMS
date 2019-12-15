import os, sys, time
from datetime import date, timedelta, datetime

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

time.sleep(1)
current_date_stamp = datetime.utcnow().date().strftime('%Y%m%d')
date_stamp = (datetime.utcnow().date() - timedelta(1)).strftime('%Y%m%d')

try:
    # connection = mysql.connector.connect(host='localhost', database='nova', user='root', password='')
    # connection = mysql.connector.connect(host='localhost', database='nova', user='nova', password='Airlink_1')
    connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1')
    cursor = connection.cursor()
    cursor.execute("USE nova")

    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if len(tables) < 1:
        cursor.execute("CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id) );")
        sys.exit("Created data Table")

    cursor.execute("SELECT time from data;")
    time_list = cursor.fetchall()

    if len(time_list) < 1: sys.exit("Empty data Table EXIT")

    last_epoch_time = time_list[-1][0]
    last_date_time = time.strftime('%Y%m%d', time.gmtime(last_epoch_time))

    if last_date_time == current_date_stamp: sys.exit("Same date no backup EXIT")
    else:
        cursor.execute("ALTER TABLE data RENAME TO " + last_date_time  + "_data;")
        cursor.execute("CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id) );")

except mysql.connector.Error as error:
    print("Failed {}".format(error))

os.system("sudo apt-get clean")

