# Тестовое задание

Сервис предоставляющий API для аналитики по сайту meduza.io.

## Используемые технологии

1. Django 1.10
2. rest_framework
3. Celery 4.0 (брокер rabbitMQ)
4. PostgreSQL

## Установка и запуск

Создать виртуальную среду c python 3.4:

    virtualenv -p /usr/bin/python3. venv
    source venv/bin/activate

Клонировать репозиторий:

    git clone https://github.com/elBroom/analytics_news.git
    cd analytics_news

Установить зависимости:

    pip install -r requirements.txt

Создать базу данных и пользователя:

    sudo -u postgres psql
    psql
    CREATE DATABASE database_name;
    CREATE USER database_user WITH PASSWORD 'database_password';
    GRANT ALL PRIVILEGES ON DATABASE database_name TO database_user;
    \q

В settings.py изменить настройки БД:

    DATABASES = {
    ....
        'NAME': 'database_name',
        'USER': 'database_user',
        'PASSWORD': 'database_password',
    ....
    }

Установить миграцию:

    python manage.py migrate

Создать супер пользователя:

    python manage.py createsuperuser

Запустить rabbitMQ и celery:

    sudo service rabbitmq-server start
    celery -A analytics_news beat -l info -S django
    celery -A analytics_news worker -l info

Запустить сервер:

    python manage.py runserver

Доступные методы:

    #login
        In: username, password
        Out: token
        
    #logout
        In: token
        
    #source_list
        In: start_date, end_date - промежуток
        Out: name - название источника, count_ref - количество ссылок, ratio - количество ссылок/общее количество новостей
    
    #news_list
        In: source - источник, start_date, end_date - промежуток
        Out: title, url, pub_date

Доступ к методам:

    Формат даты: Y-m-d
    login: curl -u username:password -X POST http://localhost:8000/login/
    logout: curl -X POST http://127.0.0.1:8000/logout/ -H 'Authorization: Token <your_token>'
    source_list: curl -X GET http://127.0.0.1:8000/source_list/?start_date=2016-11-20\&end_date=2016-11-25 -H 'Authorization: Token <your_token>'
    news_list: curl -X GET http://127.0.0.1:8000/news_list/?source=Meduza\&start_date=2016-11-20\&end_date=2016-11-25 -H 'Authorization: Token <your_token>'
