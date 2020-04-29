import os, sys, threading, time, argparse, ipaddress, logging, queue, re, yaml, datetime, platform, math
import socket as socket
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


def sql_node_status_update(update_list, connection):
    try:
        cslog("Updating node status.")
        cursor = connection.cursor()
        cursor.execute("USE " + str(connection.database) + ";")
        for item in update_list:
            search_cmd = "SELECT mac FROM nodes WHERE mac='" + item["mac"] + "';"
            cursor.execute(search_cmd)
            result = cursor.fetchall()
            if len(result) < 1:
                add_node = "INSERT INTO nodes(mac, ip, port, time_stamp, status) VALUES('" + str(item["mac"]) + "', '" + item["ip"] + "', " + str(item["port"]) + ", " + str(item["time"]) + ", TRUE)"
                cursor.execute(add_node)
            else:
                update_cmd = "UPDATE nodes SET time_stamp=" + str(item["time"]) + ", ip='" + item["ip"] + "', port=" + str(item["port"]) + ", status=true WHERE mac='" + item["mac"] + "';"
                cursor.execute(update_cmd)
        connection.commit()
    except Exception as error:
        cslog("Failed {}".format(error), flag="error")


def sql_insert(insert_list, connection):
    try:
        cslog("Inserting data into database")
        cursor = connection.cursor()
        cursor.execute("USE " + str(connection.database) + ";")
        for item in insert_list:
            packet = item["data"].decode("utf-8")[item["data"].decode("utf-8").index('[') + 1:item["data"].decode("utf-8").index(']')].split("|")
            mac = item["mac"]
            epoch = item["time"]
            temp = packet[3]
            hum = packet[4]
            sql_cmd = "INSERT INTO DATA(mac, time, temp, hum) VALUES('" + str(mac) + "', " + str(epoch) + ", " + str(temp) + ", " + str(hum) + ");"
            cursor.execute(sql_cmd)
        connection.commit()
    except Exception as error:
        cslog("Failed {}".format(error), flag="error")


def node_cmd_handler():
    if not input_arg.fetch and not input_arg.ping and not input_arg.reboot and not input_arg.set_host: return
    cmd = []
    msg_queue = queue.Queue()
    thread_listen = None
    cslog("Started UDP Command Handler")
    if input_arg.fetch: cmd.append(b"[fetch_data]\n")
    if input_arg.ping: cmd.append(b"[ping]\n")
    if input_arg.reboot: cmd.append(b"[reboot]\n")
    if input_arg.set_host != None: cmd.append(("[set_host|" + str(input_arg.HOST_IP) + "]\n").encode('utf8'))

    if input_arg.NODE_IP.split('.')[-1] == "255":
        thread_send = threading.Thread(target=udp_broadcast, args=(cmd, input_arg.NODE_IP, input_arg.NODE_PORT))
    else:
        thread_send = threading.Thread(target=udp_send, args=(cmd, input_arg.NODE_IP, input_arg.NODE_PORT))

    if input_arg.Listen_PORT > 0: thread_listen = threading.Thread(target=udp_listener, args=(msg_queue, "0.0.0.0", input_arg.Listen_PORT, input_arg.udp_timeout))

    thread_send.start()
    if input_arg.Listen_PORT > 0: thread_listen.start()

    thread_send.join()
    if input_arg.Listen_PORT > 0: thread_listen.join()

    if input_arg.update and input_arg.Listen_PORT > 0:
        db_connection = SQL_connection_handler()
        msg = msg_queue.get()
        mac_list = (list(set(msg_queue.get())))

        # sql_node_status_update(msg, db_connection)
        # sql_insert(msg, db_connection)

        SQL_disconnection_handler(db_connection)


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


def SQL_connection_handler():
    yaml_stream = open("server_info.yaml", 'r')
    mysql_cred = yaml.safe_load(yaml_stream)["mysql_cred"]
    cslog("Connecting to database " + str(mysql_cred["DATABASE"]) + ".")
    return mysql.connector.connect(host=mysql_cred["HOST"], database=mysql_cred["DATABASE"], user=mysql_cred["USER"], password=mysql_cred["PASSWORD"], auth_plugin='mysql_native_password')


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
    parser.add_argument("-s", "--status", action='store_true', help='Node(s) Status check.')
    parser.add_argument("-ts", action='store', type=int, dest="status_timeout", default=5, help='Daily average check timeout (default 5 minutes).')
    parser.add_argument("-b", "--backup", action='store_true', help='Daily data backup')
    parser.add_argument("-threads", action='store', type=int, default=1, help='Number of threads for backup SQL commands.')
    parser.add_argument("-reset", "--reset", action='store_true', help='Rest SQL database.')
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')
    input_arg = parser.parse_args()
    print(input_arg)

    input_checker()

    # TODO: NEW log BY DATE
    Date = ""
    log_path = os.getcwd() + os.sep + Date + "-appServer.log"
    if input_arg.log: logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s, %(name)s, [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    node_cmd_handler()
