import os, sys, time, logging, platform
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import date, timedelta, datetime

logging.basicConfig(filename="./backup_logs.log", filemode='a', format='%(asctime)s, [%(levelname)s] %(name)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logging.info("Back Up Started...")

date_stamp = datetime.utcnow().date().strftime('%Y%m%d')

try:
    logging.info("Connecting to database nova.")
    connection = mysql.connector.connect(host='localhost', database='nova', user='root', password='')
    # connection = mysql.connector.connect(host='localhost', database='nova', user='nova', password='Airlink_1')
    # connection = mysql.connector.connect(host='192.168.1.150', database='nova', user='zeus', password='Airlink_1', auth_plugin='mysql_native_password')

    cursor = connection.cursor()
    cursor.execute("USE nova")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if len(tables) < 1:
        cursor.execute("CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));")
        logging.error("data Table does not exist, creating data Table, EXIT.")
        sys.exit("data Table does not exist, creating data Table, EXIT.")

    cursor.execute("SELECT mac, time, temp, hum from data;")
    time_list = cursor.fetchall()

    if len(time_list) < 1:
        logging.error("Empty data Table, EXIT.")
        sys.exit("Empty data Table, EXIT.")

    logging.info("Validating time, checking data dates.")
    for item in time_list:
        data_date = time.strftime('%Y%m%d', time.gmtime(int(item[1])))
        if data_date != date_stamp:
            table_name = data_date + "_data"
            table_exist = False
            cursor.execute("""SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}' """.format(table_name.replace('\'', '\'\'')))
            if cursor.fetchone()[0] == 1: table_exist = True
            if not table_exist:
                logging.info(table_name + " Table does not exist, creating table.")
                create_cmd = "CREATE TABLE " + table_name + "(id INT NOT NULL AUTO_INCREMENT, mac CHAR(20), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));"
                cursor.execute(create_cmd)
            insert_cmd = "INSERT INTO " + table_name + "(mac,time,temp,hum) VALUES('" + str(item[0]) + "'," + str(item[1]) + "," + str(item[2]) + "," + str(item[3]) + ");"
            remove_cmd = "DELETE FROM data WHERE mac='" + str(item[0]) + "' AND time=" + str(item[1]) + ";"
            cursor.execute(insert_cmd)
            cursor.execute(remove_cmd)
            connection.commit()

    if platform.system() == "linux" or platform.system() == "linux2": os.system("sudo apt-get clean")
    logging.info("Back Up Complete.")

except mysql.connector.Error as error:
    logging.error("Failed {}".format(error))
    print("Failed {}".format(error))



