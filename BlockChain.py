import socket
import hashlib
import threading
import sys
from os import _exit
from sys import stdout
from time import sleep
class Block:
    previous_block = None
    previous_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    #Operation refers to the post and comment operations ⟨OP, username, title, content⟩:
    op = ""
    username = ""
    title = ""
    content = ""
    nonce = 0

    def to_bytes(self):
        temp_string = self.previous_block_hash + self.op + self.username + self.title + self.content + str(self.nonce)
        return bytes(temp_string, 'utf-8')

class BlockChain:
    tail = None

    def add_operation(self, op, username, title, content):
        new_block = Block()
        new_block.previous_block = self.tail
        if self.tail is None:
            new_block.previous_block_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        else:
            new_block.previous_block_hash = hashlib.sha256(self.tail.to_bytes()).hexdigest()
        new_block.op = op
        new_block.username = username
        new_block.title = title
        new_block.content = content
        new_block.nonce = 0
        while ('0' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]) and ('1' != hashlib.sha256(new_block.to_bytes()).hexdigest()[0]):
# 			new_block.nonce += 1
            new_block.nonce += 1
        self.tail = new_block

    def print(self):
        stack = []
        current = self.tail
        while current is not None:
            stack.append(current)
            current = current.previous_block
        print("[", end="")
        while len(stack) != 0:
            current = stack.pop()
            print(f"(OP: {current.op}, User: {current.username}, Title: {current.title}, Content: {current.content}, Nonce: {current.nonce}, {current.previous_block_hash})", end="")
            if len(stack) != 0:
                print(", ", end="")
        print("]")

if __name__ == "__main__":
        blockchain = BlockChain()
        while True:
            print("1. Add Operation")
            print("2. Print Blockchain")
            print("3. Exit")
            choice = int(input("Enter your choice: "))
            if choice == 1:
                op = input("Enter operation: ")
                username = input("Enter username: ")
                title = input("Enter title: ")
                content = input("Enter content: ")
                blockchain.add_operation(op, username, title, content)
            elif choice == 2:
                blockchain.print()
            elif choice == 3:
                _exit(0)
            else:
                print("Invalid choice")