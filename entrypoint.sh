#!/bin/sh

python manage.py migrate
python manage.py loaddata data/users.json data/polls-v4.json data/votes-v4.json
python manage.py createsuperuser --username admin --email admin@example.com --noinput
python manage.py runserver 0.0.0.0:8000
