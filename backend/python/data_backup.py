import os, sys, time, logging, platform, argparse, yaml
from datetime import date, timedelta, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def cslog(msg, flag="info"):
    if input_arg.verbose and flag == "info": print(msg)
    elif input_arg.verbose and flag == "error": print("\033[91m" + msg + "\033[0m")
    if input_arg.log:
        if flag == "info": logging.info(msg)
        if flag == "error": logging.error(msg)
        if flag == "critical": logging.critical(msg)
        if flag == "warning": logging.warning(msg)
        if flag == "debug": logging.debug(msg)


def db_backup(connection):
    cursor = connection.cursor()
    cursor.execute("USE nova")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if len(tables) < 1:
        cursor.execute("CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));")
        cslog("data Table does not exist, creating data Table, EXIT.", flag="error")
        sys.exit()

    cursor.execute("SELECT mac, time, temp, hum from data;")
    time_list = cursor.fetchall()

    if len(time_list) < 1:
        cslog("Empty data Table, EXIT.", flag="error")
        sys.exit()

    cmd_counter = 0
    cslog("Validating time, checking dates.")
    for item in time_list:
        data_date = time.strftime('%Y%m%d', time.gmtime(int(item[1])))
        if data_date != date_stamp:
            table_name = data_date + "_data"
            table_exist = False
            cursor.execute("""SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}' """.format(table_name.replace('\'', '\'\'')))
            if cursor.fetchone()[0] == 1: table_exist = True
            if not table_exist:
                cslog(table_name + " Table does not exist, creating table.")
                create_cmd = "CREATE TABLE " + table_name + "(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));"
                cursor.execute(create_cmd)
            insert_cmd = "INSERT INTO " + table_name + "(mac,time,temp,hum) VALUES('" + str(item[0]) + "'," + str(item[1]) + "," + str(item[2]) + "," + str(item[3]) + ");"
            remove_cmd = "DELETE FROM data WHERE mac='" + str(item[0]) + "' AND time=" + str(item[1]) + ";"
            cursor.execute(insert_cmd)
            cursor.execute(remove_cmd)
            connection.commit()
            cmd_counter += 1

    if cmd_counter == 0: cslog("No data to be backed up.")


if __name__ == "__main__":

    time.sleep(10)
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')

    input_arg = parser.parse_args()
    try: sys.argv[1]
    except: parser.print_help(); sys.exit()

    if input_arg.log: logging.basicConfig(filename="./appServer.log", filemode='a', format='%(asctime)s, [%(levelname)s] %(name)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    cslog("Back Up Started...")

    date_stamp = datetime.utcnow().date().strftime('%Y%m%d')

    try:
        with open("server_info.yaml", 'r') as stream:
            try: mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc: cslog(exc)

        cslog("Connecting to database nova.")
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        db_backup(connection)
        cslog("Closing DB connection")
        connection.close()

        logging.shutdown()
        if platform.system() == "linux" or platform.system() == "linux2": os.system("sudo apt-get clean")
        cslog("Back Up Complete.")
    except mysql.connector.Error as error:
        cslog("Failed {}".format(error), flag="error")



