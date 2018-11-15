Overview
========

This is just a small set of script for migrating content for the US Ignite website.

Running a Test Wordpress with Docker
------------------------------------

protip - you'll need docker installed.  :)

To spin up a Wordpress site to test these scripts just use the included docker-compose file to create a temp
installation.

To start up containers.
```
docker-compose up -d
```
Just open up the a web browser to localhost:8000 to see a site.  Note that as a test site, this will be a completely
fresh install of wordpress each time you start (that's kind of the point of it)

To shut down and remove containers
```
docker-compose down
```

Setting Up Anaconda
-------------------

If you use Anaconda Navigator, the dependencies for these scripts aren't in conda so you'll need to  install them via pip.

First install pip in your conda environment.  Note run from your normal command line and **not** with the environment activated.

 > conda install pip
 
 Then open a terminal from Anaconda Navigator for that environment.  From the project root pip install the dependencies in the requirements file like so:
 
 > pip install -r requirements.txt
 
 
Setting up other environments
-----------------------------

If you're using some other venv system just set that up as you need and use the pip install and install the dependencies from requirements.txt in your environment.

Executing the import
--------------------

With an appropriate environment started (i.e. if Anaconda, start a terminal for the environment you installed the dependencies to), navigate to the root directory of this project.

Make sure you've started the docker instances for the test wordpress sites as above and wait 30 seconds or so for the CLI to to provision the site.


You just need to specify the json file to import from in the command line like so:

> python main.py website.json