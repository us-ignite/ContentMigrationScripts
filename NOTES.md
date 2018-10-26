# Notes

These are various notes on the content migration that we need to keep track of.

## Applications

### Media
There are 49 applications that include media in apps.applicationmedia and encompases a mixed set of YouTube videos and
static images.  The media is stored on the webserver in a cache of some sort and it will be easier to just enter these
by hand than it will be to write an import script.  It will also serve to let us take a more sensible pass on how media
is displayed in the final site.

## Pages
Notes that conent is pulled from pages.richtextpage but metadata about the page is actually pulled from pages.page

Page parent structure will need to be re-established by hand

## News
These are an implementation of the BlogPost model.  This is a one to one relationship so the pk of news.newspost matches the corresponding blogpost pk

### Need Discussion

* Reverse Pitches not migreated, these are not actually linked anywhere.
* Playbook listing, need to re-examine how we manage.