import socket

client_socket = None
address = "192.168.72.1" # This will be the server's address on the local network. It is imperative that the client is already on the hostapd network! 
default_port = 12873
id = -1
ACK = 0x0E
game_in_progress = False
message_size = 64
READY = 1
BUSY = 2
DEV_ADDED = 3
DEV_REMOVED = 4


def setupClient():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Attempting to connect to server...")
    client_socket.connect((address, default_port))
    id = int.from_bytes(client_socket.recv(message_size), byteorder='big')
    status = int.from_bytes(client_socket.recv(message_size), byteorder='big')
    if status == ACK:
        print("Got ID %d" % id)


if __name__ == "__main__":
    setupClient()
