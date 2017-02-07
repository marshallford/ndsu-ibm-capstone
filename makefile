lint:
	find . -name '*.py' -exec flake8 {} +

test:
	python -m nose
