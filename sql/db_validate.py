import os, sys, time
import requests, datetime

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

show_tables = "http://192.168.1.150/show_tables.php"
read_table = "http://192.168.1.150/read_table.php?table="
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

tables.pop(-1)
main_table.pop(-1)
del wrong_data["DATA"]

for item in tables:
    data[item] = []
    response = requests.get(read_table + item)
    content = response.json()["data"]
    for each in content: data[item].append(each)

for line in data:
    temp_list = data[line]
    for item in temp_list:
        date = line.split("_")[0]
        epoch_time = item["TIME"]
        date_str = datetime.datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y%m%d")
        if date_str != date and line in tables:
            wrong_data[line].append(item)

        if date_str != date and date_str + "_DATA" not in new_data:
            new_data[date_str + "_DATA"] = []
            new_data[date_str + "_DATA"].append(item)
        elif date_str != date and date_str + "_DATA" in new_data:
            new_data[date_str + "_DATA"].append(item)

del response, table_resp, read_table, data, show_tables
del content, each, item, date, date_str, epoch_time, line, temp_list

pop_list = []
for item in wrong_data:
    if len(wrong_data[item]) == 0: pop_list.append(item)
for item in pop_list: wrong_data.pop(item, None)

del item, pop_list

remove_cmd = []
add_cmd = []

for key in wrong_data:
    for i in range (0, len(wrong_data[key])):
        cmd = "DELETE FROM " + key + " WHERE TIME=" + str(wrong_data[key][i]["TIME"]) + " AND ID=" + str(wrong_data[key][i]["ID"]) + ";"
        remove_cmd.append(cmd)

for key in new_data:
    for i in range (0, len(new_data[key])):

        if key not in main_table:
            cmd2 = "CREATE TABLE " + key + "(ID INT NOT NULL AUTO_INCREMENT, MAC CHAR(20), TIME BIGINT, TEMP DECIMAL (18, 2), HUM DECIMAL (18, 2), PRIMARY KEY (ID));"
            add_cmd.append(cmd2)
            main_table.append(key)

        cmd = "INSERT INTO " + key  + "(MAC,TIME,TEMP,HUM) VALUES('" + str(new_data[key][i]["MAC"]) + "'," +  str(new_data[key][i]["TIME"]) + "," + str(new_data[key][i]["TEMP"]) + "," + str(new_data[key][i]["HUM"]) + ");"
        add_cmd.append(cmd)

del tables, wrong_data, new_data, main_table
try:del key, cmd, cmd2, i
except: None

try:
    connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1')
    cursor = connection.cursor()
    cursor.execute("USE nova")
    # for item in remove_cmd: cursor.execute(item)
    # for item in add_cmd: cursor.execute(item)

except mysql.connector.Error as error:
    print(item)
    print("Failed access table {}".format(error))
