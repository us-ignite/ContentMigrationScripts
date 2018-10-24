import json
from pprint import pprint


IMPORT_FILE = 'website.json'


def get_models(content):
    models = set()
    for item in content:
        models.add(item['model'])
    return models


def get_all_user_data(content):
    users = []
    for item in content:
        if item["model"] == "profiles.user":
            users.append(item)
    return users


def get_ignite_user_data(content):
    users = []
    for item in content:
        if item["model"] == "profiles.user" and "us-ignite.org" in item['fields']['email']:
            users.append(item)
    return users


def get_blogposts(content):
    posts = []
    for item in content:
        if item['model'] == 'blog.blogpost':
            posts.append(item)
    return posts

def get_blogcatagories(content):
    catagories = []
    for item in content:
        if item['model'] == 'blog.blogcategory':
            catagories.append(item)
    return catagories


def get_applications(content):
    applications = []
    for item in content:
        if item['model'] == 'apps.application':
            applications.append(item)
    return applications


def load_website_data():
    with open(IMPORT_FILE) as f:
        datadump = json.load(f)
        return datadump


def get_tags(content):
    tags = []
    for item in content:
        if item['model'] == 'taggit.taggeditems':
            tags.append(item)
    return tags


def get_app_sectors(content):
    sectors = []
    for item in content:
        if item['model'] == 'apps.sector':
            sectors.append(item)
    return sectors


def get_app_features(content):
    features = []
    for item in content:
        if item['model'] == 'apps.feature':
            features.append(item)
    return features


def get_app_urls(content):
    urls = []
    for item in content:
        if item['model'] == 'apps.applicationurl':
            urls.append(item)
    return urls


def _print_ignite_users(content):
    users = get_ignite_user_data(content)
    for user in users:
        print(user['fields']['email'])


def _duplicate_app_urls(content):
    app_pk = []
    for item in content:
        if item['model'] == 'apps.applicatinurl':
            if item['fields']['application'] in app_pk:
                print("App Exists")
            app_pk.append(item['fields']['application'])


def get_application_catagories(content):
    catagories = set()
    for item in content:
        if item['model'] == 'apps.application':
            for entry in item['fields']['categories']:
                catagories.add(entry)
    return catagories


def get_app_media(content):
    media_list = []
    for item in content:
        if item['model'] == 'apps.applicationmedia':
            media_list.append(item)
    return media_list


if __name__ == "__main__":
    data = load_website_data()
    pprint(get_blogcatagories(data))
    for post in get_blogposts(data):
        if post['fields']['categories']:
            pprint(post)