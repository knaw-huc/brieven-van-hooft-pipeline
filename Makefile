PHONY: env

env: .env

.env:
	python -m venv .env
	pip install foliatools stam
