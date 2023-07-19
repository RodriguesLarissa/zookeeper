import socket
import json
import random

class Client:
    """ Creation of client class """

    def __init__(self):
        """ Global variables of client class """
        self.socket_server = socket.socket()
        self.ip_server_1 = ""
        self.ip_server_2 = ""
        self.ip_server_3 = ""
        self.port_server_1 = 0
        self.port_server_2 = 0
        self.port_server_3 = 0
        self.timestamp = 0

    def initialization(self):
        """ Function collect server informations """
        self.ip_server_1 = input("Digite o ip do servidor 1: ")
        self.ip_server_2 = input("Digite o ip do servidor 2: ")
        self.ip_server_3 = input("Digite o ip do servidor 3: ")
        self.port_server_1 = int(input("Digite a porta do servidor 1: "))
        self.port_server_2 = int(input("Digite a porta do servidor 2: "))
        self.port_server_3 = int(input("Digite a porta do servidor 3: "))       


    def get(self):
        """ Get value from hash table """
        key = str(input(("Digite a key do valor que está procurando: ")))
        message_to_server = {"type": "GET", "key": key}
        self.send_message_to_server(self.socket_server, message_to_server)

    def send_message_to_server(self, socket_type: socket, message_to_server: dict):
        """ Send message to server using sockets """    
        socket_type.sendall(json.dumps(message_to_server).encode())
        return socket_type.recv(2048).decode()
    
    def connect_socket_send_file(self):
        """ Create connection of socket """
        self.socket_server.bind((self.ip, self.port))
        self.socket_server.listen(5)
        self.listen_connections_thread.start()

    def connect_to_server(self):
        # Choose server to connect
        index_servidor_escolhido = random.choice([0, 1, 2])
        
        # Connect with server
        self.socket_server.connect(([self.ip_server_1, self.ip_server_2, self.ip_server_3][index_servidor_escolhido]
                                    ,[self.port_server_1, self.port_server_2, self.port_server_3][index_servidor_escolhido]))

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