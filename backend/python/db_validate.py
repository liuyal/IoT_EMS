import os, sys, time, requests, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

# ip = "192.168.1.150"
ip = "localhost"

show_tables = "http://" + ip +"/php/show_tables.php"
read_table = "http://" + ip + "/php/select_from_table.php?table="
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
del wrong_data["data"]

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
    for i in range (0, len(wrong_data[key])):
        cmd = "DELETE FROM " + key + " WHERE time=" + str(wrong_data[key][i]["time"]) + " AND mac='" + str(wrong_data[key][i]["mac"]) + "';"
        remove_cmd.append(cmd)

for key in new_data:
    for i in range (0, len(new_data[key])):

        if key not in main_table:
            cmd2 = "CREATE TABLE " + key + "(id INT NOT NULL AUTO_INCREMENT, mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));"
            add_cmd.append(cmd2)
            main_table.append(key)

        cmd = "INSERT INTO " + key  + "(mac,time,temp,hum) VALUES('" + str(new_data[key][i]["mac"]) + "'," +  str(new_data[key][i]["time"]) + "," + str(new_data[key][i]["temp"]) + "," + str(new_data[key][i]["hum"]) + ");"
        add_cmd.append(cmd)

try:
    connection = mysql.connector.connect(host=ip, database='nova', user='root', password='')
    # connection = mysql.connector.connect(host=ip, database='nova', user='zeus', password='Airlink_1', auth_plugin='mysql_native_password')
    cursor = connection.cursor()
    cursor.execute("USE nova")
    for item in remove_cmd: cursor.execute(item)
    for item in add_cmd: cursor.execute(item)

except mysql.connector.Error as error:
    print(item)
    print("Failed access table {}".format(error))
