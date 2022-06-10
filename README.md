# RS
## Рекомендательная система
### Перед началом работы с проектом выполнить:
Установку утилиты Make, менеджера зависимостей Poetry и все зависимости:
```shell
sudo apt install make -y
sudo apt install build-essential -y
make poetry_install
```
### Для первого запуска сервиса выполнить:
```shell
make create_env
make rs_init
```
### Модуль генерации событий от пользователей
Документация:
```shell
make generate_help
```
Генерация 10k событий:
```shell
make generate_data
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
