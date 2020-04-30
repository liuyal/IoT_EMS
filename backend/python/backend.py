import os, sys, threading, time, argparse, ipaddress, logging, queue, re, yaml, datetime, platform, math
import socket as socket
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


def udp_broadcast(msg, UDP_IP="192.168.1.255", UDP_PORT=9996):
    time.sleep(1)
    for item in msg:
        cslog("Start Broadcasting: " + str(item) + " to " + UDP_IP + ":" + str(UDP_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(item, (UDP_IP, UDP_PORT))
        sock.close()
        time.sleep(1)
    cslog("Broadcast Done.")


def udp_send(msg, UDP_IP="127.0.0.1", UDP_PORT=9996):
    time.sleep(2)
    for item in msg:
        cslog("Start Sending: " + str(item) + " to " + UDP_IP + ":" + str(UDP_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(item, (UDP_IP, UDP_PORT))
        sock.close()
        time.sleep(1)
    cslog("Send Done.")


def udp_listener(msg_queue, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    data_list = []
    mac_list = []
    p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(time_out)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        cslog("Start Listener on: " + UDP_IP + ":" + str(UDP_PORT))
        while True:
            data, address = sock.recvfrom(1024)
            mac = re.findall(p, str(data))
            if len(mac) != 0:
                packet = {"ip": address[0], "port": address[1], "mac": mac[0], "data": data, "time": int(time.time())}
                data_list.append(packet)
                mac_list.append(mac[0])
            cslog("Packet: " + str(address) + "\t" + str(data))
    except socket.timeout:
        cslog("Listening done, Closing socket.")
        sock.close()
    msg_queue.put(data_list)
    msg_queue.put(mac_list)


def sql_node_status_update(update_list, on_list, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("USE " + str(connection.database) + ";")
        for item in on_list:
            search_cmd = "SELECT mac FROM nodes WHERE mac='" + item["mac"] + "';"
            cursor.execute(search_cmd)
            result = cursor.fetchall()
            if len(result) < 1:
                add_node = "INSERT INTO nodes(mac, ip, port, start_time, time_stamp, status)"
                values = "VALUES('" + str(item["mac"]) + "', '" + item["ip"] + "', " + str(item["port"]) + ", " + str(item["time"]) + ", " + str(item["time"]) + ", TRUE)"
                cursor.execute(add_node + values)
                cslog("Added node " + item["mac"] + " to status table.")
            else:
                update_cmd = "UPDATE nodes SET start_time=" + str(item["time"]) + ",time_stamp=" + str(item["time"]) + ",ip='" + item["ip"] + "',port=" + str(item["port"]) + ",status=true WHERE mac='" + item["mac"] + "';"
                cursor.execute(update_cmd)
                cslog("Node " + item["mac"] + " Online.")
        for item in update_list:
            search_cmd = "SELECT mac FROM nodes WHERE mac='" + item["mac"] + "';"
            cursor.execute(search_cmd)
            result = cursor.fetchall()
            if len(result) < 1:
                add_node = "INSERT INTO nodes(mac, ip, port, start_time, time_stamp, status)"
                values = "VALUES('" + str(item["mac"]) + "', '" + item["ip"] + "', " + str(item["port"]) + ", " + str(item["time"]) + ", " + str(item["time"]) + ", TRUE)"
                cursor.execute(add_node + values)
                cslog("Added node " + item["mac"] + " to status table.")
            else:
                cursor.execute("SELECT start_time FROM nodes where mac='" + item["mac"] + "';")
                result = cursor.fetchall()
                if result[0][0] == 0: cursor.execute("UPDATE nodes SET start_time=" + str(item["time"]) + " WHERE mac='" + item["mac"] + "';")
                update_cmd = "UPDATE nodes SET time_stamp=" + str(item["time"]) + ", ip='" + item["ip"] + "', port=" + str(item["port"]) + ", status=true WHERE mac='" + item["mac"] + "';"
                cursor.execute(update_cmd)
                cslog("Updated node " + item["mac"] + " status.")
        connection.commit()
    except Exception as error:
        cslog("Failed {}".format(error), flag="error")


def sql_insert(insert_list, connection):
    try:
        cursor = connection.cursor()
        cursor.execute("USE " + str(connection.database) + ";")
        for item in insert_list:
            packet = item["data"].decode("utf-8")[item["data"].decode("utf-8").index('[') + 1:item["data"].decode("utf-8").index(']')].split("|")
            if packet[1] == "data_sent":
                temp = packet[3]
                hum = packet[4]
                cursor.execute("SELECT start_time FROM nodes where mac='" + item["mac"] + "';")
                result = cursor.fetchall()
                if result[0][0] == 0: cursor.execute("UPDATE nodes SET start_time=" + str(item["time"]) + " WHERE mac='" + item["mac"] + "';")
                cursor.execute("INSERT INTO DATA(mac, time, temp, hum) VALUES('" + item["mac"] + "', " + str(item["time"]) + ", " + str(temp) + ", " + str(hum) + ");")
                cslog("Node: " + item["mac"] + " inserted data")
        connection.commit()
    except Exception as error:
        cslog("Failed {}".format(error), flag="error")


def node_cmd_handler():
    cmd = []
    msg_queue = queue.Queue()
    thread_listen = None
    cslog("Started UDP Command Handler")
    if input_arg.fetch: cmd.append(b"[fetch_data]\n")
    if input_arg.ping: cmd.append(b"[ping]\n")
    if input_arg.set_host != None: cmd.append(("[set_host|" + str(input_arg.set_host) + "]\n").encode('utf8'))
    if input_arg.reboot: cmd.append(b"[reboot]\n")

    if input_arg.NODE_IP.split('.')[-1] == "255": thread_send = threading.Thread(target=udp_broadcast, args=(cmd, input_arg.NODE_IP, input_arg.NODE_PORT))
    else:  thread_send = threading.Thread(target=udp_send, args=(cmd, input_arg.NODE_IP, input_arg.NODE_PORT))
    if input_arg.Listen_PORT > 0: thread_listen = threading.Thread(target=udp_listener, args=(msg_queue, "0.0.0.0", input_arg.Listen_PORT, input_arg.udp_timeout))

    thread_send.start()
    if input_arg.Listen_PORT > 0: thread_listen.start()
    thread_send.join()
    if input_arg.Listen_PORT > 0: thread_listen.join()

    if input_arg.update and input_arg.Listen_PORT > 0:
        insert_list = []
        on_list = []
        update_list = []
        db_connection = SQL_connection_handler()
        msg_list = msg_queue.get()
        mac_list = (list(set(msg_queue.get())))

        for node in mac_list:
            for msg in reversed(msg_list):
                if node == msg["mac"] and "data_sent" in str(msg["data"]):
                    insert_list.append(msg)
        for node in mac_list:
            for msg in reversed(msg_list):
                if node == msg["mac"] and "reboot" not in str(msg["data"]):
                    update_list.append(msg)
                    break
        for node in mac_list:
            for msg in reversed(msg_list):
                if node == msg["mac"] and "|on|" in str(msg["data"]):
                    on_list.append(msg)
                    break
        sql_node_status_update(update_list, on_list, db_connection)
        sql_insert(insert_list, db_connection)
        SQL_disconnection_handler(db_connection)


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


def check_daily_tables(connection):
    cslog("Checking data tables in nova.")
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    cursor.execute("SHOW TABLES;")
    result = cursor.fetchall()
    date_list = []
    for item in result:
        if item[0] != "data" and item[0] != "daily_avg" and item[0] != "nodes" and item[0] != "system_config":
            cursor.execute("SELECT DISTINCT mac FROM " + item[0] + " ORDER BY mac ASC;")
            macs = cursor.fetchall()
            for mac in macs: date_list.append((mac[0], item[0].split("_")[0]))
    return date_list


def calc_daily_avg():
    db_connection = SQL_connection_handler()
    avg_list = check_daily_avg(db_connection)
    date_list = check_daily_tables(db_connection)
    cursor = db_connection.cursor()
    cursor.execute("USE " + str(db_connection.database) + ";")
    if avg_list == None: avg_list = []
    for pop in avg_list:
        for mac in date_list:
            if str(mac[0]) == str(pop[0]) and str(mac[1]) == str(pop[1]): date_list.remove(mac)
    if len(date_list) < 1:  cslog("No new dates for calculating daily average.")
    for item in date_list:
        cslog("Calculating daily averages for " + item[0] + " on " + item[1])
        mac = item[0]
        date = item[1] + "_data"
        avg_cmd = "SELECT AVG(temp), AVG(hum) FROM " + date + " WHERE mac='" + mac + "';"
        cursor.execute(avg_cmd)
        result = cursor.fetchall()
        avg_temp = round(result[0][0], 2)
        avg_hum = round(result[0][1], 2)
        insert_avg_cmd = "INSERT INTO daily_avg(mac, date, avg_temp, avg_hum) VALUES('" + mac + "', " + str(item[1]) + ", " + str(avg_temp) + ", " + str(avg_hum) + ");"
        cursor.execute(insert_avg_cmd)
    db_connection.commit()
    SQL_disconnection_handler(db_connection)


def thread(thread_id, connection, list, start, end):
    cursor = connection.cursor()
    cursor.execute("USE " + str(connection.database) + ";")
    for i in range(start, end + 1): cursor.execute(list[i])
    # sys.stdout.write(str(thread_id) + " [" + str(i) + "] " + list[i] + "\n")
    connection.commit()
    connection.close()


def sql_cmd_maker(connection):
    date_stamp = datetime.datetime.utcnow().date().strftime('%Y%m%d')
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
    cslog("Validating data time, checking dates.")
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
    if cmd_counter == 0: cslog("No data to be backed up.")
    else: cslog("Backing up " + str(cmd_counter) + " data points.")
    return insert_list, remove_list


def backup_daily_data():
    db_connection = SQL_connection_handler()
    insert_list, remove_list = sql_cmd_maker(db_connection)
    SQL_disconnection_handler(db_connection)

    insert_len = len(insert_list)
    remove_len = len(remove_list)
    insert_cmd_per_thread = int(math.floor(insert_len / input_arg.threads))
    remove_cmd_per_thread = int(math.floor(remove_len / input_arg.threads))
    insert_end = insert_len - 1
    remove_end = remove_len - 1
    thread_list = []

    for i in range(0, input_arg.threads):
        conn1 = SQL_connection_handler(verbose=False)
        conn2 = SQL_connection_handler(verbose=False)
        insert_start = int(i * insert_cmd_per_thread)
        insert_end = int(insert_cmd_per_thread * (i + 1) - 1)
        remove_start = int(i * remove_cmd_per_thread)
        remove_end = int(remove_cmd_per_thread * (i + 1) - 1)

        insert_thread = threading.Thread(target=thread, args=(i, conn1, insert_list, insert_start, insert_end))
        remove_thread = threading.Thread(target=thread, args=(i, conn2, remove_list, remove_start, remove_end))
        thread_list.append(insert_thread)
        thread_list.append(remove_thread)

    if insert_end != insert_len - 1:
        conn_end1 = SQL_connection_handler(verbose=False)
        insert_thread = threading.Thread(target=thread, args=(i + 1, conn_end1, insert_list, insert_end + 1, insert_len - 1))
        thread_list.append(insert_thread)

    if remove_end != remove_len - 1:
        conn_end2 = SQL_connection_handler(verbose=False)
        remove_thread = threading.Thread(target=thread, args=(i + 1, conn_end2, remove_list, remove_end + 1, remove_len - 1))
        thread_list.append(remove_thread)

    for item in thread_list: item.start()
    for item in thread_list: item.join()


def time_formatter(delta_seconds):
    if int(delta_seconds) < 2: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " second"
    elif int(delta_seconds) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " seconds"
    elif int(delta_seconds / 60) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " minute"
    elif int(delta_seconds / 60) > 1 and int(delta_seconds / 60) < 60: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " minutes"
    elif int(delta_seconds / (60 * 60)) == 1: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hour"
    else: time_info = str(datetime.timedelta(seconds=delta_seconds)) + " hours"
    return time_info


def check_node_status():
    db_connection = SQL_connection_handler()
    cursor = db_connection.cursor()
    cursor.execute("USE " + str(db_connection.database) + ";")
    cursor.execute("SELECT mac, start_time, time_stamp, status FROM nodes;")
    result = cursor.fetchall()
    if len(result) < 1: cslog("No Nodes found")
    else:
        cslog("Checking node status.")
        for item in result:
            current_time = int(time.time())
            node_start_time = item[1]
            last_node_time = item[2]
            if current_time - last_node_time > input_arg.status_timeout * 60:
                time_info = time_formatter(current_time - last_node_time)
                cslog("Node: " + item[0] + " last seen " + time_info + " ago. Updating status to offline.")
                update_status_sql = "UPDATE nodes SET start_time=0, status=false WHERE mac='" + item[0] + "';"
                cursor.execute(update_status_sql)
                db_connection.commit()
            else:
                time_info = time_formatter(current_time - last_node_time)
                online_time = time_formatter(current_time - node_start_time)
                cslog("Node: " + item[0] + " last seen " + time_info + " ago.")
                cslog("Node: " + item[0] + " Online for " + online_time)
                update_status_sql = "UPDATE nodes SET status=true WHERE mac='" + item[0] + "';"
                cursor.execute(update_status_sql)
                db_connection.commit()
    SQL_disconnection_handler(db_connection)


def reset_db():
    try:
        yaml_stream = open("server_info.yaml", 'r')
        mysql_cred = yaml.safe_load(yaml_stream)["mysql_cred"]

        try:
            db_connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
            cursor = db_connection.cursor()
        except:
            db_connection = mysql.connector.connect(host=mysql_cred["HOST"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
            cursor = db_connection.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS " + mysql_cred["DATABASE"] + ";")
            db_connection.commit()

        cslog("Resetting Database: " + mysql_cred["DATABASE"])
        cursor.execute("USE " + mysql_cred["DATABASE"] + ";")
        cursor.execute("DROP DATABASE " + mysql_cred["DATABASE"] + ";")
        cursor.execute("CREATE DATABASE IF NOT EXISTS " + mysql_cred["DATABASE"] + ";")
        cursor.execute("USE " + mysql_cred["DATABASE"] + ";")
        cursor.execute("CREATE TABLE IF NOT EXISTS data(id INT NOT NULL AUTO_INCREMENT, mac VARCHAR(17), time BIGINT, temp DECIMAL (18, 2), hum DECIMAL (18, 2), PRIMARY KEY (id));")
        cursor.execute("CREATE Table IF NOT EXISTS nodes(mac VARCHAR(17), ip CHAR(39), port INT, start_time BIGINT, time_stamp BIGINT, status boolean, display boolean DEFAULT False, PRIMARY KEY (mac));")
        cursor.execute("CREATE Table IF NOT EXISTS system_config(host_ip CHAR(39), host_port INT);")
        cursor.execute("CREATE TABLE IF NOT EXISTS daily_avg(mac VARCHAR(17), date BIGINT, avg_temp DECIMAL (18, 2), avg_hum DECIMAL (18, 2), PRIMARY KEY (mac, date));")
        db_connection.commit()
        cslog("Reset Complete\n")
    except mysql.connector.Error as error:
        cslog(str(error))


def input_checker():
    try:
        sys.argv[1]
    except:
        parser.print_help()
        sys.exit()
    try:
        if input_arg.set_host != None:
            ipaddress.ip_address(input_arg.set_host.split(":")[0])
            if int(input_arg.set_host.split(":")[1]) < 1 or int(input_arg.set_host.split(":")[1]) > 65535: raise Exception("Invalid Host IP/PORT to be set: " + str(input_arg.set_host))
        if input_arg.udp_timeout < 1: raise Exception("Invalid UDP Timeout set")
        if input_arg.Listen_PORT < 0 or input_arg.Listen_PORT > 65535: raise Exception("Invalid UDP Listening PORT to be set: " + str(input_arg.Listen_PORT))
        if input_arg.NODE_IP != None: ipaddress.ip_address(input_arg.NODE_IP)
        if input_arg.NODE_PORT < 1 or input_arg.NODE_PORT > 65535: raise Exception("Invalid NODE PORT to be set: " + str(input_arg.Listen_PORT))
        if input_arg.status_timeout < 1: raise Exception("Invalid Node offline Timeout set")
        if input_arg.threads < 1: raise Exception("Invalid number of Threads set")
        if input_arg.update and input_arg.Listen_PORT < 1: raise Exception("-L Listen_PORT flag must be set for updating database")
    except Exception as error:
        sys.exit(str(error) + ". -h for help")


def SQL_connection_handler(verbose=True):
    yaml_stream = open("server_info.yaml", 'r')
    mysql_cred = yaml.safe_load(yaml_stream)["mysql_cred"]
    if verbose: cslog("Connecting to database " + str(mysql_cred["DATABASE"]) + ".")
    db_connection = mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')
    return db_connection


def SQL_disconnection_handler(connection):
    cslog("Closing DB connection")
    connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--fetch", action='store_true', help='Pull data from Node(s) and send to host')
    parser.add_argument("-p", "--ping", action='store_true', help='Ping Node(s)')
    parser.add_argument("-r", "--reboot", action='store_true', help='Reboot Node(s)')
    parser.add_argument("-sh", action='store', type=str, dest="set_host", help='Set Node(s) host IP and PORT <IP:PORT> (where nodes will send data to)')
    parser.add_argument("-t", action='store', type=int, default=5, dest="udp_timeout", help='UDP listener socket time out (in seconds)')
    parser.add_argument('-L', action='store', type=int, default=0, dest="Listen_PORT", help='UDP listen mode on PORT')
    parser.add_argument('-u', "--update", action='store_true', help='Update Node Status in database with UDP response (-L flag must be set)')
    parser.add_argument("-IP", action='store', type=str, dest="NODE_IP", default="192.168.1.255", help='Send command to specified Node(s) IPV4 Address (Default: Broadcast IP)')
    parser.add_argument("-P", action='store', type=int, dest="NODE_PORT", default=9996, help='Send command to specified Node(s) UDP listening port (Default: 9996)')
    parser.add_argument("-a", "--average", action='store_true', help='Daily data average check.')
    parser.add_argument("-s", "--node_status", action='store_true', help='Node(s) Status check.')
    parser.add_argument("-ts", action='store', type=int, dest="status_timeout", default=5, help='Daily average check timeout (default 5 minutes).')
    parser.add_argument("-b", "--backup", action='store_true', help='Daily data backup')
    parser.add_argument("-threads", action='store', type=int, default=1, help='Number of threads for backup SQL commands.')
    parser.add_argument("-R", "--reset_db", action='store_true', help='Rest SQL database.')
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')
    input_arg = parser.parse_args()

    input_checker()

    log_path = os.getcwd() + os.sep + datetime.datetime.now().strftime("%y%m%d") + "_appServer.log"
    if input_arg.log: logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s, %(name)s, [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    if input_arg.fetch or input_arg.ping or input_arg.reboot or input_arg.set_host != None: node_cmd_handler()
    if input_arg.node_status: check_node_status()
    if input_arg.backup: backup_daily_data()
    if input_arg.average: calc_daily_avg()
    if input_arg.reset_db: reset_db()
    if platform.system() == "linux" or platform.system() == "linux2": os.system("sudo apt-get clean")
    if input_arg.log: logging.shutdown()
