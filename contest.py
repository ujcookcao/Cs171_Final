# server.py
# this process accepts an arbitrary number of client connections
# it echoes any message received from any client to console
# then broadcasts the message to all clients
import socket
import threading
import sys
from os import _exit
from sys import stdout
from time import sleep



# simulates network delay then handles received message
# def handle_msg(data, addr,out_socks):
# 	# simulate 3 seconds message-passing delay
# 	sleep(3) # imported from time library
# 	# decode byte data into a string
# 	data = data.decode()
# 	# echo message to console
# 	print(f"{addr[1]}: {data}", flush=True)

# 	# broadcast to all clients by iterating through each stored connection
# 	for sock in out_socks:
# 		conn = sock[0]
# 		recv_addr = sock[1]
# 		# echo message back to client
# 		try:
# 			# convert message into bytes and send through socket
# 			conn.sendall(bytes(f"{addr[1]}: {data}", "utf-8"))
# 			print(f"sent message to port {recv_addr[1]}", flush=True)
# 		# handling exception in case trying to send data to a closed connection
# 		except:
# 			print(f"exception in sending to port {recv_addr[1]}", flush=True)
# 			continue

# handle a new connection by waiting to receive from connection
def respond(conn, addr):
	print(f"accepted connection from port {addr[1]}", flush=True)

	# infinite loop to keep waiting to receive new data from this client
	while True:
		try:
			# wait to receive new data, 1024 is receive buffer size
			data = conn.recv(1024)
		# handle exception in case something happened to connection
		# but it's not properly closed
		except:
			print(f"exception in receiving from {addr[1]}", flush=True)
			break
			
		# if client's socket closed, it will signal closing without any data
		if not data:
			# close own socket to client since other end is closed
			conn.close()
			print(f"connection closed from {addr[1]}", flush=True)
			break

		# spawn a new thread to handle message 
		# so simulated network delay and message handling don't block receive
		threading.Thread(target=handle_msg, args=(data, addr)).start()

def tryconnect(in_sock, in_socks_dict):
	in_sock.listen()
	# infinite loop to keep accepting new connections
	while True:
		try:
			# wait to accept any incoming connections
			# conn: socket object used to send to and receive from connection
			# addr: (IP, port) of connection 
			conn, addr = in_sock.accept()
		except:
			print("exception in accept", flush=True)
			break
		# add connection to array to send data through it later
		in_socks_dict[in_sock] = (conn,addr)
		# spawn new thread for responding to each connection
		threading.Thread(target=respond, args=(conn, addr)).start()
		
# We also need to modify the get_user_input function to handle multiple output sockets
def get_user_input(out_socks_dict):
    while True:
        # wait for user input
        user_input = input()
        if user_input == "":
            for sock in out_socks_dict.values():
                # close all sockets before exiting
                sock.close()
            print("exiting program")
            # flush console output buffer in case there are remaining prints
            # that haven't actually been printed to console
            stdout.flush() # imported from sys library
            # exit program with status 0
            _exit(0) # imported from os library
        else:
            for sock in out_socks_dict.values():
                try:
                    # send user input string to server, converted into bytes
                    sock.sendall(bytes(user_input, "utf-8"))
                # handling exception in case trying to send data to a closed connection
                except:
                    print("exception in sending to server")
                    continue

            print("sent latest input to server")


# simulates network delay then handles received message
def handle_msg(data):
	# simulate 3 seconds message-passing delay
	sleep(3) # imported from time library
	# decode byte data into a string
	data = data.decode()
	# echo message to console
	print(data)

def try_accept_message(out_sock):
	# infinite loop to keep waiting to receive new data from server
	while True:
		try:
			# wait to receive new data, 1024 is receive buffer size
			# set bigger buffer size if data exceeds 1024 bytes
			data = out_sock.recv(1024)
		# handle exception in case something happened to connection
		# but it's not properly closed
		except:
			print("exception in receiving")
			break
		# if server's socket closed, it will signal closing without any data
		if not data:
			# close own socket since other end is closed
			out_sock.close()
			print("connection closed from server")
			break

		# spawn a new thread to handle message 
		# so simulated network delay and message handling don't block receive
		threading.Thread(target=handle_msg, args=(data,)).start()


if __name__ == "__main__":
    PROCESS_ID = int(sys.argv[1])
    # specify server's socket address
    # programatically get local machine's IP
    IP = socket.gethostbyname('localhost')
    # port 3000-49151 are generally usable
    PORT = 9000 + PROCESS_ID

    # create a socket object, SOCK_STREAM specifies a TCP socket
    in_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind socket to address
    in_sock.bind((IP, PORT))
    #store all income connection sockets in a dictionary
    in_socks_dict = {}
    threading.Thread(target=tryconnect, args=(in_sock, in_socks_dict)).start()

    # container to store all connections
    # using a list/array here for simplicity
    out_socks_dict = {}

    for x in range(1, 6):
        if x != PROCESS_ID:
            
            threading.Thread(target=try_accept_message, args=(out_sock,)).start()
            out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            out_sock.connect((IP, 9000 + x))
            out_socks_dict[x] = out_sock
            print(f"Connected to server {x}")

    # spawn a new thread to wait for user input
    # so user input and connection acceptance don't block each other
    threading.Thread(target=get_user_input, args=(out_socks_dict,)).start()

    def try_connect_to_other(out_sock):
	    while(1):
		    try:
			    outsock.connect((IP, 9000 + PROCESS_ID))
                break
	    


