import sys, os, time
from datetime import datetime

while True:
    now = str(datetime.now().time())
    print(now.split(".")[0])
    if now.split(".")[0].split(":")[2] == "00":
        print("RUN")
        os.system("python ../udp_cmd.py -f -v -L 9996")
    time.sleep(1)

