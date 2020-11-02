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
        beginConnLoop()
    elif status == NACK:
        print("Failed to get id!")
    else:
        print("UNKNOWN STATUS: {}".format(status))

def readDevUpdates():
    info = sys.stdin.readline()
    print(info + " received!")
    status = int(info[:info.index(':')])
    if status == DEV_ADDED:
        print("Device was added! Send the info next!")
    elif status == DEV_REMOVED:
        print("Device was removed!")

def beginConnLoop():
    end_flag = False
    bot_updated_thread = threading.Thread(target=readDevUpdates)
    bot_updated_thread.start()
    while True:
        if end_flag:
            break

if __name__ == "__main__":
    setupClient()
