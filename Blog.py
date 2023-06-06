# CS171 Final Project, June 2023
# Blog.py
# Author: Wenjin Li

class Post:
    def __init__(self, username, title, content):
        self.authorNtitle = (username, title)
        self.content = content

        self.comment = dict()

    def __str__(self): # need add print comments
        return f" Author: {self.authorNtitle[0]}\n  \
                   Title: {self.authorNtitle[1]}\n\
                 Content: {self.content}"

    def get_authorNtitle(self):
        return self.authorNtitle
    
    def get_content(self):
        return str(self.content)
    
    def get_comment(self):
        print(f"Looking for the comment in {self.authorNtitle[0]}---{self.authorNtitle[1]}...")
        if len(self.comment) == 0:
            print("\tThis post has no comment yet.\n")
            return
        for each_comment in self.comment:
            print(f"\t{each_comment[0]}: {each_comment[1]}") 
        print()
    
    def add_comment(self, follower, new_content):
        if (follower,new_content) in self.comment:
            print(f"Error! This comment already existed:\n\t{follower}: {new_content}\n")
            return
        self.comment[(follower,new_content)] = True

class Blog:
    def __init__(self):
        self.blog_list = dict()

    def makeNewPost(self, new_post):
        assert isinstance(new_post,Post)
        assert isinstance(new_post.get_authorNtitle(), tuple)

        if new_post.get_authorNtitle() in self.blog_list:
            print(f"Error on making a new post on {new_post.get_authorNtitle()}: ")
            print("\tthis author already has a post with the same title!\n")
            return
        self.blog_list[new_post.get_authorNtitle()] = new_post

    def get_posts_by_author(self, author):
        assert isinstance(author, str)
        found = False
        print(f"Looking for all the post from {author}...")
        for authorNtitle, post in self.blog_list.items():
            if author == authorNtitle[0]:
                print(f"\t{authorNtitle[1]}: {post.get_content()}")
                found = True
        if not found:
            print("\tThis user/author has not any post yet!")
        print()

    def get_post(self, authorNtitle):
        assert isinstance(authorNtitle, tuple)

        if authorNtitle not in self.blog_list:
            print(f"Error, Post not found with: \
                   '{authorNtitle[0]}', '{authorNtitle[1]}'")
            return
        return self.blog_list[authorNtitle]

    # def size(self):
        # return len(self.blog_list)

    def __str__(self):
        # return [x in self.blog_list for all]
        return str(self.blog_list)

    def view_all_posts(self):
        print("|author|-------|title|")
        for authorNtitle in self.blog_list:
            print(f"\t{authorNtitle[0]}-------{authorNtitle[1]}")
        # return self.blog_list
        print()


if __name__  == '__main__':
    blog = Blog()
    post1 = Post('Marcus','Answer for the final exam', 'ABCDEFG')
    post2 = Post('bob','title bob', 'cotent from bob')
    post3 = Post('Marcus','Answer2 for the final exam', 'ZXCVB')
    post4 = Post('Marcus','Answer3 for the final exam', 'BMNJL')
    post5 = Post('Marcus','Answer3 for the final exam', 'BMNJL')
    blog.makeNewPost(post1)
    blog.makeNewPost(post2)
    blog.makeNewPost(post3)
    blog.makeNewPost(post4)
    blog.makeNewPost(post5)
    # print(blog)
    blog.view_all_posts()

    # post1.add_comment(follower="bob",new_content="good post!")
    # post1.add_comment(follower="pop",new_content="good post!!")
    # post1.add_comment(follower="opo",new_content="good post!!!")
    # post1.get_comment()


    
    # try:
    #     blog.get_post(('bob','title bob')).add_comment(follower="Marcus", new_content="goood!")
    # except Exception as e:
    #     print("Double the author and title again!!!\n")
        
    # try:
    #     blog.get_post(('bob','title 2ob')).add_comment(follower="Marcus", new_content="goood!")
    # except Exception as e:
    #     print("Double the author and title again!!!\n")


    # blog.get_post(('bob','title bob')).get_comment()



    blog.get_posts_by_author("Marcus")
    blog.get_posts_by_author("asda")
    print("Done!")

