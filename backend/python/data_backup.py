import os, sys, time, logging, platform, argparse, yaml, threading, math
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


def thread(thread_id, connection, list, start, end):
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    for i in range(start, end + 1):
        #sys.stdout.write(str(thread_id) + " [" + str(i) + "] " + list[i] + "\n")
        cursor.execute(list[i])
    connection.commit()
    connection.close()


def back_up(insert_list, remove_list, n_threads):
    insert_len = len(insert_list)
    remove_len = len(remove_list)
    insert_cmd_per_thread = int(math.floor(insert_len / n_threads))
    remove_cmd_per_thread = int(math.floor(remove_len / n_threads))
    insert_end = insert_len - 1
    remove_end = remove_len - 1
    thread_list = []
    with open("./server_info.yaml", 'r') as stream:
        try:
            mysql_cred = yaml.safe_load(stream)["mysql_cred"]
        except yaml.YAMLError as exc:
            cslog(exc)
    for i in range(0, n_threads):
        conn1 = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        conn2 = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        insert_start = int(i * insert_cmd_per_thread)
        insert_end = int(insert_cmd_per_thread * (i + 1) - 1)
        remove_start = int(i * remove_cmd_per_thread)
        remove_end = int(remove_cmd_per_thread * (i + 1) - 1)

        insert_thread = threading.Thread(target=thread, args=(i, conn1, insert_list, insert_start, insert_end))
        remove_thread = threading.Thread(target=thread, args=(i, conn2, remove_list, remove_start, remove_end))
        thread_list.append(insert_thread)
        thread_list.append(remove_thread)

    if insert_end != insert_len - 1:
        conn_end1 = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        insert_thread = threading.Thread(target=thread, args=(i + 1, conn_end1, insert_list, insert_end + 1, insert_len - 1))
        thread_list.append(insert_thread)

    if remove_end != remove_len - 1:
        conn_end2 = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        remove_thread = threading.Thread(target=thread, args=(i + 1, conn_end2, remove_list, remove_end + 1, remove_len - 1))
        thread_list.append(remove_thread)

    for item in thread_list: item.start()
    for item in thread_list: item.join()


def sql_cmd_maker(connection):
    date_stamp = datetime.utcnow().date().strftime('%Y%m%d')
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    if len(tables) < 1:
        cursor.execute("CREATE TABLE data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));")
        cslog("data Table does not exist, creating data Table, EXIT.", flag="error")
        sys.exit()

    cursor.execute("SELECT mac, time, temp, hum FROM  data ORDER BY time ASC;")
    time_list = cursor.fetchall()

    if len(time_list) < 1:
        cslog("Empty data Table, EXIT.", flag="error")
        sys.exit()

    cmd_counter = 0
    insert_list = []
    remove_list = []
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
            insert_list.append(insert_cmd)
            remove_list.append(remove_cmd)
            cmd_counter += 1
    connection.close()
    if cmd_counter == 0:
        cslog("No data to be backed up.")
    else:
        cslog("Backing up " + str(cmd_counter) + " data points.")
    return insert_list, remove_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', "--threads", action='store', default=1, help='Number of threads each for SQL insert and remove.')
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

    cslog("Data Back Up Started...")
    try:
        with open("server_info.yaml", 'r') as stream: mysql_cred = yaml.safe_load(stream)["mysql_cred"]

        cslog("Connecting to database " + str(mysql_cred["DATABASE"]) + ".")
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        insert_list, remove_list = sql_cmd_maker(connection)
        back_up(insert_list, remove_list, int(input_arg.threads))
        cslog("Closing DB connection")

        logging.shutdown()
        if platform.system() == "linux" or platform.system() == "linux2": os.system("sudo apt-get clean")
        cslog("Back Up Complete.")
    except mysql.connector.Error as error:
        cslog("Failed {}".format(error), flag="error")
    except yaml.YAMLError as exc:
        cslog(exc)