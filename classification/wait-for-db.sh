#!/bin/bash

# Параметры подключения к БД
host="$1"
shift
cmd="$@"

# Функция для проверки доступности БД
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

>&2 echo "PostgreSQL is up - executing command"
exec $cmd