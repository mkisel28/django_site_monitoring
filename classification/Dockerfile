# Используйте официальный образ Python как базовый
FROM python:3.9

# Установите рабочую директорию в контейнере
WORKDIR /usr/src/classification

# Копируйте файлы зависимостей в контейнер и установите их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .

# Копирование скрипта ожидания БД и установка прав на его выполнение
COPY wait-for-db.sh /usr/wait-for-db.sh
RUN chmod +x /usr/wait-for-db.sh

# Использование скрипта ожидания БД перед запуском основного приложения
CMD ["/usr/wait-for-db.sh", "db", "python", "./main.py"]