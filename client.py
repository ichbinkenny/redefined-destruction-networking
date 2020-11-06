import socket
import threading
import sys

client_socket = None
address = "192.168.72.1" # This will be the server's address on the local network. It is imperative that the client is already on the hostapd network! 
default_port = 12873
id = -1
end_flag = True
ACK = 0x0E
NACK = ACK ^ 0xFF
game_in_progress = False
message_size = 1024
READY = 1
BUSY = 2
DEV_ADDED = 3
DEV_REMOVED = 4
GAME_START = 54


def setupClient():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Attempting to connect to server...")
    client_socket.connect((address, default_port))
    id = int.from_bytes(client_socket.recv(message_size), byteorder='big')
    status = int.from_bytes(client_socket.recv(message_size), byteorder='big')
    if status == ACK:
        print("Got ID %d" % id)
        beginConnLoop()
    elif status == NACK:
        print("Failed to get id!")
    else:
        print("UNKNOWN STATUS: {}".format(status))

def sendDevUpdates():
    while True:
        info = sys.stdin.readline().strip()
        print(info + " received!")
        status = int(info[:info.index(':')])
        if status == DEV_ADDED:
            client_socket.sendall(b"hello, world!")
        elif status == DEV_REMOVED:
            print("Device was removed!")

def receiveServerUpdates():
    while True:
        update = client_socket.recv(message_size)
        print("Update")

def beginConnLoop():
    end_flag = False
    bot_updated_thread = threading.Thread(target=sendDevUpdates)
    bot_updated_thread.start()
    server_updated_thread = threading.Thread(target=receiveServerUpdates)
    server_updated_thread.start()

if __name__ == "__main__":
    setupClient()
