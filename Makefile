server: server.py
	python3 -u server.py 100
client1: client.py
	python3 -u client.py 1
client2: client.py
	python3 -u client.py 2
client3: client.py
	python3 -u client.py 3

test1: client.py
	python3 -u client.py 1 < input_1
test2: client.py
	python3 -u client.py 2 < input_2
test3: client.py
	python3 -u client.py 3 < input_3