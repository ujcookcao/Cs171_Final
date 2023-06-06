# MultiPaxos.py
# Author: Wenjin Li

PREPARE = "PREPARE"
PROMISE = "PROMISE"
ACCEPT = "ACCEPT"
ACCEPTED = "ACCEPTED"
DECIDE = "DECIDE"

class Message:
    def __init__(self, msg_type, ballot_num=None, ballot_num_id=None, depth=None,
                  accepted_num=None, accepted_num_id=None, accepted_val=None, sender=None, receiver=None):
        self.msg_type = msg_type
        self.ballot_num = ballot_num
        self.ballot_num_id = ballot_num_id
        self.depth = depth
        self.accepted_num = accepted_num
        self.accepted_num_id = accepted_num_id
        self.accepted_val = accepted_val
        self.sender = sender
        self.receiver = receiver
    
    def to_dict(self):
        return {
            'msg_type': self.msg_type,
            'ballot_num': self.ballot_num,
            'ballot_num_id': self.ballot_num_id,
            'depth': self.depth,
            'accepted_num': self.accepted_num,
            'accepted_num_id': self.accepted_num_id,
            'accepted_val': self.accepted_val,
            'sender': self.sender,
            'receiver': self.receiver
        }
    def get_msg_type(self):
        return self.msg_type
    def get_ballot_num(self):
        return self.ballot_num
    def get_ballot_num_id(self):
        return self.accepted_num_id
    def get_depth(self):
        return self.depth
    def get_accepted_num(self):
        return self.accepted_num
    def get_accept_val(self):
        return self.accepted_val
    
# class Proposal:
#     def __init__(self, operation, username, title, content):
#         self.operation = operation
#         self.username = username
#         self.title = title
#         self.content = content
   
