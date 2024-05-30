import time
import threading
import socket
import json

deliver_msg = False
msg = ""
id = 0
desitnation = 0
payload = ""
send_packet = False

def inputsocket(input_socket):
    global deliver_msg, msg, id, desitnation, payload, send_packet

    while True:
        if not deliver_msg :
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
            if token["is_taken"] and token["distination_id"] == id:
                print("\n [node" + str(token["source_id"]) + "] : " + token["payload"] + "\npress enter to send a packet")
                token["ack"] = True
                message = json.dumps(token).encode()
            if token["is_taken"] and token["source_id"] == id:
                print()
                print(time.time()-token["time_sent"])
                print(token["ack"])
                token["is_taken"] = False
                token["payload"] = ""
                token["ack"] = False
                token["time_sent"] = None
                message = json.dumps(token).encode()
            if not token["is_taken"] and send_packet:
                token["is_taken"] = True
                token["source_id"] = id
                token["distination_id"] = int(desitnation)
                token["payload"] = payload
                token["ack"] = False
                send_packet = False
                token["time_sent"] = time.time()
                message = json.dumps(token).encode()
            input_socket.send('.'.encode())
            msg = message
            deliver_msg = True

def output(output_socket):
    global deliver_msg, msg
    neighbour, addr = output_socket.accept()
    while True:
        if deliver_msg :
            neighbour.send(msg)
            ack = neighbour.recv(1024)
            deliver_msg = False

def ui():
    global desitnation, payload, send_packet
    

def main():
    global deliver_msg, msg, id, desitnation, payload, send_packet

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
    print("you are node" + str(id))
    print()

    while True:
        if not send_packet:
            enter = input("press enter to send a packet")
            desitnation = input("enter desitnation id to send packet: ")
            payload = input("enter data: ")
            send_packet = True

main()
