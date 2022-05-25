# RS
## Рекомендательная система

Перед началом работы с проектом выполнить:
- Установку Poetry согласно https://python-poetry.org/docs/#installation
- Выполнить команду poetry install
- Выполнить команду pre-commit install

Конфигурирование сервиса выполнить:
```shell
docker-compose -f docker-compose.yml down -v
python movies_admin/manage.py collectstatic --no-input --clear
docker-compose -f docker-compose.yml up -d --build
docker-compose -f docker-compose.yml exec movies_admin python manage.py migrate --fake movies 0001
docker-compose -f docker-compose.yml exec movies_admin python manage.py makemigrations
docker-compose -f docker-compose.yml exec movies_admin python manage.py migrate
docker-compose -f docker-compose.yml exec movies_admin python manage.py createsuperuser --noinput
docker-compose exec auth flask db upgrade
docker-compose exec auth flask createsuperuser -u admin -e example@email.com -p password
docker-compose exec auth flask loaddata
```

## Ссылки:
- Панель администратора: http://0.0.0.0/admin/
- Movies API: http://0.0.0.0/api/openapi#/
- UGC API: http://0.0.0.0/ugc/api/openapi#/
- Auth Swagger: http://0.0.0.0/swagger-ui
- Auth Redoc: http://0.0.0.0/redoc-ui
