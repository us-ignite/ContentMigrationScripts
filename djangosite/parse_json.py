import json, pprint

IMPORT_FILE = 'website.json'

def print_models(data):
    models = set()
    for item in data:
        models.add(item['model'])
    print (models)

def parse_userinfo(data):
    for item in data:
        if item["model"] == "profiles.user":
            print(item['pk'], item['fields']['email'])

def load_website_data():
    with open(IMPORT_FILE) as f:
        data = json.load(f)
        print_models(data)

if __name__ == "__main__":
    load_website_data()