test:
	poetry run pytest tests/test.py -v

app:
	docker compose up --build

down-db:
	poetry run alembic downgrade base

up-db:
	poetry run alembic upgrade head

restart_db:
	make down-db
	make up-db

redis:
	docker run --name redis -d --rm -p6379:6379 redis:latest

include .env
local_up:
	poetry run alembic upgrade head && poetry run python src/wsgi.py

postgres:
	docker run --name pdb -e POSTGRES_PASSWORD=${DB_PASSWORD} -e POSTGRES_USER=${DB_USER} -e POSTGRES_DB=${DB_NAME} -e TZ=${DB_TIMEZONE} -d --rm -p${DB_PORT}:5432 postgres:15.4-bullseye


duplicate:
	poetry run python src/duplication/duplic.py
