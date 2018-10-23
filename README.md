Overview
========

This is just a small set of script for importing content into wordpress.

Running a Test Wordpress
------------------------

To spin up a Wordpress site to test these scripts just use the included docker-compose file to create a temp
installation.

To start up containers.
```
docker-compose up -d
```
Just open up the a web browser to localhost:8000 to see a site.  Note that as a test site, this will be a completely
fresh install of wordpress each time you start (that's kind of the point of it)

To shut down containers
```
docker-compose down
```

Other Notes
-----------

Plugins used for this test
- Page Builder by SiteOrigin
- SiteOrigin Widgets Bundle (recommended for Page Builder)
- Custom Post Type UI

Theme for testing:
- Polestar (setup for use with Page Builder plugin)

Setting up Custom Post Type UI
------------------------------

- Detail basic settings & Check the Settings > Supports options as needed.
    - Add Custom Post type for 'apps/Applications/Application', select Tags under Taxonomies
    - Set Settings > Show in REST API to True
    - Add appropriate taxonomies if they exist
- Setup Taxonomies
    - Add 'communities/Communities/Community'
    - Add 'status/Project Status/Project Status'
    - For checkbox select make sure Settings > Hierarchical is True

Notes on Windows 10
-------------------

*For local drives to work*

Control Panel > View network status and tasks > Change advanced sharing settings

 ... and make sure File Management settings are on.

*If you still can't get local drives to work*

This might be a problem with Norton or other 'smart' firewall software.  I had to uninstall docker, restart the machine,
reinstall docker, restart the machine and approve the rule when it autodetects.  Smart systems need to be a lot smarter.

*If a container wont start*

Sometimes on windows I would get an error like"

```
ERROR: for wordpress  Cannot start service wordpress: driver failed programming external connectivity on endpoint
wordpressscripts_wordpress_1 (5c1a6166df9aa217798a5ead92937b61d2dc0ef81c65b9c0a53b6c40bec9eb88): Error starting
userland proxy: mkdir /port/tcp:0.0.0.0:8000 :tcp:172.18.0.3:80: input/output error
````

Seems like you have to let windows start, manually shutdown docker and manually restart it to release ports properly.

