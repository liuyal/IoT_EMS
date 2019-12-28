import os, sys, time, datetime, requests, subprocess, serial, ipaddress, yaml, random, threading
from datetime import date, timedelta, timezone
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def rand_mac():
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    c = random.randint(0, 255)
    d = random.randint(0, 255)
    e = random.randint(0, 255)
    f = random.randint(0, 255)
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (a, b, c, d, e, f)


def sql_connector_test():
    try:
        with open("../server_info.yaml", 'r') as stream:
            try:
                mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc:
                print(exc)
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
    print(data)


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
        with open("../server_info.yaml", 'r') as stream:
            try:
                mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc:
                print(exc)
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        for cmd_item in remove_cmd: cursor.execute(cmd_item)
        for cmd_item in add_cmd: cursor.execute(cmd_item)
    except mysql.connector.Error as error:
        print(str(cmd_item) + "\nFailed access table {}".format(error))


def time_check(ip):
    show_tables = "http://" + ip + "/Temperature_System/backend/php/show_tables.php"
    read_table = "http://" + ip + "/Temperature_System/backend/php/select_from_table.php?table="
    response = requests.get(show_tables)
    table_resp = response.json()["data"]
    tables = []
    for item in table_resp: tables.append(item['table'])
    for date in tables:
        if date != "nodes" and date != "system_config" and date != "daily_avg":
            response = requests.get(read_table + date)
            resp = response.json()["data"]
            print(date)
            for item in resp:
                epoch_time = item["time"]
                times = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(epoch_time)))
                print("\t" + str(times))


def add_nodes(mac):
    try:
        with open("../server_info.yaml", 'r') as stream:
            try:
                mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc:
                print(exc)
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        cursor = connection.cursor()
        cursor.execute("USE nova")
        for item in mac:
            print("Adding node: " + str(item))
            cursor.execute("INSERT INTO nodes values('" + item + "', '0.0.0.0', 0, 0, FALSE, FALSE)")
            connection.commit()
    except mysql.connector.Error as error:
        print("Failed access table {}".format(error))


def random_data_generator(mac_list, ip, start_date, end_date, n=50):
    epoch_start = int(datetime.datetime(int(str(start_date)[0:4]), int(str(start_date)[4:6]), int(str(start_date)[6:8]), 0, 0, tzinfo=timezone.utc).timestamp())
    epoch_end = int(datetime.datetime(int(str(end_date)[0:4]), int(str(end_date)[4:6]), int(str(end_date)[6:8]), 0, 0, tzinfo=timezone.utc).timestamp())
    for i in range(0, n):
        # random.seed(i)
        # mac = rand_mac()
        index = random.randint(0, len(mac_list) - 1)
        mac = mac_list[index]
        epoch = random.randint(epoch_start, epoch_end)
        temp = round(random.uniform(-10, 50), 2)
        hum = round(random.uniform(0, 100), 2)
        insert_req = "http://" + ip + "/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        sys.stdout.write("[" + str(i) + "]" + time.strftime('%Y%m%d %H:%M:%S', time.gmtime(epoch)) + " " + str(epoch) + " " + str(temp) + " " + str(hum) + "\n" + insert_req + "\n" + str(response.json()) + "\n")


def data_generator(ip, mac, start, end):
    epoch = int(start)
    while epoch < int(end):
        temp = round(random.uniform(-10, 50), 2)
        hum = round(random.uniform(0, 100), 2)
        insert_req = "http://" + ip + "/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
        response = requests.get(insert_req)
        sys.stdout.write(time.strftime('%Y%m%d %H:%M:%S', time.gmtime(epoch)) + " " + str(epoch) + " " + str(temp) + " " + str(hum) + "\n" + insert_req + "\n" + str(response.json()) + "\n")
        epoch = epoch + 60


def generator_wrapper(ip, mac, start_date, end_date, threads):
    epoch_start = int(datetime.datetime(int(str(start_date)[0:4]), int(str(start_date)[4:6]), int(str(start_date)[6:8]), 0, 0, tzinfo=timezone.utc).timestamp())
    epoch_end = int(datetime.datetime(int(str(end_date)[0:4]), int(str(end_date)[4:6]), int(str(end_date)[6:8]), 0, 0, tzinfo=timezone.utc).timestamp())
    Delta = int(epoch_end - epoch_start)
    n_requests = int(Delta / 60)
    req_per_threads = int(n_requests / threads)
    print("Start:\t" + str(epoch_start))
    print("End:\t" + str(epoch_end))
    print("Delta:\t" + str(Delta))
    print("n_req:\t" + str(n_requests))
    print("req/t:\t" + str(req_per_threads))
    list = []
    thread_list = []
    for i in range(0, threads):
        list.append(epoch_start)
        epoch_start = epoch_start + req_per_threads * 60
    list.append(list[-1] + req_per_threads * 60)
    for i in range(0, threads):
        gen_thread = threading.Thread(target=data_generator, args=(ip, mac, list[i], list[i + 1]))
        thread_list.append(gen_thread)
    for item in thread_list: item.start()


if __name__ == "__main__":
    ip = "localhost"
    mac_list = ["00:00:00:00:00:01", "00:00:00:00:00:02", "00:00:00:00:00:03", "00:00:00:00:00:04", "00:00:00:00:00:05"]

    # generator_wrapper(ip="localhost", mac="00:00:00:00:00:01", start_date=20191225, end_date=20191228, threads=40)
    # add_nodes(mac_list)
    # random_data_generator(mac_list, ip, start_date=20191220, end_date=20191227, n=500)
    time_check(ip)
    # db_validate(ip)
