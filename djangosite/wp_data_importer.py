from wordpress_xmlrpc import Client, WordPressUser, WordPressPost, WordPressTerm
from wordpress_xmlrpc.methods.posts import NewPost, GetPosts, EditPost
from wordpress_xmlrpc.methods.users import GetUsers
from wordpress_xmlrpc.methods.taxonomies import GetTerms, GetTaxonomies, GetTaxonomy, NewTerm
from slugify import slugify
from xmlrpc.client import Fault
from datetime import datetime
import djangosite.django_data_parser as dp
from pprint import pprint

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

DJANGO_USERS = [] # List of django user models
DJANGO_BLOG_CATAGORIES = []
WORDPRESS_USERS = [] # List of WordPressUser objects.

try:
    API = Client('http://localhost:8000/xmlrpc.php', 'admin@us-ignite.org', 'usignite')
except:
    pass


def import_applications(content):
    app_urls = {}
    for url in dp.get_app_urls(content):
        app_urls[url['fields']['application']] = url

    for item in content:
        if item['model'] == 'apps.application':
            _add_application(item, app_urls)


def _add_application(app_data, app_urls):
    '''
    Adds an application parse from apps.application

    :param app_data: Python dict of application structure. See modelsamples/application_sample.txt
    :return:
    '''
    post = WordPressPost()
    post.title = app_data['fields']['name']
    post.slug = app_data['fields']['slug']
    post.content = _format_app_content(app_data, app_urls)
    post.date = _return_datetime(app_data['fields']['created'])
    post.date_modified = _return_datetime(app_data['fields']['updated'])
    # Assign Author
    if app_data['fields']['owner']:
        wp_userid = _get_wordpress_user_id_by_email(_get_django_user_email_by_id(app_data['fields']['owner']))
        if wp_userid:
            print("found user", wp_userid)
            post.user = wp_userid
    # catagories and tags
    if app_data['fields']['sector']:
        post.terms_names = {
            'category': [APPLICATION_SECTORS[app_data['fields']['sector']]]
        }

    if app_data['fields']['status'] == 1:
        post.post_status = 'publish'
    try:
        if app_data['fields']['status'] != 3:
            post.id = API.call(NewPost(post))
    except Fault as err:
        pprint(post)


def _format_app_content(app_data, app_urls):
    '''
    Concatinates several previous fields into a single post body

    :param app_data: Python dict of application structure. See modelsamples/application_sample.txt
    :return:
    '''
    content = ''
    # Add project url and homepage
    if app_data['pk'] in app_urls:
        project_text = _wrap_tag("Project Link:", 'strong')
        project_text += ' <a href="%s" target="blank">%s</a>' % (
            app_urls[app_data['pk']]['fields']['url'],
            app_urls[app_data['pk']]['fields']['name']
        )
        content += _wrap_tag(project_text)

    content += _wrap_tag(app_data['fields']['summary'])
    content += _wrap_tag(app_data['fields']['impact_statement'])

    # If an acknowlegement exists, add that.
    if app_data['fields']['acknowledgments']:
        ackknowlegement_text = _wrap_tag('Acknowlegements:', 'strong')
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
    return _clean_text(content)


def _get_django_user_email_by_id(id):
    email = None
    for user in DJANGO_USERS:
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
    for post in dp.get_blog_posts(content):
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
    if post_data['fields']['status'] == 1:
        post.post_status = 'publish'
    # Assign Author
    if post_data['fields']['user']:
        wp_userid = _get_wordpress_user_id_by_email(_get_django_user_email_by_id(post_data['fields']['user']))
        if wp_userid:
            print("found user", wp_userid)
            post.user = wp_userid
    # TODO set catagories and tags
    if post_data['fields']['categories']:
        catagories = []
        for category in DJANGO_BLOG_CATAGORIES:
            if category in post_data['fields']['categories']:
                catagories.append(category['fields']['name'])
        post.terms_names = {
            'category': catagories
        }
    try:
        if post_data['fields']['status'] != 3:
            post.id = API.call(NewPost(post))
            print("created post", post.id, post.title)
    except Fault as err:
        pprint(post)
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


if __name__ == "__main__":
    data = dp.load_website_data()
    DJANGO_USERS = dp.get_all_user_data(data)
    DJANGO_BLOG_CATAGORIES = dp.get_blog_catagories(data)
    WORDPRESS_USERS = API.call(GetUsers())
    import_blogposts(data)
