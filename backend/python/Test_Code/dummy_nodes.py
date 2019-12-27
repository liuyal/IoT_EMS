import os, sys, threading, time, requests, random, argparse
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import send
import socket as socket


def rand_mac():
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    c = random.randint(0, 255)
    d = random.randint(0, 255)
    e = random.randint(0, 255)
    f = random.randint(0, 255)
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (a, b, c, d, e, f)


def udp_listener(thread_id, cv, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    global data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(time_out)
    sock.bind((UDP_IP, UDP_PORT))
    try:
        while True:
            data, address = sock.recvfrom(1024)
            cv.acquire()
            cv.notifyAll()
            cv.release()
            sys.stdout.write("[" + str(thread_id) + "] Packet: " + str(address) + "\t" + str(data) + "\n")
    except socket.timeout:
        sock.close()


def dummy_node(thread_id, cv, mac, ip="0.0.0.0", host_ip="0.0.0.0", port=9996):
    global data
    dst_ip = host_ip
    msg = b""
    while True:
        try:
            cv.acquire()
            cv.wait()
            cv.release()
            if "fetch_data" in str(data):
                epoch = int(time.time())
                temp = round(random.uniform(-10, 40), 2)
                hum = round(random.uniform(0, 100), 2)
                insert_req = "http://" + host_ip + "/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
                # insert_req = "http://localhost/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
                response = requests.get(insert_req)
                msg = ("[" + mac + "|data_sent|" + str(epoch) + "|" + str(temp) + "|" + str(hum) + "]\n")
                sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n", " ") + str(response.json()) + "\n")
            elif "ping" in str(data):
                msg = ("[" + mac + "|pong|" + dst_ip + "|" + ip + "]\n")
                sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n", "") + "\n")
            elif "reboot" in str(data):
                msg = ("[" + mac + "|rebooting]\n")
                sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n", "") + "\n")
            elif "set_ip" in str(data):
                start_index = str(data).index("|")
                end_index = str(data).index("]")
                dst_ip = str(data)[start_index + 1:end_index]
                msg = "[" + mac + "|ip_set]\n"
                sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n", "") + "\n")

            packet = IP(src=ip, dst=dst_ip) / UDP(sport=port, dport=port) / msg
            send(packet, verbose=False)

        except Exception as error:
            print(str(error))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', action='store', dest="nodes", default=5, help='Verbose mode')
    input_arg = parser.parse_args()
    try: sys.argv[1]
    except: parser.print_help();

    n_nodes = int(input_arg.nodes)
    data = ""
    condition = threading.Condition()
    thread_list = []

    listener = threading.Thread(target=udp_listener, args=(0, condition, "0.0.0.0", 9996, 6000))
    thread_list.append(listener)

    print("Starting " + str(n_nodes) + " Dummy Nodes...")
    for i in range(1, n_nodes + 1):
        random.seed(i)
        node_mac = rand_mac()
        node_ip = "192.168.1." + str(i)
        dummy_node_thread = threading.Thread(target=dummy_node, args=(i, condition, node_mac, node_ip, "192.168.1.80", 9996))
        thread_list.append(dummy_node_thread)
        print("Node [" + str(i) + "]: " + node_mac + "|" + node_ip)
    try:
        for item in thread_list: item.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt. Stopping script.")