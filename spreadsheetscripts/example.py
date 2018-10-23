from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, GetPosts
from wordpress_xmlrpc.methods.taxonomies import GetTerms, GetTaxonomies
from slugify import slugify
import datetime, time

API = Client('http://localhost:8000/xmlrpc.php', 'admin', 'usignite')

# Example of adding a post
def add_post():
    post = WordPressPost()
    ts = time.time()
    title = 'Test Title' + datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    post.title = title
    post.content = 'This is a test post to see if the RPC call works.'
    post.terms_names = {
        'post_tag': ['test', 'firstpost'],
        'category': ['Introductions', 'Test']
    }
    post.slug = slugify(title) # note this if final part of slug only
    API.call(NewPost(post))

def list_posts():
    posts = API.call(GetPosts()) # Defaults to post_type: post
    for post in posts:
        print(post)

    apps = API.call(GetPosts({'post_type': 'apps'})) # Custom post type
    for app in apps:
        print(
            app.title,
            app.post_type,
            app.user,
            # app.terms_names,
            app.custom_fields
        )
        for term in app.terms:
            print(" - ", term.taxonomy, term.name, term.group, term.taxonomy_id)

def list_terms():
    taxonomies = API.call(GetTaxonomies())
    for taxonomy in taxonomies:
        print(taxonomy)
    terms = API.call(GetTerms('communities'))
    for term in terms:
        print("  - ", term.id, term.taxonomy, term.name)


if __name__ == "__main__":
    list_posts()
    print('---------------------')
    list_terms()