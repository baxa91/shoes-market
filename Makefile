.PHONY:
.SILENT:
.DEFAULT_GOAL := run


args = "$(filter-out $@,$(MAKECMDGOALS))"

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

upgrade:
	docker-compose exec shoes-market alembic upgrade head

mm:
	docker-compose exec shoes-market alembic revision --autogenerate

downgrade:
	 docker-compose exec shoes-market alembic downgrade -1
