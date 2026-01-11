setup:
	python -m pip install -r requirements.txt

init-db:
	python scripts/create_db.py

run:
	python -m app.main

test:
	pytest -q

docker-build:
	docker build -t business-bots .

docker-up:
	docker-compose up --build -d
