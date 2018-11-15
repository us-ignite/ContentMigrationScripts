from wordpress_xmlrpc import Client, WordPressPost, WordPressPage
from wordpress_xmlrpc.methods.posts import NewPost
from xmlrpc.client import Fault
from datetime import datetime
import djangosite.django_data_parser as dp
from pprint import pprint
import argparse

# Based on model data definition from https://github.com/us-ignite/us-ignite/blob/master/us_ignite/apps/models.py
APPLICATION_STAGE = {
    1: 'idea',
    2: 'prototype',
    3: 'development',
    4: 'commercialized'
}

# Based on parsing data in apps.sectors
APPLICATION_SECTORS = {
    1: 'Healthcare',
    2: 'Education & Workforce',
    3: 'Energy',
    4: 'Transportation',
    5: 'Advanced Manufaturing',
    6: 'Public Safety',
    7: 'Other'
}

APPLICATION_FEATURES = {
    1: 'SDN',
    2: 'OpenFlow',
    5: 'Low-latency',
    6: 'Local cloud / edge computing',
    7: 'Advanced wireless',
    8: 'Ultra-fast/Gigabit to end-user',
    9: 'GENI/US Ignite Rack',
    10: 'Layer 2',
    11: 'Cloud Computing',
    12: 'Data Visualization',
    13: 'Data Mobility',
    14: 'App Chaining and Resource Brokering',
    15: 'Cloud workflow composition',
    16: 'Virtual desktops and HPC ',
    17: 'Layer 2 networking for real-time collaboration',
    18: 'Accounting service to price Apps',
    19: 'GENI Rack integration for Manufacturing Cyber Workspace',
    20: 'Sensor platform',
    21: 'Interactive Query Builder',
    22: 'Census API Aliasing',
    23: 'Combining Multiple Modules',
    24: 'Distributed Computing'
}

DJANGO_DATA = None
DJANGO_PAGE_LIST = {}
WORDPRESS_USERS = []  # List of WordPressUser objects.


API = Client('http://localhost:8000/xmlrpc.php', 'admin@us-ignite.org', 'usignite')


def import_applications(content):
    app_urls = {}
    for url in dp.get_content(content, 'apps.applicationurl'):
        app_urls[url['fields']['application']] = url

    for item in content:
        if item['model'] == 'apps.application':
            _add_application(item)


def _add_application(app_data):
    '''
    Adds an application parse from apps.application

    :param app_data: Python dict of application structure. See modelsamples/application_sample.txt
    :return:
    '''
    post = WordPressPost()
    post.title = app_data['fields']['name']
    post.slug = app_data['fields']['slug']
    post.content = _format_app_content(app_data)
    post.date = _return_datetime(app_data['fields']['created'])
    post.date_modified = _return_datetime(app_data['fields']['updated'])
    # TODO add link to original listing
    # TODO assign to proper taxonomies once those are in.
    # TODO decide what to do with remaining media (likely toss)

    # Assign Author
    if app_data['fields']['owner']:
        wp_userid = _get_wordpress_user_id_by_email(_get_django_user_email_by_id(app_data['fields']['owner']))
        if wp_userid:
            post.user = wp_userid

    # Assign Categories and Tags
    post.terms_names = _parse_taxonomies(app_data)

    # Put the previous page url in a custom field.
    legacy_url = "https://www.us-ignite.org/apps/%s/" % (app_data['fields']['slug'])
    post.custom_fields = [
        {'key': 'legacy_url', 'value': legacy_url}
    ]

    # Set publish status and push to site
    if app_data['fields']['status'] == 1:
        post.post_status = 'publish'
    try:
        if app_data['fields']['status'] != 3:
            post.id = API.call(NewPost(post))
    except Fault as err:
        pprint(post, err.faultString)


def _parse_taxonomies(app_data):
    terms = {
        'category': ['Application'],
        'post_tag': []
    }
    hub = _get_hub_byid(app_data['fields']['hub'])
    if hub:
        terms['post_tag'].append(hub)
    if app_data['fields']['sector']:
        terms['post_tag'].append(APPLICATION_SECTORS[app_data['fields']['sector']])
    if app_data['fields']['status']:
        terms['post_tag'].append(APPLICATION_STAGE[app_data['fields']['status']])
    return terms


def _get_hub_byid(hub_id):
    for hub in dp.get_content(DJANGO_DATA, 'hubs.hub'):
        if hub['pk'] == hub_id:
            return hub['fields']['name']
    return None

def _format_app_content(app_data):
    '''
    Concatinates several previous fields into a single post body

    :param app_data: Python dict of application structure. See modelsamples/application_sample.txt
    :return:
    '''
    content = _content_start(app_data)

    content += _wrap_tag(app_data['fields']['summary'])
    content += _wrap_tag(app_data['fields']['impact_statement'])

    # If an acknowlegement exists, add that.
    if app_data['fields']['acknowledgments']:
        ackknowlegement_text = _wrap_tag('Acknowledgments:', 'strong')
        ackknowlegement_text += " %s" % app_data['fields']['acknowledgments']
        content += _wrap_tag(ackknowlegement_text)

    # If team information is there, add that.
    if app_data['fields']['team_name'] or app_data['fields']['team_description']:
        team_text = _wrap_tag("Team Information:", 'strong')
        if app_data['fields']['team_name'] :
            team_text += " " + app_data['fields']['team_name'] + ","
        if app_data['fields']['team_description']:
            team_text += " " + app_data['fields']['team_description']
        content += team_text

    # Merging links from apps.application.fields.website and apps.applicationurl
    links = []
    if app_data['fields']['website']:
        links.append(
            _wrap_tag('<a href="%s" target="blank">Project Homepage</a>' % (app_data['fields']['website']), 'li')
        )

    for item in dp.get_content(DJANGO_DATA, 'apps.applicationurl'):
        if item['fields']['application'] == app_data['pk']:
            links.append(
                _wrap_tag('<a href="%s" target="blank">%s</a>' % (
                    item['fields']['url'],
                    item['fields']['name']
                ),
                          'li')
            )

    if links:
        content += _wrap_tag('Project Links', 'h3')
        content += _wrap_tag(''.join(links), 'ul')
    return _clean_text(content)


