import socket
import threading
import sys

client_socket = None
address = "asimplenerd.com"#"192.168.72.1" # This will be the server's address on the local network. It is imperative that the client is already on the hostapd network! 
default_port = 1287
id = -1
end_flag = True
ACK = 'e'
NACK = 'f'
game_in_progress = False
message_size = 256
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
    status = client_socket.recv(message_size).decode('utf-8')
    if status == ACK:
        print("Got ID %d" % id)
        beginConnLoop()
    elif status == NACK:
        print("Failed to get id!")
    else:
        print("UNKNOWN STATUS: {}".format(str(status)))

def readDevUpdates():
    info = sys.stdin.readline()
    # print(info + " received!")
    # status = int(info[:info.index(':')])
    # if status == DEV_ADDED:
    #     print("Device was added! Send the info next!")
    # elif status == DEV_REMOVED:
    #     print("Device was removed!")

def beginConnLoop():
    end_flag = False
    bot_updated_thread = threading.Thread(target=readDevUpdates)
    bot_updated_thread.start()
    components = "0:0:0:Sword" # No armor and sword weapon
    client_socket.sendall(bytes(components, 'utf-8'))
    client_socket.sendall(bytes("I am ready to rumble.", 'utf-8'))
    while True:
        msg = client_socket.recv(message_size).decode('utf-8')
        print('Msg: %s' % msg)
        ## the next 2 lines are for testing
        msg = input()
        client_socket.sendall(bytes(msg, 'utf-8'))
        if end_flag:
            break

if __name__ == "__main__":
    setupClient()
