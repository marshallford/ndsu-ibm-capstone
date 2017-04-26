.PHONY: all lint test

all: lint test

lint:
	find ./* -name '*.py' -exec flake8 {} +

test:
	python -m nose
