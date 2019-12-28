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
    cursor.execute("USE " + str(connection.database))
    cslog("Checking daily_avg table.")
    try:
        cursor.execute("SELECT mac, date FROM daily_avg;")
        result = cursor.fetchall()
        return result
    except Exception as e:
        cslog("Failure: " + str(e))


def check_nova(connection):
    cslog("Checking tables in nova.")
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database))
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


def calc_avg(avg_list, mac_list, connection):
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database))
    for pop in avg_list:
        for item in mac_list:
            if str(item[0]) == str(pop[0]) and str(item[1]) == str(pop[1]):
                mac_list.remove(item)

    print()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')
    input_arg = parser.parse_args()
    try:
        sys.argv[1]
    except:
        parser.print_help()

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
        mac_list = check_nova(connection)
        calc_avg(avg_list, mac_list, connection)

        cslog("Closing DB connection")
        connection.close()
        logging.shutdown()
    except mysql.connector.Error as error:
        cslog("Failed {}".format(error), flag="error")
