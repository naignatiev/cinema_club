#!/bin/sh

python3 manage.py migrate
python3 manage.py collectstatic --no-input
python3 manage.py compilemessages -l ru -l en
python3 manage.py createsuperuser --no-input
uwsgi --ini uwsgi.ini
