import os, sys, time, datetime, requests, subprocess, serial, ipaddress, yaml
from datetime import date, timedelta
from random import seed
from random import randint
from random import uniform
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def sql_connector_test(ip):
    try:
        with open("server_info.yaml", 'r') as stream:
            try: mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc: print(exc)
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(tables)
    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


def request_test(ip):
    req = "http://" + ip + "/backend/php/show_tables.php"
    response = requests.get(req)
    data = response.json()["data"]


def time_check(ip):
    show_tables = "http://" + ip + "/Temperature_System/backend/php/show_tables.php"
    read_table = "http://" + ip + "/Temperature_System/backend/php/select_from_table.php?table="
    response = requests.get(show_tables)
    table_resp = response.json()["data"]
    tables = []
    for item in table_resp: tables.append(item['table'])
    for date in tables:
        if date != "nodes" and date != "system_config":
            response = requests.get(read_table + date)
            resp = response.json()["data"]
            print(date)
            for item in resp:
                epoch_time = item["time"]
                times = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(epoch_time)))
                print("\t" + str(times))


def data_generator(ip, n=10):
    for _ in range(n):
        mac = "BC:DD:C2:2F:47:79"
        epoch = randint(1575158400, 1575590400)
        temp = round(uniform(-10, 40), 2)
        hum = round(uniform(0, 100), 2)
        insert_req = "http://" + ip +"/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        print(str(epoch) + " " + time.strftime('%Y%m%d', time.gmtime(epoch)) + " " + str(temp) + " " + str(hum) + "\n" + insert_req)
        print(response.json())


def add_nodes(mac):
    try:
        with open("server_info.yaml", 'r') as stream:
            try: mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc: print(exc)
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        for item in mac:
            cursor.execute("INSERT INTO nodes values('" + item + "', '0.0.0.0', 9996, 0, FALSE)")
            connection.commit()
    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


def db_validate(ip):
    show_tables = "http://" + ip + "/Temperature_System/backend/php/show_tables.php"
    read_table = "http://" + ip + "/Temperature_System/backend/php/select_from_table.php?table="
    main_table = []
    tables = []
    wrong_data = {}
    new_data = {}
    data = {}
    response = requests.get(show_tables)
    table_resp = response.json()["data"]

    for item in table_resp:
        tables.append(item["table"])
        main_table.append(item["table"])
        wrong_data[item["table"]] = []
    tables.remove("nodes")
    tables.remove("system_config")
    main_table.remove("nodes")
    main_table.remove("system_config")
    del wrong_data["nodes"], wrong_data["system_config"]

    for item in tables:
        data[item] = []
        response = requests.get(read_table + item)
        content = response.json()["data"]
        for each in content: data[item].append(each)

    for line in data:
        temp_list = data[line]
        for item in temp_list:
            date = line.split("_")[0]
            epoch_time = item["time"]
            date_str = datetime.datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y%m%d")
            if date_str != date and line in tables:
                wrong_data[line].append(item)
            if date_str != date and date_str + "_data" not in new_data:
                new_data[date_str + "_data"] = []
                new_data[date_str + "_data"].append(item)
            elif date_str != date and date_str + "_data" in new_data:
                new_data[date_str + "_data"].append(item)
    pop_list = []
    for item in wrong_data:
        if len(wrong_data[item]) == 0: pop_list.append(item)
    for item in pop_list: wrong_data.pop(item, None)
    remove_cmd = []
    add_cmd = []
    for key in wrong_data:
        for i in range(0, len(wrong_data[key])):
            cmd = "DELETE FROM " + key + " WHERE time=" + str(wrong_data[key][i]["time"]) + " AND mac='" + str(wrong_data[key][i]["mac"]) + "';"
            remove_cmd.append(cmd)
    for key in new_data:
        for i in range(0, len(new_data[key])):
            if key not in main_table:
                cmd2 = "CREATE TABLE " + key + "(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));"
                add_cmd.append(cmd2)
                main_table.append(key)
            cmd = "INSERT INTO " + key + "(mac,time,temp,hum) VALUES('" + str(new_data[key][i]["mac"]) + "'," + str(new_data[key][i]["time"]) + "," + str(new_data[key][i]["temp"]) + "," + str(new_data[key][i]["hum"]) + ");"
            add_cmd.append(cmd)
    try:
        with open("server_info.yaml", 'r') as stream:
            try: mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc: print(exc)
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        for item in remove_cmd: cursor.execute(item)
        for item in add_cmd: cursor.execute(item)
    except mysql.connector.Error as error:
        print(str(item) + "\nFailed access table {}".format(error))


if __name__ == "__main__":

    ip = "localhost"
    port = 9996
    mac = ["BC:DD:C2:2F:47:79", "5C:CF:7F:AC:72:78"]

    # data_generator(ip , 20)
    # add_nodes(mac)
    # time_check(ip)
    db_validate(ip)










