# Small test script to examine the structure of the pixel pillow content coming from the docker containers.

from wordpress_xmlrpc import Client, InvalidCredentialsError
from wordpress_xmlrpc.methods.posts import GetPosts
import argparse

# PYhy1ANJwCSMLULpVUh

class WPContentReader:

    API = None

    def __init__(self, api_user, api_pw):
        self.set_api(api_user, api_pw)

    def set_api(self, user, pw):
        self.API = Client('http://us-ignite.local/xmlrpc.php', user, pw)

    def read_posts(self):
        posts = self.API.call(GetPosts({'post_type': 'application'}))
        for post in posts:
            print(post)

    def read_pages(self):
        pass


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("username", help="WP Username to connect to the API")
    arg_parser.add_argument("password", help="WP User password to connect to the API")
    args = arg_parser.parse_args()
    try:
        wp = WPContentReader(args.username, args.password)
        wp.read_posts()
    except InvalidCredentialsError as err:
        print(err, wp.API.username, wp.API.password)
