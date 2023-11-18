#!/bin/bash

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
echo "parser app wait 30s..."

sleep 30
echo "Start parser app..."
python parser_app/main.py