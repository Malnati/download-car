# Atualização do Makefile - Alvo env

## Resumo das Mudanças

Adicionado o alvo `env` ao Makefile para garantir que o arquivo `.config.env` seja sempre copiado para `.env` antes de qualquer operação que use o Docker Compose.

## Mudanças Implementadas

### 1. Novo Alvo `env`

```makefile
# Copy .config.env to .env
.PHONY: env
env:
	@cp -f .config.env .env
```

### 2. Alvos de Build Atualizados

Todos os alvos principais de build agora dependem de `env`:

```makefile
# Build all images
build: env requirements.txt build-base build-pro build-download build-api build-nginx

# Build development images
build-dev: env build-base build-dev build-download-dev build-api-dev build-nginx

# Build production images
build-pro: env requirements.txt build-base build-pro build-download-pro build-api-pro build-nginx
```

### 3. Alvos de Docker Compose Atualizados

Todos os alvos que usam `docker compose` agora dependem de `env`:

```makefile
# Inicialização de serviços
up: env
	@echo "🔼  Iniciando todos os serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up -d

api-up: env
	@echo "🚀  Executando container API $(API_IMAGE):latest..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up api -d

download-up: env
	@echo "🚀  Iniciando serviço download-car..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose up download-car -d

# Controle de containers
down: env
	@echo "🛑  Parando e removendo containers..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down

# Limpeza
clean: env
	@echo "🗑️  Removendo imagens, volumes e containers órfãos..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --rmi all --volumes --remove-orphans || true

clean-volumes: env
	@echo "🗑️  Removendo volumes Docker, incluindo arquivos montados..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose down --volumes --remove-orphans
	# ... resto do comando

# Monitoramento
logs: env
	@echo "📜  Exibindo logs do serviço $(service)..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose logs -f $(service)

ps: env
	@echo "📋  Listando containers e serviços..."
	DOCKER_CONFIG=$(DOCKER_CONFIG) docker compose ps
```

## Benefícios

1. **Consistência**: Garante que o arquivo `.env` sempre esteja atualizado com as configurações do `.config.env`
2. **Automatização**: Elimina a necessidade de copiar manualmente o arquivo antes de executar comandos
3. **Silencioso**: O comando `cp -f` não gera erro se o arquivo já existir
4. **Dependência**: Todos os alvos relevantes agora dependem automaticamente de `env`

## Comportamento

- O alvo `env` é executado automaticamente antes de qualquer operação que use Docker Compose
- A cópia é silenciosa (usa `@` para suprimir a saída do comando)
- O flag `-f` garante que não há erro se o arquivo `.env` já existir
- O alvo é marcado como `.PHONY` para garantir que sempre seja executado

## Teste

Para testar as mudanças:

```bash
# Testar o alvo env isoladamente
make env

# Testar um alvo que depende de env
make up

# Verificar se o arquivo .env foi criado
ls -la .env
```

## Alvos Afetados

- `build` - Build de todas as imagens (produção)
- `build-dev` - Build de todas as imagens (desenvolvimento)
- `build-pro` - Build de todas as imagens (produção)
- `up` - Iniciar todos os serviços
- `api-up` - Iniciar apenas o serviço API
- `download-up` - Iniciar apenas o serviço download-car
- `down` - Parar e remover containers
- `clean` - Limpeza completa
- `clean-volumes` - Limpeza de volumes
- `logs` - Exibir logs
- `ps` - Listar containers

## Arquivos Modificados

- `Makefile` - Adicionado alvo `env` e dependências
- `MAKEFILE_ENV_UPDATE.md` - Esta documentação 