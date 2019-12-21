import os, sys, threading, time, argparse, ipaddress, logging, queue, re
from argparse import RawTextHelpFormatter
import socket as socket
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

# TODO: Add logging
def cslog(msg, flag="info"):
    print(msg)


def udp_broadcast(msg, v_flag=False, UDP_IP="192.168.1.255", UDP_PORT=9996):
    time.sleep(2)
    for item in msg:
        if v_flag: cslog("Start Broadcasting: " + str(item) + " to " + UDP_IP + ":" + str(UDP_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(item, (UDP_IP, UDP_PORT))
        sock.close()
        time.sleep(1)
    if v_flag: cslog("Broadcast Done")


def udp_send(msg, v_flag=False, UDP_IP="127.0.0.1", UDP_PORT=9996):
    time.sleep(2)
    for item in msg:
        if v_flag: cslog("Start Sending: " + str(item) + " to " + UDP_IP + ":" + str(UDP_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(item, (UDP_IP, UDP_PORT))
        sock.close()
        time.sleep(1)
    if v_flag: cslog("Send Done")


def udp_listener(msg_queue, v_flag=False, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    data_list = []
    p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(time_out)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        if v_flag: cslog("Start Listener on: " + UDP_IP + ":" + str(UDP_PORT))
        while True:
            data, address = sock.recvfrom(1024)
            mac = re.findall(p, str(data))
            if len(mac) != 0:
                packet = {"ip" : address[0], "port" : address[1], "mac" : mac, "data" : data, "time": int(time.time())}
                data_list.append(packet)
            if v_flag: cslog(str(address) + ": " + str(data))
    except socket.timeout:
        if v_flag: cslog("Listening done, Closing socket")
        sock.close()
    msg_queue.put(data_list)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=RawTextHelpFormatter)
    parser.add_argument("-f", "--fetch", action='store_true', help='Pull data from Node(s) and send to host')
    parser.add_argument("-P", "--ping", action='store_true', help='Ping Node(s)')
    parser.add_argument("-r", "--reboot",action='store_true', help='Reboot Node(s)')
    parser.add_argument("-s", "--set", action='store', type=str, dest="HOST_IP", help='Set Node(s) host IP (where nodes will send data to)')
    parser.add_argument("-ip", action='store', type=str, dest="NODE_IP", default="192.168.1.255", help='Send command to specified Node(s) IPV4 Address (Default: Broadcast IP)')
    parser.add_argument("-p", action='store', type=int, dest="NODE_PORT", default=9996, help='Send command to specified Node(s) UDP listening port (Default: 9996)')
    parser.add_argument("-t", action='store', type=int, default=5, help='UDP listener socket time out (in seconds)')
    parser.add_argument('-u', action='store_true', help='Update Node Status in database with UDP response')
    parser.add_argument('-v', "--verbose", action='store_true', help='Verbose mode')
    input_arg = parser.parse_args()

    try: ipaddress.ip_address(str(input_arg.NODE_IP))
    except: input_arg.NODE_IP = "192.168.1.255";
    try:
        if input_arg.NODE_PORT < 0 or input_arg.NODE_PORT > 65535: raise Exception("Invalid Port")
    except: cslog("Invalid IP, using Default: 9996"); input_arg.NODE_PORT = 9996
    try:
        if input_arg.HOST_IP != None: ipaddress.ip_address(str(input_arg.HOST_IP))
    except: parser.print_usage(); sys.exit("Invalid Host IP to be set: " + str(input_arg.HOST_IP));

    cmd = []
    if input_arg.fetch: cmd.append(b"[fetch_data]\n")
    if input_arg.ping: cmd.append(b"[ping]\n")
    if input_arg.reboot: cmd.append(b"[reboot]\n")
    if input_arg.HOST_IP != None: cmd.append(("[set_ip|" + str(input_arg.HOST_IP) + "]\n").encode('utf8'))
    if len(cmd) == 0: parser.print_help(); cslog("\nNo command parameters set, default to [Ping]"); input_arg.ping = True; cmd.append(b"[ping]\n")

    if input_arg.verbose: cslog(input_arg)

    msg_queue = queue.Queue()
    if input_arg.NODE_IP.split('.')[-1] == "255": thread_send = threading.Thread(target=udp_broadcast, args=(cmd, input_arg.verbose, input_arg.NODE_IP, input_arg.NODE_PORT))
    else: thread_send = threading.Thread(target=udp_send, args=(cmd, input_arg.verbose, input_arg.NODE_IP, input_arg.NODE_PORT))
    thread_listen = threading.Thread(target=udp_listener, args=(msg_queue, input_arg.verbose, "0.0.0.0", input_arg.NODE_PORT, input_arg.t))
    thread_send.start()
    thread_listen.start()
    thread_send.join()
    thread_listen.join()

    # TODO: Check/update db status
    msg = msg_queue.get()


    print()







