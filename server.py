import socket
import threading

server_socket = None
address = "0.0.0.0"
port = 1287

clients = dict() # format for client is addr, id
client_sockets = dict() #socket, id
message_size = 256

next_id = 1

ACK = 'e'
NACK = 'f'

game_in_progress = False

def setupServer():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((address, port))
    server_socket.listen(1)

def sendIDToClient(client : socket, addr : int):
    idLock.acquire()
    global clients
    cli_id = clients.get(addr[0], None)
    if cli_id is None:
        print("New client detected. Adding to log.")
        global next_id
        client.sendall(bytes([next_id]))
        clients[addr[0]] = next_id
        next_id += 1
    else:
        client.sendall(bytes([cli_id]))
    client.sendall(bytes(ACK, 'utf-8'))
    idLock.release()

def getClientComponents(client, addr):
    message = client.recv(message_size)
    print("Client components %s" % str(message))
    if len(message.strip()) == 0:
        client.sendall(bytes(NACK, 'utf-8'))

def broadcast_message(msg):
    for k, v in client_sockets.items():
        v.sendall(bytes(msg, 'utf-8'))

def checkClientReadyState(client, addr):
    status = str(client.recv(message_size))
    if status.lower() == "ready":
        return True
    else:
        print("Msg: {}".format(status))
        broadcast_message(status)
    return False

def handleClientInfo(client : socket, addr : int):
    print("I am a thread handling client with address %s" % str(addr))
    # We need to let the client know we established a connection.
    sendIDToClient(client, addr)
    global client_sockets
    client_sockets[clients[addr[0]]] = client
    #client.sendall(bytes(ACK, 'utf-8'))
    components = getClientComponents(client, addr)
    global game_in_progress
    while not game_in_progress:
        checkClientReadyState(client, addr)



if __name__ == "__main__":
    # setup socket needed
    print("Battle Bots server started!")
    setupServer()
    # setup lock for client ids
    idLock = threading.Lock()
    while True:
        if not game_in_progress:
            print("Waiting for client")
            client, addr = server_socket.accept()
            if addr not in clients:
                print("Found client!")
                threading.Thread(target=handleClientInfo, args=(client, addr)).start()