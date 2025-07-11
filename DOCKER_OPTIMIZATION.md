<!-- DOCKER_OPTIMIZATION.md -->
# Otimização dos Dockerfiles

## Visão Geral

Esta otimização reorganiza as dependências dos Dockerfiles para minimizar o tamanho das imagens de produção enquanto mantém todas as ferramentas necessárias para desenvolvimento e debug.

## Estrutura dos Dockerfiles

### 1. Dockerfile.base
**Imagem base com dependências mínimas necessárias:**
- Python 3.11.9 via pyenv
- Dependências de sistema para Python e OCR
- Tesseract OCR
- Dependências Python core: httpx, urllib3, pytesseract, opencv-python, numpy, tqdm, matplotlib, beautifulsoup4

### 2. Dockerfile.dev
**Estende base + ferramentas de desenvolvimento:**
- git, curl, wget, ca-certificates (debug)
- PaddleOCR (OCR alternativo mais pesado)
- Ferramentas de desenvolvimento: coverage, interrogate, black, coveralls
- download-car com todas as dependências

### 3. Dockerfile.pro
**Estende base + apenas produção:**
- download-car sem PaddleOCR (mais leve)

### 4. Dockerfile.api
**Estende dev ou pro conforme variável BASE_IMAGE:**
- Dependências específicas da API: fastapi, uvicorn, python-multipart, geopandas, fiona

### 5. Dockerfile.download-car
**Estende dev ou pro conforme variável BASE_IMAGE:**
- Scripts de download

## Variáveis de Ambiente

### BASE_IMAGE
Controla qual imagem base usar:
- `download-car-dev:latest` - Desenvolvimento (com PaddleOCR e ferramentas)
- `download-car-pro:latest` - Produção (otimizado)

### Exemplo de uso:
```bash
# Desenvolvimento
BASE_IMAGE=download-car-dev:latest docker compose up

# Produção
BASE_IMAGE=download-car-pro:latest docker compose up

# Ou via .env
echo "BASE_IMAGE=download-car-pro:latest" > .env
docker compose up
```

## Comandos Makefile

### Build de Desenvolvimento
```bash
make build-dev    # Builda todas as imagens de desenvolvimento
make build-api-dev    # Builda apenas API de desenvolvimento
make build-download-dev    # Builda apenas download de desenvolvimento
```

### Build de Produção
```bash
make build-pro    # Builda todas as imagens de produção
make build-api-pro    # Builda apenas API de produção
make build-download-pro    # Builda apenas download de produção
```

### Build Base
```bash
make build-base    # Builda apenas a imagem base
```

## Tamanhos Estimados

- **Base**: ~800MB (Python + dependências core)
- **Dev**: ~2.5GB (base + PaddleOCR + ferramentas)
- **Pro**: ~900MB (base + apenas download-car)
- **API Dev**: ~3GB (dev + FastAPI + geopandas)
- **API Pro**: ~1.5GB (pro + FastAPI + geopandas)

## Benefícios

1. **Imagens menores em produção**: Remove PaddleOCR e ferramentas de desenvolvimento
2. **Flexibilidade**: Pode alternar entre dev/pro via variável de ambiente
3. **Compatibilidade**: Funciona com Docker Compose e Makefile
4. **BuildKit**: Utiliza recursos modernos do Docker para builds mais eficientes
5. **Manutenibilidade**: Estrutura clara e organizada

## Migração

### Antes:
```bash
make build
docker compose up
```

### Depois:
```bash
# Desenvolvimento
make build-dev
BASE_IMAGE=download-car-dev:latest docker compose up

# Produção
make build-pro
BASE_IMAGE=download-car-pro:latest docker compose up
```

## Configuração Recomendada

### Para Desenvolvimento (.env):
```bash
BASE_IMAGE=download-car-dev:latest
```

### Para Produção (.env):
```bash
BASE_IMAGE=download-car-pro:latest
``` 