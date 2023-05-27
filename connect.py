import socket
import hashlib
import threading
import sys
import BlockChain
from os import _exit
from sys import stdout
from time import sleep

#Make a new post: given a username, a title, and the content, create a new blog post authored under the username with the title and the content

MY_IP = socket.gethostbyname('localhost')
OFFSET_PORT = 9000
in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sockets = [None] * 3
client_ports = [-1,-1,-1,-1]
id_to_port = [-1,-1,-1,-1] # id_to_port[i] has the port number of the client with id i+1
blockchain = BlockChain()
connect_lock = threading.Lock()
DELAY_TIME = 0.1

def get_user_input():
	while True:
		user_input = input()
		parameters = user_input.split()
		if 0 == len(parameters) or "exit" == parameters[0]:
			in_sock.close()
			for sock in client_sockets:
				if None != sock:
					sock[0].close()
			#print("exiting program", flush=True)
			stdout.flush()
			_exit(0)

def respond(conn, addr):
	#print(f"accepted connection from port {addr[1]}", flush=True)

	while True: # handle message sent from a client
		try:
			data = conn.recv(1024)
		except:
			#print(f"exception in receiving from {addr[1]}", flush=True)
			break
		if not data:
			conn.close()
			#print(f"connection closed from {addr[1]}", flush=True)
			break



PROCESS_ID = -1
PROCESS_PORT = -1
SERVER_IP = socket.gethostbyname('localhost')
SERVER_PORT = 9000
sockets = [None] * 5 # 0 is for myself; 1,2,3,4 are for rest process
logical_time = 0

def get_user_input():
	global logical_time, request_queue, reply_dicitonary # have to specify global because the function changes the variables

	while True:
		user_input = input()
		parameters = user_input.split()
		if 0 == len(parameters) or "exit" == parameters[0]:
			for sock in sockets:
				if None != sock:
					sock.close()
			stdout.flush()
			_exit(0)
		elif "hi" == parameters[0]: # say hi to all clients, for debugging
			for i in range(1, 4):
				if PROCESS_ID != i and None != sockets[i]:
					try:
						sockets[i].sendall(bytes(f"Hello from P{PROCESS_ID}", "utf-8"))
					except:
						print(f"can't send hi to {i}\n")



def handle_message_from(id, data): #id is the id that current process receives from
	global reply_dicitonary_cond, reply_dicitonary, using_server, request_queue, logical_time
	parameters = data.split(" ")

	if "connect" == parameters[0]:
		if int(parameters[1]) >= PROCESS_ID: # only connect to client with smaller id
			return
		sockets[int(parameters[1])] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sockets[int(parameters[1])].connect((SERVER_IP, int(parameters[2])))
		sockets[int(parameters[1])].sendall(bytes(f"init {PROCESS_ID}\n", "utf-8"))
		threading.Thread(target=listen_message_from, args=[int(parameters[1])]).start() # listen to message from the target client

def listen_message_from(id):

	global logical_time

	while True:
		try:
			data = sockets[id].recv(4096)
		except:
			break
		if not data: # connection closed
			sockets[id].close()
			break
		
		data = data.decode()
		data = data.split("\n") # to prevent recving mutiple messgaes, the last element is always ""
		for line in data:
			if "" == line:
				continue
			threading.Thread(target=handle_message_from, args=[id, line]).start()

def accept_connection():
	global logical_time
	while True:
		try:
			conn, addr = sockets[PROCESS_ID].accept() # accept connection from client with larger id
			client_id = conn.recv(1024)
			client_id = client_id.decode()
			client_id = client_id.split()
			sockets[int(client_id[1])] = conn
			threading.Thread(target=listen_message_from, args=[int(client_id[1])]).start() # listen to message from the target client
		except:
			break



if __name__ == "__main__":
	PROCESS_ID = int(sys.argv[1])
	in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	in_sock.bind((MY_IP, OFFSET_PORT))
	in_sock.listen()
	
	threading.Thread(target=get_user_input).start() # handle user inputs to the server
		
	sockets[PROCESS_ID] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockets[PROCESS_ID].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sockets[PROCESS_ID].bind((SERVER_IP, 0))
	sockets[PROCESS_ID].listen()
	threading.Thread(target=accept_connection).start()

	sleep(DELAY_TIME)
	sockets[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockets[0].connect((SERVER_IP, SERVER_PORT))
	sockets[0].sendall(bytes(f"init {PROCESS_ID} {sockets[PROCESS_ID].getsockname()[1]}", "utf-8")) # send client id and port to the server when connecting

	threading.Thread(target=get_user_input).start() # listen to user input from terminal
	threading.Thread(target=listen_message_from, args=[0]).start() # listen to message from server

	while True: # handle connection from clients
		try:
			conn, addr = in_sock.accept()
		except:
			#print("exception in accept", flush=True)
			break

	threading.Thread(target=respond, args=(conn, addr)).start()
