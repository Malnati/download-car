# Makefile

# Variables
DOCKER_CONFIG ?= /tmp/docker-config-noauth
IMAGE ?= download-car

API_IMAGE ?= download-car-api
DOCKERFILE ?= Dockerfile
API_DOCKERFILE ?= Dockerfile.api

# Build Docker image
build:
	@echo "🛠️  Buildando imagem $(IMAGE):latest via $(DOCKERFILE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t $(IMAGE):latest -f $(DOCKERFILE) .

# Build API Docker image
build-api:
	@echo "🛠️  Buildando imagem $(API_IMAGE):latest via $(API_DOCKERFILE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t $(API_IMAGE):latest -f $(API_DOCKERFILE) .

# Run container with optional command
run:
	@echo "🚀 Executando container $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest $(CMD)

# Run API container
run-api:
	@echo "🚀 Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -p 8000:8000 $(API_IMAGE):latest

# Open shell inside container
shell:
	@echo "🔗 Entrando no container $(IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest bash

# Open shell inside API container
shell-api:
	@echo "🔗 Entrando no container API $(API_IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm $(API_IMAGE):latest bash

# Remove local image
clean-image:
	@echo "🗑️  Removendo imagem $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(IMAGE):latest

# Remove API image
clean-api:
	@echo "🗑️  Removendo imagem $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):latest

# Execute Python unit tests
unit-test:
	@echo "🧪 Executando testes unitários..."
	python -m unittest download_car/tests/unit/*.py download_car/tests/unit/drivers/*.py

# Execute Python integration tests
integration-test:
	@echo "🧪 Executando testes de integração..."
	python -m unittest download_car/tests/integration/*.py

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
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-base:latest -f Dockerfile.base .

build-download:
	@echo "🛠️  Building download image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-download:latest -f Dockerfile.download-car .

build: build-base build-download build-api

up:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up

down:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down

clean:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down -v --rmi all

logs:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f $(service)

ps:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps

download-up:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car

api-up:
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api

# Limpeza de imagens, volumes e órfãos
clean:
	@echo "🗑️  Removendo imagens, volumes e containers órfãos..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --rmi all --volumes --remove-orphans
