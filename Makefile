# Makefile
# Variables
DOCKER_CONFIG  ?= /tmp/docker-config-noauth
IMAGE          ?= download-car
API_IMAGE      ?= download-car-api
API_DOCKERFILE ?= Dockerfile.api

# Build base image
build-base:
	@echo "🛠️  Building base image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-base:latest -f Dockerfile.base .

# Build development image
build-dev:
	@echo "🛠️  Building development image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-dev:latest -f Dockerfile.dev .

# Build production image
build-pro:
	@echo "🛠️  Building production image..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker build -t download-car-pro:latest -f Dockerfile.pro .

# Build API with development base
build-api-dev:
	@echo "🗑️  Removendo imagem $(API_IMAGE):dev..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):dev || true
	@echo "🛠️  Buildando imagem $(API_IMAGE):dev..."
	DOCKER_BUILDKIT=1 DOCKER_CONFIG=$(DOCKER_CONFIG) docker build \
		--build-arg BASE_IMAGE=download-car-dev:latest \
		-t $(API_IMAGE):dev \
		-f $(API_DOCKERFILE) .

# Build API with production base
build-api-pro:
	@echo "🗑️  Removendo imagem $(API_IMAGE):pro..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):pro || true
	@echo "🛠️  Buildando imagem $(API_IMAGE):pro..."
	DOCKER_BUILDKIT=1 DOCKER_CONFIG=$(DOCKER_CONFIG) docker build \
		--build-arg BASE_IMAGE=download-car-pro:latest \
		-t $(API_IMAGE):pro \
		-f $(API_DOCKERFILE) .

# Build download-car with development base
build-download-dev:
	@echo "🗑️  Removendo imagem download-car-download:dev..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi download-car-download:dev || true
	@echo "🛠️  Building download development image..."
	DOCKER_BUILDKIT=1 DOCKER_CONFIG=$(DOCKER_CONFIG) docker build \
		--build-arg BASE_IMAGE=download-car-dev:latest \
		-t download-car-download:dev \
		-f Dockerfile.download-car .

# Build download-car with production base
build-download-pro:
	@echo "🗑️  Removendo imagem download-car-download:pro..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi download-car-download:pro || true
	@echo "🛠️  Building download production image..."
	DOCKER_BUILDKIT=1 DOCKER_CONFIG=$(DOCKER_CONFIG) docker build \
		--build-arg BASE_IMAGE=download-car-pro:latest \
		-t download-car-download:pro \
		-f Dockerfile.download-car .

# Default builds (production)
build-api: build-api-pro
build-download: build-download-pro

# Gerar requirements.txt para produção
requirements.txt: pyproject.toml
	@if [ -f poetry.lock ]; then \
		poetry export --only main --format=requirements.txt > requirements.txt; \
	else \
		echo "poetry.lock não encontrado, usando requirements.txt existente"; \
	fi

# Build all images
build: requirements.txt build-base build-pro build-download build-api

# Build development images
build-dev: build-base build-dev build-download-dev build-api-dev

# Build production images
build-pro: requirements.txt build-base build-pro build-download-pro build-api-pro

api-up:
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api -d

clean:
	@echo "🗑️  Removendo imagens, volumes e containers órfãos..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --rmi all --volumes --remove-orphans || true


