import json
from pprint import pprint

IMPORT_FILE = 'website.json'

def get_models(data):
    models = set()
    for item in data:
        models.add(item['model'])
    return models

def get_all_user_data(data):
    users = []
    for item in data:
        if item["model"] == "profiles.user":
            users.append(item)
    return users

def get_ignite_user_data(data):
    users = []
    for item in data:
        if item["model"] == "profiles.user" and "us-ignite.org" in item['fields']['email']:
            users.append(item)
    return users

def get_blogposts(data):
    posts = []
    for item in data:
        if item['model'] == 'blog.blogpost':
            posts.append(item)
    return posts

def get_applications(data):
    applications = []
    for item in data:
        if item['model'] == 'apps.application':
            applications.append(item)
    return applications

def load_website_data():
    with open(IMPORT_FILE) as f:
        data = json.load(f)
        return data

def get_tags(data):
    tags = []
    for item in data:
        if item['model'] == 'taggit.taggeditems':
            tags.append(item)
    return tags

def get_app_sectors(data):
    sectors = []
    for item in data:
        if item['model'] == 'apps.sector':
            sectors.append(item)
    return sectors

def get_app_features(data):
    features = []
    for item in data:
        if item['model'] == 'apps.feature':
            features.append(item)
    return features


def _print_ignite_users(data):
    users = get_ignite_user_data(data)
    for user in users:
        print(user['fields']['email'])

def get_application_catagories(data):
    catagories = set()
    for item in data:
        if item['model'] == 'apps.application':
            for entry in item['fields']['categories']:
                catagories.add(entry)
    return catagories

if __name__ == "__main__":
    data =  load_website_data()
    features = get_app_features(data)
    for feature in features:
        print ("%d: '%s'," % (feature['pk'], feature['fields']['name']))