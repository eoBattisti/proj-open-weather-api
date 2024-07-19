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
	docker compose -f docker-compose.yaml -f docker-compose.ci.yaml up api --build
