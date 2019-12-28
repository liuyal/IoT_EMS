import os, sys, threading, time, ipaddress, queue
import socket as socket


def udp_broadcast(msg, UDP_IP="192.168.1.255", UDP_PORT=9996):
    time.sleep(1)
    for item in msg:
        print("Start Broadcasting: " + str(item) + " to " + UDP_IP + ":" + str(UDP_PORT))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(item, (UDP_IP, UDP_PORT))
        sock.close()
        time.sleep(1)
    print("Broadcast Done.")


def udp_listener(msg_queue, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    data_list = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(time_out)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        print("Start Listener on: " + UDP_IP + ":" + str(UDP_PORT))
        while True:
            data, address = sock.recvfrom(1024)
            print("Packet: " + str(address) + "\t" + str(data))
    except socket.timeout:
        print("Listening done, Closing socket.")
        sock.close()
    msg_queue.put(data_list)


if __name__ == "__main__":
    cmd = [b"[ping]"]
    msg_queue = queue.Queue()
    
    # thread_send = threading.Thread(target=udp_broadcast, args=(cmd, "192.168.1.255", 9996))
    thread_listen = threading.Thread(target=udp_listener, args=(msg_queue, "0.0.0.0", 9996, 600))

    # thread_send.start()
    thread_listen.start()

    # thread_send.join()
    thread_listen.join()
