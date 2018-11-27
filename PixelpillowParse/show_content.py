# Small test script to examine the structure of the pixel pillow content coming from the docker containers.

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods.posts import GetPosts
import argparse


class WPContentReader:

    API = None

    def __init__(self, api_user, api_pw):
        self.API = Client('http://us-ignite.local/xmlrpc.php', api_user, api_pw)

    def read_posts(self):
        posts = self.API.call(GetPosts())
        for post in posts:
            print(post)

    def read_pages(self):
        pass


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("username", help="WP Username to connect to the API")
    arg_parser.add_argument("password", help="WP User password to connect to the API")
    args = arg_parser.parse_args()
    wp = WPContentReader(args.username, args.password)
    wp.read_posts()