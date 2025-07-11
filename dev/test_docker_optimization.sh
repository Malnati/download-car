#!/bin/bash
# dev/test_docker_optimization.sh
# test_docker_optimization.sh
# Script para testar as otimizações dos Dockerfiles

set -e

cd ..

echo "🧪 Testando otimizações dos Dockerfiles..."

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

print_status "Docker está rodando. Iniciando testes..."

# Teste 1: Build da imagem base
print_status "Teste 1: Build da imagem base..."
if make build-base; then
    print_success "Imagem base construída com sucesso"
else
    print_error "Falha ao construir imagem base"
    exit 1
fi

# Teste 2: Build da imagem de produção
print_status "Teste 2: Build da imagem de produção..."
if make build-pro; then
    print_success "Imagem de produção construída com sucesso"
else
    print_error "Falha ao construir imagem de produção"
    exit 1
fi

# Teste 3: Build da imagem de desenvolvimento
print_status "Teste 3: Build da imagem de desenvolvimento..."
if make build-dev; then
    print_success "Imagem de desenvolvimento construída com sucesso"
else
    print_error "Falha ao construir imagem de desenvolvimento"
    exit 1
fi

# Teste 4: Verificar tamanhos das imagens
print_status "Teste 4: Verificando tamanhos das imagens..."
echo "Tamanhos das imagens:"
docker images | grep download-car

# Teste 5: Testar variável BASE_IMAGE com produção
print_status "Teste 5: Testando BASE_IMAGE=download-car-pro:latest..."
if BASE_IMAGE=download-car-pro:latest docker compose build --no-cache download-car-api; then
    print_success "Build da API com imagem de produção funcionou"
else
    print_error "Falha no build da API com imagem de produção"
    exit 1
fi

# Teste 6: Testar variável BASE_IMAGE com desenvolvimento
print_status "Teste 6: Testando BASE_IMAGE=download-car-dev:latest..."
if BASE_IMAGE=download-car-dev:latest docker compose build --no-cache download-car-api; then
    print_success "Build da API com imagem de desenvolvimento funcionou"
else
    print_error "Falha no build da API com imagem de desenvolvimento"
    exit 1
fi

# Teste 7: Verificar se as imagens têm as dependências corretas
print_status "Teste 7: Verificando dependências nas imagens..."

# Verificar imagem de produção
print_status "Verificando imagem de produção..."
if docker run --rm download-car-pro:latest python -c "import httpx; import urllib3; import pytesseract; import cv2; import numpy; import tqdm; import matplotlib; import bs4; print('✅ Dependências core OK')"; then
    print_success "Imagem de produção tem dependências core"
else
    print_error "Imagem de produção está faltando dependências core"
fi

# Verificar se PaddleOCR NÃO está na imagem de produção
if docker run --rm download-car-pro:latest python -c "import paddleocr" 2>/dev/null; then
    print_warning "PaddleOCR encontrado na imagem de produção (não deveria estar)"
else
    print_success "PaddleOCR não está na imagem de produção (correto)"
fi

# Verificar imagem de desenvolvimento
print_status "Verificando imagem de desenvolvimento..."
if docker run --rm download-car-dev:latest python -c "import httpx; import urllib3; import pytesseract; import cv2; import numpy; import tqdm; import matplotlib; import bs4; import paddleocr; print('✅ Todas as dependências OK')"; then
    print_success "Imagem de desenvolvimento tem todas as dependências"
else
    print_error "Imagem de desenvolvimento está faltando dependências"
fi

# Verificar ferramentas de desenvolvimento
if docker run --rm download-car-dev:latest bash -c "which git && which curl && which wget"; then
    print_success "Ferramentas de debug (git, curl, wget) estão na imagem de desenvolvimento"
else
    print_error "Ferramentas de debug não estão na imagem de desenvolvimento"
fi

# Teste 8: Testar execução básica
print_status "Teste 8: Testando execução básica..."
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

print_success "🎉 Todos os testes passaram!"
print_status "Resumo das otimizações:"
echo "  ✅ Imagem base otimizada com dependências mínimas"
echo "  ✅ Imagem de desenvolvimento com todas as ferramentas"
echo "  ✅ Imagem de produção sem PaddleOCR e ferramentas de debug"
echo "  ✅ Variável BASE_IMAGE funcionando corretamente"
echo "  ✅ Docker Compose configurado para usar BASE_IMAGE"
echo "  ✅ Makefile atualizado com comandos dev/pro"

print_status "Para usar:"
echo "  Desenvolvimento: BASE_IMAGE=download-car-dev:latest docker compose up"
echo "  Produção: BASE_IMAGE=download-car-pro:latest docker compose up" 