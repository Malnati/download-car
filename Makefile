# Variables
DOCKER_CONFIG  ?= /tmp/docker-config-noauth
IMAGE          ?= download-car
API_IMAGE      ?= download-car-api
DOCKERFILE     ?= Dockerfile
API_DOCKERFILE ?= Dockerfile.api

api-up:
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api

build:
	@echo "🛠️  Buildando imagem $(IMAGE):latest via $(DOCKERFILE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t $(IMAGE):latest -f $(DOCKERFILE) .
	@$(MAKE) build-base build-download build-api

build-api:
	@echo "🗑️  Removendo imagem $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):latest || true
	@echo "🛠️  Buildando imagem $(API_IMAGE):latest via $(API_DOCKERFILE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t $(API_IMAGE):latest -f $(API_DOCKERFILE) .

build-base:
	@echo "🛠️  Building base image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-base:latest -f Dockerfile.base .

build-download:
	@echo "🗑️  Removendo imagem download-car-download:latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi download-car-download:latest || true
	@echo "🛠️  Building download image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-download:latest -f Dockerfile.download-car .

clean:
	@echo "🗑️  Removendo imagens, volumes e containers órfãos..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --rmi all --volumes --remove-orphans

clean-api:
	@echo "🗑️  Removendo imagem $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):latest

clean-image:
	@echo "🗑️  Removendo imagem $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(IMAGE):latest

down:
	@echo "🛑  Parando e removendo containers..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down

download:
	@echo "🛠️  Executando download_state.sh com parâmetros: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	./download_state.sh --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries)

download-up:
	@echo "🚀  Iniciando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car

git-update:
	@echo "🔄  Atualizando repositório Git..."
	git reset --hard && git fetch && git pull

integration-test:
	@echo "🧪  Executando testes de integração..."
	python -m unittest download_car/tests/integration/*.py

logs:
	@echo "📜  Exibindo logs do serviço $(service)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f $(service)

ps:
	@echo "📋  Listando containers e serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps

run:
	@echo "🚀  Executando container $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest $(CMD)

run-api:
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -p 8000:8000 $(API_IMAGE):latest

shell:
	@echo "🔗  Entrando no container $(IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest bash

shell-api:
	@echo "🔗  Entrando no container API $(API_IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm $(API_IMAGE):latest bash

test:
	@echo "✅  Executando testes unitários e de integração..."
	@$(MAKE) unit-test
	@$(MAKE) integration-test

unit-test:
	@echo "🧪  Executando testes unitários..."
	python -m unittest download_car/tests/unit/*.py download_car/tests/unit/drivers/*.py

up:
	@echo "🔼  Iniciando todos os serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up
