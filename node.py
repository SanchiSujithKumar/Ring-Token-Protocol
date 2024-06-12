import time
import threading
import socket
import json
import random
import bisect

id = 0
forward_packet = False
packet = ""
payload = []
send_packet = False
limit = 3
tl = 0
num_of_packets_to_send = 0
ready = False
time_tracking = 0
token = {}
msg_to_be_received = 0
MAX_NOP = 5

def distribute_tuples(tuples):
    from collections import defaultdict
    global MAX_NOP
    groups = defaultdict(list)
    for a, b in tuples:
        groups[a].append((a, b))
    result = []
    max_consecutive = MAX_NOP
    
    while groups:
        for a in sorted(groups.keys()):
            count = min(max_consecutive, len(groups[a]))
            result.extend(groups[a][:count])
            groups[a] = groups[a][count:]
            if not groups[a]:
                del groups[a]
    
    return result

def set_tl():
    global tl
    tl = 1
    threading.Timer(10, reset_tl).start()
    
def reset_tl():
    global tl
    tl = 0

def inputsocket(input_socket):
    global forward_packet, packet, id, payload, token, send_packet, limit, tl, num_of_packets_to_send, ready, time_tracking, msg_to_be_received

    start_time = 0
    retransmission = 0
    waiting_for_token = False
    total_time_taken = 0.0
    num_of_packets_deliverd = 0
    
    def check_time():
        threading.Timer(1.5, send_signal).start()
            
    def send_signal():
        global time_tracking, token, packet, forward_packet, msg_to_be_received

        if msg_to_be_received and time.time()-time_tracking>1.5:
            token["ack"] = False
            msg_to_be_received = 0
            packet = json.dumps(token).encode()
            forward_packet = True

    while True:
        if not forward_packet:
            message = input_socket.recv(1024)
            
            # expanding the ring
            if message == b'cis':
                input_socket.send('.'.encode())
                host = 'localhost'
                port = input_socket.recv(1024).decode()
                input_socket.send('.'.encode())
                input_socket.close()
                input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                input_socket.connect((host, int(port)))
                continue

            received_packet = message.decode()

            if not received_packet.startswith("{") :
                if not waiting_for_token :
                    if msg_to_be_received > 0 :
                        print("\n[Message received] <node" + str(token["source_id"]) + ">: " + received_packet[:-1])
                        msg_to_be_received -= 1
                        idx = (MAX_NOP-1)-int(received_packet[-1])
                        token["bitmap"] = token["bitmap"][:idx] + '1' + token["bitmap"][idx+1:]
                        if msg_to_be_received == 0 :
                            token["ack"] = True
                            packet = json.dumps(token).encode()
                            forward_packet = True
                    else :
                        packet = message
                        forward_packet = True
                input_socket.send('.'.encode())
                continue

            token = json.loads(received_packet)
            if token["destination_id"] == id and token["source_id"] != 0:
                x = random.random()
                x = 0.4
                if x > 0.3:
                    msg_to_be_received = token["num_of_packets"]
                    time_tracking = time.time()
                    check_time()
                    # token["ack"] = True
                    input_socket.send('.'.encode())
                    continue
                message = json.dumps(token).encode()

            if not token["is_taken"] and send_packet and tl==0:
                token["source_id"] = id
                token["is_taken"] = True
                print("\nHolding Token\n")
                start_time = time.time()
            
            if token["is_taken"] and token["source_id"] == id:
                if token["ack"] or retransmission == 2:
                    rtt = time.time() - token["time_sent"]
                    print(token["num_of_packets"], "packets sent to node", token["destination_id"])
                    print("RTT:", rtt)
                    print()
                    total_time_taken += rtt
                    num_of_packets_deliverd += token["num_of_packets"]
                    token["num_of_packets"] = 0
                    token["ack"] = False
                    token["time_sent"] = None
                    token["destination_id"] = 0
                    waiting_for_token = False
                    retransmission = 0
                    for i in range(num_of_packets_to_send) :
                        payload.remove(payload[0])
                    num_of_packets_to_send = 0
                    message = json.dumps(token).encode()
                else:
                    retransmission += 1
                    for i in range(token["num_of_packets"]):
                        if token["bitmap"][MAX_NOP-1-i]=='1':
                            payload.remove(payload[i])
                tht = time.time() - start_time
                
                if tht > limit or not len(payload):
                    if tht > limit:
                        print("\nToken Timeout")
                    print("Token Holding Time:", tht)
                    print("Average RTT per packet:", total_time_taken / num_of_packets_deliverd)
                    token["is_taken"] = False
                    token["source_id"] = 0
                    send_packet = False
                    ready = False
                    if len(payload):
                        send_packet = True
                    message = json.dumps(token).encode()
                    set_tl()

                if token["is_taken"] and len(payload):
                    token["destination_id"] = int(payload[0][0])
                    num_of_packets_to_send = 1
                    while len(payload) > num_of_packets_to_send :
                        if tht > limit - 0.1 * num_of_packets_to_send:
                            break
                        if payload[num_of_packets_to_send][0] == payload[0][0] :
                            num_of_packets_to_send += 1
                        else :
                            break
                        if num_of_packets_to_send == MAX_NOP:
                            break 
                    token["num_of_packets"] = num_of_packets_to_send
                    token["bitmap"] = "".join(["0" for x in range(num_of_packets_to_send)])
                    token["ack"] = False
                    waiting_for_token = True
                    token["time_sent"] = time.time()
                    message = json.dumps(token).encode()
                
            packet = message
            forward_packet = True
            input_socket.send('.'.encode())

