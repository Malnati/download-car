# Makefile
# Variables
DOCKER_CONFIG  ?= /tmp/docker-config-noauth
IMAGE          ?= download-car
API_IMAGE      ?= download-car-api
API_DOCKERFILE ?= Dockerfile.api

# Build all images
build: env requirements.txt build-base build-pro build-download build-api build-nginx

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

# Default builds (production)
build-api: build-api-pro
build-download: build-download-pro

# Build nginx
build-nginx:
	@echo "🌐  Buildando imagem nginx..."
	DOCKER_BUILDKIT=1 DOCKER_CONFIG=$(DOCKER_CONFIG) docker build \
		-t download-car-nginx:latest \
		-f Dockerfile.nginx .

# Build development images
build-dev: env build-base build-dev build-download-dev build-api-dev build-nginx

# Build production images
build-pro: env requirements.txt build-base build-pro build-download-pro build-api-pro build-nginx

# Verificar versão do Poetry e gerar requirements.txt
check-poetry:
	@echo "🔍 Verificando versão do Poetry..."
	@if ! poetry --version > /dev/null 2>&1; then \
		echo "❌ Poetry não está instalado!"; \
		echo ""; \
		echo "📦 Para instalar o Poetry:"; \
		if [ "$$(uname -s)" = "Darwin" ]; then \
			echo "   macOS: brew install poetry"; \
		elif command -v apt-get > /dev/null 2>&1; then \
			echo "   Ubuntu/Debian: curl -sSL https://install.python-poetry.org | python3 -"; \
		elif command -v yum > /dev/null 2>&1; then \
			echo "   CentOS/RHEL: curl -sSL https://install.python-poetry.org | python3 -"; \
		else \
			echo "   Linux: curl -sSL https://install.python-poetry.org | python3 -"; \
		fi; \
		echo ""; \
		echo "   Ou visite: https://python-poetry.org/docs/#installation"; \
		exit 1; \
	fi
	@if ! poetry export --help > /dev/null 2>&1; then \
		echo "❌ Poetry não suporta o comando 'export'!"; \
		echo ""; \
		echo "📦 Para instalar o plugin de exportação:"; \
		echo "   poetry self add poetry-plugin-export"; \
		echo ""; \
		echo "   Veja mais em: https://github.com/python-poetry/poetry-plugin-export"; \
		exit 1; \
	fi
	@echo "✅ Poetry e plugin de exportação disponíveis: $$(poetry --version)"

# Verificação automática de dependências
check-dependencies:
	@echo " Verificando dependências..."
	@if ! poetry run python -c "from download_car.drivers import PaddleOCR; print('PaddleOCR disponível')" 2>/dev/null; then \
		echo "⚠️  PaddleOCR não encontrado. Instalando automaticamente..."; \
		$(MAKE) install-paddle; \
	fi

