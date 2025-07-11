<!-- README.md -->
# Download CAR files (shape) 

Ferramenta que automatiza o download de arquivos do [Cadastro Ambiental Rural (SICAR)](https://car.gov.br/publico/imoveis/index). Ela é voltada para estudantes, pesquisadores e analistas que precisam acessar shapefiles do sistema de maneira simples.

## Badges

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Pulls](https://img.shields.io/docker/pulls/malnati/download-car)](https://hub.docker.com/r/malnati/download-car)
[![Coverage Status](https://coveralls.io/repos/github/Malnati/download-car/badge.svg?branch=main)](https://coveralls.io/github/Malnati/download-car?branch=main)
[![interrogate](https://img.shields.io/badge/interrogate-documentation-blue.svg)](https://interrogate.readthedocs.io/)
[![translate](https://img.shields.io/badge/Translate-Google-blue.svg)](https://translate.google.com/translate?hl=en&sl=pt&tl=en&u=https://github.com/Malnati/download-car/blob/main/README.md)

# ✨ Objetivo

Permitir o download programático dos dados públicos do SICAR. O projeto inclui drivers para reconhecimento de captcha via **Tesseract** (padrão) ou **PaddleOCR**.

> :globe_with_meridians: **Looking for this README in English?**
>
> Use [Google Translate version](https://translate.google.com/translate?hl=en&sl=pt&tl=en&u=https://github.com/Malnati/download-car/blob/main/README.md) (auto-generated).
>
> This project automates downloads of SICAR shapefiles (Brazilian Rural Environmental Registry), with CLI, Python, Docker, API and Jupyter support. See below for parameter examples, references and data sources.

---

# Índice

- [⚙️ Funções principais](#️-funções-principais)
- [📥 Parâmetros disponíveis](#-parâmetros-disponíveis)
- [🔧 Variáveis de Ambiente](#-variáveis-de-ambiente)
  - [📋 Variáveis de Download](#-variáveis-de-download)
  - [🌐 Variáveis da API](#-variáveis-da-api)
  - [🏠 Variáveis de Propriedades](#-variáveis-de-propriedades)
  - [🌍 Variáveis do Frontend (Nginx)](#-variáveis-do-frontend-nginx)
  - [⏱️ Timeouts por Estado](#️-timeouts-por-estado)
  - [🔧 Variáveis de Configuração do Sistema](#-variáveis-de-configuração-do-sistema)
  - [📷 Variáveis de Configuração OCR](#-variáveis-de-configuração-ocr)
  - [📝 Como Usar as Variáveis de Ambiente](#-como-usar-as-variáveis-de-ambiente)
- [🚀 Como usar](#-como-usar)
  - [1️⃣ Execução via Python (direto)](#1️⃣-execução-via-python-direto)
  - [2️⃣ Execução via Shell Script](#2️⃣-execução-via-shell-script)
  - [3️⃣ Execução via Docker Compose](#3️⃣-execução-via-docker-compose)
  - [4️⃣ Execução via API](#4️⃣-execução-via-api)
    - [Campos esperados (multipart/form)](#campos-esperados-multipartform)
    - [Exemplo via curl](#exemplo-via-curl)
    - [Rodando localmente com FastAPI](#rodando-localmente-com-fastapi)
  - [5️⃣ Importação como módulo Python](#5️⃣-importação-como-módulo-python)
  - [6️⃣ Comandos Makefile](#6️⃣-comandos-makefile)
  - [📓 Suporte ao Jupyter Notebook](#-suporte-ao-jupyter-notebook)
- [🛠️ Ferramentas de Desenvolvimento](#️-ferramentas-de-desenvolvimento)
  - [📋 Scripts de Teste e Verificação](#-scripts-de-teste-e-verificação)
  - [🔧 Ferramentas de Qualidade de Código](#-ferramentas-de-qualidade-de-código)
  - [📦 Dependências Opcionais](#-dependências-opcionais)
  - [🎨 Assets e Recursos](#-assets-e-recursos)
  - [🐳 Configurações Docker Específicas](#-configurações-docker-específicas)
  - [📊 Configurações de Teste](#-configurações-de-teste)
  - [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [📦 Resultados e arquivos de saída](#-resultados-e-arquivos-de-saída)
- [📊 Data dictionary](#data-dictionary)
- [📝 Licença](#license)

```bash
pip install git+https://github.com/Malnati/download-car
```

Prerequisite:

---

# ⚙️ Funções principais

A classe central deste pacote é `DownloadCar`, que disponibiliza três métodos principais:

- `download_state(state, polygon, folder="temp", tries=25, debug=False, chunk_size=1024, timeout=30)`
- `download_country(polygon, folder="brazil", tries=25, debug=False, chunk_size=1024, timeout=30)`
- `get_release_dates()`

---

# 📊 Fontes de Dados

| Fonte                         | Descrição                                   | Link |
|-------------------------------|---------------------------------------------|------|
| Cadastro Ambiental Rural (CAR)| Limites de imóveis rurais                   | [SICAR](https://www.car.gov.br/publico/municipios/downloads) |
| Mapbiomas                     | Uso e cobertura da terra, qualidade da pastagem, etc. | [Mapbiomas](https://mapbiomas.org/colecoes-mapbiomas-1?cama_set_language=pt-BR) |
| Limites Territoriais           | País, estados, municípios (IBGE)            | [IBGE Malhas](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html) |
| Terras Indígenas              | Limites oficiais FUNAI                      | [FUNAI](https://www.gov.br/funai/pt-br/atuacao/terras-indigenas/geoprocessamento-e-mapas) |
| Unidades de Conservação       | Polígonos e tipos do MMA                    | [MMA](http://mapas.mma.gov.br/i3geo/datadownload.htm) |

---

# 📥 Parâmetros disponíveis

| Parâmetro  | Tipo         | Obrigatório | Padrão | Descrição                                                                          | Exemplo Python                      |
|------------|--------------|-------------|--------|------------------------------------------------------------------------------------|-------------------------------------|
| `state`    | `State`/str  | ✅          |  —     | Sigla do estado a ser baixado.                                                     | `state=State.SP`                    |
| `polygon`  | `Polygon`/str| ✅          |  —     | Tipo de camada para download (`APPS`, `AREA_PROPERTY`, etc.).                      | `polygon=Polygon.APPS`              |
| `folder`   | str/`Path`   | ❌          | `"temp"` | Diretório de saída.                                                                | `folder="dados/SP"`                |
| `tries`    | int          | ❌          | `25`   | Número máximo de tentativas em caso de falha.                                      | `tries=10`                          |
| `debug`    | bool         | ❌          | `False`| Exibe mensagens extras de depuração.                                              | `debug=True`                        |
| `chunk_size`| int         | ❌          | `1024` | Tamanho do bloco para escrita do arquivo (em bytes).                               | `chunk_size=2048`                   |
| `timeout`   | int         | ❌          | `30`    | Tempo máximo em segundos para cada tentativa de download.                         | `timeout=60`                     |

Esses parâmetros se aplicam principalmente ao método `download_state`. O método `download_country` utiliza a mesma assinatura (exceto pelo parâmetro `state`).

---

# 🔧 Variáveis de Ambiente

O projeto utiliza diversas variáveis de ambiente para configurar diferentes aspectos da aplicação. Estas variáveis podem ser definidas em arquivos `.env`, passadas diretamente nos comandos Docker ou configuradas no sistema.

## 📋 Variáveis de Download

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `STATE` | string | `"DF"` | Sigla do estado a ser baixado | `STATE=SP` |
| `POLYGON` | string | `"AREA_PROPERTY"` | Tipo de polígono para download | `POLYGON=APPS` |
| `FOLDER` | string | `"data/DF"` | Diretório de saída dos arquivos | `FOLDER=temp/SP` |
| `TRIES` | integer | `25` | Número máximo de tentativas em caso de falha | `TRIES=10` |
| `DEBUG` | boolean | `"False"` | Ativa modo debug com mensagens detalhadas | `DEBUG=true` |
| `TIMEOUT` | integer | `30` | Timeout em segundos para cada tentativa | `TIMEOUT=60` |
| `MAX_RETRIES` | integer | `5` | Número máximo de tentativas para download de cada arquivo | `MAX_RETRIES=10` |

## 🌐 Variáveis da API

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `API_URL` | string | - | URL base da API | `API_URL=http://localhost:8000` |
| `CORS_ALLOW_ORIGINS` | string | `"*"` | Origens permitidas para CORS (separadas por vírgula) | `CORS_ALLOW_ORIGINS=http://localhost:3000,https://example.com` |
| `CORS_ALLOW_CREDENTIALS` | boolean | `"true"` | Permite credenciais em requisições CORS | `CORS_ALLOW_CREDENTIALS=true` |
| `CORS_ALLOW_METHODS` | string | `"GET,POST,OPTIONS"` | Métodos HTTP permitidos para CORS | `CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS` |
| `CORS_ALLOW_HEADERS` | string | `"*"` | Headers permitidos para CORS | `CORS_ALLOW_HEADERS=Content-Type,Authorization` |

## 🏠 Variáveis de Propriedades

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `PROPERTY_FOLDER` | string | `"PROPERTY"` | Pasta para armazenamento de arquivos de propriedades | `PROPERTY_FOLDER=properties` |
| `PROPERTY_TRIES` | integer | `25` | Número máximo de tentativas para download de propriedades | `PROPERTY_TRIES=10` |
| `PROPERTY_DEBUG` | boolean | `"false"` | Ativa modo debug para downloads de propriedades | `PROPERTY_DEBUG=true` |
| `PROPERTY_TIMEOUT` | integer | `30` | Timeout em segundos para downloads de propriedades | `PROPERTY_TIMEOUT=60` |
| `PROPERTY_MAX_RETRIES` | integer | `5` | Número máximo de tentativas para cada propriedade | `PROPERTY_MAX_RETRIES=10` |

## 🌍 Variáveis do Frontend (Nginx)

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `API_ENDPOINT_URL` | string | `"http://192.168.5.179:8787"` | URL do endpoint da API | `API_ENDPOINT_URL=http://localhost:8000` |
| `DEFAULT_POLYGON` | string | `"AREA_PROPERTY"` | Polígono padrão selecionado no frontend | `DEFAULT_POLYGON=APPS` |
| `DEFAULT_TIMEOUT` | integer | `800000` | Timeout padrão em milissegundos | `DEFAULT_TIMEOUT=600000` |
| `TIMEOUT_INCREMENT` | integer | `10000` | Incremento do timeout em milissegundos | `TIMEOUT_INCREMENT=5000` |
| `MIN_TIMEOUT` | integer | `10000` | Timeout mínimo em milissegundos | `MIN_TIMEOUT=5000` |
| `MAX_TIMEOUT` | integer | `300000` | Timeout máximo em milissegundos | `MAX_TIMEOUT=600000` |
| `API_HOST` | string | - | Host da API | `API_HOST=localhost` |
| `API_PORT` | string | - | Porta da API | `API_PORT=8000` |
| `API_PATH` | string | - | Caminho base da API | `API_PATH=/api` |
| `NETWORK_TIMEOUT` | integer | - | Timeout de rede em milissegundos | `NETWORK_TIMEOUT=30000` |

## ⏱️ Timeouts por Estado

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `STATE_TIMEOUT_AC` | integer | `60000` | Timeout específico para Acre | `STATE_TIMEOUT_AC=120000` |
| `STATE_TIMEOUT_AL` | integer | `60000` | Timeout específico para Alagoas | `STATE_TIMEOUT_AL=90000` |
| `STATE_TIMEOUT_AM` | integer | `60000` | Timeout específico para Amazonas | `STATE_TIMEOUT_AM=180000` |
| `STATE_TIMEOUT_AP` | integer | `60000` | Timeout específico para Amapá | `STATE_TIMEOUT_AP=120000` |
| `STATE_TIMEOUT_BA` | integer | `60000` | Timeout específico para Bahia | `STATE_TIMEOUT_BA=150000` |
| `STATE_TIMEOUT_CE` | integer | `60000` | Timeout específico para Ceará | `STATE_TIMEOUT_CE=120000` |
| `STATE_TIMEOUT_DF` | integer | `60000` | Timeout específico para Distrito Federal | `STATE_TIMEOUT_DF=60000` |
| `STATE_TIMEOUT_ES` | integer | `60000` | Timeout específico para Espírito Santo | `STATE_TIMEOUT_ES=90000` |
| `STATE_TIMEOUT_GO` | integer | `60000` | Timeout específico para Goiás | `STATE_TIMEOUT_GO=120000` |
| `STATE_TIMEOUT_MA` | integer | `60000` | Timeout específico para Maranhão | `STATE_TIMEOUT_MA=150000` |
| `STATE_TIMEOUT_MG` | integer | `60000` | Timeout específico para Minas Gerais | `STATE_TIMEOUT_MG=180000` |
| `STATE_TIMEOUT_MS` | integer | `60000` | Timeout específico para Mato Grosso do Sul | `STATE_TIMEOUT_MS=120000` |
| `STATE_TIMEOUT_MT` | integer | `60000` | Timeout específico para Mato Grosso | `STATE_TIMEOUT_MT=180000` |
| `STATE_TIMEOUT_PA` | integer | `60000` | Timeout específico para Pará | `STATE_TIMEOUT_PA=240000` |
| `STATE_TIMEOUT_PB` | integer | `60000` | Timeout específico para Paraíba | `STATE_TIMEOUT_PB=90000` |
| `STATE_TIMEOUT_PE` | integer | `60000` | Timeout específico para Pernambuco | `STATE_TIMEOUT_PE=120000` |
| `STATE_TIMEOUT_PI` | integer | `60000` | Timeout específico para Piauí | `STATE_TIMEOUT_PI=120000` |
| `STATE_TIMEOUT_PR` | integer | `60000` | Timeout específico para Paraná | `STATE_TIMEOUT_PR=150000` |
| `STATE_TIMEOUT_RJ` | integer | `60000` | Timeout específico para Rio de Janeiro | `STATE_TIMEOUT_RJ=120000` |
| `STATE_TIMEOUT_RN` | integer | `60000` | Timeout específico para Rio Grande do Norte | `STATE_TIMEOUT_RN=90000` |
| `STATE_TIMEOUT_RO` | integer | `60000` | Timeout específico para Rondônia | `STATE_TIMEOUT_RO=120000` |
| `STATE_TIMEOUT_RR` | integer | `60000` | Timeout específico para Roraima | `STATE_TIMEOUT_RR=120000` |
| `STATE_TIMEOUT_RS` | integer | `60000` | Timeout específico para Rio Grande do Sul | `STATE_TIMEOUT_RS=150000` |
| `STATE_TIMEOUT_SC` | integer | `60000` | Timeout específico para Santa Catarina | `STATE_TIMEOUT_SC=120000` |
| `STATE_TIMEOUT_SE` | integer | `60000` | Timeout específico para Sergipe | `STATE_TIMEOUT_SE=90000` |
| `STATE_TIMEOUT_SP` | integer | `60000` | Timeout específico para São Paulo | `STATE_TIMEOUT_SP=180000` |
| `STATE_TIMEOUT_TO` | integer | `60000` | Timeout específico para Tocantins | `STATE_TIMEOUT_TO=120000` |

## 🔧 Variáveis de Configuração do Sistema

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `BASE_IMAGE` | string | `"download-car-pro:latest"` | Imagem base para containers (dev/pro) | `BASE_IMAGE=download-car-dev:latest` |
| `PRELOAD_MODELS` | boolean | - | Habilita pré-carregamento dos modelos do PaddleOCR durante build | `PRELOAD_MODELS=1` |
| `DOCKER_CONFIG` | string | `/tmp/docker-config-noauth` | Configuração do Docker para builds | `DOCKER_CONFIG=/path/to/docker/config` |
| `PYTHON_VERSION` | string | `"3.11.9"` | Versão do Python utilizada no container | `PYTHON_VERSION=3.11.9` |

## 📷 Variáveis de Configuração OCR

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `TESSERACT_CONFIG` | string | `"--oem 3 --psm 8"` | Configuração do Tesseract OCR para reconhecimento de captcha | `TESSERACT_CONFIG="--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"` |
| `PADDLE_OCR_LANG` | string | `"en"` | Idioma para reconhecimento PaddleOCR | `PADDLE_OCR_LANG=pt` |
| `PADDLE_OCR_USE_GPU` | boolean | `"false"` | Habilita uso de GPU para PaddleOCR | `PADDLE_OCR_USE_GPU=true` |
| `PADDLE_OCR_SHOW_LOG` | boolean | `"false"` | Exibe logs do PaddleOCR | `PADDLE_OCR_SHOW_LOG=true` |

## 📝 Como Usar as Variáveis de Ambiente

### 1. Arquivo .env (Recomendado)

Crie um arquivo `.env` na raiz do projeto:

```bash
# Variáveis de Download
STATE=SP
POLYGON=APPS
FOLDER=temp/SP
TRIES=25
DEBUG=false
TIMEOUT=30
MAX_RETRIES=5

# Variáveis da API
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=*

# Variáveis de Propriedades
PROPERTY_FOLDER=PROPERTY
PROPERTY_TRIES=25
PROPERTY_DEBUG=false
PROPERTY_TIMEOUT=30
PROPERTY_MAX_RETRIES=5

# Variáveis do Frontend
API_ENDPOINT_URL=http://localhost:8000
DEFAULT_POLYGON=AREA_PROPERTY
DEFAULT_TIMEOUT=800000
TIMEOUT_INCREMENT=10000
MIN_TIMEOUT=10000
MAX_TIMEOUT=300000

# Timeouts por Estado (exemplos)
STATE_TIMEOUT_SP=180000
STATE_TIMEOUT_PA=240000
STATE_TIMEOUT_AM=180000

# Configurações OCR
TESSERACT_CONFIG=--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
PADDLE_OCR_LANG=en
PADDLE_OCR_USE_GPU=false
PADDLE_OCR_SHOW_LOG=false

### 2. Linha de Comando

```bash
# Docker Compose com variáveis
STATE=SP POLYGON=APPS docker compose up

# Makefile com variáveis
make download state=SP polygon=APPS folder=temp/SP debug=true

# Build com pré-carregamento de modelos
PRELOAD_MODELS=1 make build
```

### 3. Docker Compose

```yaml
version: '3.8'
services:
  download-car-api:
    environment:
      - CORS_ALLOW_ORIGINS=http://localhost:3000
      - PROPERTY_FOLDER=properties
      - PROPERTY_TIMEOUT=60
```

### 4. Configuração de Timeouts por Estado

Para estados com muitos dados (como PA, AM, MT), configure timeouts maiores:

```bash
# Estados com muitos dados
STATE_TIMEOUT_PA=240000  # 4 minutos
STATE_TIMEOUT_AM=180000  # 3 minutos
STATE_TIMEOUT_MT=180000  # 3 minutos

# Estados com dados moderados
STATE_TIMEOUT_SP=180000  # 3 minutos
STATE_TIMEOUT_MG=180000  # 3 minutos
STATE_TIMEOUT_BA=150000  # 2.5 minutos

# Estados com dados menores
STATE_TIMEOUT_DF=60000   # 1 minuto
STATE_TIMEOUT_AL=90000   # 1.5 minutos
STATE_TIMEOUT_SE=90000   # 1.5 minutos
```

### 5. Configuração de OCR

Para otimizar o reconhecimento de captcha, configure as variáveis OCR:

```bash
# Configuração do Tesseract (padrão)
TESSERACT_CONFIG="--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Configuração do PaddleOCR
PADDLE_OCR_LANG=en
PADDLE_OCR_USE_GPU=false
PADDLE_OCR_SHOW_LOG=false

# Para melhor performance com GPU
PADDLE_OCR_USE_GPU=true

# Para debug de reconhecimento
PADDLE_OCR_SHOW_LOG=true
```

**Dicas de configuração OCR:**

- **Tesseract**: Use `--psm 8` para reconhecimento de texto único
- **PaddleOCR**: Configure `PADDLE_OCR_LANG=pt` para português
- **GPU**: Habilite `PADDLE_OCR_USE_GPU=true` se disponível
- **Debug**: Use `PADDLE_OCR_SHOW_LOG=true` para diagnosticar problemas

---

# 🚀 Como usar

## 1️⃣ Execução via Python (direto)

```python
from download_car import DownloadCar, State, Polygon

car = DownloadCar()
car.download_state(state=State.PA, polygon=Polygon.APPS, folder="PA")
```

## 2️⃣ Execução via Shell Script

O repositório inclui o script `download_state.sh` que facilita a configuração do
ambiente e a execução do exemplo `download_state.py`. Basta informar os
parâmetros desejados:

```bash
./download_state.sh --state DF --polygon APPS --folder data/DF --tries 25 --debug True
```

O script irá garantir que a versão correta do Python esteja disponível via
`pyenv`, criar um ambiente virtual e executar o exemplo com as variáveis de
ambiente apropriadas.

## 3️⃣ Execução via Docker Compose

O repositório possui um `docker-compose.yml` configurado com três serviços e suporte a imagens otimizadas:

#### Estrutura dos Dockerfiles:
- **Dockerfile.base** - Imagem base com dependências mínimas
- **Dockerfile.dev** - Desenvolvimento (base + PaddleOCR + ferramentas)
- **Dockerfile.pro** - Produção (base + apenas download-car)
- **Dockerfile.api** - API (estende dev ou pro conforme BASE_IMAGE)
- **Dockerfile.download-car** - Download (estende dev ou pro conforme BASE_IMAGE)

#### Configuração via Variável de Ambiente:
```bash
# Para desenvolvimento (com PaddleOCR e ferramentas)
BASE_IMAGE=download-car-dev:latest docker compose up

# Para produção (otimizado, sem PaddleOCR)
BASE_IMAGE=download-car-pro:latest docker compose up

# Ou via arquivo .env
echo "BASE_IMAGE=download-car-pro:latest" > .env
docker compose up
```

#### Build das Imagens:

```bash
# Build de desenvolvimento (com todas as ferramentas)
make build-dev

# Build de produção (otimizado)
make build-pro

# Build apenas da imagem base
make build-base
```

#### Serviços:
* **download-car-download** – roda o script `entrypoint.download.sh` para baixar os arquivos
  desejados. Defina as variáveis `STATE`, `POLYGON` e `FOLDER` conforme a
  necessidade.
* **download-car-api** – executa o `uvicorn` servindo a aplicação FastAPI em
  `http://localhost:8000`.
* **nginx** – expõe a porta `8787` e redireciona requisições para a API.

#### Tamanhos Estimados:
- **Base**: ~800MB (Python + dependências core)
- **Dev**: ~2.5GB (base + PaddleOCR + ferramentas)
- **Pro**: ~900MB (base + apenas download-car)
- **API Dev**: ~3GB (dev + FastAPI + geopandas)
- **API Pro**: ~1.5GB (pro + FastAPI + geopandas)

A API poderá ser acessada em `http://localhost:8787` via Nginx.

## 4️⃣ Execução via API

A API FastAPI está disponível em `http://localhost:8000` e oferece os seguintes endpoints:

### Endpoints de Download
- `POST /download_state` &ndash; recebe `state` e `polygon` (além dos
  parâmetros opcionais) e retorna um arquivo ZIP com o shapefile do estado.
- `POST /download_country` &ndash; recebe apenas `polygon` e retorna um ZIP
  contendo os arquivos de todos os estados.
- `POST /download-property` &ndash; baixa dados de uma propriedade específica pelo número do CAR.

### Endpoints de Busca
- `GET /state` &ndash; busca o estado de um imóvel pelo número do CAR.
- `GET /property` &ndash; busca uma propriedade específica pelo número do CAR.

### Endpoints de Informação
- `GET /states` &ndash; retorna a lista completa de estados brasileiros disponíveis.
- `GET /polygons` &ndash; retorna a lista completa de tipos de polígonos disponíveis.
- `GET /` &ndash; página inicial da API com informações gerais.

### Endpoints de Status e Gerenciamento
- `GET /state_status/{state}` &ndash; verifica se existe arquivo baixado para um estado específico.
- `GET /download_state_file/{state}/{polygon_type}` &ndash; faz download de um arquivo específico de estado.
- `DELETE /delete_state` &ndash; exclui todos os arquivos relacionados a um estado específico.

### Campos esperados (multipart/form)

#### POST /download_state
- `state` (obrigatório): Sigla do estado (ex: "SP", "RJ", "MG")
- `polygon` (opcional): Tipo de polígono (padrão: "AREA_PROPERTY")
- `folder` (opcional): Pasta de destino (padrão: "temp")
- `tries` (opcional): Número de tentativas (padrão: 25)
- `debug` (opcional): Modo debug (padrão: false)
- `timeout` (opcional): Timeout em segundos (padrão: 30)
- `max_retries` (opcional): Máximo de retry (padrão: 5)

#### POST /download_country
- `polygon` (opcional): Tipo de polígono (padrão: "AREA_PROPERTY")
- `folder` (opcional): Pasta de destino (padrão: "brazil")
- `tries` (opcional): Número de tentativas (padrão: 25)
- `debug` (opcional): Modo debug (padrão: false)
- `timeout` (opcional): Timeout em segundos (padrão: 30)
- `max_retries` (opcional): Máximo de retry (padrão: 5)

#### DELETE /delete_state
- `state` (obrigatório): Sigla do estado a ser excluído (ex: "SP", "RJ", "MG")
- `folder` (opcional): Pasta onde estão os arquivos (padrão: "temp")
- `include_properties` (opcional): Se deve excluir também arquivos de propriedades (padrão: true)

### Exemplo via curl

```bash
# Download de um estado
curl -X POST "http://localhost:8000/download_state" \
     -F "state=SP" \
     -F "polygon=APPS" \
     -F "folder=temp" \
     -F "tries=25" \
     -F "debug=false" \
     --output SP_APPS.zip

# Download de todo o país
curl -X POST "http://localhost:8000/download_country" \
     -F "polygon=AREA_PROPERTY" \
     -F "folder=brazil" \
     -F "tries=25" \
     -F "debug=false" \
     --output brazil_AREA_PROPERTY.zip

# Excluir arquivos de um estado
curl -X DELETE "http://localhost:8000/delete_state" \
     -F "state=SP" \
     -F "folder=temp" \
     -F "include_properties=true"
```

### Rodando localmente com FastAPI

Execute o script `api.sh` para iniciar um servidor FastAPI local:

```bash
./api.sh
```

O script cria um ambiente virtual via `pyenv`, instala as dependências
necessárias e disponibiliza o serviço em `http://localhost:8000`.

Rotas disponíveis:

- `POST /download_state` &ndash; recebe `state` e `polygon` (além dos
  parâmetros opcionais) e retorna um arquivo ZIP com o shapefile do estado.
- `POST /download_country` &ndash; recebe apenas `polygon` e retorna um ZIP
  contendo os arquivos de todos os estados.

## 5️⃣ Importação como módulo Python

Após instalar com `pip install git+https://github.com/Malnati/download-car`, basta importar e usar:

```python
from download_car import DownloadCar, State, Polygon

car = DownloadCar()
car.download_state(State.MG, Polygon.LEGAL_RESERVE, folder="MG")
```

## 📓 Suporte ao Jupyter Notebook

O projeto é compatível com Jupyter Notebooks para análise de dados geoespaciais:

```python
# Em um Jupyter Notebook
import geopandas as gpd
from download_car import DownloadCar, State, Polygon

# Baixar dados
car = DownloadCar()
car.download_state(State.SP, Polygon.AREA_PROPERTY, folder="notebook_data")

# Carregar e analisar dados
gdf = gpd.read_file("notebook_data/SP_AREA_IMOVEL.zip")
print(f"Total de propriedades: {len(gdf)}")
print(f"Área total: {gdf['num_area'].sum():.2f} hectares")

# Visualizar dados
gdf.plot(column='num_area', legend=True, figsize=(12, 8))
```

### Dependências para Jupyter
```bash
# Instalar dependências para análise geoespacial
pip install jupyter geopandas matplotlib folium

# Ou usar o ambiente completo
pip install "download-car[all]"
```

## 6️⃣ Comandos Makefile

O projeto inclui um Makefile com diversos comandos úteis para facilitar o desenvolvimento e uso:

### 🚀 Comandos de inicialização:
- `make up` - Inicia todos os serviços
- `make api-up` - Inicia apenas o serviço API
- `make download-up` - Inicia apenas o serviço download-car

### 🛠️ Comandos de build:
- `make build` - Builda todas as imagens (produção)
- `make build-dev` - Builda todas as imagens (desenvolvimento)
- `make build-pro` - Builda todas as imagens (produção)
- `make build-base` - Builda a imagem base
- `make build-api` - Builda apenas a imagem da API (produção)
- `make build-api-dev` - Builda apenas a imagem da API (desenvolvimento)
- `make build-api-pro` - Builda apenas a imagem da API (produção)
- `make build-download` - Builda apenas a imagem de download (produção)
- `make build-download-dev` - Builda apenas a imagem de download (desenvolvimento)
- `make build-download-pro` - Builda apenas a imagem de download (produção)

### 🗑️ Comandos de limpeza:
- `make clean` - Remove imagens, volumes e containers órfãos
- `make clean-volumes` - Remove volumes Docker, incluindo arquivos montados
- `make clean-api` - Remove apenas a imagem da API
- `make clean-image` - Remove apenas a imagem principal

### 🛑 Comandos de controle:
- `make down` - Para e remove containers
- `make ps` - Lista containers e serviços
- `make logs service=X` - Exibe logs do serviço especificado

### 🔗 Comandos de acesso:
- `make shell` - Entra no container principal
- `make shell-api` - Entra no container da API
- `make run CMD=X` - Executa comando no container
- `make run-api` - Executa container da API

### 🧪 Comandos de teste:
- `make test` - Executa todos os testes
- `make unit-test` - Executa testes unitários
- `make integration-test` - Executa testes de integração

### 📥 Comandos de download:
- `make download state=X polygon=Y folder=Z debug=W timeout=T max_retries=R` - Executa download com parâmetros específicos
- `make search-car car=X` - Busca estado do CAR
- `make download-property car=X` - Baixa propriedade do CAR

### 🔄 Comandos de manutenção:
- `make git-update` - Atualiza repositório Git

### 🛠️ Comandos de desenvolvimento:
- `make format` - Formata código com Black
- `make lint` - Verifica estilo do código
- `make docs` - Gera documentação com Interrogate
- `make coverage` - Executa testes com cobertura

Para ver todos os comandos disponíveis:

```bash
make help
```

---

# 🛠️ Ferramentas de Desenvolvimento

O projeto inclui diversas ferramentas para desenvolvimento, teste e qualidade de código.

## 📋 Scripts de Teste e Verificação

### Scripts de Teste da API

| Script | Descrição | Uso |
|--------|-----------|-----|
| `verify_features.sh` | Testa todos os endpoints da API | `./verify_features.sh` |
| `test_delete_state.py` | Testa o endpoint DELETE /delete_state | `python test_delete_state.py` |
| `verify_property.py` | Verifica e compara arquivos de propriedades | `python verify_property.py --state data/SP_AREA_PROPERTY.zip --property data/property_SP-123.zip` |

### Exemplos de Uso dos Scripts

```bash
# Testar todos os endpoints da API
./verify_features.sh

# Testar exclusão de arquivos de estado
python test_delete_state.py

# Verificar arquivos de propriedades
python verify_property.py \
  --state data/MA_AREA_PROPERTY.zip \
  --property data/property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip \
  --verbose
```

## 🔧 Ferramentas de Qualidade de Código

### Black (Formatação)
```bash
# Formatar código automaticamente
black download_car/

# Verificar se o código está formatado
black --check download_car/
```

### Interrogate (Documentação)
```bash
# Gerar documentação
interrogate download_car/

# Verificar cobertura de documentação
interrogate --fail-under 80 download_car/
```

### Coverage (Cobertura de Testes)
```bash
# Executar testes com cobertura
coverage run -m unittest discover download_car/tests/
coverage report
coverage html  # Gera relatório HTML
```

## 📦 Dependências Opcionais

O projeto suporta dependências opcionais para diferentes casos de uso:

```bash
# Instalação básica
pip install download-car

# Com suporte ao PaddleOCR
pip install "download-car[paddle]"

# Com ferramentas de desenvolvimento
pip install "download-car[dev]"

# Com todas as dependências
pip install "download-car[all]"
```

### Dependências por Categoria

| Categoria | Dependências | Descrição |
|-----------|--------------|-----------|
| `paddle` | `paddlepaddle>=3.0.0`, `paddleocr>=2.10.0` | Suporte ao PaddleOCR para reconhecimento de captcha |
| `dev` | `coverage`, `interrogate`, `black`, `coveralls` | Ferramentas de desenvolvimento e qualidade |
| `all` | Todas as dependências | Instalação completa com todas as funcionalidades |

## 🎨 Assets e Recursos

O projeto inclui recursos visuais para o frontend:

### Bandeiras dos Estados
- Localização: `assets/flags/`
- Formato: PNG
- Estados disponíveis: Todos os 27 estados brasileiros (AC.png, AL.png, AM.png, etc.)

### Estrutura de Assets
```
assets/
└── flags/
    ├── AC.png  # Acre
    ├── AL.png  # Alagoas
    ├── AM.png  # Amazonas
    └── ...     # Todos os estados
```

## 🐳 Configurações Docker Específicas

### Dockerfile.nginx
- Base: `nginx:alpine`
- Instala Node.js para geração dinâmica de configuração
- Scripts: `entrypoint.nginx.sh`, `generate-config.nginx.js`

### Dockerfile.api
- Base: `download-car-base:latest`
- Dependências: FastAPI, Uvicorn, httpx, Pillow, tqdm, python-multipart
- Entrypoint: `entrypoint.api.sh`

### Dockerfile.base
- Base: `ubuntu:22.04`
- Python: 3.11.9 via pyenv
- Dependências: Tesseract OCR, OpenCV
- Instalação: `download_car[paddle]`

### Arquivos de Configuração
- `.dockerignore`: Exclui `.git`, `__pycache__`, `.venv*`, `tests`
- `entrypoint.nginx.sh`: Substitui variáveis de ambiente no nginx.conf
- `entrypoint.api.sh`: Configura ambiente Python e inicia API
- `generate-config.nginx.js`: Gera configuração do frontend dinamicamente

## 📊 Configurações de Teste

### Cobertura de Código
- Configuração: `pyproject.toml`
- Meta: 100% de cobertura
- Exclusões: `download_car/tests/integration/*`
- Relatórios: HTML, XML, Coveralls

### Documentação
- Ferramenta: Interrogate
- Meta: 100% de documentação
- Exclusões: `download_car/tests*`
- Badge: `.github`

### Formatação
- Ferramenta: Black
- Configuração: Padrão do Black
- Badge: Status no README

## 📁 Estrutura do Projeto

```
download-car/
├── download_car/                 # Módulo principal
│   ├── __init__.py
│   ├── sicar.py                  # Classe principal DownloadCar
│   ├── state.py                  # Enumeração dos estados
│   ├── polygon.py                # Enumeração dos polígonos
│   ├── url.py                    # Geração de URLs
│   ├── exceptions.py             # Exceções customizadas
│   └── drivers/                  # Drivers de OCR
│       ├── __init__.py
│       ├── captcha.py            # Classe base para captcha
│       ├── tesseract.py          # Driver Tesseract
│       └── paddle.py             # Driver PaddleOCR
├── download_car/tests/           # Testes
│   ├── unit/                     # Testes unitários
│   └── integration/              # Testes de integração
├── assets/                       # Recursos do frontend
│   └── flags/                    # Bandeiras dos estados
├── app.py                        # API FastAPI
├── download_state.py             # Script de download
├── download_state.sh             # Script shell
├── api.sh                        # Script da API
├── verify_features.sh            # Script de teste da API
├── verify_property.py            # Script de verificação
├── test_delete_state.py          # Script de teste
├── docker-compose.yml            # Configuração Docker Compose
├── Dockerfile.*                  # Dockerfiles específicos
├── entrypoint.*.sh               # Scripts de entrada
├── generate-config.nginx.js      # Geração de configuração
├── nginx.conf.template           # Template do Nginx
├── index.html                    # Frontend
├── Makefile                      # Comandos de automação
├── pyproject.toml                # Configuração do projeto
└── README.md                     # Esta documentação
```

### Arquivos de Configuração Importantes

| Arquivo | Descrição |
|---------|-----------|
| `pyproject.toml` | Configuração do projeto Python, dependências, ferramentas |
| `docker-compose.yml` | Orquestração dos serviços Docker |
| `Makefile` | Automação de comandos comuns |
| `.env` | Variáveis de ambiente (criar localmente) |
| `.gitignore` | Arquivos ignorados pelo Git |
| `.dockerignore` | Arquivos ignorados pelo Docker |

---

# 📦 Resultados e arquivos de saída

O download gera um arquivo `.zip` contendo os shapefiles correspondentes. Exemplo de estrutura:

```plain
data.zip
├── dados.shp
├── dados.shx
├── dados.dbf
└── dados.prj
```

# Data dictionary

| **Atributo**  | **Descrição**                                                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| cod_estado    | Unidade da Federação onde o cadastro está localizado.                                                                                     |
| municipio     | Município onde o cadastro está localizado.                                                                                                |
| num_area      | Área bruta do imóvel rural ou do assunto que compõe o cadastro, em hectares.                                                              |
| cod_imovel    | Número de inscrição no Cadastro Ambiental Rural (CAR).                                                                                   |
| ind_status    | Situação do cadastro no CAR, conforme a Instrução Normativa nº 2, de 6 de maio de 2014, do Ministério do Meio Ambiente (https://www.car.gov.br/leis/IN_CAR.pdf), e a Resolução nº 3, de 27 de agosto de 2018, do Serviço Florestal Brasileiro (https://imprensanacional.gov.br/materia/-/asset_publisher/Kujrw0TZC2Mb/content/id/38537086/do1-2018-08-28-resolucao-n-3-de-27-de-agos-de-2018-38536774), sendo AT - Ativo; PE - Pendente; SU - Suspenso; e CA - Cancelado. |
| des_condic    | Condição em que o cadastro se encontra no fluxo de análise pelo órgão competente.                                                         |
| ind_tipo      | Tipo de Imóvel Rural, podendo ser IRU - Imóvel Rural; AST - Assentamentos de Reforma Agrária; PCT - Território de Povos e Comunidades Tradicionais. |
| mod_fiscal    | Número de módulos fiscais do imóvel rural.                                                                                                |
| nom_tema      | Nome do tema que compõe o cadastro (Área de Preservação Permanente, Caminho, Remanescente de Vegetação Nativa, Área de Uso Restrito, Servidão Administrativa, Reserva Legal, Hidrografia, Áreas Úmidas, Área Rural Consolidada, Áreas com Altitude Superior a 1800 metros, Áreas com Declividade Superior a 45 graus, Topos de Morro, Bordas de Chapada, Áreas em Pousio, Manguezal e Restinga). |

---

## Acknowledgements

- [Sicar - Sistema Nacional de Cadastro Ambiental Rural](https://www.car.gov.br/)
- [Sicar - Base de Downloads](https://consultapublica.car.gov.br/publico/estados/downloads)

## Roadmap

- [ ] Upload to pypi registry

## Contributing

The development environment with all necessary packages is available using [Visual Studio Code Dev Containers](https://code.visualstudio.com/docs/remote/containers).

[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Malnati/download-car)

Contributions are always welcome!

## Feedback

If you have any feedback, please reach me at ricardomalnati@gmail.com

# ❓ FAQ

**Como faço para baixar todos os estados automaticamente?**
- Use um loop shell com o script, ou modifique os exemplos para percorrer todos os códigos de estado.

**Como saber se o download terminou corretamente?**
- O script gera logs e arquivos zip por estado. Verifique os diretórios de saída.

**Posso contribuir?**
- Sim! Veja a seção "Contributing". Issues e pull requests são bem-vindos.

**Como resolver problemas de captcha?**
- Verifique se o Tesseract OCR está instalado: `tesseract --version`
- Para melhor precisão, use PaddleOCR: `pip install "download-car[paddle]"`
- Configure timeouts maiores para estados com muitos dados

**Como debugar problemas de download?**
- Ative o modo debug: `DEBUG=true`
- Verifique logs do container: `docker compose logs download-car-download`
- Use o script de verificação: `./verify_features.sh`

**Como configurar para produção?**
- Use variáveis de ambiente específicas para produção
- Configure timeouts adequados para seu ambiente
- Monitore logs e métricas da API

# License

[MIT](LICENSE)

Se utilizar este projeto, cite: **Urbano, Gilson**. *download-car Package*. Consulte o arquivo [CITATION.cff](CITATION.cff) para mais detalhes.
