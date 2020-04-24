run -- directory which contains runtime data, like static files, sockets, etc..
doc -- folder to keep documentation
log -- all loggers should write to files in this folder
env -- env
src -- django root


setup environments
    goto root level
    python3 -m venv env
    source env/bin/activate
    pip install --upgrade pip
    pip install -r /path/to/requirements.txt

DB setup for site
https://www.digitalocean.com/community/tutorials/how-to-create-a-django-app-and-connect-it-to-a-database
CURRENT VERSION OF PYTHON 3.7.1 adjust doc based on this