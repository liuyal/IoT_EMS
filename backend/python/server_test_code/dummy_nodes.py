import os, sys, threading, time, requests, random, queue
import socket as socket


def rand_mac():
    a = random.randint(0, 255)
    b = random.randint(0, 255)
    c = random.randint(0, 255)
    d = random.randint(0, 255)
    e = random.randint(0, 255)
    f = random.randint(0, 255)
    mac = "%02x:%02x:%02x:%02x:%02x:%02x" % (a, b, c, d, e, f)
    return mac


def udp_listener(thread_id, cv, UDP_IP="0.0.0.0", UDP_PORT=9996, time_out=5):
    global data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
    msg = b""

    while True:
        cv.acquire()
        cv.wait()
        cv.release()

        if "fetch_data" in str(data):
            epoch = int(time.time())
            temp = round(random.uniform(-10, 40), 2)
            hum = round(random.uniform(0, 100), 2)
            # insert_req = "http://" + host_ip + "/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
            insert_req = "http://localhost/Temperature_System/backend/php/insert.php?mac=" + mac + "&time=" + str(epoch) + "&temp=" + str(temp) + "&hum=" + str(hum)
            response = requests.get(insert_req)
            msg = ("[" + mac + "|data_sent|" + str(epoch) + "|" + str(temp) + "|" + str(hum) + "]\n")
            sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n","") + str(response.json()) + "\n")
        if "ping" in str(data):
            msg = ("[" + mac + "|pong|" + host_ip + "|" + ip + "]\n")
            sys.stdout.write("[" + str(thread_id) + "] " + msg.replace("\n","") + "\n")

        # TODO: add missing commands

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg.encode("utf-8"), (host_ip, port))
        sock.close()


if __name__ == "__main__":

    n_nodes = 5
    data = ""
    condition = threading.Condition()
    thread_list = []

    listener = threading.Thread(target=udp_listener, args=(0, condition, "0.0.0.0", 9996, 600))
    thread_list.append(listener)

    print("Starting " + str(n_nodes) + " Dummy Nodes...")
    for i in range(1, n_nodes+1):
        random.seed(i)
        node_mac = rand_mac()
        print("Node [" + str(i) + "]: " + node_mac)
        dummy_node_thread = threading.Thread(target=dummy_node, args=(i, condition, node_mac, "0.0.0.0", "192.168.1.103", 9996))
        thread_list.append(dummy_node_thread)
    print()
    for item in thread_list: item.start()
