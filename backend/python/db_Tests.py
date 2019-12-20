import os, sys, time, datetime, requests, subprocess
from datetime import date, timedelta
from random import seed
from random import randint
from random import uniform

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def sql_connector_test():
    try:
        connection = mysql.connector.connect(host='localhost', database='nova', user='root', password='', auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


def request_test():
    req = "http://localhost/php/django_php/show_tables.php"
    response = requests.get(req)
    data = response.json()["data"]


def time_check():
    show_tables = "http://192.168.1.150/php/show_tables.php"
    read_table = "http://192.168.1.150/php/select_from_table.php?table="
    response = requests.get(show_tables)
    table_resp = response.json()["data"]
    tables = []
    for item in table_resp: tables.append(item['table'])
    for date in tables:
        try:
            response = requests.get(read_table + date)
            resp = response.json()["data"]
            print(date)
            for item in resp:
                epoch_time = item["time"]
                times = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(epoch_time)))
                print("\t" + str(times))
        except:
            None


def data_generator():
    for _ in range(10):
        mac = "BC:DD:C2:2F:47:79"
        epoch = randint(1575158400, 1575590400)
        temp = round(uniform(-10, 40), 2)
        hum = round(uniform(0, 100), 2)
        insert_req = "http://localhost/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        print(str(epoch) + " " + time.strftime('%Y%m%d', time.gmtime(epoch)) + " " + str(temp) + " " + str(hum) + "\n" + insert_req)
        print(response.json())


if __name__ == "__main__":

    # data_generator()
    
    time_check()
