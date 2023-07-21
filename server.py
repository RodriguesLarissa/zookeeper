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
        self.server_ports = [10097, 10098, 10099]

        #Creation of thread connection that listens to other servers
        self.listen_servers = Thread(target=self.listen_servers)

    def start(self):
        """ Start server application """
        self.ip = input("Digite o ip: ")
        self.port = int(input("Digite a porta: "))
        self.ip_lider = input("Digite o ip do lider: ")
        self.port_lider = int(input("Digite a porta do lider: "))
        self.socket_connection()
        for i in range(3):
            self.connect_replication_socket('', self.server_ports[i])
        self.thread()

    def socket_connection(self):
        """ Start of the connection with socket """
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(5)

    def thread(self):
        """ Start connection with thread """
        while True:
            connection, address = self.socket_server.accept()
            thread = Thread(target=self.process_message, args=(connection, address))
            thread.start()

    def process_message(self, socket_server: socket, address: tuple):
        """ Process message based on PUT a (key, value) in the server or GET a value based on its key """
        while True:
            # Receive request from the client
            request = json.loads(socket_server.recv(4096).decode())

            # Check type of request
            match request["type"]:
                #Performs the PUT request
                case "PUT":
                    if (self.ip == self.ip_lider):
                        print(f'Cliente {address} PUT key:{request["key"]} value:{request["value"]}')
                        new_timestamp = self.add_or_replace_hash_table(request["key"], request["value"])
                        server_replicated = self.replicate_in_all_servers(request["key"], request["value"], new_timestamp)
                        if(server_replicated):
                            socket_server.send(f'PUT_OK: {new_timestamp}'.encode())
                            print(f'Enviando PUT_OK ao Cliente {address} da key:{request["key"]} ts:{new_timestamp}')
                    else:
                        print(f'Encaminhando PUT key:{request["key"]} value:{request["value"]}')
                        self.connect_and_send_message(self.ip_lider, self.port_lider, request)

                case "GET":
                    item = self.search_by_key(request["key"])

                    if(item.timestamp < request["timestamp"]):
                        socket_server.send("TRY_OTHER_SERVER_OR_LATER".encode())
                    else:
                        valor_and_timestamp = {"value": item.value, "timestamp": item.timestamp}
                        socket_server.send(json.dumps(valor_and_timestamp).encode())
                    
                    print(f'Cliente {address} GET key:{request["key"]} ts:{request["timestamp"]}. Meu ts é {item.timestamp},' +
                          f'portanto devolvendo {item if item else "TRY_OTHER_SERVER_OR_LATER"}')

    def search_by_key(self, key: int):
        """ Search item on hash table by key """
        for item in self.hash_table:
            if item.key == key:
                return item
            
        return


    def add_or_replace_hash_table(self, key: int, value: int):
        """ TODO """
        # Verify if key already exists on the list
        item_found = self.search_by_key(key)

        if(item_found):
            # Replace the object
            item_found.timestamp += 1
            item_found.value = value
            return item_found.timestamp

        # Create new object and add to the list
        new_hash_table = HashTable(key, 0, value)
        self.hash_table.append(new_hash_table)
        return 0

    def replicate_in_all_servers(self, key, value, timestamp) -> bool:
        """ Send replication to other server """
        message_to_server = {"type": "REPLICATION", "hash_table": self.hash_table, "key": key, "value": value, "timestamp": timestamp}
        for i in range(3):
            response = self.connect_and_send_message('', self.server_ports[i], message_to_server)
            if response != 'REPLICATION_OK':
                return False
        return True
    
    def connect_and_send_message(self, ip: str, port: int, message: str):
        """ Connect and send message """
        self.socket_request_replication.connect((ip, port))
        self.socket_request_replication.sendall(json.dumps(message).encode())
        return self.socket_request_replication.recv(2048)

    def listen_server(self):
        """ Listen for connections from other servers """
        while True:
            connection, _ = self.socket_replication.accept()
            request = json.loads(connection.recv(2048).decode())

            if request["type"] ==  "REPLICATION":
                self.hash_table = request["hash_table"]
                connection.send("REPLICATION_OK".encode())
                print(f'REPLICATION key:{request["key"]} value:{request["value"]} ts:{request["timestamp"]}')

            connection.close()

    def connect_replication_socket(self, ip: str, port: int) -> str:
        """ Connect to listen replication requests """
        self.socket_replication.bind((ip, port))
        self.socket_replication.listen(5)
        self.listen_servers.start()

server = Server()
server.start()