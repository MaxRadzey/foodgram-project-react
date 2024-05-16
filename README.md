# Проект «Foodgram»

## Содержание
- [Авторы](#авторы)
- [Описание](#описание)
- [Технологии](#технологии)
- [Как запустить проект](#Как-запустить-проект)
- [Примеры запросов к API](#Примеры-запросов-к-API)

##  Авторы

- [Maxim Radzey](https://github.com/MaxRadzey)

##  Описание
Проект Foodgram представляет собой сервис для публикации рецептов, добавления чужих рецептов в избранное и подписки на публикации других авторов. 

## Технологии
- [Django](https://docs.djangoproject.com/en/stable/)
- [Python 3.11](https://www.python.org)
- [Django REST framework](https://www.django-rest-framework.org)
- Gunicorn

### Как запустить проект:

Клонировать репозиторий:

```
git@github.com:MaxRadzey/foodgram-project-react.git
```

Скачать файл:

```
docker-compose.production.yml
```

Создать файл .env и указать актуальные данные

```
POSTGRES_USER=Пользователь БД
POSTGRES_PASSWORD=Пароль пользователя БД
POSTGRES_DB=БД
DB_NAME=Имя БД
DB_HOST=db
DB_PORT=5432

SECRET_KEY = Секретный ключ джанго-проекта
ALLOWED_HOSTS = Разрешенные хосты
DEBUG='False'
```

Запустить Dockercompose

```
sudo docker compose -f docker-compose.yml pull
sudo docker compose -f docker-compose.yml down
sudo docker compose -f docker-compose.yml up -d
```

Собрать статику и выполнить миграции

```
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
```

## Автоматический деплой

В репозитории есть файл main.yml, он необходим для автоматического деплоя проекта на сервер. В клонированном репозитории необходимо добавить перменные в Secrets:

```
DB_PORT - порт, по которому Django будет обращаться к базе данных  
DEBUG - режим запуска сервера
DOCKER_PASSWORD - пароль от Docker Hub
DOCKER_USERNAME - имя пользователя Docker Hub
HOST - адрес, по которому Django будет соединяться с базой данных
POSTGRES_DB - БД
POSTGRES_PASSWORD - пароль пользователя БД
POSTGRES_USER - пользователь БД
SECRET_KEY - секретный ключ джанго проекта
SSH_KEY - ключ ssh для доступа к удаленному серверу
SSH_PASSPHRASE - пароль ssh
TELEGRAM_TO - id пользователя TELEGRAM
TELEGRAM_TOKEN - TELEGRAM токен
USER - имя пользователя сервера
```
Далее запуште обновленный репозиторий.
