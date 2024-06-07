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
limit = 4
sent = 0
start = 0
tl = 0
nop = 0
should_continue = True
active_state = True 


def set_tl():
    global tl
    tl = 1
    threading.Timer(10, reset_tl).start()
    
def reset_tl():
    global tl
    tl = 0

def inputsocket(input_socket):
    global forward_packet, packet, id, payload, send_packet, retransmission, start_time, limit, sent, start, tl, nop, active_state

    input_socket.settimeout(1)  
    while active_state:
        if not forward_packet:
            try:
                message = input_socket.recv(1024)
                if not message:
                    break
                if not active_state:
                    input_socket.send('.'.encode())
                    packet = message
                    forward_packet = True  
                    continue
                if active_state:
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
                        if x > 0.3:
                            print("\n[Message received] <node" + str(token["source_id"]) + "> : " + token["payload"])
                            token["ack"] = True
                        message = json.dumps(token).encode()

                    if token["is_taken"] and token["source_id"] == id and sent == 1:
                        if token["ack"] or retransmission == 2:
                            print("\nRTT:", time.time() - token["time_sent"])
                            token["payload"] = ""
                            token["ack"] = False
                            token["time_sent"] = None
                            token["destination_id"] = -1
                            token["source_id"] = -1
                            payload.remove(payload[0])
                            sent = 0
                            retransmission = 0
                            message = json.dumps(token).encode()
                        else:
                            retransmission += 1
                        tht = time.time() - start_time

                        if tht > limit or not len(payload):
                            if tht > limit:
                                print("\nToken Timeout")
                            start = 0
                            print("Token Holding Time:", tht)
                            print()
                            token["is_taken"] = False
                            send_packet = False
                            set_tl()

                    if not token["is_taken"] and send_packet and tl == 0:
                        token["is_taken"] = True
                        print("\nHolding Token\n")

                    if token["is_taken"] and len(payload) and sent == 0:
                        if start == 0:
                            while len(payload) != nop:
                                pass
                            start_time = time.time()
                            start = 1
                        token["is_taken"] = True
                        token["source_id"] = id
                        token["destination_id"] = int(payload[0][0])
                        token["payload"] = payload[0][1]
                        token["ack"] = False
                        sent = 1
                        token["time_sent"] = time.time()
                        message = json.dumps(token).encode()

                    input_socket.send('.'.encode())
                    packet = message
                    forward_packet = True

            except socket.timeout:
                continue  
            except socket.error as e:
                print(f"Socket error: {e}")
                break

def output(output_socket):
    global forward_packet, packet
    neighbour, addr = output_socket.accept()
    while True:
        if forward_packet:
            neighbour.send(packet)
            Ack = neighbour.recv(1024)
            forward_packet = False

def main():
    global forward_packet, packet, id, payload, send_packet,nop, active_state

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
        decision = input("\nDo you want to continue or exit? (continue/exit): ").strip().lower()
        if decision.lower() == "exit":
            active_state=False
            time.sleep(1)
            # input_socket.close()  
            # output_socket.close()  
            print("Connection closed. Exiting the program.")
            
            if thread_input.is_alive():
                thread_input.join()
            break  
        
        else:
            nop = int(input("\n**Enter the number of packets you want to send:**\n"))
            for i in range(nop):
                destination = int(input(f"Enter destination id for sending {i+1}st packet: "))
                payl = input("Enter the message: ")
                payload.append((destination, payl))
            send_packet = True

main()


