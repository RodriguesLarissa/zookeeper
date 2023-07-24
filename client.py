import socket
import json
import random
import pickle
from message import Message

class Client:
    """ Creation of client class """

    def __init__(self):
        """ Global variables of client class """
        self.socket_server = socket.socket()
        self.ips_server = []
        self.ports_server = []
        self.timestamp = []

    def initialization(self):
        """ Function to collect server informations 
            Collect the ip and port of three servers
        """
        for i in range(3):
            self.ips_server.append(input(f"Digite o ip do servidor {i}: "))
            self.ports_server.append(int(input(f"Digite a porta do servidor {i}: ")))

    def connect_to_random_server(self) -> tuple[str, int]:
        """ Connect with a random server """
        # Choose server to connect
        random_index = random.choice([0, 1, 2])
        
        # Connect with server
        self.socket_server.connect((self.ips_server[random_index], self.ports_server[random_index]))
        return self.ips_server[random_index], self.ports_server[random_index]

    def send_message_to_server(self, socket_type: socket, message_to_server: dict):
        """ Send message to server using sockets """    
        socket_type.sendall(pickle.dumps(message_to_server))
        return socket_type.recv(2048).decode()

    def get(self):
        """ Get value from hash table """
        self.socket_server = socket.socket()

        # Capture the key to be search
        key = str(input(("Digite a key do valor que está procurando: ")))

        # Connect to a random server
        ip, port = self.connect_to_random_server()

        last_timestamp = self.search_item_and_timestamp(key)["timestamp"] if self.search_item_and_timestamp(key) else 0

        # Send to server the key and the last timestamp from the key saved in this client
        message_to_server = Message("GET", key, last_timestamp)
        server_message = self.send_message_to_server(self.socket_server, message_to_server)
        if (server_message != "TRY_OTHER_SERVER_OR_LATER"):
            message_to_json = json.loads(server_message)
            print(f'GET key: {key} value: {message_to_json["value"]} obtido do servidor {ip}:{port}, meu timestamp ' + 
                f'{last_timestamp} e do servidor {message_to_json["timestamp"]}')
            
            if last_timestamp == 0:
                self.add_or_update_item_timestamp(key, message_to_json["timestamp"])

        self.socket_server.close()

    def search_item_and_timestamp(self, key: str) -> dict:
        """ Search timestamp by key """
        for item in self.timestamp:
            if item["key"] == key:
                return item

    def put(self):
        """ Insert value to the hash table """
        self.socket_server = socket.socket()

        # Collect key and value
        key = str(input(("Digite a key: ")))
        value = str(input(("Digite o value: ")))
        last_timestamp = self.search_item_and_timestamp(key)["timestamp"] if self.search_item_and_timestamp(key) else 0

        # Connect to a random server
        ip, port = self.connect_to_random_server()
        message_to_server = Message("PUT", key, last_timestamp, value)

        # Receives confirmation of put with the timestamp of the server
        server_message = self.send_message_to_server(self.socket_server, message_to_server)
        if ('PUT_OK' in server_message):
            new_timestamp = server_message.split(": ")[1].strip()
            self.add_or_update_item_timestamp(key, new_timestamp)
            print(f'PUT_OK key: {key} value {value} timestamp {new_timestamp} ' +
                f'realizada no servidor {ip}:{port}')
        self.socket_server.close()

    def add_or_update_item_timestamp(self, key: str, timestamp: int):
        """ Add or update item with their timestamp """
        item = self.search_item_and_timestamp(key)

        if(item):
            item["timestamp"] = timestamp
        else:
            self.timestamp.append({"key": key, "timestamp": timestamp})

    def start(self):
        """ Function with interactive menu to start the funcionality """
        while True:
            action = int(input('''Escolha uma ação:  
                1 - INIT
                2 - GET
                3 - PUT
            '''))

            match action:
                case 1: self.initialization()
                case 2: self.get()
                case 3: self.put()

client = Client()
client.start()
