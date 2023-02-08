
init:
	pip install poetry
	poetry install

migrations:
	poetry run alembic revision --autogenerate

migrate_db:
	poetry run alembic upgrade head
