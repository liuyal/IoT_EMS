import os, sys, time, argparse, logging, yaml, datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


def cslog(msg, flag="info"):
    if input_arg.verbose: print(msg)
    if input_arg.log:
        if flag == "info": logging.info(msg)
        if flag == "error": logging.error(msg)
        if flag == "critical": logging.critical(msg)
        if flag == "warning": logging.warning(msg)
        if flag == "debug": logging.debug(msg)


def check_node_status(connection, timeout):
    cslog("Checking node status.")
    cursor = connection.cursor()
    cursor.execute("USE nova")
    cursor.execute("SELECT mac, time_stamp, status FROM nodes;")
    result = cursor.fetchall()
    if len(result) < 1: cslog("No Nodes found")
    else:
        for item in result:
            current_time = int(time.time())
            last_node_time = item[1]
            delta_seconds = current_time - last_node_time
            if delta_seconds > timeout:
                if int(delta_seconds) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " seconds"
                elif int(delta_seconds / 60) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds))+ " minute"
                elif int(delta_seconds / 60) > 1 and int(delta_seconds / 60) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " minutes"
                elif int(delta_seconds / (60 * 60)) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hour"
                else: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hours"
                cslog("Node: " + item[0] + " last seen " + time_info + " ago. Updating status to offline.")
                update_status_sql = "UPDATE nodes SET status=false WHERE mac='" + item[0] + "';"
                cursor.execute(update_status_sql)
                connection.commit()
            else:
                if int(delta_seconds) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " seconds"
                elif int(delta_seconds / 60) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds))+ " minute"
                elif int(delta_seconds / 60) > 1 and int(delta_seconds / 60) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " minutes"
                elif int(delta_seconds / (60 * 60)) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hour"
                else: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hours"
                cslog("Node: " + item[0] + " last seen " + time_info + " ago.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', "--timeout", action='store', dest="timeout", default=5, help='Verbose mode')
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')

    input_arg = parser.parse_args()
    try: sys.argv[1]
    except: parser.print_help(); sys.exit()

    if input_arg.log: logging.basicConfig(filename="./appServer.log", filemode='a', format='%(asctime)s, [%(levelname)s] %(name)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    try:
        with open("server_info.yaml", 'r') as stream:
            try:
                mysql_cred = yaml.safe_load(stream)["mysql_cred"]
            except yaml.YAMLError as exc:
                cslog(exc)

        cslog("Connecting to database nova.")
        connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
        check_node_status(connection, input_arg.timeout * 60)
        cslog("Closing DB connection")
        connection.close()

        logging.shutdown()
    except mysql.connector.Error as error:
        cslog("Failed {}".format(error), flag="error")
