#!/bin/sh
chmod +x entrypoint.sh
if [ "$DATABASE" = "postgres" ]
then
    # если база еще не запущена
    echo "DB not yet run..."

    # Проверяем доступность хоста и порта
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 0.2
    done

    echo "DB did run."
fi
python manage.py makemigrations
python manage.py migrate

if [ ! -f "db_loaded.txt" ]; then
    python manage.py loaddata db.json
    touch db_loaded.txt
fi 

gunicorn  site_main.wsgi:application --bind 0.0.0.0:8000
exec "$@"