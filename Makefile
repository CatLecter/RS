poetry_install:
	sudo apt update && sudo apt upgrade -y
	sudo apt install curl
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
	source $HOME/.poetry/env
	poetry --version
	poetry install
	pre-commit install

create_env:
	cp -f auth/example.env-db auth/.env-db
	cp -f auth/example.env-flask auth/.env-flask
	cp -f etl/example.env etl/.env
	cp -f event_generator/example.env event_generator/.env
	cp -f movies_admin/example.env movies_admin/.env
	cp -f movies_db/example.env movies_db/.env
	cp -f rs/example.rabbitmq_env rs/.rabbitmq_env
	cp -f rs/example.rs_env rs/.rs_env
	cp -f rs/example.rs_env rs/.rs_env
	cp -f rs_api/example.env rs_api/.env
	cp -f rs_db/example.env rs_db/.env
	cp -f search_api/example.env search_api/.env
	cp -f sqlite_to_postgres/example.env sqlite_to_postgres/.env
	cp -f ugc/example.env ugc/.env

rs_init:
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

generate_help:
	python -m event_generator --help

generate_data:
	python -m event_generator -E10 -U50 -F20
