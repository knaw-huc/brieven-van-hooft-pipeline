PHONY: env

env: .env

.env:
	python -m venv .env
	. .env/bin/activate && pip install folia-tools stam
