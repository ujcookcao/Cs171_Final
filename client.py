# CS171 Final Project, June 2023
# client.py
# Author: Wenjin Li

import socket
import sys
import threading
import time
import json

import BlockChain as BC
import Blog
import MultiPaxos

from time import sleep
from os import _exit


class Server:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        # linstening socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR allowing it to bind to the same address \
        #   even if it's still in use by a previous connection.
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.connections = {}
        self.peers = ['P1', 'P2', 'P3', 'P4', 'P5']
        self.ports = {peer: 9000 + i for i, peer in enumerate(self.peers)}
        self.name = [peer for peer, port in self.ports.items() if port == self.port][0]
        self.Paxos = MultiPaxos.Paxos(id=self.name)
        self.receiceNum = 0
        self.acceptedNum = 0
        self.promise_all_val = []
        self.promises = {}
        self.ImAleader = False
        self.curr_leader = ''
        self.prev_leader = ''

    def print_ports_dict(self):
        print(f'{self.ports}')

    def start(self):
        self.server.listen()
        print(f"{self.name}: Server started on port {self.port}")
        self.accept_connections_thread = threading.Thread(target=self.accept_connections).start()
        # if checkpoint.txt able to open, and 
            # self.curr_leader = [0]
            # self.prev_leader = [1]
        # else if txt, doesnt exist
        
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
        print(f"{self.name}: {client_name} has connected with me.")

        threading.Thread(target=self.receive_messages, args=(client,)).start()

    def read_commands(self):
        while True:
            # message = input()
            # self.broadcast_message(message)
            user_input = input()
            if user_input.split()[0] == 'exit':
                print("exiting...")
                self.server.close()
                sys.stdout.flush()
                _exit(0)

            elif user_input.split()[0] == "show":
                self.show_command()
                sys.stdout.flush()

            elif user_input.split()[0] == "info":
                print(f"curr_leader is:{self.curr_leader}")
                print(self.Paxos)
                sys.stdout.flush()

            elif user_input.split()[0] == "BlockChain" or user_input.split()[0] == "BC":
                if len(BC_Logs) == 0:
                    print("[]")
                    sys.stdout.flush()
                    continue
                # print('asked to print the entire blockchain')
                bc_string = ""
                for log in BC_Logs:
                    each_log_str = f"{log._OP}, {log._username}, {log._title}, {log._content}, {log.hash}"
                    bc_string += f"({each_log_str}), "
                print( f'[{bc_string[:-2]}]' )
                sys.stdout.flush()

            elif user_input.split()[0] == 'POST' or user_input.split()[0] == 'P':
            # message_tokens: POST username title content
                if BC.check_if_post_exist(user_input.split()[1],user_input.split()[2]):
                    print("this author already has a post with the same title!")
                
                else:
                    # send PERPARE with BallotNumber
                    self.receiceNum = 0
                    if self.curr_leader == '':
                        self.Paxos.add_proposal(user_input)
                        message_dict = self.Paxos.prepare().to_dict()
                        message_json = json.dumps(message_dict)
                        self.broadcast_message(message_json)
                    else: # if curr leader is not empty
                        if self.curr_leader == self.name: # if it's ourself

                            self.create_new_post(user_input)
                        else: # if not ourself
                            msgToLeader = MultiPaxos.Message(msg_type=user_input[0], sender=self.Paxos)
                            self.broadcast_msg_to(self.curr_leader, user_input)
                   
            else:
                    print(f"{user_input}, wrong input")

    def create_new_post(self,user_input):
        hash_val = '0'*64
        if len(BC_Logs) > 0:
            hash_val = BC_Logs[-1].compute_block_hash()
        # blog_str = generate_send_string(sender, message_tokens[1], requested_amt)
        blog_str = user_input.split()
        new_blog_str = ''
        for i in blog_str:
            new_blog_str += i
        right_nonce = BC.compute_nonce(f'{hash_val}{new_blog_str}')
        new_log = BC.Log(
            hash = hash_val,
            OP = user_input.split()[0],
            username = user_input.split()[1],
            title = user_input.split()[2],
            content = user_input.split()[3],
            nonce = right_nonce,
        )
        BC_Logs.append(new_log)
        print(f"SUCCESS created a new post: {user_input}")

    def broadcast_message(self, message):
        for peer, connection in self.connections.items():
            try:
                self.send_message(peer, message)
            except BrokenPipeError:
                print(f"{self.name}: Connection to {peer} lost.")
                del self.connections[peer]

    def broadcast_msg_to(self, id, message):
        try:
            self.send_message(id, message)
        except BrokenPipeError:
            print(f"{self.name}: Connection to P{id} lost.")
            del self.connections[id]

    def send_message(self, peer, message):
        # message = f"{self.name}: {message}"
        message = f"{message}"
        self.connections[peer].send(message.encode('utf-8'))

    def receive_messages(self, client):
        while True:
            try:
                message_json = client.recv(1024).decode('utf-8')
                if message_json:  # Check if the message is not empty
                    message = json.loads(message_json)
                    # print(type(message)) # it's dict here
                    # print(f"Received in client.py: {message}")
                    if 
                    elif message["msg_type"] == "PREPARE":
                        pre_PROMISE_msg = self.Paxos.receive_prepare(message)
                        # print(f"Received in client.py: {pre_PROMISE_msg.id}")
                        if pre_PROMISE_msg is not None: # if not rejected
                            pre_PROMISE_dict = pre_PROMISE_msg.to_dict()
                            message_json = json.dumps(pre_PROMISE_dict)
                            self.broadcast_msg_to(id=pre_PROMISE_dict['ballot_num_id'], message=message_json)

                    elif message["msg_type"] == "PROMISE": # Phase two: handling all promise msg
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['ballot_num']},{message['ballot_num_id']}> <{message['accepted_num']},{message['accepted_num_id']}> {message['accepted_val']}")
                        self.receiceNum += 1
                        self.promise_all_val.append(message['accepted_val'])
                        self.promises[message['sender']] = message
                        if self.receiceNum >= (len(self.peers)-1) / 2:  # More than half peers/majority responded
                            self.curr_leader = self.n
                            self.receiceNum = -999
                            # print(f"before chceking if all None, receiceNum={self.receiceNum}")
                            if all(x is None for x in self.promise_all_val):
                                # print("im here1")
                                # myVal = initial_value
                                self.Paxos.update_my_accepted_value()
                                # send to all 
                                message_dict = self.Paxos.received_majority_promise().to_dict()
                                message_json = json.dumps(message_dict)
                                self.broadcast_message(message_json)
                                self.promise_all_val = []
                                self.promises = {}
                                # set myself to be a leader:
                                self.curr_leader = self.Paxos.get_id()
                            else: # TODO: need to handle here
                                print("goes into the else case")
                                # max(all massage(class) in this dict(), x)
                                # print("im here2")
                                # temp_id = self.Paxos.id
                                # self.promises[temp_id] = MultiPaxos.Message("PROMISE", ballot_num=self.Paxos.ballot_num, ballot_num_id=self.Paxos.ballot_num_id,
                                #                         accepted_num=self.Paxos.accepted_ballot_num, accepted_num_id=self.Paxos.accepted_ballot_num_id,
                                #                         accepted_val=self.Paxos.accepted_value, sender=self.Paxos.id).to_dict()
                                highest_b_message = max(self.promises.values(), key=lambda m: m['accepted_num'])
                                # print(highest_b_message)
                                self.Paxos.update_my_accepted_value(highest_b_message['accepted_val'], self.Paxos.ballot_num, self.Paxos.id)
                                # pre_ACCEPT_msg = self.Paxos.receive_promise(message)
                        else:
                            pass
                            # print(f"Not enough PROMISE, only have receiceNum={self.receiceNum}")

                        # print(f"after chceking if all None, receiceNum={self.receiceNum}")  
                    elif message["msg_type"] == "ACCEPT": # Phase two: non-leader handling ACCEPT msg
                        # ACCEPT <1,P1> 'POST username title content'
                        msg = self.Paxos.receive_accept(message)
                        if msg is not None:
                            msg_in_dict= msg.to_dict()
                            message_json = json.dumps(msg_in_dict)
                            self.broadcast_msg_to(id=msg.accepted_num_id, message=message_json)
                        else:
                            print(f"I have a highter ballot num than {message['sender']}")

                    elif message["msg_type"] == "ACCEPTED":
                        # ACCEPTED <1,P1> 'POST username title content'
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['accepted_num']},{message['accepted_num_id']}> {message['accepted_val']}")
                        print(f"current acceptnum counter :{self.acceptedNum}")
                        self.acceptedNum += 1
                        print(len(self.peers))
                        if self.acceptedNum == (len(self.peers)-1) / 2:  # More than half peers/majority responded
                            print("enter majority decide")
                            
                            #decide
                            # TODO: decision
                            self.create_new_post(message['accepted_val'])
                            # send to all
                            print() 
                            message_dict = self.Paxos.received_majority_accepted().to_dict()
                            message_json = json.dumps(message_dict)
                            self.broadcast_message(message_json)
                        
                            #delete 
                            self.Paxos.clear()

                    elif message["msg_type"] == "DECIDE":
                        # DECIDE <1,P1> 'POST username title content'
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['ballot_num']},{message['ballot_num_id']}> {message['accepted_val']}")
                        # decision
                        
                        self.create_new_post(message['accepted_val'])
                        # set the sender to curr_leader
                        self.curr_leader =  message['sender']
                        self.Paxos.clear()


                    
                # else:
                    # print("receive_messages() receive nothings")
        
            except ConnectionResetError:
                print("ConnectionResetError")
                sys.stdout.flush()
                break

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

    def show_command(self):
        print("POST username title content")
        print("COMMENT username title content")
        print("info")
        print("exit")
        print("")


################      global      ################
BC_Logs = []
REPLIED = {}

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
    print(f"{server.name}: I have finished setting up the server!")