clean-volumes:
	@echo "🗑️  Removendo volumes Docker, incluindo arquivos montados..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --volumes --remove-orphans
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker volume prune -f
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker system prune -f --volumes
	@echo "🗑️  Limpando arquivos locais em temp/"
	rm -rf temp/* || true
	@echo "🗑️  Limpando arquivos locais em data/"
	rm -rf data/* || true
	@echo "🗑️  Limpando arquivos locais em __pycache__/"
	rm -rf __pycache__/* || true
	@echo "🗑️  Limpando arquivos locais em download_car.egg-info/"
	rm -rf download_car.egg-info/* || true

clean-api:
	@echo "🗑️  Removendo imagem $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(API_IMAGE):latest

clean-image:
	@echo "🗑️  Removendo imagem $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker rmi $(IMAGE):latest

down:
	@echo "🛑  Parando e removendo containers..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down

install:
	poetry install

# Comandos de instalação de dependências
install-paddle:
	@echo "🔧 Instalando dependências PaddleOCR..."
	poetry install --extras paddle

install-full:
	@echo "🔧 Instalando todas as dependências..."
	poetry install --extras full

install-dev:
	@echo "🔧 Instalando dependências de desenvolvimento..."
	poetry install --extras dev

# Comandos de download com verificação automática
download: check-dependencies install
	@echo "🛠️  Executando cli.py com fallback simples: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --simple-fallback

download-tesseract: install
	@echo "🛠️  Executando cli.py com Tesseract: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --driver tesseract

download-paddle: install-paddle
	@echo "🛠️  Executando cli.py com PaddleOCR: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --driver paddle

download-no-vpn: check-dependencies install
	@echo "🛠️  Executando cli.py SEM VPN: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --driver tesseract

# Comandos para VPN e fallback automático
download-with-vpn: install
	@echo "🔒  Executando download com VPN (Tor)..."
	@echo "🛠️  Parâmetros: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --use-vpn

download-with-fallback: install
	@echo "🔄  Executando download com fallback automático (Tesseract → PaddleOCR → VPN)..."
	@echo "🛠️  Parâmetros: state=$(state), polygon=$(polygon), folder=$(folder), debug=$(debug), timeout=$(timeout), max_retries=$(max_retries)"
	poetry run python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --auto-fallback

# Comandos Docker com VPN
download-docker-vpn:
	@echo "🔒  Executando download com VPN no Docker..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm \
		-v $(PWD):/download-car \
		download-car-download:dev \
		/usr/local/bin/start-tor.sh \
		python cli.py --state $(state) --polygon $(polygon) --folder $(folder) --debug $(debug) --timeout $(timeout) --max_retries $(max_retries) --use-vpn

# Verificação automática de dependências
check-dependencies:
	@echo " Verificando dependências..."
	@if ! poetry run python -c "from download_car.drivers import PaddleOCR; print('PaddleOCR disponível')" 2>/dev/null; then \
		echo "⚠️  PaddleOCR não encontrado. Instalando automaticamente..."; \
		$(MAKE) install-paddle; \
	fi

# Comandos para as novas funcionalidades
search-car:
	@echo "🔍  Buscando estado do CAR: $(car)"
	curl -X GET "http://localhost:8000/state?car=$(car)"

download-property:
	@echo "🏠  Baixando propriedade do CAR: $(car)"
	curl -X GET "http://localhost:8000/property?car=$(car)" --output property_$(car).zip

delete-state:
	@echo "🗑️  Excluindo arquivos do estado: $(state)"
	curl -X DELETE "http://localhost:8000/delete_state" \
		-F "state=$(state)" \
		-F "folder=$(folder)" \
		-F "include_properties=$(include_properties)"

download-up:
	@echo "🚀  Iniciando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car -d

git-update:
	@echo "🔄  Atualizando repositório Git..."
	git reset --hard && git fetch && git pull

publish:
	@echo "📦  Publicando pacote Python..."
	@echo "🔄  Incrementando versão (patch)..."
	python dev/bump_version.py patch
	@echo "🏗️  Construindo pacote..."
	rm -rf dist/* && python -m build && python -m twine upload dist/*

publish-minor:
	@echo "📦  Publicando pacote Python (minor version)..."
	@echo "🔄  Incrementando versão (minor)..."
	python dev/bump_version.py minor
	@echo "🏗️  Construindo pacote..."
	rm -rf dist/* && python -m build && python -m twine upload dist/*

publish-major:
	@echo "📦  Publicando pacote Python (major version)..."
	@echo "🔄  Incrementando versão (major)..."
	python dev/bump_version.py major
	@echo "🏗️  Construindo pacote..."
	rm -rf dist/* && python -m build && python -m twine upload dist/*

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

# Testar drivers OCR (versão corrigida)
test-ocr:
	@echo "🧪  Testando drivers OCR..."
	poetry run python -c 'from download_car.drivers import Tesseract; print("Tesseract disponível:", Tesseract is not None)'

# Comandos de banco de dados
init-db:
	@echo "🗄️  Inicializando banco de dados PostgreSQL/PostGIS..."
	python init_database.py

db-status:
	@echo "🔍  Verificando status da conexão com banco de dados..."
	curl -X GET "http://localhost:8000/database_status" | jq .

sync-state:
	@echo "🔄  Sincronizando dados do estado $(state) com banco de dados..."
	curl -X POST "http://localhost:8000/sync_to_database" \
		-F "sync_type=state" \
		-F "state=$(state)" \
		-F "polygon_type=$(polygon)" \
		-F "folder=temp" \
		-F "create_tables=true" | jq .

sync-car:
	@echo "🔄  Sincronizando dados do CAR $(car) com banco de dados..."
	curl -X POST "http://localhost:8000/sync_to_database" \
		-F "sync_type=car" \
		-F "car_code=$(car)" \
		-F "state=$(state)" \
		-F "polygon_type=$(polygon)" \
		-F "folder=temp" \
		-F "create_tables=true" | jq .

query-car:
	@echo "🔍  Consultando dados do CAR $(car) no banco de dados..."
	curl -X GET "http://localhost:8000/car_data?car_code=$(car)" | jq .

query-state:
	@echo "🔍  Consultando dados do estado $(state) no banco de dados..."
	curl -X GET "http://localhost:8000/car_data?state=$(state)&limit=$(limit)" | jq .

up:
	@echo "🔼  Iniciando todos os serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up -d

help:
	@echo "📋  Comandos disponíveis no Makefile:"
	@echo ""
	@echo "🚀  Comandos de inicialização:"
	@echo "  up              - Inicia todos os serviços"
	@echo "  api-up          - Inicia apenas o serviço API"
	@echo "  download-up     - Inicia apenas o serviço download-car"
	@echo ""
	@echo "🛠️  Comandos de build:"
	@echo "  build           - Builda todas as imagens (produção)"
	@echo "  build-dev       - Builda todas as imagens (desenvolvimento)"
	@echo "  build-pro       - Builda todas as imagens (produção)"
	@echo "  build-base      - Builda a imagem base"
	@echo "  build-api       - Builda apenas a imagem da API (produção)"
	@echo "  build-api-dev   - Builda apenas a imagem da API (desenvolvimento)"
	@echo "  build-api-pro   - Builda apenas a imagem da API (produção)"
	@echo "  build-download  - Builda apenas a imagem de download (produção)"
	@echo "  build-download-dev - Builda apenas a imagem de download (desenvolvimento)"
	@echo "  build-download-pro - Builda apenas a imagem de download (produção)"
	@echo ""
	@echo "🗑️  Comandos de limpeza:"
	@echo "  clean           - Remove imagens, volumes e containers órfãos"
	@echo "  clean-volumes   - Remove volumes Docker, incluindo arquivos montados"
	@echo "  clean-api       - Remove apenas a imagem da API"
	@echo "  clean-image     - Remove apenas a imagem principal"
	@echo ""
	@echo "🛑  Comandos de controle:"
	@echo "  down            - Para e remove containers"
	@echo "  ps              - Lista containers e serviços"
	@echo "  logs service=X  - Exibe logs do serviço especificado"
	@echo ""
	@echo "🔗  Comandos de acesso:"
	@echo "  shell           - Entra no container principal"
	@echo "  shell-api       - Entra no container da API"
	@echo "  run CMD=X       - Executa comando no container"
	@echo "  run-api         - Executa container da API"
	@echo ""
	@echo "🧪  Comandos de teste:"
	@echo "  test            - Executa todos os testes"
	@echo "  unit-test       - Executa testes unitários"
	@echo "  integration-test - Executa testes de integração"
	@echo ""
	@echo "📥  Comandos de download:"
	@echo "  download state=X polygon=Y folder=Z debug=W timeout=T max_retries=R"
	@echo "  search-car car=X - Busca estado do CAR"
	@echo "  download-property car=X - Baixa propriedade do CAR"
	@echo "  delete-state state=X folder=Y include_properties=Z - Exclui arquivos de um estado"
	@echo ""
	@echo "🔄  Comandos de manutenção:"
	@echo "  git-update      - Atualiza repositório Git"
	@echo "  publish         - Publica pacote Python no PyPI (incrementa patch)"
	@echo "  publish-minor   - Publica pacote Python no PyPI (incrementa minor)"
	@echo "  publish-major   - Publica pacote Python no PyPI (incrementa major)"
	@echo ""
	@echo "🗄️  Comandos de banco de dados:"
	@echo "  init-db         - Inicializa banco de dados PostgreSQL/PostGIS"
	@echo "  db-status       - Verifica status da conexão com banco de dados"
	@echo "  sync-state state=X polygon=Y - Sincroniza dados de um estado com o banco"
	@echo "  sync-car car=X state=Y polygon=Z - Sincroniza dados de um CAR específico"
	@echo "  query-car car=X - Consulta dados de um CAR no banco"
	@echo "  query-state state=X limit=Y - Consulta dados de um estado no banco"

# Limpar arquivos de download
clean-downloads:
	@echo "🗑️  Limpando arquivos de download..."
	sudo rm -f data/*.zip || true
	sudo rm -f temp/*.zip || true
	@echo "✅ Arquivos de download removidos"
