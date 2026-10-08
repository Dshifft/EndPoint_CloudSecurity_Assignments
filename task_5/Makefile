.PHONY: build up down logs restart reset-data test

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

test:
	docker compose -f docker-compose.test.yml down --volumes
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from pytest
