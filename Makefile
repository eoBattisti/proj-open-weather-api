.PHONY: pytest docker

help:
	@echo "======= Utility Tools Executor ======="
	@echo "Please use \`make X' where X is one of"
	@echo "build -> Build the FastAPI container and Redis."
	@echo "run -> Run the development environment."
	@echo "test -> Run the ci environment"

build:
	docker compose up --build

run:
	docker compose up

test:
	docker compose -f docker-compose.ci.yaml up

test-api:
	docker compose -f docker-compose.ci.yaml up --exit-code-from api api

test-consumer:
	docker compose -f docker-compose.ci.yaml up --exit-code-from consumer consumer
