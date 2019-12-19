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


def data_generator():
    for _ in range(100):
        mac = "BC:DD:C2:2F:47:79"
        epoch = randint(1575158400, 1575590400)
        temp = round(uniform(-10, 40), 2)
        hum = round(uniform(0, 100), 2)
        insert_req = "http://localhost/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        print(str(epoch) + " " + time.strftime('%Y%m%d', time.gmtime(epoch)) + " " + str(temp) + " " + str(hum) + "\n" + insert_req)
        print(response.json())


if __name__ == "__main__":

    data_generator()
