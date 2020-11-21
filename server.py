import socket
import threading
import sys

server_socket = None
address = "0.0.0.0"
port = 1287
close_message = "PLZCLOSENOW"

DEV_ADDED = 3
DEV_REMOVED = 4

clients = dict() # format for client is addr, id
client_sockets = dict() #addr, client
client_threads = []
message_size = 256
client_lock = threading.Lock()

next_id = 1

ACK = 'e'
NACK = 'f'

game_in_progress = False

def setupServer():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((address, port))
    server_socket.listen(1)

def teardownServer():
    global client_sockets
    for addr, client in client_sockets.items():
        client.sendall(close_message.encode('utf-8'))
        client.close()
    del client_sockets
    global server_socket
    server_socket.close()

def sendIDToClient(client : socket, addr):
    idLock.acquire()
    global clients
    cli_id = clients.get(addr[0], None)
    if cli_id is not None:
        print("Client %d reconnected!" % cli_id)
        client.sendall(bytes([cli_id]))
    else:
        print("New client detected. Adding to log.")
        global next_id
        client.sendall(bytes([next_id]))
        clients[addr[0]] = next_id
        next_id = next_id + 1
    client.sendall(bytes(ACK, 'utf-8'))
    idLock.release()

def getClientComponents(client, addr):
    message = client.recv(message_size)
    print("Client components %s" % str(message))
    if len(message.strip()) == 0:
        client.sendall(bytes(NACK, 'utf-8'))
    return message

def broadcast_message(msg):
    client_lock.acquire()
    for k, cli in client_sockets.items():
        try:
            cli.sendall(bytes(msg, 'utf-8'))
        except socket.error:
            pass
        except socket.timeout:
            pass
    client_lock.release()

def checkClientReadyState(client, addr):
    clientID = clients[addr[0]]
    status = client.recv(message_size).decode('utf-8')
    if status.lower() == "ready":
        return True
    code = "-1"
    if ':' in status:
        code = int(status[:status.index(':')])
    if code == DEV_ADDED:
        print("New device added for client with ID: %d" % clientID)
        broadcast_message(status + " " + str(clientID))
    elif code == DEV_REMOVED:
        print("Device removed from client with ID: %d" % clientID)
        broadcast_message(status + " " + str(clientID))
    else:
        print("Msg: {}".format(status))
        broadcast_message(status)
    return False

def handleClientInfo(client : socket, addr : int):
    print("I am a thread handling client with address %s" % str(addr))
    # We need to let the client know we established a connection.
    client.settimeout(100)
    sendIDToClient(client, addr)
    client_lock.acquire()
    global client_sockets
    client_sockets[clients[addr[0]]] = client
    client_lock.release()
    components = getClientComponents(client, addr)
    global game_in_progress
    while not game_in_progress:
        checkClientReadyState(client, addr)



if __name__ == "__main__":
    try: # setup socket needed
        print("Battle Bots server started!")
        setupServer()
        # setup lock for client ids
        idLock = threading.Lock()
        while True:
            if not game_in_progress:
                print("Waiting for client")
                client, addr = server_socket.accept()
                print("Found client!")
                thd = threading.Thread(target=handleClientInfo, args=(client, addr))
                thd.daemon = True
                thd.start()
    except KeyboardInterrupt:
        teardownServer()
        sys.exit(0)