# Limpar arquivos de download
clean-downloads:
	@echo "🗑️  Limpando arquivos de download..."
	sudo rm -f data/*.zip || true
	sudo rm -f temp/*.zip || true
	@echo "✅ Arquivos de download removidos"

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

# Comandos de banco de dados
db-status:
	@echo "🔍  Verificando status da conexão com banco de dados PostgreSQL/PostGIS..."
	curl -X GET "http://localhost:8000/database_status" | jq .

sync-state:
	@echo "🔄  Inserindo dados do estado $(state) no banco de dados PostgreSQL/PostGIS..."
	curl -X POST "http://localhost:8000/sync_to_database" \
		-F "sync_type=state" \
		-F "state=$(state)" \
		-F "polygon_type=$(polygon)" \
		-F "folder=temp" \
		-F "create_tables=true" | jq .

sync-car:
	@echo "🔄  Inserindo dados do CAR $(car) no banco de dados PostgreSQL/PostGIS..."
	curl -X POST "http://localhost:8000/sync_to_database" \
		-F "sync_type=car" \
		-F "car_code=$(car)" \
		-F "state=$(state)" \
		-F "polygon_type=$(polygon)" \
		-F "folder=temp" \
		-F "create_tables=true" | jq .

query-car:
	@echo "🔍  Consultando dados do CAR $(car) no banco de dados PostgreSQL/PostGIS..."
	curl -X GET "http://localhost:8000/car_data?car_code=$(car)" | jq .

query-state:
	@echo "🔍  Consultando dados do estado $(state) no banco de dados PostgreSQL/PostGIS..."
	curl -X GET "http://localhost:8000/car_data?state=$(state)&limit=$(limit)" | jq .

# Comandos de controle de serviços
up: env
	@echo "🔼  Iniciando todos os serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up -d

down: env
	@echo "🛑  Parando e removendo containers..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down

down-api: env
	@echo "🛑  Parando e removendo container API..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop api
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f api

down-download: env
	@echo "🛑  Parando e removendo container download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop download-car
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f download-car

down-nginx: env
	@echo "🛑  Parando e removendo container nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop nginx
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f nginx

# Comandos de restart de serviços
restart: env
	@echo "🔄  Reiniciando todos os serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose restart

restart-api: env
	@echo "🔄  Reiniciando serviço API..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose restart api

restart-download: env
	@echo "🔄  Reiniciando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose restart download-car

restart-nginx: env
	@echo "🔄  Reiniciando serviço nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose restart nginx

# Comandos de logs por serviço
logs: env
	@echo "📜  Exibindo logs do serviço $(service)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f $(service)

logs-api: env
	@echo "📜  Exibindo logs do serviço API..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f api

logs-download: env
	@echo "📜  Exibindo logs do serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f download-car

logs-nginx: env
	@echo "📜  Exibindo logs do serviço nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f nginx

# Comandos de status dos serviços
ps: env
	@echo "📋  Listando containers e serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps

ps-api: env
	@echo "📋  Listando status do serviço API..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps api

ps-download: env
	@echo "📋  Listando status do serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps download-car

ps-nginx: env
	@echo "📋  Listando status do serviço nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps nginx

# Comandos de inicialização individual
api-up: env
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api -d

download-up: env
	@echo "🚀  Iniciando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car -d

nginx-up: env
	@echo "🚀  Iniciando serviço nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up nginx -d

# Comandos de limpeza
clean: env
	@echo "🗑️  Removendo imagens, volumes e containers órfãos..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --rmi all --volumes --remove-orphans || true

clean-volumes: env
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

# Copy .config.env to .env
.PHONY: env
env:
	@cp -fv .config.env .env

# Comandos de instalação
install:
	poetry install

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

# Comandos de execução
run:
	@echo "🚀  Executando container $(IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest $(CMD)

run-api:
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -p 8000:8000 $(API_IMAGE):latest

# Comandos de shell
shell:
	@echo "🔗  Entrando no container $(IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm -v $(PWD):/download-car $(IMAGE):latest bash

shell-api:
	@echo "🔗  Entrando no container API $(API_IMAGE)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker run -it --rm $(API_IMAGE):latest bash

# Comandos de teste
test:
	@echo "✅  Executando testes unitários e de integração..."
	@$(MAKE) unit-test
	@$(MAKE) integration-test

unit-test:
	@echo "🧪  Executando testes unitários..."
	python -m unittest download_car/tests/unit/*.py download_car/tests/unit/drivers/*.py

integration-test:
	@echo "🧪  Executando testes de integração..."
	python -m unittest download_car/tests/integration/*.py

# Testar drivers OCR (versão corrigida)
test-ocr:
	@echo "🧪  Testando drivers OCR..."
	poetry run python -c 'from download_car.drivers import Tesseract; print("Tesseract disponível:", Tesseract is not None)'

# Comandos de publicação
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

# Comandos de manutenção
git-update:
	@echo "🔄  Atualizando repositório Git..."
	git reset --hard && git fetch && git pull

# Gerar requirements.txt para produção
requirements.txt: pyproject.toml check-poetry
	@echo "📦 Gerando requirements.txt..."
	@if [ -f poetry.lock ]; then \
		poetry export --only main --format=requirements.txt > requirements.txt; \
		echo "✅ requirements.txt gerado com sucesso"; \
	else \
		echo "⚠️  poetry.lock não encontrado, usando requirements.txt existente"; \
	fi

# Ajuda
help:
	@echo "📋  Comandos disponíveis no Makefile:"
	@echo ""
	@echo "🚀  Comandos de inicialização:"
	@echo "  up              - Inicia todos os serviços"
	@echo "  api-up          - Inicia apenas o serviço API"
	@echo "  download-up     - Inicia apenas o serviço download-car"
	@echo "  nginx-up        - Inicia apenas o serviço nginx"
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
	@echo "  build-nginx     - Builda apenas a imagem do nginx"
	@echo ""
	@echo "🗑️  Comandos de limpeza:"
	@echo "  clean           - Remove imagens, volumes e containers órfãos"
	@echo "  clean-volumes   - Remove volumes Docker, incluindo arquivos montados"
	@echo "  clean-api       - Remove apenas a imagem da API"
	@echo "  clean-image     - Remove apenas a imagem principal"
	@echo "  clean-downloads - Remove arquivos de download"
	@echo ""
	@echo "🛑  Comandos de controle:"
	@echo "  down            - Para e remove containers"
	@echo "  down-api        - Para e remove apenas o container API"
	@echo "  down-download   - Para e remove apenas o container download-car"
	@echo "  down-nginx      - Para e remove apenas o container nginx"
	@echo "  restart         - Reinicia todos os serviços"
	@echo "  restart-api     - Reinicia apenas o serviço API"
	@echo "  restart-download - Reinicia apenas o serviço download-car"
	@echo "  restart-nginx   - Reinicia apenas o serviço nginx"
	@echo "  ps              - Lista containers e serviços"
	@echo "  ps-api          - Lista status do serviço API"
	@echo "  ps-download     - Lista status do serviço download-car"
	@echo "  ps-nginx        - Lista status do serviço nginx"
	@echo "  logs service=X  - Exibe logs do serviço especificado"
	@echo "  logs-api        - Exibe logs do serviço API"
	@echo "  logs-download   - Exibe logs do serviço download-car"
	@echo "  logs-nginx      - Exibe logs do serviço nginx"
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
	@echo "  test-ocr        - Testa drivers OCR"
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
	@echo "  db-status       - Verifica status da conexão com banco de dados PostgreSQL/PostGIS"
	@echo "  sync-state state=X polygon=Y - Insere dados de um estado no banco PostgreSQL/PostGIS"
	@echo "  sync-car car=X state=Y polygon=Z - Insere dados de um CAR específico no banco PostgreSQL/PostGIS"
	@echo "  query-car car=X - Consulta dados de um CAR no banco PostgreSQL/PostGIS"
	@echo "  query-state state=X limit=Y - Consulta dados de um estado no banco PostgreSQL/PostGIS"

# Update API
update-api: env
	@echo "🔄  Atualizando serviço API..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop api
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f api
	$(MAKE) build-base
	$(MAKE) build-pro
	$(MAKE) build-api
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api -d
	@echo "✅  Serviço API atualizado com sucesso!"

# Update download-car
update-download: env
	@echo "🔄  Atualizando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop download-car
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f download-car
	$(MAKE) build-base
	$(MAKE) build-pro
	$(MAKE) build-download
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car -d
	@echo "✅  Serviço download-car atualizado com sucesso!"

# Update nginx
update-nginx: env
	@echo "🔄  Atualizando serviço nginx..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose stop nginx
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose rm -f nginx
	$(MAKE) build-nginx
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up nginx -d
	@echo "✅  Serviço nginx atualizado com sucesso!"
