from wordpress_xmlrpc import Client, WordPressPost, WordPressTerm
from xmlrpc.client import Fault
from csv import DictReader
from wordpress_xmlrpc.methods.posts import NewPost, GetPosts
from wordpress_xmlrpc.methods.taxonomies import GetTerms, GetTaxonomies, GetTaxonomy, NewTerm
from slugify import slugify
import datetime, time, re

# All of this is just throw away code I'm keeping from when I was experimenting with the
# wordpress api.  Keeping it here for reference for later.

try:
    API = Client('http://localhost:8000/xmlrpc.php', 'admin', 'usignite')
except:
    pass

def html_format(content):
    content = replace_url_to_link(content)
    return '<p>' + content + '</p>'

def parse_communitylist(filename):
    """
    Parses the CSV export of communities list from the Status Spreadsheet

    :param filename: string of the file to parse
    :return:
    """
    communities = []
    with open(filename) as csvfile:
        reader = DictReader(csvfile)
        if reader:
            for row in reader:
                communities.append({
                    'name': row['COMMUNITY']
                })
    return communities

def parse_applist(filename):
    """
    Prase the CSV export of the apps list from the tech status spreadsheet.

    :param filename: string of the file to parse.
    :return:
    """
    apps = []
    with open(filename) as appfile:
        reader = DictReader(appfile)
        if reader:
            for row in reader:
                apps.append(row)
    return apps

def replace_url_to_link(text):
    # Replace url to link
    urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE|re.UNICODE)
    text = urls.sub(r'<a href="\1" target="_blank">\1</a>', text)
    # Replace email to mailto
    urls = re.compile(r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)", re.MULTILINE|re.UNICODE)
    text = urls.sub(r'<a href="mailto:\1">\1</a>', text)
    return text

def import_terms(taxonomy_name, terms=[]):
    """
    Imports a list of terms provided into a particular taxonomy.  If the term already exists, the import skips it.

    :param taxonomy_name: string of taxonomy name.
    :param terms: list of strings of terms
    :return:
    """
    taxonomy = API.call(GetTaxonomy(taxonomy_name))
    for item in terms: # raises xmlrpc.client.Fault error if term exists
        try:
            term = WordPressTerm()
            term.taxonomy = taxonomy.name
            term.name = item
            API.call(NewTerm(term))
        except Fault as err:
            print("error inserting %s: %s" % (item, err))

def import_application(data):
    """
    Creates an Application post from a spreadsheet row.

    :param data: Dict of imported row from csv via DictReader
    :return:
    """
    for app in data:
        post = WordPressPost()
        post.post_status = 'publish'
        post.title = app['Application'].strip()
        post.slug = slugify(post.title)
        post.post_type = 'apps'

        # Compile post body
        content = html_format(app['Description'])
        if app['CCX']:
            content += html_format('CCX Page:' + app['CCX'])
        if app['Website']:
            content += html_format('Website: ' + app['Website'])
        if app['POC']:
            content += html_format('Contact: ' + app['POC'])
        if content:
            post.content = content

        terms = {}
        # Community terms
        community = []
        if app['SGC']:
            community.append(app['SGC'])
        if community:
            terms['communities'] = community

        # Status Terms
        status = []
        if app['Status']:
            status.append(app['Status'])
        if app['Sharing'] == 'Shareable':
            status.append(app['Sharing'])
        if status:
            terms['status'] = status

        # General Tags
        tags = []
        if app['Priority Area']:
            tags.append(app['Priority Area'])
        if tags:
            terms['post_tag'] = tags

        if terms:
            post.terms_names = terms

        API.call(NewPost(post))

if __name__ == "__main__":

    # Import Communities as terms
    communities = parse_communitylist('communities.csv')
    if communities:
        import_terms('communities', [community['name'] for community in communities])

    # Import App information
    apps = parse_applist('applist.csv')
    status = set()
    for app in apps:
        if app['Status']:
            status.add(app['Status'])
        if app['Sharing'] == 'Shareable':
            status.add(app['Sharing'])
    if status:
        import_terms('status', status)
    import_application(apps)
