# образ на основе которого создаём контейнер
FROM python:3.9-slim

RUN mkdir /site


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ADD . /site

WORKDIR /site
RUN chmod +x ./entrypoint.sh
