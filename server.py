import socket
import threading
import sys

server_socket = None
address = "0.0.0.0"
port = 1287
close_message = "PLZCLOSENOW"

DEV_ADDED = 3
DEV_REMOVED = 4
ENTER_COMBAT = 5
EXIT_COMBAT = 6


clients = dict() # format for client is addr, id
client_sockets = dict() #addr, client
client_threads = []
current_combatants = []
message_size = 256
client_lock = threading.Lock()
multiple_combatants = False

next_id = 1

ACK = 'e'
NACK = 'f'

game_in_progress = False

### Server setup notes
# server is visible and can be connected to through any socket implementation, not just battle bots!
# This allows for future devices to be introduced without convoluded protocols.
# If the socket is already being used, this function will still work 100%
def setupServer():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((address, port))
    server_socket.listen(1)

### Test notes
# all CONNECTED clients are receiving the disconnect request!
# a disconnected client will not delay the close request and is simply discarded.
def teardownServer():
    global client_sockets
    for addr, client in client_sockets.items():
        client.sendall(close_message.encode('utf-8'))
        client.close()
    del client_sockets
    global server_socket
    server_socket.close()

### Test notes
# If client was connected before, the previous ID is sent to the device. This is correct.
# If a new client is connected, a new id is assigned and the global id counter is incremented.
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

### Test notes
# The expected client response of 0:0:0:Sword is received here!
# incorrect messages are ignored and a NACK is sent to the bot.
def getClientComponents(client, addr):
    message = client.recv(message_size)
    print("Client components %s" % str(message))
    if len(message.strip()) == 0:
        client.sendall(bytes(NACK, 'utf-8'))
    return message

### Test notes
# All clients are receiving updates for devices added and removed from
# a particular client. This allows for future game modes and decisions
# on the bot end!
# Disconnected clients are ignored and will be removed on server teardown.
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

### Test notes
# Client status is properly parsed for all options, and 
# all clients are being notified properly!
def checkClientReadyState(client, addr):
    global current_combatants
    global multiple_combatants
    clientID = clients[addr[0]]
    status = client.recv(message_size).decode('utf-8')
    code = -1
    if ':' in status:
        code = int(status[:status.index(':')])
    if code == DEV_ADDED:
        print("New device added for client with ID: %d" % clientID)
        broadcast_message(status + " " + str(clientID) + "\n")
    elif code == DEV_REMOVED:
        print("Device removed from client with ID: %d" % clientID)
        broadcast_message(status + " " + str(clientID) + "\n")
    elif code == ENTER_COMBAT:
        print("%d is entering combat!!" % clientID)
        current_combatants.append(client)
        if not multiple_combatants:
            multiple_combatants = len(current_combatants) > 1
    elif code == EXIT_COMBAT:
        current_combatants.remove(client)
        if multiple_combatants and len(current_combatants) == 1:
            winnerID = clients[addr[0]]
            broadcast_message("WINNER: %s" % str(clientID))
            multiple_combatants = False
            current_combatants.clear()
        print("%d is exiting combat!!" % clientID)
    else:
        print("Msg: {}".format(status))
        broadcast_message(status + "\n")
    return False

### Client threads generated correctly and allowing
# for reassignment of previous IDs for client reconnection!
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


### Test notes
# Server is setup appropriately without worry of previous
# server runs still being active due to the teardown method call!
# If a previous server is running, the new file will simply use the
# socket that was setup!
# Daemon threads are properly killed on server exit!
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
