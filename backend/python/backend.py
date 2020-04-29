import os, sys, threading, time, argparse, ipaddress, logging, queue, re, yaml, datetime
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



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--fetch", action='store_true', help='Pull data from Node(s) and send to host')
    parser.add_argument("-P", "--ping", action='store_true', help='Ping Node(s)')
    parser.add_argument("-r", "--reboot", action='store_true', help='Reboot Node(s)')
    parser.add_argument("-sh", "--sethost", action='store', type=str, dest="dest", help='Set Node(s) host IP and PORT <IP:PORT> (where nodes will send data to)')
    parser.add_argument("-t", "--timeout", action='store', type=int, default=5, help='UDP listener socket time out (in seconds)')
    parser.add_argument('-L', "--listen", action='store', type=int, default=0, dest="ListenPORT", help='UDP listen mode on PORT')
    parser.add_argument('-u', "--update", action='store_true', help='Update Node Status in database with UDP response (-L flag must be set)')
    parser.add_argument("-ip", action='store', type=str, dest="NODE_IP", default="192.168.1.255", help='Send command to specified Node(s) IPV4 Address (Default: Broadcast IP)')
    parser.add_argument("-p", action='store', type=int, dest="NODE_PORT", default=9996, help='Send command to specified Node(s) UDP listening port (Default: 9996)')
    parser.add_argument("-a", "--average", action='store_true', help='Daily data average check.')
    parser.add_argument("-s", "--status", action='store_true', help='Node(s) Status check.')
    parser.add_argument("-ts", "--statusTimeout", action='store', type=int, default=5, help='Daily average check.')
    parser.add_argument("-b", "--backup", action='store_true', help='Daily data backup')
    parser.add_argument('-th', "--threads", action='store', default=1, help='Number of threads each for SQL insert and remove.')
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    parser.add_argument('-l', "--log", action='store_true', help='Log to file')

    input_arg = parser.parse_args()

    try:
        sys.argv[1]
    except:
        parser.print_help()
        sys.exit()

    log_path = os.getcwd() + os.sep + "appServer.log"

    if input_arg.log:
        logging.basicConfig(filename=log_path, filemode='a', format='%(asctime)s, %(name)s, [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    print(input_arg)
