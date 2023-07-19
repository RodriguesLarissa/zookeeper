import socket
import json
from threading import Thread

class HashTable:
    """ Creation of Hash Table class """

    def __init__(self, key, timestamp, value):
        self.key = key
        self.timestamp = timestamp
        self.value = value

class Server:
    """ Creation of server class """

    def __init__(self):
        """ Global variables of server class """
        self.content = {}
        self.socket_server = socket.socket()
        self.socket_request_replication = socket.socket()
        self.socket_replication = socket.socket()
        self.ip = ""
        self.port = 0
        self.ip_lider = ""
        self.port_lider = 0
        self.hash_table: list[HashTable] = []

        #Creation of thread connection that listens to other servers
        self.listen_servers = Thread(target=self.listen_servers)

    def start(self):
        """ Start server application """
        self.ip = input("Digite o ip: ")
        self.port = int(input("Digite a porta: "))
        self.ip_lider = input("Digite o ip do lider: ")
        self.port_lider = int(input("Digite a porta do lider: "))
        self.socket_connection()
        self.thread()

    def socket_connection(self):
        """ Start of the connection with socket """
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(5)

    def thread(self):
        """ Start connection with thread """
        while True:
            connection, addr = self.socket_server.accept()
            thread = Thread(target=self.process_message, args=(connection))
            thread.start()

    def process_message(self, socket_server: socket):
        """ Process message based on PUT a (key, value) in the server or GET a value based on its key """
        while True:
            # Receive request from the client
            request = json.loads(socket_server.recv(4096).decode())

            # Check type of request
            match request["type"]:
                #Performs the PUT request
                case "PUT":
                    if (self.ip == self.ip_lider):
                        self.add_or_replace_hash_table(request["key"], request["timestamp"], request["value"])
                        self.replicate_in_all_servers()
                        socket_server.send("PUT_OK".encode())


    def add_or_replace_hash_table(self, key: int, timestamp: int, value: int):
        """ TODO """
        # Verify if key already exists on the list
        for item in self.hash_table:
            if item.key == key:
                # Replace the object
                item.timestamp = timestamp
                item.value = value
                return

        # Create new object and add to the list
        new_hash_table = HashTable(key, timestamp, value)
        self.hash_table.append(new_hash_table)

    def replicate_in_all_servers(self):
        """ Send replication to other server """
        message_to_server = {"type": "REPLICATION", "hash_table": self.hash_table}
        self.socket_request_replication.sendall(json.dumps(message_to_server).encode())

    def listen_server(self):
        """ Listen for connections from other servers """
        while True:
            connection, _ = self.socket_replication.accept()
            request = json.loads(connection.recv(2048).decode())

            if request["type"] ==  "REPLICATION":
                self.hash_table = request["hash_table"]

            connection.close()

server = Server()
server.start()