def _content_start(app_data):
    '''
    This parses the application media associated with the application and determines if there is a embedded video
    that can start the content, otherwise returns a blank string.

    :param app_data:
    :return: Media embed string or blank string
    '''
    def _get_pk(elm): # sorting function for list sort below.
        return elm['pk']

    media_list = []
    for item in dp.get_content(DJANGO_DATA, 'apps.applicationmedia'):
        if item['fields']['application'] == app_data['pk']:
            media_list.append(item)
    media_list.sort(key=_get_pk)

    content = []
    for item in media_list:
        if item['fields']['url']:
            content.append('[embed]%s[/embed]' % item['fields']['url'])

    return '\n'.join(content) or ''


def _get_django_user_email_by_id(id):
    email = None
    for user in dp.get_content(DJANGO_DATA, 'profiles.user'):
        if user['pk'] == id:
            email = user['fields']['email']
    return email


def _get_wordpress_user_id_by_email(email):
    id = None
    for user in WORDPRESS_USERS:
        if user.email == email:
            id = user.id
    return id


def import_blogposts(content):
    for post in dp.get_content(content, 'blog.blogpost'):
        _add_blogpost(post)

def _add_blogpost(post_data):
    '''
    Adds a blog post parsed from blog.blogpost

    Model published status codes are as follows:  PUBLISHED = 1, DRAFT = 2, DELETED = 3

    :param post_data: Python dict of post structure.  See modelsamples/blogpost_sample.txt for structure.
    :return:
    '''
    post = WordPressPost()
    post.title = post_data['fields']['title']
    post.content = post_data['fields']['content']
    post.date = _return_datetime(post_data['fields']['publish_date'])
    post.date_modified = _return_datetime(post_data['fields']['updated'])
    post.slug = post_data['fields']['slug']
    if post_data['fields']['status'] == 2:
        post.post_status = 'publish'
    # Assign Author
    if post_data['fields']['user']:
        wp_userid = _get_wordpress_user_id_by_email(_get_django_user_email_by_id(post_data['fields']['user']))
        if wp_userid:
            post.user = wp_userid
    # TODO set catagories and tags to proper taxonomy
    post.terms_names = {
        'category': ['Blogpost']
    }
    if post_data['fields']['categories']:
        categories = []
        for category in dp.get_content(DJANGO_DATA, 'blog.blogcategory'):
            if category['pk'] in post_data['fields']['categories']:
                categories.append(category['fields']['title'])
        post.terms_names['post_tag'] = categories
    try:
        if post_data['fields']['status'] != 3:
            post.id = API.call(NewPost(post))
            print("created post", post.id, post.title)
    except Fault as err:
        pprint(post)
        print(err.faultCode, err.faultString)


def import_pages(content):
    # Index page content to be references from metdata
    page_content = {item['pk']: item for item in dp.get_content(content,'pages.richtextpage')}
    # Iterate through page metadata to normalize with page content
    for item in dp.get_content(content, 'pages.page'):
        DJANGO_PAGE_LIST[item['pk']] = item
        if item['pk'] in page_content:
            DJANGO_PAGE_LIST[item['pk']]['fields']['content'] = page_content[item['pk']]['fields']['content']
        else:
            DJANGO_PAGE_LIST[item['pk']]['fields']['content'] = None
    for page in DJANGO_PAGE_LIST.values():
        _add_page(page)


def _add_page(page_data):
    page = WordPressPage()
    page.title = page_data['fields']['title']
    page.slug = page_data['fields']['slug']
    page.order = page_data['fields']['_order']
    page.date = _return_datetime(page_data['fields']['publish_date'])
    page.date_modified = _return_datetime(page_data['fields']['updated'])
    page.content = page_data['fields']['content']
    if page_data['fields']['status'] == 1:
        page.publish_status = 'publish'
    try:
        page.id = API.call(NewPost(page))
        print("created page", page.id, page.title)
    except Fault as err:
        pprint(page)
        print(err.faultCode, err.faultString)


def _return_datetime(item):
    d = datetime.utcnow()
    try:
        d = datetime.strptime(item, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        d = datetime.strptime(item, '%Y-%m-%dT%H:%M:%SZ')
    return d


def _clean_text(item):
    '''
    Text in this site is a mess, adding general text cleanup here as discovered and needed.

    :param item:
    :return:
    '''
    text = str(item)
    replace = ['\r', '\t', '\n']
    for element in replace:
        text.replace(element, "")
    return text


def _wrap_tag(item, tag='P'):
    text = str(item).strip()
    if not text.startswith(("<%s>", tag)):
        text = "<%s>%s</%s>" % (tag, text, tag)
    return text

def run_imports(importfile):
    global DJANGO_DATA
    DJANGO_DATA = dp.load_website_data(importfile)
    import_pages(DJANGO_DATA)
    import_applications(DJANGO_DATA)
    import_blogposts(DJANGO_DATA)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("import_file", help="Include the file to parse.")
#     args = parser.parse_args()
#     DJANGO_DATA = dp.load_website_data(args.import_file)
#     run_imports()