def output(output_socket):
    global forward_packet, packet, num_of_packets_to_send, payload, retransmission
    neighbour, addr = output_socket.accept()
    while True:
        if forward_packet:
            neighbour.send(packet)
            Ack = neighbour.recv(1024)
            for i in range(num_of_packets_to_send):
                neighbour.send((payload[i][1]+f"{i}").encode())
                Ack = neighbour.recv(1024)
            forward_packet = False

def main():
    global forward_packet, packet, id, payload, send_packet, ready

    input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12345
    input_socket.connect((host, port))

    port = input_socket.recv(1024).decode()
    output_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    output_socket.bind((host, int(port)))
    output_socket.listen(1)
    input_socket.send('.'.encode())

    thread_output = threading.Thread(target=output, args=(output_socket,))
    thread_output.start()
    thread_input = threading.Thread(target=inputsocket, args=(input_socket,))
    thread_input.start()

    id = int(port) - 12345
    print("Station: Node " + str(id))
    while True:
        if not ready:
            inpl = int(input("\n**Enter the no. of packets you want to send:**\n"))
            if inpl == 0 :
                destination = 0
                for __ in range (100):
                    # while(True):
                    #     destination = random.randint(1, 5)
                    #     if destination != id:
                    #         break
                    # # destination = id + i + 1
                    # # payload.append((destination, str("sample text")))
                    destination += 1
                    if destination == id :
                        destination += 1
                    if destination > 5 :
                        destination %= 5
                        if id == 1 :
                            destination += 1
                    bisect.insort(payload, (destination, str("Sample Text")))
                payload = distribute_tuples(payload)
            if inpl == -1 :
                for __ in range (20):
                    while(True):
                        destination = random.randint(1, 5)
                        if destination != id:
                            break
                    # payload.append((destination, str("sample text"))) 
                    bisect.insort(payload, (destination, str("Sample Text"))) 
                payload = distribute_tuples(payload)           
            else :
                for i in range(inpl):
                    destination = int(input(f"Enter destination id for sending {i+1}st packet: "))
                    payl = input("Enter the message: ")
                    bisect.insort(payload, (destination, payl))            
                    # payload.append((destination, payl))
                payload = distribute_tuples(payload)
            send_packet = True
            ready = True

main()