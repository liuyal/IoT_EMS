import sys, threading, os, time
import socket as socks
from socket import *


def udp_broadcast(msg, UDP_IP="192.168.1.255", UDP_PORT=9996):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.sendto(msg, (UDP_IP, UDP_PORT))

def udp_send(msg, UDP_IP="127.0.0.1", UDP_PORT=9996):
    time.sleep(2)
    sock = socks.socket(socks.AF_INET, socks.SOCK_DGRAM)
    sock.sendto(msg, (UDP_IP, UDP_PORT))

def udp_listener(mac="", UDP_IP="0.0.0.0", UDP_PORT=9996):
    sock = socks.socket(socks.AF_INET, socks.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    # TODO: add TIME OUT
    # TODO: Check/update db status
    while True:
        data, address = sock.recvfrom(1024)
        print(str(address) + ": " + str(data))
        if mac in str(data): break

if __name__ == "__main__":


    # UDP_IP = "192.168.1.255"
    UDP_IP = "192.168.1.74"
    UDP_PORT = 9996
    mac = "BC:DD:C2:2F:47:79"
    try: cmd = sys.argv[1]
    except:
        print("No Arguments, Usage:\n\t[get_data]\n\t[ping]\n\t[set_ip|<IP>]")
        sys.exit()
    msg = b"[" + cmd.encode('utf-8') + b"]\n"

    if UDP_IP.split('.')[-1] == "255": thread_send = threading.Thread(target=udp_broadcast, args=(msg, UDP_IP, UDP_PORT))
    else: thread_send = threading.Thread(target=udp_send, args=(msg, UDP_IP, UDP_PORT))
    thread_listen  = threading.Thread(target=udp_listener, args=(mac, "0.0.0.0",UDP_PORT))

    thread_send.start()
    thread_listen.start()

    thread_send.join()
    thread_listen.join()















