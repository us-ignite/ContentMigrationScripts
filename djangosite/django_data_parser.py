import json
from pprint import pprint


IMPORT_FILE = 'website.json'


def load_website_data():
    with open(IMPORT_FILE) as f:
        datadump = json.load(f)
        return datadump


def get_models(content):
    models = set()
    for item in content:
        models.add(item['model'])
    return models


def get_ignite_user_data(content):
    users = []
    for item in get_content(content, 'profiles.user'):
        if "us-ignite.org" in item['fields']['email']:
            users.append(item)
    return users


def _print_ignite_users(content):
    users = get_ignite_user_data(content)
    for user in users:
        print(user['fields']['email'])


def get_application_catagories(content):
    categories = set()
    for item in get_content(content,'apps.application'):
        for entry in item['fields']['categories']:
            categories.add(entry)
    return categories


def get_content(content, model):
    items = []
    for item in content:
        if item['model'] == model:
            items.append(item)
    return items

if __name__ == "__main__":
    data = load_website_data()
    for hub in get_content(data, 'hubs.hub'):
        pprint(hub)

