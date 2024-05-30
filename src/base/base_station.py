import time
import threading
import socket
import json

deliver_msg = False
msg = ""
has_ring = False
new_node = False
i=1

def input(input_socket):
    global deliver_msg, msg
    while True:
        if not deliver_msg :
            message = input_socket.recv(1024)
            token = json.loads(message.decode())
            # if token["is_taken"]:
            #     print(token)
            input_socket.send('.'.encode())
            msg = message
            deliver_msg = True

def deliver(neighbour):
    global deliver_msg, msg, new_node, i
    while True:
        if deliver_msg :
            neighbour.send(msg)
            ack = neighbour.recv(1024)
            deliver_msg = False
        if new_node:
            neighbour.send('cis'.encode())
            ack = neighbour.recv(1024)
            port = 12345 + i - 1
            port = str(port)
            neighbour.send(port.encode())
            ack = neighbour.recv(1024)
            neighbour.close()
            new_node=False
            break

def output(output_socket):
    global deliver_msg, msg, i, new_node, has_ring
    while True:
        neighbour, addr = output_socket.accept()
        port = 12345 + i
        i = i + 1
        port = str(port)
        neighbour.send(port.encode())
        ack = neighbour.recv(1024)

        if not has_ring:
            input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = 'localhost'
            input_socket.connect((host, int(port)))
            thread_input = threading.Thread(target=input, args=(input_socket,))
            thread_input.start()
            token={
                "is_taken" : False,
                "source_id" : 0,
                "distination_id" : 0,
                "payload" : "",
                "ack" : False,
                "time_sent" : None
            }
            token_string = json.dumps(token)
            neighbour.send(token_string.encode())
            ack = neighbour.recv(1024)
            has_ring = True
        else:
            new_node = True
            thread_deliver.join()

        thread_deliver = threading.Thread(target=deliver, args=(neighbour,))
        thread_deliver.start()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    thread_output = threading.Thread(target=output, args=(server_socket,))
    thread_output.start()

main()