class Paxos:
    def __init__(self, id):
        self.id = id #PID
        self.ballot_num = 0
        self.ballot_num_id = None
        self.depth = 0
        self.accepted_ballot_num = -1
        self.accepted_ballot_num_id = None # this num from who
        self.accepted_value = None 
        self.proposal = []
    
    def __str__(self):
        return (f"self.id:{self.id}\nself.ballot_num:{self.ballot_num}\nself.ballot_num_id:{self.ballot_num_id}\nself.depth:{self.depth}\n") + \
                (f"self.accepted_ballot_num:{self.accepted_ballot_num}\nself.accepted_ballot_num_id:{self.accepted_ballot_num_id}\n") + \
                (f"self.accepted_value:{self.accepted_value}\nself.proposal:{self.proposal}\n")
            
    def get_id(self):
        return self.id

    def get_proposal(self):
        # return f"{self.proposal.operation} {self.proposal.username} {self.proposal.title} {self.proposal.content}"
        return self.proposal

    def add_proposal(self, command):
        self.proposal = command

    def prepare(self):
        self.ballot_num += 1
        print(f"{self.id} sent: {PREPARE} <{self.ballot_num},{self.id}>")
        # return Message(PREPARE, ballot_num=self.ballot_num, ballot_num_id=self.id, sender=self.id)
        return Message(PREPARE, ballot_num=self.ballot_num, ballot_num_id=self.id)

    def receive_prepare(self, message):
        # if here is P2's terminal now:
        # Receive from P1: PREPARE <1,P1>
        print(f"Receive from {message['ballot_num_id']}: {message['msg_type']} <{message['ballot_num']},{message['ballot_num_id']}>")
        # msg is dict() type
        if message['ballot_num'] >= self.ballot_num or \
            ((message['ballot_num'] == self.ballot_num and int(message['ballot_num_id'][1:]) > int(self.id[1:]))):
            self.ballot_num = message['ballot_num']
            self.ballot_num_id = message['ballot_num_id']

            print(f"{self.id} sending back to {message['ballot_num_id']}: {PROMISE} <{self.ballot_num},{self.ballot_num_id}> <{self.accepted_ballot_num},{self.accepted_ballot_num_id}> {self.accepted_value}")
            return Message(PROMISE, ballot_num=self.ballot_num, ballot_num_id=self.ballot_num_id,
                            accepted_num=self.accepted_ballot_num, accepted_num_id=self.accepted_ballot_num_id,
                            accepted_val=self.accepted_value,
                            sender=self.id)
        else:
            return None  # reject

    def update_my_accepted_value(self, highest_b_message=None, accepted_ballot_num=None, accepted_ballot_num_id=None):
        if highest_b_message == None and accepted_ballot_num == None and accepted_ballot_num_id == None:
            self.ballot_num_id = self.id
            self.accepted_ballot_num = self.ballot_num
            self.accepted_ballot_num_id = self.id
            self.accepted_value = self.proposal # it's a list here
        else:
            self.accepted_ballot_num = accepted_ballot_num
            self.accepted_ballot_num_id = accepted_ballot_num_id
            self.accepted_value = highest_b_message

    def received_majority_promise(self): # TODO:need to add more
        print(f"{self.id} sent: {ACCEPT} <{self.accepted_ballot_num},{self.accepted_ballot_num_id}> '{self.get_proposal()}'")
        return Message(ACCEPT, accepted_num=self.accepted_ballot_num, accepted_num_id=self.accepted_ballot_num_id, accepted_val=self.get_proposal(), sender=self.id)
        # P1 will receive from all other servers PROMISE msg.
        # eg: Received from P5: PROMISE <1,P1> None None
        # print(f"Received from {message['sender']}: {message['msg_type']} <{message['ballot_num']},{message['id']}> {message['accepted_num']} {message['accepted_val']}")
        # if message['ballot_num'] >= self.ballot_num:
        #     if message.get_accept_val() is not None:
        #         if self.accepted_num is None or message.get_accepted_num() > self.accepted_num:
        #             self.accepted_num = message.get_accepted_num()
        #             self.accepted_value = message.get_accept_val()
        # else:
        #     return None # reject, need check

    def received_majority_accepted(self,accepted_value=None):
        if accepted_value is not None:
            self.accepted_value = accepted_value
        print(f"{self.id} sent: {DECIDE} <{self.ballot_num},{self.ballot_num_id}> '{self.accepted_value}'")
        return Message(DECIDE, ballot_num=self.ballot_num, ballot_num_id=self.ballot_num_id, accepted_val=self.accepted_value, sender=self.id)

    def receive_accept(self, message):
        print(f"Receive from {message['sender']}: {message['msg_type']} <{message['accepted_num']},{message['accepted_num_id']}> {message['accepted_val']}")
        if message['accepted_num'] >= self.ballot_num or \
            ((message['accepted_num'] == self.ballot_num and int(message['accepted_num_id'][1:]) > int(self.id[1:]))):
            self.ballot_num = message['accepted_num']
            self.ballot_num_id = message["accepted_num_id"]
            self.accepted_ballot_num = message['accepted_num']
            self.accepted_ballot_num_id = message['accepted_num_id']
            self.accepted_value = message['accepted_val']
            # print(f"{self.id} sending back to {message['id']}: {PROMISE} <{self.ballot_num},{self.accepted_num_id}> {self.accepted_ballot_num} {self.accepted_value}")
            print(f"{self.id} sending back to {message['sender']}: {ACCEPTED} <{self.accepted_ballot_num},{self.accepted_ballot_num_id}> '{self.accepted_value}'")
            return Message(ACCEPTED, accepted_num=self.accepted_ballot_num, accepted_num_id=self.accepted_ballot_num_id, accepted_val=self.accepted_value, sender=self.id)
        else:
            return None  # reject
    
    def clear(self):
        self.accepted_ballot_num = -1 
        self.accepted_ballot_num_id = None # this num from who
        self.accepted_value = None
        self.proposal = []

if __name__ == '__main__':
    exit()
    