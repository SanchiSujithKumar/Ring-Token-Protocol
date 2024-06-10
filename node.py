import time
import threading
import socket
import json
import random

id = 0
forward_packet = False
packet = ""
payload = []
send_packet = False
limit = 3
tl = 0
num_of_packets_to_send = 0
avg_rtt = 0

def set_tl():
    global tl
    tl = 1
    threading.Timer(10, reset_tl).start()
    
def reset_tl():
    global tl
    tl = 0

def inputsocket(input_socket):
    global forward_packet, packet, id, payload, send_packet, limit, tl, num_of_packets_to_send, avg_rtt

    token = {}
    msg_to_be_received = 0
    start_time = 0
    retransmission = 0

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
                if msg_to_be_received > 0 :
                    print("\n[Message received] <node" + str(token["source_id"]) + "> : " + received_packet)
                    msg_to_be_received -= 1
                    if msg_to_be_received == 0 :
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
                x=0.4
                if x > 0.3:
                    msg_to_be_received = token["num_of_packets"]
                    token["ack"] = True
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
                    avg_rtt += time.time() - token["time_sent"]
                    print("\nRTT:", time.time() - token["time_sent"])
                    token["num_of_packets"] = 0
                    token["ack"] = False
                    token["time_sent"] = None
                    token["destination_id"] = 0
                    retransmission = 0
                    for i in range(num_of_packets_to_send) :
                        payload.remove(payload[0])
                    num_of_packets_to_send = 0
                    message = json.dumps(token).encode()
                else:
                    retransmission += 1
                tht = time.time() - start_time
                
                if tht > limit or not len(payload):
                    if tht > limit:
                        print("\nToken Timeout")
                    print("Token Holding Time:", tht)
                    if not len(payload):
                        print("Average RTT for a packet:", avg_rtt/30)
                    print()
                    token["is_taken"] = False
                    token["source_id"] = 0
                    send_packet = False
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
                        if num_of_packets_to_send == 7:
                            break 
                    token["num_of_packets"] = num_of_packets_to_send
                    token["ack"] = False
                    retransmission = 0
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
                neighbour.send((payload[i][1]).encode())
                Ack = neighbour.recv(1024)
            forward_packet = False

def main():
    global forward_packet, packet, id, payload, send_packet

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
        if not send_packet:
            inpl = int(input("\n**Enter the no. of packets you want to send:**\n"))
            if inpl == 0 :
                for __ in range (10):
                    while(True):
                        destination = random.randint(1, 5)
                        if destination != id:
                            break
                    for _ in range(3):
                        # destination = id + i + 1
                        payload.append((destination, str("sample text")))
            if inpl == -1 :
                for __ in range (20):
                    while(True):
                        destination = random.randint(1, 5)
                        if destination != id:
                            break
                    payload.append((destination, str("sample text")))             
            else :
                for i in range(inpl):
                    destination = int(input(f"Enter destination id for sending {i+1}st packet: "))
                    payl = input("Enter the message: ")
                    payload.append((destination, payl))
            send_packet = True

main()