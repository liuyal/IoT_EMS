import os, sys, threading, time
import socket as socket


def print_usage():
    print("Usage: udp_cmd.py <IP>:<PORT> [Command]")
    print("\tIP:\t\tNode(s) IPV4 Address (Default: Broadcast IP)")
    print("\tPORT:\tNode(s) UDP listening port (Default: 9996)")
    print("\tCommands:")
    print("\t\t[fetch_data] - Tell Node(s) to send data to host")
    print("\t\t[ping] - Tell Node(s) to send data to host")
    print("\t\t[reboot] - Reboot Node(s)")
    print("\t\t[set_ip|<IP>] - Set Node(s) host IP (where to send data)")
    sys.exit("")


def udp_broadcast(msg, UDP_IP="192.168.1.255", UDP_PORT=9996):
    time.sleep(2)
    print("Start Broadcasting: " + str(msg) + " to " + UDP_IP + ":" + str(UDP_PORT))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(msg, (UDP_IP, UDP_PORT))
    sock.close()
    print("Broadcast Done")


def udp_send(msg, UDP_IP="127.0.0.1", UDP_PORT=9996):
    time.sleep(2)
    print("Start Sending: " + str(msg) + " to " + UDP_IP + ":" + str(UDP_PORT))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (UDP_IP, UDP_PORT))
    sock.close()
    print("Send Done")


# TODO: Check/update db status
def udp_listener(cmd, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    data_list = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(time_out)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        print("Start Listener on: " + UDP_IP + ":" + str(UDP_PORT))
        while True:
            data, address = sock.recvfrom(1024)
            packet = {"ip": address[0], "port": address[1], "data": data}
            data_list.append(packet)
            print(str(address) + ": " + str(data))
    except socket.timeout:
        print("Listening done, Closing socket")
        sock.close()



if __name__ == "__main__":

    cmd_list = ["fetch_data", "ping", "reboot", "set_ip"]
    cmd = ""
    UDP_IP = "192.168.1.255"
    UDP_PORT = 9996
    socket_time_out = 5

    try: cmd = sys.argv[1]
    except: print_usage()

    if len(sys.argv) == 2:
        in_list = False
        for item in cmd_list:
            if item in cmd: in_list = True; break;
        if not in_list: print_usage()
    elif len(sys.argv) == 3:
        cmd = sys.argv[2]
        try:
            UDP_IP = sys.argv[1].split(":")[0]
            socket.inet_aton(UDP_IP)
        except socket.error: UDP_IP = "192.168.1.255"; print("Invalid IP, using Default: " + UDP_IP)
        try:
            UDP_PORT = int(sys.argv[1].split(":")[1])
            if UDP_PORT < 0 or UDP_PORT > 65535: raise Exception("Invalid Port")
        except Exception as error: UDP_PORT = 9996; print("Invalid Port, using Default: " + str(UDP_PORT))
        in_list = False
        for item in cmd_list:
            if item in cmd: in_list = True; break;
        if not in_list: print_usage()

    msg = cmd.encode('utf-8') + b"\n"
    if UDP_IP.split('.')[-1] == "255": thread_send = threading.Thread(target=udp_broadcast, args=(msg, UDP_IP, UDP_PORT))
    else: thread_send = threading.Thread(target=udp_send, args=(msg, UDP_IP, UDP_PORT))
    thread_listen = threading.Thread(target=udp_listener, args=(cmd, "0.0.0.0", UDP_PORT, socket_time_out))
    thread_send.start()
    thread_listen.start()
    thread_send.join()
    thread_listen.join()















