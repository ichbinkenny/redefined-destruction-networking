import socket
import threading
import sys
import select

client_socket = None
address = "asimplenerd.com"#"192.168.72.1" # This will be the server's address on the local network. It is imperative that the client is already on the hostapd network! 
default_port = 1287
id = -1
end_flag = True
close_message = "PLZCLOSENOW"
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
        # Send id back to bluetooth device
        sys.stdout.write("id: %d\n" % id)
        sys.stdout.flush()
        beginConnLoop()
    elif status == NACK:
        print("Failed to get id!")
    else:
        print("UNKNOWN STATUS: {}".format(str(status)))

def readDevUpdates():
    global end_flag
    while not end_flag:
        info = sys.stdin.readline().strip()
        status = "NONE"
        if ':' in info:
            status = int(info[:info.index(':')])
        if status == DEV_ADDED:
            client_socket.sendall(bytes(info, 'utf-8'))
        elif status == DEV_REMOVED:
            client_socket.sendall(bytes(info, 'utf-8'))
        else:
            client_socket.sendall(bytes(info, 'utf-8'))

def beginConnLoop():
    global end_flag
    end_flag = False
    bot_updated_thread = threading.Thread(target=readDevUpdates)
    bot_updated_thread.setDaemon(True)
    bot_updated_thread.start()
    components = "0:0:0:Sword" # No armor and sword weapon
    client_socket.sendall(bytes(components, 'utf-8'))
    while not end_flag:
        read_list, write_list, err = select.select([client_socket], [], [])
        for sock in read_list:
            msg = sock.recv(message_size).decode('utf-8')
            end_flag = msg == close_message
            if end_flag:
                sys.stdout.write("SOCKCLOSED")
                client_socket.close()
                break
            else:
                sys.stdout.write(msg + "\n") # TODO handle message and send back info over bluetooth
            sys.stdout.flush()

if __name__ == "__main__":
    setupClient()
