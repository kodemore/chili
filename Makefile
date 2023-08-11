sources = chili tests
.DEFAULT_GOAL := all

toml_sort:
	poetry run toml-sort pyproject.toml --all --in-place

isort:
	poetry run isort $(sources)

black:
	poetry run black --line-length=120 --target-version py38 $(sources)

ruff:
	poetry run ruff chili

pylint:
	poetry run pylint chili

mypy:
	poetry run mypy --install-types --non-interactive .

bandit:
	poetry run bandit -r . -x ./tests,./test,./.venv

test:
	poetry run pytest tests

lint: isort black ruff mypy toml_sort

tests: test

all: lint tests
