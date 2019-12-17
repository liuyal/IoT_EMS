import os, sys, time, requests, datetime

show_tables = "http://192.168.1.150/php/show_tables.php"
read_table = "http://192.168.1.150/php/select_from_table.php?table="

response = requests.get(show_tables)
table_resp = response.json()["data"]
tables = []

for item in table_resp: tables.append(item['table'])
# tables.pop(-1)

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
