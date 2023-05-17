# CS171 Final Project

## Week 1

branch/blog
Implement blog functionality for single client

Inputs:
post(username, title, content): issue a Post operation for creating a new blog post authored under username with the given title and content
comment(username, title, content): issue a Comment operation for creating a new comment authored under username with content for the blog post with title blog: print a list of the title of all blog posts in chronological order. If there are no blog posts, print “BLOG EMPTY” instead
view(username): print a list of the title and content of all blog posts authored under username in chronological order. If there are no posts authored under username, print “NO POST” instead
read(title): print the content of the blog post with title, and the list of comments for the post with their respective authors in chronological order. If a post with title doesn’t exist, print “POST NOT FOUND” instead

Outputs:
“NEW POST <title> from <username>”: output when a node successfully applies a decided Post operation to its blog. If a blog post with title already exists, the node should print “DUPLICATE TITLE” instead without creating any post
“NEW COMMENT on <title> from <username>”: output when a node applies a Comment operation to its blog. if a blog post with title does not exist, the node should print “CANNOT COMMENT” instead without creating any comment
“PREPARE/PROMISE/ACCEPT/ACCEPTED/DECIDE <ballot num>”: clearly indicate in console output whenever a protocol-related message is sent or received. You should include sender/recipient information and any additional information associated with these messages
“TIMEOUT”: output when an acceptor times out on waiting for the leader to decide on the operation it forwarded

branch/connect
5 'servers' interconnect
support blog functions
dummy leader election
replicated log

## Week 2

Leader election
Multi-Paxos consensus between servers

## Week 3

Crash failure & disk recovery
Network partition
Protocol relayed interface:
crash, failLink(dest), fixLink, blockchain, queue
Repair from other nodes
