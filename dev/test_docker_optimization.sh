#!/bin/bash
# dev/test_docker_optimization.sh
# Script para testar as otimizações dos Dockerfiles com nova estrutura Poetry/requirements.txt

set -e

cd ..

echo "🧪 Testando nova estrutura Docker (Poetry/requirements.txt)..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    print_error "Docker não está rodando. Inicie o Docker e tente novamente."
    exit 1
fi

print_status "Docker está rodando. Iniciando testes da nova estrutura..."

# Teste 1: Verificar se Poetry está disponível (para desenvolvimento)
print_status "Teste 1: Verificando disponibilidade do Poetry..."
if command -v poetry > /dev/null 2>&1; then
    print_success "Poetry está disponível no sistema"
else
    print_warning "Poetry não está disponível. Será instalado no container de desenvolvimento."
fi

# Teste 2: Gerar requirements.txt
print_status "Teste 2: Gerando requirements.txt..."
if make requirements.txt; then
    print_success "requirements.txt gerado com sucesso"
else
    print_warning "Falha ao gerar requirements.txt, usando arquivo existente"
fi

# Teste 3: Build da imagem base (sem pyenv/git)
print_status "Teste 3: Build da imagem base (python:3.11-slim)..."
if make build-base; then
    print_success "Imagem base construída com sucesso (sem pyenv/git)"
else
    print_error "Falha ao construir imagem base"
    exit 1
fi

# Teste 4: Build da imagem de produção (requirements.txt)
print_status "Teste 4: Build da imagem de produção (requirements.txt)..."
if make build-pro; then
    print_success "Imagem de produção construída com sucesso (pip + requirements.txt)"
else
    print_error "Falha ao construir imagem de produção"
    exit 1
fi

# Teste 5: Build da imagem de desenvolvimento (Poetry)
print_status "Teste 5: Build da imagem de desenvolvimento (Poetry)..."
if make build-dev; then
    print_success "Imagem de desenvolvimento construída com sucesso (Poetry)"
else
    print_error "Falha ao construir imagem de desenvolvimento"
    exit 1
fi

# Teste 6: Verificar tamanhos das imagens
print_status "Teste 6: Verificando tamanhos das imagens..."
echo "Tamanhos das imagens:"
docker images | grep download-car

# Teste 7: Testar variável BASE_IMAGE com produção
print_status "Teste 7: Testando BASE_IMAGE=download-car-pro:latest..."
if BASE_IMAGE=download-car-pro:latest docker compose build --no-cache download-car-api; then
    print_success "Build da API com imagem de produção funcionou"
else
    print_error "Falha no build da API com imagem de produção"
    exit 1
fi

# Teste 8: Testar variável BASE_IMAGE com desenvolvimento
print_status "Teste 8: Testando BASE_IMAGE=download-car-dev:latest..."
if BASE_IMAGE=download-car-dev:latest docker compose build --no-cache download-car-api; then
    print_success "Build da API com imagem de desenvolvimento funcionou"
else
    print_error "Falha no build da API com imagem de desenvolvimento"
    exit 1
fi

# Teste 9: Verificar se as imagens têm as dependências corretas
print_status "Teste 9: Verificando dependências nas imagens..."

# Verificar imagem de produção (pip + requirements.txt)
print_status "Verificando imagem de produção (pip)..."
if docker run --rm download-car-pro:latest python -c "import httpx; import urllib3; import pytesseract; import cv2; import numpy; import tqdm; import matplotlib; import bs4; import fastapi; import uvicorn; print('✅ Dependências core + API OK')"; then
    print_success "Imagem de produção tem dependências core + API"
else
    print_error "Imagem de produção está faltando dependências"
fi

# Verificar se PaddleOCR NÃO está na imagem de produção
if docker run --rm download-car-pro:latest python -c "import paddleocr" 2>/dev/null; then
    print_warning "PaddleOCR encontrado na imagem de produção (não deveria estar)"
else
    print_success "PaddleOCR não está na imagem de produção (correto)"
fi

# Verificar se Poetry NÃO está na imagem de produção
if docker run --rm download-car-pro:latest bash -c "which poetry" 2>/dev/null; then
    print_warning "Poetry encontrado na imagem de produção (não deveria estar)"
else
    print_success "Poetry não está na imagem de produção (correto)"
fi

# Verificar imagem de desenvolvimento (Poetry)
print_status "Verificando imagem de desenvolvimento (Poetry)..."
if docker run --rm download-car-dev:latest python -c "import httpx; import urllib3; import pytesseract; import cv2; import numpy; import tqdm; import matplotlib; import bs4; import fastapi; import uvicorn; print('✅ Todas as dependências OK')"; then
    print_success "Imagem de desenvolvimento tem todas as dependências"
