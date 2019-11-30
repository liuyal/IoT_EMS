import socket
from socket import *

UDP_IP = "192.168.1.255"
UDP_PORT = 9996
msg = b"[get_data]\n"

sock = socket(AF_INET, SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
sock.sendto(msg, (UDP_IP, UDP_PORT))