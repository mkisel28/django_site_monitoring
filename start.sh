#!/bin/bash

python site_main/manage.py migrate
if [ ! -f "db_loaded.txt" ]; then
    python site_main/manage.py loaddata site_main/db.json
    touch db_loaded.txt
fi
python site_main/manage.py runserver 0.0.0.0:8000