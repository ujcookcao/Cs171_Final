import socket
import threading
import sys
from os import _exit
from sys import stdout
from time import sleep

from queue import PriorityQueue # queue module is thread safe
request_queue = PriorityQueue() # each element is (time, id)

reply_dicitonary = dict() # key is time, value is a list on wether the client heard back the reply or not
reply_dicitonary_cond = threading.Condition() # use to lock reply_dicitonary and sleep/wakeup threads as necessary
using_server = False


DELAY_TIME = 3

PROCESS_ID = -1
PROCESS_PORT = -1
SERVER_IP = socket.gethostbyname('localhost')
SERVER_PORT = 9000
sockets = [None] * 4 # 0 is for server; 1,2,3 are for clients
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
		elif "wait" == parameters[0]:
			sleep(int(parameters[1]))
		elif "hi" == parameters[0]: # say hi to all clients, for debugging
			for i in range(1, 4):
				if PROCESS_ID != i and None != sockets[i]:
					try:
						sockets[i].sendall(bytes(f"Hello from P{PROCESS_ID}", "utf-8"))
					except:
						print(f"can't send hi to {i}\n")
		elif "q" == parameters[0]: # print request queue, for debugging
			new_queue = PriorityQueue()
			while False == request_queue.empty():
				temp = request_queue.get()
				print(temp)
				new_queue.put(temp)
			request_queue = new_queue
		# might need to add more commands here
		elif "b" == parameters[0] or "Balance" == parameters[0]:
			sockets[0].sendall(bytes(user_input, "utf-8"))
		
		elif "t" == parameters[0] or "Transfer" == parameters[0]:

			reply_dicitonary_cond.acquire()
			logical_time = logical_time+1
			print(f"Local time: {logical_time}; REQUEST (T{logical_time}, P{PROCESS_ID})\n")

			while True == using_server:
				reply_dicitonary_cond.wait()
			request_queue.put((logical_time, PROCESS_ID))

			reply_dicitonary[logical_time] = [True,False,False,False] # first element is not used
			reply_dicitonary[logical_time][PROCESS_ID] = True
			transfer_timestamp = logical_time 

			for i in range(1, 4):
				if PROCESS_ID != i:
					logical_time = logical_time+1
					try:
						sockets[i].sendall(bytes(f"request {transfer_timestamp} {logical_time}\n", "utf-8"))
					except:
						print(f"can't send request to {i}\n")
			reply_dicitonary_cond.release()

			threading.Thread(target=complete_transfer, args=[transfer_timestamp, user_input]).start()


def complete_transfer(transfer_time, user_input):
	global request_queue, reply_dicitonary_cond, reply_dicitonary, using_server, logical_time

	reply_dicitonary_cond.acquire()
	while True:
		queue_front = request_queue.get()
		can_transfer = ((True == reply_dicitonary[transfer_time][1]) and (True == reply_dicitonary[transfer_time][2]) and (True == reply_dicitonary[transfer_time][3])) and ((transfer_time == queue_front[0]) and (PROCESS_ID == queue_front[1]))
		if True == can_transfer:
			break
		request_queue.put(queue_front)
		if False == reply_dicitonary_cond.wait(timeout=10):
			print(f"Local time: {logical_time}; request (T{transfer_time}, P{PROCESS_ID}) timed out\n")
			reply_dicitonary_cond.release()
			return
	logical_time = logical_time + 1 # for removing element from priority queue
	using_server = True

	print(f"Local time: {logical_time}; SERVER (({user_input}), T{transfer_time})\n")

	logical_time = logical_time+1 # for sending message to server
	sockets[0].sendall(bytes(f"{user_input} {transfer_time} {logical_time}", "utf-8"))
	reply_dicitonary_cond.release()

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

	# parameter[1] is the transfer timestamp of sender, parameter[2] is the logical time of the sender
	elif "request" == parameters[0]:
		sleep(DELAY_TIME)
		reply_dicitonary_cond.acquire()
		logical_time = max(logical_time, int(parameters[2]))+1

		print(f"Local time: {logical_time}; REPLY (T{parameters[1]}, P{id})\n")

		while True == using_server:
			reply_dicitonary_cond.wait()
		
		#put need logical time increment 
		logical_time = logical_time+2 # 1 for adding element from priority queue, 1 for sending message to the client
		request_queue.put((int(parameters[1]), id))
		try:
			sockets[id].sendall(bytes(f"reply {parameters[1]} {logical_time}\n", "utf-8"))
		except:
			print(f"can't send reply to {id}\n")
		reply_dicitonary_cond.release()

	elif "reply" == parameters[0]:
		sleep(DELAY_TIME)
		reply_dicitonary_cond.acquire()
		logical_time = max(logical_time, int(parameters[2]))+1
		
		print(f"Local time: {logical_time}; {id} REPLIED (T{parameters[1]}, P{PROCESS_ID})\n")

		reply_dicitonary[int(parameters[1])][id] = True
		reply_dicitonary_cond.notify_all()
		reply_dicitonary_cond.release()

	elif "Success" == parameters[0] or "Insufficient_Balance" == parameters[0]:
		sleep(DELAY_TIME)
		reply_dicitonary_cond.acquire()
		logical_time = max(int(parameters[2]), logical_time)+1
		print(f"{parameters[0]}\n")
		print(f"Local time: {logical_time}; RELEASE (T{parameters[1]}, P{PROCESS_ID})\n")
		
		for i in range(1, 4):
				if PROCESS_ID != i:
					logical_time = logical_time+1
					try:
						sockets[i].sendall(bytes(f"release {parameters[1]} {logical_time}\n", "utf-8"))
					except:
						print(f"can't send release to {i}\n")
		
		using_server = False
		reply_dicitonary_cond.notify_all()
		reply_dicitonary_cond.release()

	elif "release" == parameters[0]:
		sleep(DELAY_TIME)
		reply_dicitonary_cond.acquire()
		logical_time = max(logical_time, int(parameters[2]))+1

		print(f"Local time: {logical_time}; DONE (T{parameters[1]}, P{id})\n")

		new_queue = PriorityQueue()
		while False == request_queue.empty():
			temp = request_queue.get()
			if temp[0] != int(parameters[1]) or temp[1] != id:
				new_queue.put(temp)
		request_queue = new_queue
		logical_time += 1
		reply_dicitonary_cond.notify_all()
		reply_dicitonary_cond.release()

	elif "Balance:" == parameters[0]:
		reply_dicitonary_cond.acquire()
		print(f"{data}\n")
		reply_dicitonary_cond.release()

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

	while True:
		pass # do nothing
