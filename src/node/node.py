import time
import threading
import socket

deliver_msg = False
msg = ""
id = 0

def input(input_socket):
    global deliver_msg, msg
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

            print(message.decode())
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
            time.sleep(1)
            deliver_msg = False

def main():
    global deliver_msg, msg, id

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

    thread_input = threading.Thread(target=input, args=(input_socket,))
    thread_input.start()

    id = int(port) - 12345

main()
