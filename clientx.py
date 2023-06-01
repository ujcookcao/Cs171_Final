
import socket
import sys
import threading
import time
import json
from BlockChainheader import BlockChain


from time import sleep
from os import _exit
from sys import stdout



class Server:
    def __init__(self, host='localhost', port=9000):
        self.blockchain = BlockChain()
        self.host = host
        self.port = port
        # linstening socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR allowing it to bind to the same address \
        #   even if it's still in use by a previous connection.
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.connections = {}
        self.peers =['P1', 'P2', 'P3', 'P4', 'P5']
        self.ports = {peer: 9000 + i for i, peer in enumerate(self.peers)}
        self.name = [peer for peer, port in self.ports.items() if port == self.port][0]
    
    def print_ports_dict(self):
        print(f'{self.ports}')
    def start(self):
        self.server.listen()
        print(f"{self.name}: Server started on port {self.port}")
        self.accept_connections_thread = threading.Thread(target=self.accept_connections).start()

        self.command_thread = threading.Thread(target=self.read_commands).start()

    def accept_connections(self):
        while True:
            client, _ = self.server.accept() # address no needed so: _
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        client_name = client.recv(1024).decode('utf-8')
        if not client_name:
            return
        self.connections[client_name] = client
        print(f"{self.name}: Connection established with {client_name}")

        threading.Thread(target=self.receive_messages, args=(client,)).start()

    def read_commands(self):
        #create a dictionary to store the message in json format to send to other peers
        json_message = {}
        while True:
            message = input().strip().split() # split the input into a list of words
            print("message: ", message)
            #if len(message) == 0:, close all existing connections and exit
            if len(message) == 0:
                for peer, connection in self.connections.items():
                    connection.close()
                self.server.close()
                _exit(0)
            elif message[0].lower() == "b" or message[0].lower() == "bc":
                self.blockchain.print()
            elif message[0].lower() == "p" or message[0].lower() == "post":
                if len(message) < 4:
                    print("Invalid post. Please provide an operation, username, title, and content.")
                else:
                    json_message["op"] = message[0]
                    json_message["username"] = message[1]
                    json_message["title"] = message[2]
                    json_message["content"] = message[3]
                    self.blockchain.add_operation(json_message["op"], json_message["username"], json_message["title"], json_message["content"])
                    print(f"self.name: {self.name}, op: {json_message['op']}, username: {json_message['username']}, title: {json_message['title']}, content: {json_message['content']}")
                    transmited_message = json.dumps(json_message)
                    self.broadcast_message(transmited_message)




    def broadcast_message(self, message):
        for peer, connection in self.connections.items():
            try:
                self.send_message(peer, message)
            except BrokenPipeError:
                print(f"{self.name}: Connection to {peer} lost.")
                del self.connections[peer]

    def send_message(self, peer, message):
        message = f"{self.name}: {message}"
        self.connections[peer].send(message.encode('utf-8'))

    def receive_messages(self, client):
        while True:
            try:
                data = client.recv(1024).decode('utf-8')
                sender, message = data.split(": ", 1)
                #message = message.split()

                print(f"Received from {sender}: {message}")
                json_message = json.loads(message)
                if len(message) == 0:
                    print("Invalid input. Please provide an operation, username, title, and content.")
                elif json_message["op"].lower() == "p" or json_message["op"].lower() == "post":
                    if json_message["username"] == "" or json_message["title"] == "" or json_message["content"] == "": 
                        print("Invalid post. Please provide an operation, username, title, and content.")
                    else:
                        op, username, title, content = json_message["op"], json_message["username"], json_message["title"], json_message["content"]
                        self.blockchain.add_operation(op, username, title, content)
                        print(f"{self.name}: {op} {username} {title} {content}")
                        print("Successfully added to blockchain")
                elif json_message["op"].lower() == "b" or json_message["op"].lower() == "bc":
                    self.blockchain.print()
            except BrokenPipeError:
                print("error")
                    


    def connect_to_peer(self, peer):
        if peer != self.name and peer not in self.connections and self.ports[peer] > self.port:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((self.host, self.ports[peer]))
                client.send(self.name.encode('utf-8'))
                self.connections[peer] = client
                print(f"{self.name}: Connected to {peer}")

                threading.Thread(target=self.receive_messages, args=(client,)).start()
            except ConnectionRefusedError:
                pass

    def connect_to_peers(self):
        while True:
            for peer in self.peers:
                self.connect_to_peer(peer)
            sleep(2)
            # print("trying to reconnecting to other peer")



################     __main__     ################
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Need to provide an ID of the client process')
        _exit(0)
    
    # clients sleep for 1 second as soon as they are up.
    sleep(1)
    client_name = sys.argv[1]
    port = 9000 + ['P1', 'P2', 'P3', 'P4', 'P5'].index(client_name)
    server = Server(port=port)
    server.start()
    threading.Thread(target=server.connect_to_peers, args=()).start()

    # server.print_ports_dict()
    print("I have finished setting up the server!")
