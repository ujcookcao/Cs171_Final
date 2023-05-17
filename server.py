import socket
import hashlib
import threading
import sys
from os import _exit
from sys import stdout
from time import sleep

#Make a new post: given a username, a title, and the content, create a new blog post authored under the username with the title and the content
class Post:
	author = ""
	title = ""
	content = ""
	def __init__(self, author, title, content):
		self.author = author
		self.title = title
		self.content = content
		self.comment = []

class Blog:
	def __init__(self):
		self.Blogchain = []
	def add_post(self, author, title , content):
		#check if the post already exist
		for post in self.Blogchain:
			if post.author == author and post.title == title and post.content == content:
				print(f"Post ( {author}, {title} )already exist")
				return
		new_post = Post(author, title, content)
		self.Blogchain.append(new_post)
	def delete_post(self, author,title,content):
		for post in self.Blogchain:
			if post.author == author and post.title == title and post.content == content:
				self.Blogchain.remove(post)

	#Comment on a post: given a username, a title, and a comment, if a blog post with the given title exists, create a new comment authored under the username for that post. Otherwise, the creation of the comment fails.
	def add_comment(self, author, title, commenter,comment_content):
		comment = [commenter, comment_content]
		found = 0
		for post in self.Blogchain:
			if post.author == author and post.title == title:
				post.comment.append(comment)
				found = 1
		if found == 0:
			print("No post found given the author and title")
	def delete_comment(self, author, title,commenter,comment_content):

		for post in self.Blogchain:
			if post.author == author and post.title ==title:
				for comment in post.comment:
					if comment[0] == commenter and comment[1] == comment_content:
							post.comment.remove(comment)
					else:
						print("No comment found given the commenter and comment_content")


# View all posts: list the title and the author for all blog posts in chronological order
#  View all posts made by a user: given a username, list the title and content of all blog posts made by this user in chronological order
#  View all comments on a post: given the title of a blog post, get its content, and list all the comments on the post and their authors
	def View_all_posts(self):
		print("All posts ====================")
		for post in self.Blogchain:
			print("Title: ", post.title, "Author: ", post.author)
		print("====================================")
	def View_all_posts_by_user(self, author):
		print(f"Posts by {author} ====================")
		for post in self.Blogchain:
			if post.author == author:
				print("Title: ", post.title, "Content: ", post.content)
		print("====================================")
	def View_all_comments_on_post(self, title):
		print(f"Comments on {title} ====================")
		for post in self.Blogchain:
			if post.title == title:
				print("Author: ",post.author ,"Title: ", post.title, "Content: ", post.content)
				for comment in post.comment:
					print("Commenter: ", comment[0], "||", "Content: ", comment[1])
		print("====================================")
				
if __name__ == "__main__":
	Blogchain = Blog()
	Blogchain.add_post("Alice", "First Post", "Hello World")
	Blogchain.add_post("Alice", "First Post", "Hello World")
	Blogchain.add_post("Alice", "Second Post", "Hello World")
	Blogchain.add_post("Bob", "Second Post", "Hello World")
	Blogchain.add_comment("Alice", "First Post", "Bob", "Nice Post")
	Blogchain.add_comment("Alice", "First Post", "Bob", "1111comment")
	

	Blogchain.View_all_comments_on_post("First Post")

class Block:
	pervious_block = None
	pervious_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
	#Operation refers to the post and comment operations ⟨OP, username, title, content⟩:
	op = ""
	username = ""
	title = ""
	content = ""
	nonce = 0
	#timestamp for one block 
	logical_time = -1

	
	def to_bytes(self):
		temp_string = self.pervious_block_hash + self.op + self.username + self.title + self.content + str(self.nonce) + str(self.logical_time)
		#print(temp_string)
		return bytes(temp_string, 'utf-8')
		#return self.pervious_block_hash + self.sender.to_bytes(4, 'big') + self.receiver.to_bytes(4, 'big') + self.amount.to_bytes(4, 'big') + self.nonce.to_bytes(4, 'big') 

class BlockChain:
	tail = None

	def add_transaction(self, sender, receiver, amount, time):
		new_block = Block()
		new_block.pervious_block = self.tail
		if None == self.tail:
			new_block.pervious_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
		else:
			new_block.pervious_block_hash = hashlib.sha256(self.tail.to_bytes()).hexdigest()
		new_block.sender = sender
		new_block.receiver = receiver
		new_block.amount = amount
		new_block.nonce = 0
		new_block.logical_time = time
		while ('0' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]) and ('1' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]) and ('2' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]) and ('3' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]):
			new_block.nonce += 1

		self.tail = new_block

	def get_balance(self, target):
		current = self.tail
		res = START_MONEY
		while None != current:
			if target == current.sender:
				res -= current.amount
			if target == current.receiver:
				res += current.amount
			current = current.pervious_block
		
		return res

	def print(self):
		stack = []
		current = self.tail
		while None != current:
			stack.append(current)
			current = current.pervious_block

		print("[", end="", flush=True)
		while 0 != len(stack):
			current = stack.pop()
			print(f"(P{current.sender}, P{current.receiver}, ${current.amount}, T{current.logical_time}, {current.pervious_block_hash})", end="", flush=True)
			#print(f"(P{current.sender}, P{current.receiver}, ${current.amount}, {hashlib.sha256(current.to_bytes()).hexdigest()})", end="")
			if 0 != len(stack):
				print(", ", end="", flush=True)
		print("]", flush=True)

