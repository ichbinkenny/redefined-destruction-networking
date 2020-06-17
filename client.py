import socket

client_socket = None
address = "127.0.0.1"
default_port = 12873
id = -1
ACK = 0x0E
game_in_progress = False
message_size = 64

def setupClient():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Attempting to connect to server...")
    client_socket.connect(("192.168.1.130", default_port))
    id = int.from_bytes(client_socket.recv(message_size), byteorder='big')
    print("Got ID %d" % id)

setupClient()