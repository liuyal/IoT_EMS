import socket, sys
from socket import *

try:
    sys.argv[1]
except:
    print("No Arguments, Usage:")
    print("\tget_data")
    print("\tping")
    print("\tset_ip|<IP>")
    sys.exit()

UDP_IP = "192.168.1.74"
# UDP_IP = "192.168.1.255"
UDP_PORT = 9996

cmd = sys.argv[1]
msg = b"[" + cmd.encode('utf-8') + b"]\n"

# sock = socket(AF_INET, SOCK_DGRAM)
# sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
# sock.sendto(msg, (UDP_IP, UDP_PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(msg, (UDP_IP, UDP_PORT))
