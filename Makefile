start:
	uvicorn src.main:app --reload --reload-dir src/ --host 0.0.0.0 --port 8090

docker-up:
	docker compose -f docker-compose-services.yaml up -d

docker-down:
	docker compose -f docker-compose-services.yaml down

r:
	pip install -r requirements.txt

test:
	pytest src/tests