.PHONY: build up down logs restart reset-data

build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs --follow

restart: down up

reset-data:
	docker compose down -v
	docker compose up -d
