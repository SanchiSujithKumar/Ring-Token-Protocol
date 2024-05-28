import time
import threading
import socket
# node 1

deliver_msg = False
msg = ""

def output(output_socket):
    global deliver_msg, msg
    neighbour, addr = output_socket.accept()
    while True:
        if deliver_msg :
            neighbour.send(msg)
            message = neighbour.recv(1024)
            deliver_msg = False

def main():
    output_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12341
    output_socket.bind((host, port))
    output_socket.listen(1)
    thread = threading.Thread(target=output, args=(output_socket,))
    thread.start()
    input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12345
    time.sleep(5)
    input_socket.connect((host, port))
    global deliver_msg, msg
    while True:
        message = input_socket.recv(1024)
        print(message.decode())
        input_socket.send('.'.encode())
        msg = message
        deliver_msg = True
    input_socket.close()

main()
