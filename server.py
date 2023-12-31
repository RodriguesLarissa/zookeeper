import socket
import json
import pickle
from threading import Thread
from message import Message

class Server:
    """ Creation of server class """

    def __init__(self):
        """ Global variables of server class """
        self.content = {}
        self.socket_server = socket.socket()
        self.ip = ""
        self.port = 0
        self.ip_lider = ""
        self.port_lider = 0
        self.hash_table: list[dict] = []
        self.server_ports = [10097, 10098, 10099]

    def start(self):
        """ Start server application """

        # Capture ip and port from the server and the leader
        self.ip = input("Digite o ip: ")
        self.port = int(input("Digite a porta: "))
        self.ip_lider = input("Digite o ip do lider: ")
        self.port_lider = int(input("Digite a porta do lider: "))
        self.socket_connection()

        # Thread to listen from clients
        thread = Thread(target=self.listen_clients)
        thread.start()

    def socket_connection(self):
        """ Start of the connection with socket """
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(5)

    def listen_clients(self):
        """ Start connection with thread """
        while True:
            connection, address = self.socket_server.accept()

            # Thread to process messages from clients and from others servers
            thread = Thread(target=self.process_message, args=(connection, address))
            thread.start()

    def process_message(self, socket_server: socket, address: tuple):
        """ Process message based on PUT a (key, value) in the server or GET a value based on its key """
        # Receive request from the client
        request = pickle.loads(socket_server.recv(4096))

        # Check type of request
        match request.type:
            #Performs the PUT request
            case "PUT":
                # Check if the server is the leader
                if (self.port == self.port_lider):
                    print(f'Cliente {address} PUT key:{request.key} value:{request.value}')

                    # Add or replace the information in the dict hash_table
                    new_timestamp = self.add_or_replace_hash_table(request.key, request.value)

                    # Send information to other servers
                    server_replicated = self.replicate_in_all_servers(request.key, request.value, new_timestamp)

                    # If all servers respond positively, send confirmation with new timestamp to the client
                    if(server_replicated):
                        socket_server.send(f'PUT_OK: {new_timestamp}'.encode())
                        print(f'Enviando PUT_OK ao Cliente {address} da key:{request.key} ts:{new_timestamp}')
                else:
                    print(f'Encaminhando PUT key:{request.key} value:{request.value}')

                    # Send the request to the leader
                    return_from_server = self.connect_and_send_message(self.ip_lider, self.port_lider, request)
                    socket_server.send(return_from_server)

            case "GET":
                # Search for item in the hash table
                item = self.search_by_key(request.key)

                # If item is not found, return dict with value NULL
                if(not item):
                    item = {"value": None, "timestamp": 0}

                # If item has timestamp lower from the request, that means that server is not update, return error to user
                if(item["timestamp"] < int(request.timestamp)):
                    socket_server.send("TRY_OTHER_SERVER_OR_LATER".encode())

                else:
                    # Return value and timestamp to the client
                    valor_and_timestamp = {"value": item["value"], "timestamp": item["timestamp"]}
                    socket_server.send(json.dumps(valor_and_timestamp).encode())
                
                print(f'Cliente {address} GET key:{request.key} ts:{request.timestamp}. Meu ts é {item["timestamp"]},' +
                        f'portanto devolvendo {item if item else "TRY_OTHER_SERVER_OR_LATER"}')

            case "REPLICATION":
                # Save new hash table locally
                self.hash_table = request.hash_table

                # Confirm the replication to the leader
                socket_server.send("REPLICATION_OK".encode())
                print(f'REPLICATION key:{request.key} value:{request.value} ts:{request.timestamp}')

        socket_server.close()

    def search_by_key(self, key: int) -> dict:
        """ Search item on hash table by key """
        for item in self.hash_table:
            if item["key"] == key:
                return item


    def add_or_replace_hash_table(self, key: int, value: int):
        """ TODO """
        # Verify if key already exists on the list
        item_found = self.search_by_key(key)

        if(item_found):
            # Replace the object
            item_found["timestamp"] += 1
            item_found["value"] = value
            return item_found["timestamp"]

        # Create new object and add to the list
        new_hash_table = {"key": key, "timestamp": 0, "value": value}
        self.hash_table.append(new_hash_table)
        return 0

    def replicate_in_all_servers(self, key, value, timestamp) -> bool:
        """ Send replication to other server """
        message_to_server = Message("REPLICATION", key, timestamp, value, self.hash_table)

        # Send message to all servers, except the leader
        for i in range(3):
            if (self.server_ports[i] != self.port):
                response = self.connect_and_send_message('', self.server_ports[i], message_to_server)
                if response != b'REPLICATION_OK':
                    return False
        return True
    
    def connect_and_send_message(self, ip: str, port: int, message: str):
        """ Connect and send message """
        socket_request_replication = socket.socket()
        socket_request_replication.connect((ip, port))
        socket_request_replication.sendall(pickle.dumps(message))
        return socket_request_replication.recv(2048)

server = Server()
server.start()