# server_logical_time = 0
# START_MONEY = -1
# IP = socket.gethostbyname('localhost')
# PORT = 9000
# in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_sockets = [None] * 3
# client_ports = [-1,-1,-1]
# id_to_port = [-1,-1,-1] # id_to_port[i] has the port number of the client with id i+1
# blockchain = BlockChain()
# connect_lock = threading.Lock()

# def get_user_input():
# 	while True:
# 		user_input = input()
# 		parameters = user_input.split()
# 		if 0 == len(parameters) or "exit" == parameters[0]:
# 			in_sock.close()
# 			for sock in client_sockets:
# 				if None != sock:
# 					sock[0].close()
# 			#print("exiting program", flush=True)
# 			stdout.flush()
# 			_exit(0)
# 		elif "wait" == parameters[0]:
# 			sleep(int(parameters[1]))
# 		elif "b" == parameters[0] or "Balance" == parameters[0]:
# 			print(f"P1: ${blockchain.get_balance(1)}, P2: ${blockchain.get_balance(2)}, P3: ${blockchain.get_balance(3)}", flush=True)
# 		elif "c" == parameters[0] or "Blockchain" == parameters[0]:
# 			blockchain.print()

# def respond(conn, addr):
# 	#print(f"accepted connection from port {addr[1]}", flush=True)

# 	while True: # handle message sent from a client
# 		try:
# 			data = conn.recv(1024)
# 		except:
# 			#print(f"exception in receiving from {addr[1]}", flush=True)
# 			break
# 		if not data:
# 			conn.close()
# 			#print(f"connection closed from {addr[1]}", flush=True)
# 			break

# 		threading.Thread(target=handle_msg, args=(data, conn, addr)).start()

# def handle_msg(data, conn, addr):
# 	global server_logical_time 
# 	data = data.decode()
# 	parameters = data.split()

# 	#print(f"{addr[1]}: {parameters}", flush=True)

# 	if "init" == parameters[0]:
# 		connect_lock.acquire()
# 		client_ports[int(parameters[1])-1] = int(parameters[2])

# 		for sock in client_sockets: # tell existing clients to connect to the new client
# 			if None != sock:
# 				sock[0].sendall(bytes(f"connect {parameters[1]} {parameters[2]}\n", "utf-8"))

# 		for i in range(3): # tell the new client to connect to existing clients
# 			if None != client_sockets[i]:
# 				conn.sendall(bytes(f"connect {i+1} {client_ports[i]}\n", "utf-8"))
		
# 		id_to_port[int(parameters[1])-1] = addr[1]
# 		client_sockets[int(parameters[1])-1] = (conn, addr)
# 		connect_lock.release()

# 	elif "t" == parameters[0] or "Transfer" == parameters[0]:
# 		source = id_to_port.index(addr[1]) + 1
# 		target = int(parameters[1][1:])
# 		amount = int(parameters[2][1:])
# 		transfer_time = int(parameters[3])
# 		server_logical_time = max(server_logical_time, int(parameters[4])) + 1

		
# 		if target < 1 or target > 3:
# 			conn.sendall(bytes(f"transfer request with a non-existing receiver,  logical_time = {transfer_time}", "utf-8"))
# 			return

# 		server_logical_time += 2
# 		if blockchain.get_balance(source) < amount:
# 			conn.sendall(bytes(f"Insufficient_Balance {parameters[3]} {server_logical_time}\n", "utf-8"))
# 			return

# 		blockchain.add_transaction(source, target, amount,transfer_time)
# 		conn.sendall(bytes(f"Success {parameters[3]} {server_logical_time}\n", "utf-8"))

# 	elif "b" == parameters[0] or "Balance" == parameters[0]:
# 		if 2 != len(parameters):
# 			conn.sendall(bytes(f"balance request with wrong number of arguments", "utf-8"))
# 			return
# 		target = int(parameters[1][1:])

# 		if target < 1 or target > 3:
# 			conn.sendall(bytes(f"balance request with a non-existing client", "utf-8"))
# 			return
		
# 		res = blockchain.get_balance(target)
# 		conn.sendall(bytes(f"Balance: ${res}", "utf-8"))

# 	else:
# 		conn.sendall(bytes(f"invalid operation", "utf-8"))


# if __name__ == "__main__":
# 	START_MONEY = int(sys.argv[1])
# 	in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 	in_sock.bind((IP, PORT))
# 	in_sock.listen()
	
# 	threading.Thread(target=get_user_input).start() # handle user inputs to the server

# 	while True: # handle connection from clients
# 		try:
# 			conn, addr = in_sock.accept()
# 		except:
# 			#print("exception in accept", flush=True)
# 			break

# 		threading.Thread(target=respond, args=(conn, addr)).start()
