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
retransmission = 0
start_time = 0
limit = 3
tl = 0

def set_tl():
    global tl
    tl = 1
    threading.Timer(10, reset_tl).start()
    
def reset_tl():
    global tl
    tl = 0

def inputsocket(input_socket):
    global forward_packet, packet, id, payload, send_packet, retransmission, start_time, limit, tl
    num_of_packets_deliverd = 0
    total_time_taken = 0.0
    while True:
        if not forward_packet:
            message = input_socket.recv(1024)
            
            if message == b'cis':
                input_socket.send('.'.encode())
                host = 'localhost'
                port = input_socket.recv(1024).decode()
                input_socket.send('.'.encode())
                input_socket.close()
                input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                input_socket.connect((host, int(port)))
                continue
            token = json.loads(message.decode())
            
            if token["destination_id"] == id and token["source_id"] != 0:
                x = random.random()
                x = 0.4
                if x > 0.3:
                    print("\n[Message received] <node" + str(token["source_id"]) + "> : " + token["payload"])
                    token["ack"] = True
                message = json.dumps(token).encode()
            
            if not token["is_taken"] and send_packet and tl==0:
                token["source_id"] = id
                token["is_taken"] = True
                print("\nHolding Token\n")
                start_time = time.time()
            
            if token["is_taken"] and token["source_id"] == id:
                if token["ack"] or retransmission == 2:
                    rtt = time.time() - token["time_sent"]
                    print("\nRTT:", rtt)
                    total_time_taken += rtt
                    token["payload"] = ""
                    token["ack"] = False
                    token["time_sent"] = None
                    token["destination_id"] = 0
                    payload.remove(payload[0])
                    num_of_packets_deliverd += 1
                    message = json.dumps(token).encode()
                else:
                    retransmission += 1
                tht = time.time() - start_time
                
                if tht > limit or not len(payload):
                    if tht > limit:
                        print("\nToken Timeout")
                    print("Token Holding Time:", tht)
                    print("avg time to deliver per packet:", total_time_taken / num_of_packets_deliverd)
                    print()
                    token["is_taken"] = False
                    send_packet = False
                    if len(payload):
                        send_packet = True
                    message = json.dumps(token).encode()
                    set_tl()      

                if token["is_taken"] and len(payload):
                    token["destination_id"] = int(payload[0][0])  # Ensure correct type
                    token["payload"] = payload[0][1]
                    token["ack"] = False
                    retransmission = 0
                    token["time_sent"] = time.time()
                    message = json.dumps(token).encode()
                
            input_socket.send('.'.encode())
            packet = message
            forward_packet = True

def output(output_socket):
    global forward_packet, packet
    neighbour, addr = output_socket.accept()
    while True:
        if forward_packet:
            neighbour.send(packet)
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
            if inpl == 0:
                destination = 0
                for __ in range (100):
                    destination += 1
                    if destination == id :
                        destination += 1
                    if destination > 5 :
                        destination %= 5
                        if id == 1 :
                            destination += 1
                    payload.append((destination, str("sample text")))
            else: 
                for i in range(inpl):
                    destination = int(input(f"Enter destination id for sending {i+1}st packet: "))
                    payl = input("Enter the message: ")
                    payload.append((destination, payl))
            send_packet = True

main()