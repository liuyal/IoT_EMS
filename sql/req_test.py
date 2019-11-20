import requests, datetime

req = "http://192.168.1.150/read_table.php?table=20190918_DATA"
response = requests.get(req)
data = response.json()["data"]

list = []

for item in data:
    epoch_time = item["TIME"]
    time_str = datetime.datetime.utcfromtimestamp(int(epoch_time)).strftime("%Y-%m-%d %H:%M:%S")
    list.append(time_str)
    print(time_str)

print(0)