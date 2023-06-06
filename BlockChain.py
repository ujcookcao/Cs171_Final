# BlockChain.py
# Author: Wenjin Li
import hashlib

class Log:
	def __init__(self, hash, OP, username, title, content, nonce):
		self.hash = hash
		self._OP = OP
		self._username = username
		self._title = title
		self._content = content
		self.nonce = nonce
	
	def compute_block_hash(self):
		sha = hashlib.sha256()
		block_str = self.hash
		block_str += generate_send_string(self._OP, self._username, self._title, self._content)
		block_str += str(self.nonce)
		sha.update(block_str.encode('utf-8'))
		return sha.hexdigest()
	
	def __str__(self):
		return f'{self._OP} {self._username} {self._title} {self._content} {self.hash}'
	
	def __repr__(self):
		return self.__str__()

def generate_send_string(OP, username, title, content):
	return f"{OP}{username}{title}{content}"

def check_if_post_exist(username, title):
    for log in Logs:
        if log._username == username and log._title == title:
            return True
    return False

def compute_nonce(pre_string):
	potential_nonce = 0
	while True:
		sha = hashlib.sha256()
		sha.update( (pre_string + str(potential_nonce) ).encode('utf-8') )
		sha_digest = sha.hexdigest()
		first_letter = sha_digest[0]

		# print(f'digest for nonce: {potential_nonce}: {sha_digest}')
		accept_range = ['0', '1']
		if first_letter in accept_range:
			break
		potential_nonce += 1
	return potential_nonce

Logs = []

if __name__ == "__main__":
	# create blockchain
	while True:
		user_input = input()
		if user_input.split()[0] == 'a':
			print("exiting...")
			break
		elif user_input.split()[0] == 'BlockChain' or user_input.split()[0] == 'BC':
			if len(Logs) == 0:
				print("[]")
				# sys.stdout.flush()
				continue
			# print('asked to print the entire blockchain')
			bc_string = ""
			for log in Logs:
				each_log_str = f"{log._OP}, {log._username}, {log._title}, {log._content}, {log.hash}"
				bc_string += f"({each_log_str}), "
			print( f'[{bc_string[:-2]}]' )
			# sys.stdout.flush()
		elif user_input.split()[0] == 'POST' or user_input.split()[0] == 'P':
		# message_tokens: POST username title content
			if check_if_post_exist(user_input.split()[1],user_input.split()[2]):
				# connection.sendall(bytes(f"Insufficient Balance", "utf-8"))
				print("this author already has a post with the same title!")
			else:
				hash_val = '0'*64
				if len(Logs) > 0:
					hash_val = Logs[-1].compute_block_hash()

				# blog_str = generate_send_string(sender, message_tokens[1], requested_amt)
				blog_str = user_input.split()
				new_blog_str = ''
				for i in blog_str:
					new_blog_str += i
				# right_nonce = compute_nonce(f'{hash_val}{blog_str[0]}{blog_str[1]}{blog_str[2]}{blog_str[3]}')
				right_nonce = compute_nonce(f'{hash_val}{new_blog_str}')
				new_log = Log(
					hash = hash_val,
					OP = user_input.split()[0],
					username = user_input.split()[1],
					title = user_input.split()[2],
					content = user_input.split()[3],
					nonce = right_nonce,
				)
				Logs.append(new_log)
				print("SUCCESS")
				# connection.sendall(bytes(f"SUCCESS", "utf-8"))
		
		else:
				print(f"{user_input}, worong input")