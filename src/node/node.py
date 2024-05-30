import time
import threading
import socket
import json
import random

forward_packet = False
packet = ""
id = 0
destination = 0
payload = ""
send_packet = False
retransmission = 0

def inputsocket(input_socket):
    global forward_packet, packet, id, destination, payload, send_packet, retransmission

    while True:
        if not forward_packet :
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
            
            if token["is_taken"] and token["destination_id"] == id:
                print("\n [node" + str(token["source_id"]) + "] : " + token["payload"] + "\npress enter to send a packet")
                if(random.random() > 0.4):
                    token["ack"] = True
                message = json.dumps(token).encode()
            
            if token["is_taken"] and token["source_id"] == id:
                print()
                if token["ack"] or retransmission==2:
                    print(time.time()-token["time_sent"])
                    print(token["ack"])
                    token["is_taken"] = False
                    token["payload"] = ""
                    token["ack"] = False
                    token["time_sent"] = None
                    message = json.dumps(token).encode()
                else:
                    retransmission += 1
            
            if not token["is_taken"] and send_packet:
                token["is_taken"] = True
                token["source_id"] = id
                token["destination_id"] = int(destination)
                token["payload"] = payload
                token["ack"] = False
                send_packet = False
                token["time_sent"] = time.time()
                message = json.dumps(token).encode()
            input_socket.send('.'.encode())
            packet = message
            forward_packet = True

def output(output_socket):
    global forward_packet, packet
    neighbour, addr = output_socket.accept()
    while True:
        if forward_packet :
            neighbour.send(packet)
            ack = neighbour.recv(1024)
            forward_packet = False

def main():
    global forward_packet, packet, id, destination, payload, send_packet

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
    print()

    while True:
        if not send_packet:
            enter = input("Press enter to send a packet")
            destination = input("Enter destination id to send packet: ")
            payload = input("Enter the message: ")
            send_packet = True

main()
