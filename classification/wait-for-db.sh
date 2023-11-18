#!/bin/sh

# Параметры подключения к БД
host="$1"
shift
cmd="$@"

# Функция для проверки доступности БД
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"
exec $cmd