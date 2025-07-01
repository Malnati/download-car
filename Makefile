# Makefile
# Variables
DOCKER_CONFIG ?= /tmp/docker-config-noauth
IMAGE ?= sicar
DOCKERFILE ?= Dockerfile

# Build Docker image
build:
	@echo "🛠️  Buildando imagem $(IMAGE):latest via $(DOCKERFILE)..."
	docker build -t $(IMAGE):latest -f $(DOCKERFILE) .

# Run container with optional command
run:
	@echo "🚀 Executando container $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest $(CMD)

# Open shell inside container
shell:
	@echo "🔗 Entrando no container $(IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest bash

# Remove local image
clean-image:
	@echo "🗑️  Removendo imagem $(IMAGE):latest..."
	docker rmi $(IMAGE):latest

# Execute Python unit tests
unit-test:
	@echo "🧪 Executando testes unitários..."
	python -m unittest SICAR/tests/unit/*.py SICAR/tests/unit/drivers/*.py

# Execute Python integration tests
integration-test:
	@echo "🧪 Executando testes de integração..."
	python -m unittest SICAR/tests/integration/*.py

test: unit-test integration-test

download:
	@echo "🛠️  Executando download_state.sh com parâmetros: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	./download_state.sh --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries)

# Valores padrão para os parâmetros
state ?= DF
polygon ?= APPS
folder ?= data/DF
debug ?= True
timeout ?= 30
max_retries ?= 5


# Docker Compose targets
build-base:
	@echo "🛠️  Building base image..."
	docker build -t sicar-base:latest -f Dockerfile.base .

build-download:
	@echo "🛠️  Building download image..."
	docker build -t sicar-download:latest -f Dockerfile.download-car .

build-api:
	@echo "🛠️  Building api image..."
	docker build -t sicar-api:latest -f Dockerfile.api .

build: build-base build-download build-api

up:
	docker compose up

down:
	docker compose down

clean:
	docker compose down -v --rmi all

logs:
	docker compose logs -f $(service)

ps:
	docker compose ps

download-up:
	docker compose up download-car

api-up:
	docker compose up api
