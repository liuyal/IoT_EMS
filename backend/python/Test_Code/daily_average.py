import os, sys, time, logging, platform, argparse, yaml
from datetime import date, timedelta, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def cslog(msg, flag="info"):
    if input_arg.verbose and flag == "info":
        print(msg)
    elif input_arg.verbose and flag == "error":
        print("\033[91m" + msg + "\033[0m")
    if input_arg.log:
        if flag == "info": logging.info(msg)
        if flag == "error": logging.error(msg)
        if flag == "critical": logging.critical(msg)
        if flag == "warning": logging.warning(msg)
        if flag == "debug": logging.debug(msg)


def check_daily_avg(connection):
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    cslog("Checking daily_avg table.")
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS daily_avg(mac VARCHAR(17), date BIGINT, avg_temp DECIMAL (18, 2), avg_hum DECIMAL (18, 2), PRIMARY KEY (mac, date));")
        cursor.execute("SELECT mac, date FROM daily_avg;")
        result = cursor.fetchall()
        return result
    except Exception as e:
        cslog("Failure: " + str(e))


def check_tables(connection):
    cslog("Checking tables in nova.")
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    cursor.execute("SHOW TABLES;")
    result = cursor.fetchall()
    mac_list = []
    for item in result:
        if item[0] != "data" and item[0] != "daily_avg" and item[0] != "nodes" and item[0] != "system_config":
            cursor.execute("SELECT DISTINCT mac FROM " + item[0] + " ORDER BY mac ASC;")
            macs = cursor.fetchall()
            for mac in macs:
                mac_list.append((mac[0], item[0].split("_")[0]))
    return mac_list


def calc_daily_avg(avg_list, mac_list, connection):
    cslog("Calculating daily averages")
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    if avg_list == None:
        avg_list = []
    for pop in avg_list:
        for mac in mac_list:
            if str(mac[0]) == str(pop[0]) and str(mac[1]) == str(pop[1]):
                mac_list.remove(mac)
    for item in mac_list:
        mac = item[0]
        date = item[1] + "_data"
        avg_cmd = "SELECT AVG(temp), AVG(hum) FROM " + date + " WHERE mac='" + mac + "';"
        cursor.execute(avg_cmd)
        result = cursor.fetchall()
        avg_temp = round(result[0][0], 2)
        avg_hum = round(result[0][1], 2)
        insert_avg_cmd = "INSERT INTO daily_avg(mac, date, avg_temp, avg_hum) VALUES('" + mac + "', " + str(item[1]) + ", " + str(avg_temp) + ", " + str(avg_hum) + ");"
        cursor.execute(insert_avg_cmd)
    connection.commit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')
    input_arg = parser.parse_args()
    try:
        sys.argv[1]
    except:
        parser.print_help()

    log_path = os.getcwd() + os.sep + "appServer.log"
    if input_arg.log: 
        logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s, %(name)s, [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
        logging.Formatter.converter = time.gmtime

    cslog("Calculating Daily Averages.")
    try:
        with open("server_info.yaml", 'r') as stream:
            try:
                mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc:
                cslog(exc)

        cslog("Connecting to database " + str(mysql_cred["DATABASE"]) + ".")
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')

        avg_list = check_daily_avg(connection)
        mac_list = check_tables(connection)
        calc_daily_avg(avg_list, mac_list, connection)
        cslog("Closing DB connection")
        connection.close()

        logging.shutdown()
    except mysql.connector.Error as error:
        cslog("Failed {}".format(error), flag="error")