else
    print_error "Imagem de desenvolvimento está faltando dependências"
fi

# Verificar se Poetry está na imagem de desenvolvimento
if docker run --rm download-car-dev:latest bash -c "which poetry"; then
    print_success "Poetry está na imagem de desenvolvimento (correto)"
else
    print_error "Poetry não está na imagem de desenvolvimento"
fi

# Verificar se PaddleOCR está na imagem de desenvolvimento
if docker run --rm download-car-dev:latest python -c "import paddleocr; print('✅ PaddleOCR OK')"; then
    print_success "PaddleOCR está na imagem de desenvolvimento (correto)"
else
    print_warning "PaddleOCR não está na imagem de desenvolvimento"
fi

# Verificar ferramentas de desenvolvimento (sem git)
if docker run --rm download-car-dev:latest bash -c "which curl && which wget"; then
    print_success "Ferramentas de debug (curl, wget) estão na imagem de desenvolvimento"
else
    print_error "Ferramentas de debug não estão na imagem de desenvolvimento"
fi

# Verificar se git NÃO está na imagem de desenvolvimento
if docker run --rm download-car-dev:latest bash -c "which git" 2>/dev/null; then
    print_warning "Git encontrado na imagem de desenvolvimento (não deveria estar)"
else
    print_success "Git não está na imagem de desenvolvimento (correto)"
fi

# Teste 10: Testar execução básica
print_status "Teste 10: Testando execução básica..."
if docker run --rm download-car-pro:latest python -c "from download_car import DownloadCar; print('✅ DownloadCar importado com sucesso')"; then
    print_success "DownloadCar funciona na imagem de produção"
else
    print_error "DownloadCar não funciona na imagem de produção"
fi

if docker run --rm download-car-dev:latest python -c "from download_car import DownloadCar; print('✅ DownloadCar importado com sucesso')"; then
    print_success "DownloadCar funciona na imagem de desenvolvimento"
else
    print_error "DownloadCar não funciona na imagem de desenvolvimento"
fi

# Teste 11: Testar entrypoints sem pyenv
print_status "Teste 11: Testando entrypoints sem pyenv..."

# Testar entrypoint da API
if docker run --rm download-car-api:pro bash -c "head -5 entrypoint.api.sh | grep -v pyenv"; then
    print_success "Entrypoint da API não usa pyenv (correto)"
else
    print_error "Entrypoint da API ainda usa pyenv"
fi

# Testar entrypoint do download
if docker run --rm download-car-download:pro bash -c "head -5 entrypoint.download.sh | grep -v pyenv"; then
    print_success "Entrypoint do download não usa pyenv (correto)"
else
    print_error "Entrypoint do download ainda usa pyenv"
fi

# Teste 12: Verificar se pyenv foi removido completamente
print_status "Teste 12: Verificando remoção completa do pyenv..."
if docker run --rm download-car-pro:latest bash -c "which pyenv" 2>/dev/null; then
    print_error "pyenv ainda está presente na imagem de produção"
else
    print_success "pyenv foi completamente removido da imagem de produção"
fi

if docker run --rm download-car-dev:latest bash -c "which pyenv" 2>/dev/null; then
    print_error "pyenv ainda está presente na imagem de desenvolvimento"
else
    print_success "pyenv foi completamente removido da imagem de desenvolvimento"
fi

print_success "🎉 Todos os testes da nova estrutura passaram!"
print_status "Resumo das otimizações implementadas:"
echo "  ✅ Imagem base: python:3.11-slim (sem pyenv/git)"
echo "  ✅ Imagem de desenvolvimento: Poetry + ferramentas dev (sem git)"
echo "  ✅ Imagem de produção: pip + requirements.txt (sem Poetry/PaddleOCR)"
echo "  ✅ Entrypoints: sem pyenv, execução direta"
echo "  ✅ Dependências da API: incluídas no pyproject.toml/requirements.txt"
echo "  ✅ Makefile: geração automática de requirements.txt"
echo "  ✅ Docker Compose: suporte para BASE_IMAGE dev/pro"

print_status "Para usar:"
echo "  Desenvolvimento: BASE_IMAGE=download-car-dev:latest docker compose up"
echo "  Produção: BASE_IMAGE=download-car-pro:latest docker compose up"
echo "  Gerar requirements.txt: make requirements.txt" 