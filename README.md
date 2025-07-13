<!-- README.md -->
# Download CAR files (shape) 


> :globe_with_meridians: **Looking for this README in English?**
>
> Use [Google Translate version](https://translate.google.com/translate?hl=en&sl=pt&tl=en&u=https://github.com/Malnati/download-car/blob/main/README.md) (auto-generated).
>
> This project automates downloads of SICAR shapefiles (Brazilian Rural Environmental Registry), with CLI, Python, Docker, API and Jupyter support. See below for parameter examples, references and data sources.


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

## 🐳 Arquitetura Docker

O projeto utiliza uma arquitetura Docker modular e otimizada:

### 🏗️ Estrutura da Arquitetura
- **Imagem Base Otimizada**: `python:3.11-slim` com dependências core
- **Builds Separados**: Desenvolvimento e produção com dependências específicas
- **Arquitetura Modular**: Cada serviço tem seu próprio Dockerfile
- **Configuração Dinâmica**: Nginx com Node.js para configuração em tempo real
- **Geração Automática**: `requirements.txt` gerado do `pyproject.toml`
- **Tamanhos Otimizados**: Imagens menores e mais eficientes

### 🚀 Benefícios
- **Desenvolvimento**: Imagem completa com todas as ferramentas
- **Produção**: Imagem otimizada sem dependências desnecessárias
- **Flexibilidade**: Escolha entre dev/pro via variável de ambiente
- **Manutenibilidade**: Estrutura clara e organizada
- **Performance**: Builds mais rápidos e imagens menores

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
  - [🗄️ Variáveis do Banco de Dados PostgreSQL/PostGIS](#️-variáveis-do-banco-de-dados-postgresqlpostgis)
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
pip install download-car
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
| SICAR - Consulta Pública      | Base de dados principal do sistema          | [Consulta Pública](https://consultapublica.car.gov.br/publico/imoveis/index) |
| SICAR - Downloads por Estado  | Downloads de shapefiles por estado          | [Downloads](https://consultapublica.car.gov.br/publico/estados/downloads) |
| SICAR - ReCaptcha             | Sistema de captcha para downloads           | [ReCaptcha](https://consultapublica.car.gov.br/publico/municipios/ReCaptcha) |
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
| `max_retries`| int        | ❌          | `5`     | Número máximo de tentativas para download de cada arquivo.                        | `max_retries=10`                    |

### 📋 Valores Disponíveis para Estados

| Estado | Sigla | Nome Completo | Timeout Padrão (ms) | Exemplo |
|--------|-------|---------------|-------------------|---------|
| AC | Acre | Acre | 60000 | `State.AC` |
| AL | Alagoas | Alagoas | 120000 | `State.AL` |
| AM | Amazonas | Amazonas | 60000 | `State.AM` |
| AP | Amapá | Amapá | 60000 | `State.AP` |
| BA | Bahia | Bahia | 600000 | `State.BA` |
| CE | Ceará | Ceará | 240000 | `State.CE` |
| DF | Distrito Federal | Distrito Federal | 60000 | `State.DF` |
| ES | Espírito Santo | Espírito Santo | 120000 | `State.ES` |
| GO | Goiás | Goiás | 300000 | `State.GO` |
| MA | Maranhão | Maranhão | 180000 | `State.MA` |
| MG | Minas Gerais | Minas Gerais | 300000 | `State.MG` |
| MS | Mato Grosso do Sul | Mato Grosso do Sul | 60000 | `State.MS` |
| MT | Mato Grosso | Mato Grosso | 60000 | `State.MT` |
| PA | Pará | Pará | 120000 | `State.PA` |
| PB | Paraíba | Paraíba | 60000 | `State.PB` |
| PE | Pernambuco | Pernambuco | 180000 | `State.PE` |
| PI | Piauí | Piauí | 60000 | `State.PI` |
| PR | Paraná | Paraná | 120000 | `State.PR` |
| RJ | Rio de Janeiro | Rio de Janeiro | 120000 | `State.RJ` |
| RN | Rio Grande do Norte | Rio Grande do Norte | 60000 | `State.RN` |
| RO | Rondônia | Rondônia | 120000 | `State.RO` |
| RR | Roraima | Roraima | 60000 | `State.RR` |
| RS | Rio Grande do Sul | Rio Grande do Sul | 180000 | `State.RS` |
| SC | Santa Catarina | Santa Catarina | 180000 | `State.SC` |
| SE | Sergipe | Sergipe | 60000 | `State.SE` |
| SP | São Paulo | São Paulo | 840000 | `State.SP` |
| TO | Tocantins | Tocantins | 600000 | `State.TO` |

### 📋 Valores Disponíveis para Polígonos

| Polígono | Valor Interno | Descrição | Exemplo |
|----------|---------------|-----------|---------|
| AREA_PROPERTY | AREA_IMOVEL | Perímetros dos imóveis (Property perimeters) | `Polygon.AREA_PROPERTY` |
| APPS | APPS | Área de Preservação Permanente (Permanent preservation area) | `Polygon.APPS` |
| NATIVE_VEGETATION | VEGETACAO_NATIVA | Remanescente de Vegetação Nativa (Native Vegetation Remnants) | `Polygon.NATIVE_VEGETATION` |
| CONSOLIDATED_AREA | AREA_CONSOLIDADA | Área Consolidada (Consolidated Area) | `Polygon.CONSOLIDATED_AREA` |
| AREA_FALL | AREA_POUSIO | Área de Pousio (Fallow Area) | `Polygon.AREA_FALL` |
| HYDROGRAPHY | HIDROGRAFIA | Hidrografia (Hydrography) | `Polygon.HYDROGRAPHY` |
| RESTRICTED_USE | USO_RESTRITO | Uso Restrito (Restricted Use) | `Polygon.RESTRICTED_USE` |
| ADMINISTRATIVE_SERVICE | SERVIDAO_ADMINISTRATIVA | Servidão Administrativa (Administrative Servitude) | `Polygon.ADMINISTRATIVE_SERVICE` |
| LEGAL_RESERVE | RESERVA_LEGAL | Reserva Legal (Legal reserve) | `Polygon.LEGAL_RESERVE` |

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
| `API_URL` | string | `"http://192.168.5.179:8787"` | URL base da API | `API_URL=http://localhost:8000` |
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
| `STATE_TIMEOUT_AL` | integer | `120000` | Timeout específico para Alagoas | `STATE_TIMEOUT_AL=180000` |
| `STATE_TIMEOUT_AM` | integer | `60000` | Timeout específico para Amazonas | `STATE_TIMEOUT_AM=180000` |
| `STATE_TIMEOUT_AP` | integer | `60000` | Timeout específico para Amapá | `STATE_TIMEOUT_AP=120000` |
| `STATE_TIMEOUT_BA` | integer | `600000` | Timeout específico para Bahia | `STATE_TIMEOUT_BA=900000` |
| `STATE_TIMEOUT_CE` | integer | `240000` | Timeout específico para Ceará | `STATE_TIMEOUT_CE=300000` |
| `STATE_TIMEOUT_DF` | integer | `60000` | Timeout específico para Distrito Federal | `STATE_TIMEOUT_DF=60000` |
| `STATE_TIMEOUT_ES` | integer | `120000` | Timeout específico para Espírito Santo | `STATE_TIMEOUT_ES=180000` |
| `STATE_TIMEOUT_GO` | integer | `300000` | Timeout específico para Goiás | `STATE_TIMEOUT_GO=450000` |
| `STATE_TIMEOUT_MA` | integer | `180000` | Timeout específico para Maranhão | `STATE_TIMEOUT_MA=240000` |
| `STATE_TIMEOUT_MG` | integer | `300000` | Timeout específico para Minas Gerais | `STATE_TIMEOUT_MG=450000` |
| `STATE_TIMEOUT_MS` | integer | `60000` | Timeout específico para Mato Grosso do Sul | `STATE_TIMEOUT_MS=120000` |
| `STATE_TIMEOUT_MT` | integer | `60000` | Timeout específico para Mato Grosso | `STATE_TIMEOUT_MT=180000` |
| `STATE_TIMEOUT_PA` | integer | `120000` | Timeout específico para Pará | `STATE_TIMEOUT_PA=240000` |
| `STATE_TIMEOUT_PB` | integer | `60000` | Timeout específico para Paraíba | `STATE_TIMEOUT_PB=90000` |
| `STATE_TIMEOUT_PE` | integer | `180000` | Timeout específico para Pernambuco | `STATE_TIMEOUT_PE=240000` |
| `STATE_TIMEOUT_PI` | integer | `60000` | Timeout específico para Piauí | `STATE_TIMEOUT_PI=120000` |
| `STATE_TIMEOUT_PR` | integer | `120000` | Timeout específico para Paraná | `STATE_TIMEOUT_PR=180000` |
| `STATE_TIMEOUT_RJ` | integer | `120000` | Timeout específico para Rio de Janeiro | `STATE_TIMEOUT_RJ=180000` |
| `STATE_TIMEOUT_RN` | integer | `60000` | Timeout específico para Rio Grande do Norte | `STATE_TIMEOUT_RN=90000` |
| `STATE_TIMEOUT_RO` | integer | `120000` | Timeout específico para Rondônia | `STATE_TIMEOUT_RO=180000` |
| `STATE_TIMEOUT_RR` | integer | `60000` | Timeout específico para Roraima | `STATE_TIMEOUT_RR=120000` |
| `STATE_TIMEOUT_RS` | integer | `180000` | Timeout específico para Rio Grande do Sul | `STATE_TIMEOUT_RS=240000` |
| `STATE_TIMEOUT_SC` | integer | `180000` | Timeout específico para Santa Catarina | `STATE_TIMEOUT_SC=240000` |
| `STATE_TIMEOUT_SE` | integer | `60000` | Timeout específico para Sergipe | `STATE_TIMEOUT_SE=90000` |
| `STATE_TIMEOUT_SP` | integer | `840000` | Timeout específico para São Paulo | `STATE_TIMEOUT_SP=1200000` |
| `STATE_TIMEOUT_TO` | integer | `600000` | Timeout específico para Tocantins | `STATE_TIMEOUT_TO=900000` |

## 🔧 Variáveis de Configuração do Sistema

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `BASE_IMAGE` | string | `"download-car-pro:latest"` | Imagem base para containers (dev/pro) | `BASE_IMAGE=download-car-dev:latest` |
| `DOCKER_CONFIG` | string | `/tmp/docker-config-noauth` | Configuração do Docker para builds | `DOCKER_CONFIG=/path/to/docker/config` |
| `PYTHON_VERSION` | string | `"3.11"` | Versão do Python utilizada no container | `PYTHON_VERSION=3.11` |
| `BUILD_TARGET` | string | `"pro"` | Target de build (dev/pro) | `BUILD_TARGET=dev` |
| `DOCKER_BUILDKIT` | boolean | `"1"` | Habilita BuildKit para builds otimizados | `DOCKER_BUILDKIT=1` |

## 📷 Variáveis de Configuração OCR

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `TESSERACT_CONFIG` | string | `"--oem 3 --psm 8"` | Configuração do Tesseract OCR para reconhecimento de captcha | `TESSERACT_CONFIG="--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"` |
| `PADDLE_OCR_LANG` | string | `"en"` | Idioma para reconhecimento PaddleOCR | `PADDLE_OCR_LANG=pt` |
| `PADDLE_OCR_USE_GPU` | boolean | `"false"` | Habilita uso de GPU para PaddleOCR | `PADDLE_OCR_USE_GPU=true` |
| `PADDLE_OCR_SHOW_LOG` | boolean | `"false"` | Exibe logs do PaddleOCR | `PADDLE_OCR_SHOW_LOG=true` |

## 🗄️ Variáveis do Banco de Dados PostgreSQL/PostGIS

| Variável | Tipo | Padrão | Descrição | Exemplo |
|----------|------|--------|-----------|---------|
| `DB_HOST` | string | `"localhost"` | Host do banco de dados PostgreSQL/PostGIS | `DB_HOST=postgres` |
| `DB_PORT` | string | `"5432"` | Porta do banco de dados PostgreSQL/PostGIS | `DB_PORT=5432` |
| `DB_NAME` | string | `"download_car"` | Nome do banco de dados | `DB_NAME=car_data` |
| `DB_USER` | string | `"postgres"` | Usuário do banco de dados | `DB_USER=car_user` |
| `DB_PASSWORD` | string | `"postgres"` | Senha do banco de dados | `DB_PASSWORD=secure_password` |
| `DB_SCHEMA` | string | `"public"` | Schema do banco de dados | `DB_SCHEMA=car_schema` |
| `DB_POOL_SIZE` | integer | `"5"` | Pool de conexões | `DB_POOL_SIZE=10` |
| `DB_TIMEOUT` | integer | `"30"` | Timeout de conexão em segundos | `DB_TIMEOUT=60` |

## 📝 Como Usar as Variáveis de Ambiente

### 1. Arquivo .env (Recomendado)

Crie um arquivo `.env` na raiz do projeto:

```bash
# Variáveis de Download
STATE=SP
POLYGON=AREA_PROPERTY
FOLDER=temp/SP
TRIES=25
DEBUG=false
TIMEOUT=30
MAX_RETRIES=5

# Variáveis da API
API_URL=http://192.168.5.179:8787
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=*

# Variáveis do Frontend
API_ENDPOINT_URL=http://192.168.5.179:8787
DEFAULT_POLYGON=AREA_PROPERTY
DEFAULT_TIMEOUT=800000
TIMEOUT_INCREMENT=10000
MIN_TIMEOUT=10000
MAX_TIMEOUT=300000

# Timeouts específicos por estado (exemplos)
STATE_TIMEOUT_SP=840000
STATE_TIMEOUT_BA=600000
STATE_TIMEOUT_MG=300000
STATE_TIMEOUT_GO=300000
STATE_TIMEOUT_CE=240000
```

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

# Configurações do Banco de Dados PostgreSQL/PostGIS
DB_HOST=postgres
DB_PORT=5432
DB_NAME=download_car
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public
DB_POOL_SIZE=5
DB_TIMEOUT=30

### 2. Linha de Comando

```bash
# Docker Compose com variáveis
STATE=SP POLYGON=AREA_PROPERTY docker compose up

# Makefile com variáveis
make download state=SP polygon=AREA_PROPERTY folder=temp/SP debug=true timeout=60

# Build com configuração específica
BASE_IMAGE=download-car-dev:latest make build-dev
BUILD_TARGET=dev make build

# Exemplos com diferentes estados e polígonos
STATE=MG POLYGON=APPS make download folder=temp/MG debug=true timeout=300
STATE=BA POLYGON=AREA_PROPERTY make download folder=temp/BA debug=false timeout=600
```

### 3. Docker Compose

```yaml
version: '3.8'
services:
  download-car-api:
    build:
      context: .
      dockerfile: Dockerfile.api
      args:
        BASE_IMAGE: ${BASE_IMAGE:-download-car-pro:latest}
    environment:
      - CORS_ALLOW_ORIGINS=http://localhost:3000
      - PROPERTY_FOLDER=properties
      - PROPERTY_TIMEOUT=60
      - API_URL=http://192.168.5.179:8787
      - STATE_TIMEOUT_SP=840000
      - STATE_TIMEOUT_BA=600000
      - STATE_TIMEOUT_MG=300000
      - TESSERACT_CONFIG=--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
```

### 4. Configuração de Timeouts por Estado

Para estados com muitos dados, configure timeouts maiores baseados nos valores reais do sistema:

```bash
# Estados com muitos dados (timeouts altos)
STATE_TIMEOUT_SP=840000   # 14 minutos (São Paulo - maior timeout)
STATE_TIMEOUT_BA=600000   # 10 minutos (Bahia)
STATE_TIMEOUT_TO=600000   # 10 minutos (Tocantins)
STATE_TIMEOUT_MG=300000   # 5 minutos (Minas Gerais)
STATE_TIMEOUT_GO=300000   # 5 minutos (Goiás)

# Estados com dados moderados (timeouts médios)
STATE_TIMEOUT_CE=240000   # 4 minutos (Ceará)
STATE_TIMEOUT_MA=180000   # 3 minutos (Maranhão)
STATE_TIMEOUT_PE=180000   # 3 minutos (Pernambuco)
STATE_TIMEOUT_RS=180000   # 3 minutos (Rio Grande do Sul)
STATE_TIMEOUT_SC=180000   # 3 minutos (Santa Catarina)
STATE_TIMEOUT_PA=120000   # 2 minutos (Pará)
STATE_TIMEOUT_ES=120000   # 2 minutos (Espírito Santo)
STATE_TIMEOUT_PR=120000   # 2 minutos (Paraná)
STATE_TIMEOUT_RJ=120000   # 2 minutos (Rio de Janeiro)
STATE_TIMEOUT_RO=120000   # 2 minutos (Rondônia)

# Estados com dados menores (timeouts baixos)
STATE_TIMEOUT_AL=120000   # 2 minutos (Alagoas)
STATE_TIMEOUT_AC=60000    # 1 minuto (Acre)
STATE_TIMEOUT_AM=60000    # 1 minuto (Amazonas)
STATE_TIMEOUT_AP=60000    # 1 minuto (Amapá)
STATE_TIMEOUT_DF=60000    # 1 minuto (Distrito Federal)
STATE_TIMEOUT_MS=60000    # 1 minuto (Mato Grosso do Sul)
STATE_TIMEOUT_MT=60000    # 1 minuto (Mato Grosso)
STATE_TIMEOUT_PB=60000    # 1 minuto (Paraíba)
STATE_TIMEOUT_PI=60000    # 1 minuto (Piauí)
STATE_TIMEOUT_RN=60000    # 1 minuto (Rio Grande do Norte)
STATE_TIMEOUT_RR=60000    # 1 minuto (Roraima)
STATE_TIMEOUT_SE=60000    # 1 minuto (Sergipe)
```

### 5. Configuração de OCR

Para otimizar o reconhecimento de captcha, configure as variáveis OCR:

```bash
# Configuração do Tesseract (padrão)
TESSERACT_CONFIG="--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

# Configuração do PaddleOCR (recomendado para melhor precisão)
PADDLE_OCR_LANG=en
PADDLE_OCR_USE_GPU=false
PADDLE_OCR_SHOW_LOG=false

# Para melhor performance com GPU (se disponível)
PADDLE_OCR_USE_GPU=true

# Para debug de reconhecimento (útil para diagnosticar problemas)
PADDLE_OCR_SHOW_LOG=true

# Configuração específica para português (se necessário)
PADDLE_OCR_LANG=pt
```

**Dicas de configuração OCR:**

- **Tesseract**: Use `--psm 8` para reconhecimento de texto único
- **PaddleOCR**: Configure `PADDLE_OCR_LANG=pt` para português
- **GPU**: Habilite `PADDLE_OCR_USE_GPU=true` se disponível
- **Debug**: Use `PADDLE_OCR_SHOW_LOG=true` para diagnosticar problemas

**URLs do Sistema SICAR:**
- **Base**: `https://consultapublica.car.gov.br/publico`
- **Consulta**: `https://consultapublica.car.gov.br/publico/imoveis/index`
- **Downloads**: `https://consultapublica.car.gov.br/publico/estados/downloads`
- **ReCaptcha**: `https://consultapublica.car.gov.br/publico/municipios/ReCaptcha`

---

# 🚀 Como usar

## 1️⃣ Execução via Python (direto)

```python
from download_car import DownloadCar, State, Polygon

# Exemplo básico
car = DownloadCar()
car.download_state(state=State.SP, polygon=Polygon.AREA_PROPERTY, folder="dados/SP")

# Exemplo com todos os parâmetros
car.download_state(
    state=State.MG, 
    polygon=Polygon.APPS, 
    folder="dados/MG", 
    tries=25, 
    debug=True, 
    chunk_size=1024, 
    timeout=60,
    max_retries=5
)

# Exemplo para download de todo o país
car.download_country(polygon=Polygon.AREA_PROPERTY, folder="dados/brasil")
```

## 2️⃣ Execução via Shell Script

O repositório inclui o script `cli.py` que facilita a configuração do
ambiente e a execução do download. Basta informar os
parâmetros desejados:

```bash
python cli.py --state DF --polygon APPS --folder data/DF --tries 25 --debug True
```

O script irá garantir que a versão correta do Python esteja disponível via
`pyenv`, criar um ambiente virtual e executar o exemplo com as variáveis de
ambiente apropriadas.

## 3️⃣ Execução via Docker Compose

O repositório possui um `docker-compose.yml` configurado com três serviços e suporte a imagens otimizadas:

### 🏗️ Estrutura dos Dockerfiles
- **Dockerfile.base** - Imagem base com Python 3.11-slim e dependências core (Tesseract OCR, OpenCV)
- **Dockerfile.dev** - Desenvolvimento (base + Poetry + PaddleOCR + ferramentas de debug)
- **Dockerfile.pro** - Produção (base + requirements.txt otimizado)
- **Dockerfile.api** - API FastAPI (estende dev ou pro conforme BASE_IMAGE)
- **Dockerfile.download-car** - Serviço de download (estende dev ou pro conforme BASE_IMAGE)
- **Dockerfile.nginx** - Frontend Nginx com Node.js para configuração dinâmica

### 🔧 Configuração via Variável de Ambiente
```bash
# Para desenvolvimento (com PaddleOCR e ferramentas)
BASE_IMAGE=download-car-dev:latest docker compose up

# Para produção (otimizado, sem PaddleOCR)
BASE_IMAGE=download-car-pro:latest docker compose up

# Ou via arquivo .env
echo "BASE_IMAGE=download-car-pro:latest" > .env
docker compose up
```

### 🛠️ Build das Imagens

### 🛠️ Comandos Makefile para Build
```bash
# Build completo de desenvolvimento
make build-dev

# Build completo de produção
make build-pro

# Build apenas da imagem base
make build-base

# Build específico da API
make build-api-dev    # API com base de desenvolvimento
make build-api-pro    # API com base de produção

# Build específico do download
make build-download-dev    # Download com base de desenvolvimento
make build-download-pro    # Download com base de produção
```

### 📦 Geração de Requirements
O sistema automaticamente gera `requirements.txt` a partir do `pyproject.toml`:
```bash
# Geração manual (se necessário)
make requirements.txt
```

### 🚀 Serviços Disponíveis

#### **download-car-download**
- **Função**: Executa downloads via script `entrypoint.download.sh`
- **Configuração**: Variáveis `STATE`, `POLYGON`, `FOLDER`
- **Volume**: Monta o diretório atual em `/download-car`

#### **download-car-api**
- **Função**: Servidor FastAPI na porta 8000
- **Configuração**: Variáveis de CORS, propriedades e timeouts
- **Volume**: Monta o diretório atual em `/download-car`
- **Dependências**: FastAPI, Uvicorn, httpx, Pillow, tqdm

#### **nginx**
- **Função**: Frontend e proxy reverso na porta 8787
- **Configuração**: Template dinâmico com Node.js
- **Assets**: Bandeiras dos estados e interface web
- **Dependências**: download-car-api, download-car-download

### 📊 Tamanhos Estimados das Imagens

| Imagem | Tamanho | Descrição |
|--------|---------|-----------|
| **Base** | ~800MB | Python 3.11-slim + Tesseract OCR + OpenCV |
| **Dev** | ~2.5GB | Base + Poetry + PaddleOCR + ferramentas |
| **Pro** | ~900MB | Base + requirements.txt otimizado |
| **API Dev** | ~3GB | Dev + FastAPI + geopandas |
| **API Pro** | ~1.5GB | Pro + FastAPI + geopandas |
| **Download Dev** | ~2.5GB | Dev + scripts de download |
| **Download Pro** | ~900MB | Pro + scripts de download |
| **Nginx** | ~50MB | Alpine + Node.js + frontend |

### 🔧 Configuração Avançada

#### Variáveis de Ambiente por Serviço:
```yaml
# download-car-download
environment:
  - POLYGON

# download-car-api  
environment:
  - API_URL
  - CORS_ALLOW_ORIGINS
  - PROPERTY_FOLDER
  - PROPERTY_TIMEOUT

# nginx
environment:
  - API_ENDPOINT_URL
  - DEFAULT_POLYGON
  - STATE_TIMEOUT_*  # Timeouts específicos por estado
```

#### Volumes e Persistência:
```yaml
volumes:
  - .:/download-car                    # Código fonte
  - ./nginx.conf.template:/etc/nginx/conf.d/default.conf.template:ro
  - ./index.html:/usr/share/nginx/html/index.html:rw
  - ./assets:/usr/share/nginx/html/assets:ro
```

### 🌐 Acesso aos Serviços

- **Frontend**: `http://localhost:8787` (via Nginx)
- **API Direta**: `http://localhost:8000` (FastAPI)
- **Logs**: `docker compose logs -f [serviço]`
- **Shell**: `make shell-api` ou `make shell`

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

### Endpoints de Sincronização com Banco de Dados
- `POST /sync_to_database` &ndash; sincroniza shapefiles com o banco de dados PostgreSQL/PostGIS.
- `GET /database_status` &ndash; verifica o status da conexão com o banco de dados.
- `GET /car_data` &ndash; busca dados do CAR armazenados no banco de dados.

### Campos esperados (multipart/form)

#### POST /download_state
- `state` (obrigatório): Sigla do estado (ex: "SP", "RJ", "MG")
- `polygon` (opcional): Tipo de polígono (padrão: "AREA_PROPERTY")
  - Valores válidos: "AREA_PROPERTY", "APPS", "NATIVE_VEGETATION", "CONSOLIDATED_AREA", "AREA_FALL", "HYDROGRAPHY", "RESTRICTED_USE", "ADMINISTRATIVE_SERVICE", "LEGAL_RESERVE"
- `folder` (opcional): Pasta de destino (padrão: "temp")
- `tries` (opcional): Número de tentativas (padrão: 25)
- `debug` (opcional): Modo debug (padrão: false)
- `timeout` (opcional): Timeout em segundos (padrão: 30)
- `max_retries` (opcional): Máximo de retry (padrão: 5)

**Exemplos de valores válidos:**
- `state`: "SP", "MG", "BA", "PA", "AM", "MT", "GO", "PR", "RS", "SC", "CE", "PE", "MA", "ES", "RJ", "RO", "PI", "AL", "PB", "RN", "SE", "TO", "AC", "AP", "RR", "DF", "MS"
- `polygon`: "AREA_PROPERTY" (Área do Imóvel), "APPS" (Área de Preservação Permanente), "LEGAL_RESERVE" (Reserva Legal)

#### POST /download_country
- `polygon` (opcional): Tipo de polígono (padrão: "AREA_PROPERTY")
  - Valores válidos: "AREA_PROPERTY", "APPS", "NATIVE_VEGETATION", "CONSOLIDATED_AREA", "AREA_FALL", "HYDROGRAPHY", "RESTRICTED_USE", "ADMINISTRATIVE_SERVICE", "LEGAL_RESERVE"
- `folder` (opcional): Pasta de destino (padrão: "brazil")
- `tries` (opcional): Número de tentativas (padrão: 25)
- `debug` (opcional): Modo debug (padrão: false)
- `timeout` (opcional): Timeout em segundos (padrão: 30)
- `max_retries` (opcional): Máximo de retry (padrão: 5)

#### POST /download-property
- `car` (obrigatório): Número do CAR da propriedade (ex: "SP12345678901234567890")
  - Formato: {SIGLA_ESTADO}{20_DIGITOS_ALFANUMERICOS}
  - Exemplos: "SP12345678901234567890", "MG98765432109876543210", "BA11111111111111111111"

#### DELETE /delete_state
- `state` (obrigatório): Sigla do estado a ser excluído (ex: "SP", "RJ", "MG")
  - Valores válidos: "SP", "MG", "BA", "PA", "AM", "MT", "GO", "PR", "RS", "SC", "CE", "PE", "MA", "ES", "RJ", "RO", "PI", "AL", "PB", "RN", "SE", "TO", "AC", "AP", "RR", "DF", "MS"
- `folder` (opcional): Pasta onde estão os arquivos (padrão: "temp")
- `include_properties` (opcional): Se deve excluir também arquivos de propriedades (padrão: true)

#### GET /state?car={CAR}
- `car` (obrigatório): Número do CAR da propriedade
  - Exemplo: `GET /state?car=SP12345678901234567890`

#### GET /property?car={CAR}
- `car` (obrigatório): Número do CAR da propriedade
  - Exemplo: `GET /property?car=SP12345678901234567890`

#### POST /sync_to_database
- `sync_type` (obrigatório): Tipo de sincronização ("state" ou "car")
- `state` (obrigatório): Sigla do estado brasileiro (2 letras maiúsculas)
- `polygon_type` (opcional): Tipo de polígono (padrão: "AREA_PROPERTY")
- `car_code` (opcional): Código CAR específico (obrigatório quando sync_type=car)
- `folder` (opcional): Pasta onde buscar os arquivos shapefile (padrão: "temp")
- `create_tables` (opcional): Se deve criar tabelas automaticamente (padrão: true)

#### GET /database_status
- Sem parâmetros obrigatórios
- Retorna status da conexão e configuração do banco de dados

#### GET /car_data
- `car_code` (opcional): Código CAR específico para busca
- `state` (opcional): Sigla do estado para filtrar resultados
- `polygon_type` (opcional): Tipo de polígono para filtrar resultados
- `limit` (opcional): Limite de resultados retornados (padrão: 100, máximo: 1000)

### Exemplo via curl

```bash
# Download de um estado (São Paulo - Área do Imóvel)
curl -X POST "http://localhost:8000/download_state" \
     -F "state=SP" \
     -F "polygon=AREA_PROPERTY" \
     -F "folder=temp" \
     -F "tries=25" \
     -F "debug=false" \
     -F "timeout=30" \
     -F "max_retries=5" \
     --output SP_AREA_IMOVEL.zip

# Download de APPS (Minas Gerais - Área de Preservação Permanente)
curl -X POST "http://localhost:8000/download_state" \
     -F "state=MG" \
     -F "polygon=APPS" \
     -F "folder=temp" \
     -F "tries=25" \
     -F "debug=true" \
     -F "timeout=60" \
     --output MG_APPS.zip

# Download de todo o país (Área do Imóvel)
curl -X POST "http://localhost:8000/download_country" \
     -F "polygon=AREA_PROPERTY" \
     -F "folder=brazil" \
     -F "tries=25" \
     -F "debug=false" \
     -F "timeout=30" \
     --output brazil_AREA_IMOVEL.zip

# Buscar estado de um CAR específico
curl -X GET "http://localhost:8000/state?car=SP12345678901234567890"

# Baixar propriedade específica
curl -X POST "http://localhost:8000/download-property" \
     -F "car=SP12345678901234567890" \
     --output property_SP12345678901234567890.zip

# Excluir arquivos de um estado
curl -X DELETE "http://localhost:8000/delete_state" \
     -F "state=SP" \
     -F "folder=temp" \
     -F "include_properties=true"

# Sincronizar dados de um estado com banco de dados
curl -X POST "http://localhost:8000/sync_to_database" \
     -F "sync_type=state" \
     -F "state=SP" \
     -F "polygon_type=AREA_PROPERTY" \
     -F "folder=temp" \
     -F "create_tables=true"

# Sincronizar dados de um CAR específico
curl -X POST "http://localhost:8000/sync_to_database" \
     -F "sync_type=car" \
     -F "car_code=SP12345678901234567890" \
     -F "state=SP" \
     -F "polygon_type=AREA_PROPERTY"

# Verificar status do banco de dados
curl -X GET "http://localhost:8000/database_status"

# Buscar dados do CAR no banco de dados
curl -X GET "http://localhost:8000/car_data?state=SP&limit=10"

# Buscar dados de um CAR específico
curl -X GET "http://localhost:8000/car_data?car_code=SP12345678901234567890"
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
- `POST /sync_to_database` &ndash; sincroniza shapefiles com o banco de dados PostgreSQL/PostGIS.
- `GET /database_status` &ndash; verifica o status da conexão com o banco de dados.
- `GET /car_data` &ndash; busca dados do CAR armazenados no banco de dados.

## 5️⃣ Importação como módulo Python

Após instalar com `pip install download-car`, basta importar e usar:

```python
from download_car import DownloadCar, State, Polygon

# Exemplo básico
car = DownloadCar()
car.download_state(State.MG, Polygon.LEGAL_RESERVE, folder="MG")

# Exemplo com configuração específica de OCR
from download_car.drivers import Paddle
car = DownloadCar(driver=Paddle())
car.download_state(State.SP, Polygon.AREA_PROPERTY, folder="dados/SP", debug=True)

# Exemplo para obter datas de release
release_dates = car.get_release_dates()
print(f"Data de release para SP: {release_dates.get(State.SP)}")
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

# Análise por município
municipio_stats = gdf.groupby('municipio').agg({
    'num_area': ['count', 'sum', 'mean'],
    'mod_fiscal': 'mean'
}).round(2)
print("Estatísticas por município:")
print(municipio_stats)

# Análise por status do CAR
status_stats = gdf.groupby('ind_status').agg({
    'num_area': ['count', 'sum'],
    'mod_fiscal': 'mean'
}).round(2)
print("Estatísticas por status do CAR:")
print(status_stats)

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

O projeto inclui um Makefile abrangente com comandos para facilitar o desenvolvimento, build e operação:

### 🚀 Comandos de Inicialização
- `make up` - Inicia todos os serviços (API, download, nginx)
- `make api-up` - Inicia apenas o serviço API
- `make download-up` - Inicia apenas o serviço download-car

### 🛠️ Comandos de Build

#### Builds Completos:
- `make build` - Builda todas as imagens (produção)
- `make build-dev` - Builda todas as imagens (desenvolvimento)
- `make build-pro` - Builda todas as imagens (produção)

#### Builds Específicos:
- `make build-base` - Builda a imagem base (Python + dependências core)
- `make build-api` - Builda apenas a imagem da API (produção)
- `make build-api-dev` - Builda apenas a imagem da API (desenvolvimento)
- `make build-api-pro` - Builda apenas a imagem da API (produção)
- `make build-download` - Builda apenas a imagem de download (produção)
- `make build-download-dev` - Builda apenas a imagem de download (desenvolvimento)
- `make build-download-pro` - Builda apenas a imagem de download (produção)

#### Geração de Dependências:
- `make requirements.txt` - Gera requirements.txt a partir do pyproject.toml

### 🗑️ Comandos de Limpeza
- `make clean` - Remove imagens, volumes e containers órfãos
- `make clean-volumes` - Remove volumes Docker, incluindo arquivos montados
- `make clean-api` - Remove apenas a imagem da API
- `make clean-image` - Remove apenas a imagem principal

### 🛑 Comandos de Controle
- `make down` - Para e remove containers
- `make ps` - Lista containers e serviços
- `make logs service=X` - Exibe logs do serviço especificado

### 🔗 Comandos de Acesso
- `make shell` - Entra no container principal
- `make shell-api` - Entra no container da API
- `make run CMD=X` - Executa comando no container
- `make run-api` - Executa container da API

### 🧪 Comandos de Teste
- `make test` - Executa todos os testes (unitários + integração)
- `make unit-test` - Executa testes unitários
- `make integration-test` - Executa testes de integração

### 📥 Comandos de Download
- `make download state=X polygon=Y folder=Z debug=W timeout=T max_retries=R` - Executa download com parâmetros específicos
- `make search-car car=X` - Busca estado do CAR via API
- `make download-property car=X` - Baixa propriedade do CAR via API
- `make delete-state state=X folder=Y include_properties=Z` - Exclui arquivos de um estado

### 🔄 Comandos de Manutenção
- `make git-update` - Atualiza repositório Git

### 🛠️ Comandos de Desenvolvimento
- `make format` - Formata código com Black
- `make lint` - Verifica estilo do código
- `make docs` - Gera documentação com Interrogate
- `make coverage` - Executa testes com cobertura

### 📋 Ajuda
- `make help` - Exibe todos os comandos disponíveis com descrições

### 💡 Exemplos de Uso

```bash
# Build completo para desenvolvimento
make build-dev

# Iniciar apenas a API
make api-up

# Executar download específico (São Paulo - Área do Imóvel)
make download state=SP polygon=AREA_PROPERTY folder=temp/SP debug=true timeout=60

# Executar download específico (Minas Gerais - APPS)
make download state=MG polygon=APPS folder=temp/MG debug=true timeout=300

# Buscar estado de um CAR específico
make search-car car=SP12345678901234567890

# Baixar propriedade específica
make download-property car=SP12345678901234567890

# Excluir arquivos de um estado
make delete-state state=SP folder=temp include_properties=true

# Ver logs da API
make logs service=download-car-api

# Entrar no container da API
make shell-api

# Limpar tudo e recomeçar
make clean && make build && make up
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

### Dockerfile.base
- **Base**: `python:3.11-slim`
- **Python**: 3.11 nativo (sem pyenv)
- **Dependências**: Tesseract OCR, OpenCV, build-essential
- **Pacotes Python**: httpx, urllib3, pytesseract, opencv-python, numpy, tqdm, matplotlib, beautifulsoup4
- **Tamanho**: ~800MB

### Dockerfile.dev
- **Base**: `download-car-base:latest`
- **Ferramentas**: Poetry, curl, wget
- **Dependências**: Todas as dependências de desenvolvimento
- **PaddleOCR**: Instalado automaticamente
- **Tamanho**: ~2.5GB

### Dockerfile.pro
- **Base**: `download-car-base:latest`
- **Dependências**: Apenas requirements.txt (otimizado)
- **Sem**: PaddleOCR, ferramentas de desenvolvimento
- **Tamanho**: ~900MB

### Dockerfile.api
- **Base**: Configurável via `BASE_IMAGE` (dev ou pro)
- **Dependências**: FastAPI, Uvicorn, python-multipart
- **Entrypoint**: Uvicorn direto (sem script)
- **Porta**: 8000

### Dockerfile.download-car
- **Base**: Configurável via `BASE_IMAGE` (dev ou pro)
- **Entrypoint**: `entrypoint.download.sh`
- **Volume**: Monta código fonte

### Dockerfile.nginx
- **Base**: `nginx:alpine`
- **Node.js**: Instalado para configuração dinâmica
- **Scripts**: `entrypoint.nginx.sh`, `generate-config.nginx.js`
- **Porta**: 80 (mapeada para 8787)
- **Tamanho**: ~50MB

### Arquivos de Configuração
- **`.dockerignore`**: Exclui `.git`, `__pycache__`, `.venv*`, `tests`
- **`entrypoint.nginx.sh`**: Substitui variáveis de ambiente no nginx.conf
- **`generate-config.nginx.js`**: Gera configuração do frontend dinamicamente
- **`nginx.conf.template`**: Template com variáveis de ambiente
- **`requirements.txt`**: Gerado automaticamente do pyproject.toml

### Estratégia de Build
```bash
# 1. Build da imagem base
make build-base

# 2. Build das imagens específicas (dev ou pro)
make build-dev    # ou make build-pro

# 3. Build dos serviços (API e download)
make build-api-dev    # ou make build-api-pro
make build-download-dev    # ou make build-download-pro
```

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
├── api.py                        # API FastAPI
├── cli.py                        # Script de download
├── cli.sh             # Script shell
├── api.sh                        # Script da API
├── verify_features.sh            # Script de teste da API
├── verify_property.py            # Script de verificação
├── test_delete_state.py          # Script de teste
├── docker-compose.yml            # Configuração Docker Compose
├── Dockerfile.base               # Imagem base (Python + dependências core)
├── Dockerfile.dev                # Imagem de desenvolvimento
├── Dockerfile.pro                # Imagem de produção
├── Dockerfile.api                # Imagem da API FastAPI
├── Dockerfile.download-car       # Imagem do serviço de download
├── Dockerfile.nginx              # Imagem do frontend Nginx
├── entrypoint.download.sh        # Script de entrada do download
├── entrypoint.nginx.sh           # Script de entrada do Nginx
├── generate-config.nginx.js      # Geração de configuração dinâmica
├── nginx.conf.template           # Template do Nginx
├── index.html                    # Frontend
├── Makefile                      # Comandos de automação
├── pyproject.toml                # Configuração do projeto
├── requirements.txt              # Dependências de produção (gerado)
├── .config.env                   # Configurações de exemplo
└── README.md                     # Esta documentação
```

### Arquivos de Configuração Importantes

| Arquivo | Descrição |
|---------|-----------|
| `pyproject.toml` | Configuração do projeto Python, dependências, ferramentas |
| `docker-compose.yml` | Orquestração dos serviços Docker |
| `Makefile` | Automação de comandos comuns |
| `.config.env` | Configurações de exemplo (copiar para .env) |
| `.env` | Variáveis de ambiente (criar localmente) |
| `.gitignore` | Arquivos ignorados pelo Git |
| `.dockerignore` | Arquivos ignorados pelo Docker |

### Estrutura Docker

| Dockerfile | Base | Propósito | Tamanho |
|------------|------|-----------|---------|
| `Dockerfile.base` | `python:3.11-slim` | Dependências core | ~800MB |
| `Dockerfile.dev` | `download-car-base` | Desenvolvimento + PaddleOCR | ~2.5GB |
| `Dockerfile.pro` | `download-car-base` | Produção otimizada | ~900MB |
| `Dockerfile.api` | Configurável | API FastAPI | ~1.5-3GB |
| `Dockerfile.download-car` | Configurável | Serviço de download | ~900MB-2.5GB |
| `Dockerfile.nginx` | `nginx:alpine` | Frontend + proxy | ~50MB |

---

# 📦 Resultados e arquivos de saída

O download gera um arquivo `.zip` contendo os shapefiles correspondentes. Exemplo de estrutura:

```plain
# Exemplo de arquivo para São Paulo - Área do Imóvel
SP_AREA_IMOVEL.zip
├── SP_AREA_IMOVEL.shp
├── SP_AREA_IMOVEL.shx
├── SP_AREA_IMOVEL.dbf
└── SP_AREA_IMOVEL.prj

# Exemplo de arquivo para Minas Gerais - APPS
MG_APPS.zip
├── MG_APPS.shp
├── MG_APPS.shx
├── MG_APPS.dbf
└── MG_APPS.prj

# Exemplo de arquivo para todo o Brasil
brazil_AREA_IMOVEL.zip
├── AC_AREA_IMOVEL.shp
├── AL_AREA_IMOVEL.shp
├── AM_AREA_IMOVEL.shp
└── ... (todos os estados)
```

**Convenção de nomenclatura:**
- Estados: `{SIGLA}_{TIPO_POLIGONO}.zip`
- Brasil: `brazil_{TIPO_POLIGONO}.zip`
- Propriedades: `property_{CAR}.zip`

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

- [x] Upload to pypi registry

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
- Configure timeouts maiores para estados com muitos dados:
  - São Paulo: `STATE_TIMEOUT_SP=840000` (14 minutos)
  - Bahia: `STATE_TIMEOUT_BA=600000` (10 minutos)
  - Minas Gerais: `STATE_TIMEOUT_MG=300000` (5 minutos)

**Como debugar problemas de download?**
- Ative o modo debug: `DEBUG=true`
- Verifique logs do container: `docker compose logs download-car-download`
- Use o script de verificação: `./verify_features.sh`

**Como resolver problemas de build Docker?**
- Limpe imagens antigas: `make clean`
- Use BuildKit: `DOCKER_BUILDKIT=1 make build`
- Verifique dependências: `make requirements.txt`
- Build específico: `make build-base && make build-dev`

**Como alternar entre desenvolvimento e produção?**
- Desenvolvimento: `BASE_IMAGE=download-car-dev:latest docker compose up`
- Produção: `BASE_IMAGE=download-car-pro:latest docker compose up`
- Ou via arquivo .env: `echo "BASE_IMAGE=download-car-dev:latest" > .env`

**Como configurar para produção?**
- Use variáveis de ambiente específicas para produção
- Configure timeouts adequados para seu ambiente
- Monitore logs e métricas da API

# License

[MIT](LICENSE)

Se utilizar este projeto, cite: **Urbano, Gilson**. *download-car Package*. Consulte o arquivo [CITATION.cff](CITATION.cff) para mais detalhes.
