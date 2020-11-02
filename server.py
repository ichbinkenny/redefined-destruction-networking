import socket
import threading

server_socket = None
address = "0.0.0.0"
port = 12873

clients = dict() # format for client is addr, id

message_size = 64

next_id = 1

ACK = 0x0E
NACK = ACK ^ 0xFF

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
    client.sendall(bytes([ACK]))
    idLock.release()

def getClientComponents(client, addr):
    message = client.recv(message_size)
    print("Client components %s" % str(message))
    if len(message.strip()) == 0:
        client.sendall(bytes(NACK))
    return message.split(' ')

def checkClientReadyState(client, addr):
    status = client.recv(message_size)
    return str(status).lower() == "ready"

def handleClientInfo(client : socket, addr : int):
    print("I am a thread handling client with address %s" % str(addr))
    # We need to let the client know we established a connection.
    client.sendall(bytes(ACK))
    sendIDToClient(client, addr)
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
            print("Found client!")
            threading.Thread(target=handleClientInfo, args=(client, addr)).start()

