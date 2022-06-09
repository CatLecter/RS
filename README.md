# RS
## Рекомендательная система

### Перед началом работы с проектом выполнить:
- Установку Poetry согласно https://python-poetry.org/docs/#installation
- Выполнить команду poetry install
- Выполнить команду pre-commit install
- Во всех директориях, где лежат файлы example.env создать аналогичные .env файлы.

### Для запуска сервиса выполнить:
```shell
python movies_admin/manage.py collectstatic --no-input --clear
docker-compose -f docker-compose.yml down -v
docker-compose -f docker-compose.yml up -d --build
docker-compose -f docker-compose.yml exec movies_admin python manage.py migrate --fake movies 0001
docker-compose -f docker-compose.yml exec movies_admin python manage.py makemigrations
docker-compose -f docker-compose.yml exec movies_admin python manage.py migrate
docker-compose -f docker-compose.yml exec movies_admin python manage.py createsuperuser --noinput
docker-compose exec auth flask db upgrade
docker-compose exec auth flask createsuperuser -u admin -e example@email.com -p password
docker-compose exec auth flask loaddata
```

### Модуль генерации событий от пользователей

Документация
```
python -m event_generator --help
```
Пример использования (необходимо запустить после поднятия контейнеров и дождаться пока сервис rs обработает данные)
```
python -m event_generator -E2 -U10 -F10
```

### Ссылки:
- Панель администратора: http://0.0.0.0/admin/
- Movies search API: http://0.0.0.0/api/openapi#/
- UGC OpenAPI: http://0.0.0.0/ugc/api/openapi#/
- Auth Swagger: http://0.0.0.0/swagger-ui
- Auth Redoc: http://0.0.0.0/redoc-ui
- Панель Kafdrop: http://0.0.0.0:19000/
- Панель RabbitMQ: http://0.0.0.0:15672/#/

### Основная ссылка:
- Получение списка рекомендованных фильмов по UUID пользователя: http://0.0.0.0/rs/api/openapi#/

### Примечание:
UUID пользователя для тестирования можно получить из
базы данных rs_db перейдя по ссылке: http://0.0.0.0:9200/movies/_search
