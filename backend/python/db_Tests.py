import os, sys, time, datetime, requests, subprocess, serial
from datetime import date, timedelta
from random import seed
from random import randint
from random import uniform

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def sql_connector_test(ip):
    try:
        connection = mysql.connector.connect(host=ip, database='nova', user='root', password='', auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


def request_test(ip, folder="backend/php/"):
    req = "http://" + ip + "/" + folder + "show_tables.php"
    response = requests.get(req)
    data = response.json()["data"]


def time_check(ip):
    show_tables = "http://" + ip + "/php/show_tables.php"
    read_table = "http://" + ip + "/php/select_from_table.php?table="
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
        except: None


def data_generator(ip, n=10):
    for _ in range(n):
        mac = "BC:DD:C2:2F:47:79"
        epoch = randint(1575158400, 1575590400)
        temp = round(uniform(-10, 40), 2)
        hum = round(uniform(0, 100), 2)
        insert_req = "http://" + ip +"/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        print(str(epoch) + " " + time.strftime('%Y%m%d', time.gmtime(epoch)) + " " + str(temp) + " " + str(hum) + "\n" + insert_req)
        print(response.json())


def add_nodes(mac, ip):
    try:
        connection = mysql.connector.connect(host=ip, database='nova', user='root', password='', auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        for item in mac:
            cursor.execute("INSERT INTO nodes values('" + item + "', '0.0.0.0', 9996, 0, FALSE)")
            connection.commit()

    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


if __name__ == "__main__":

    ip = "localhost"
    port = 9996

    mac = ["BC:DD:C2:2F:47:79", "5C:CF:7F:AC:72:78"]
    add_nodes(mac, ip)
    # data_generator(ip , 20)
    # time_check()

