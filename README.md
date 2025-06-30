# SICAR

Ferramenta que automatiza o download de arquivos do [Cadastro Ambiental Rural (SICAR)](https://car.gov.br/publico/imoveis/index). Ela é voltada para estudantes, pesquisadores e analistas que precisam acessar shapefiles do sistema de maneira simples.

## Badges

[![Open In Collab](.github/colab-badge.svg)](https://colab.research.google.com/github/urbanogilson/SICAR/blob/main/examples/colab.ipynb)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Pulls](https://img.shields.io/docker/pulls/urbanogilson/sicar)](https://hub.docker.com/r/urbanogilson/sicar)
[![Coverage Status](https://coveralls.io/repos/github/urbanogilson/SICAR/badge.svg?branch=main)](https://coveralls.io/github/urbanogilson/SICAR?branch=main)
[![interrogate](.github/interrogate_badge.svg)](https://interrogate.readthedocs.io/)

# ✨ Objetivo

Permitir o download programático dos dados públicos do SICAR. O projeto inclui drivers para reconhecimento de captcha via **Tesseract** (padrão) ou **PaddleOCR**.

---

# Índice

- [⚙️ Funções principais](#️-funções-principais)
- [📥 Parâmetros disponíveis](#-parâmetros-disponíveis)
- [🚀 Como usar](#-como-usar)
  - [1️⃣ Execução via Python (direto)](#1️⃣-execução-via-python-direto)
  - [2️⃣ Execução via Docker Compose](#2️⃣-execução-via-docker-compose)
  - [3️⃣ Execução via Google Colab (Notebook Interativo)](#3️⃣-execução-via-google-colab-notebook-interativo)
  - [4️⃣ Execução via API](#4️⃣-execução-via-api)
    - [Campos esperados (multipart/form)](#campos-esperados-multipartform)
    - [Exemplo via curl](#exemplo-via-curl)
  - [5️⃣ Importação como módulo Python](#5️⃣-importação-como-módulo-python)
- [📦 Resultados e arquivos de saída](#-resultados-e-arquivos-de-saída)
- [📊 Data dictionary](#data-dictionary)
- [📝 Licença](#license)

---

# ⚙️ Funções principais

A classe central deste pacote é `Sicar`, que disponibiliza três métodos principais:

- `download_state(state, polygon, folder="temp", tries=25, debug=False, chunk_size=1024)`
- `download_country(polygon, folder="brazil", tries=25, debug=False, chunk_size=1024)`
- `get_release_dates()`

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

Esses parâmetros se aplicam principalmente ao método `download_state`. O método `download_country` utiliza a mesma assinatura (exceto pelo parâmetro `state`).

---

# 🚀 Como usar

## 1️⃣ Execução via Python (direto)

```python
from SICAR import Sicar, State, Polygon

car = Sicar()
car.download_state(state=State.PA, polygon=Polygon.APPS, folder="PA")
```

## 2️⃣ Execução via Docker Compose

Crie um arquivo `docker-compose.yml` simples apontando para este repositório:

```yaml
version: "3.8"
services:
  sicar:
    build: .
    volumes:
      - .:/sicar
    command: python examples/docker.py
```

Execute:

```bash
docker compose up --build
```

## 3️⃣ Execução via Google Colab (Notebook Interativo)

[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/urbanogilson/SICAR/blob/main/examples/colab.ipynb)

O notebook permite baixar os shapefiles diretamente no navegador sem instalar nada.

## 4️⃣ Execução via API

Uma API pública de demonstração está disponível em [gilsonurbano.com/sicar-api](https://gilsonurbano.com/sicar-api/). O endpoint `/download` aceita requisições `POST` contendo o estado e o tipo de polígono desejado.

### Campos esperados (multipart/form)

| Campo    | Tipo  | Obrigatório | Descrição                                           |
|----------|-------|-------------|-----------------------------------------------------|
| `state`  | str   | ✅          | Sigla do estado (ex.: `SP`).                         |
| `polygon`| str   | ✅          | Tipo de camada (`APPS`, `AREA_PROPERTY`, etc.).      |

### Exemplo via curl

```bash
curl -X POST https://gilsonurbano.com/sicar-api/download \
  -F "state=SP" \
  -F "polygon=APPS" \
  --output SP_APPS.zip
```

## 5️⃣ Importação como módulo Python

Após instalar com `pip install git+https://github.com/urbanogilson/SICAR`, basta importar e usar:

```python
from SICAR import Sicar, State, Polygon

car = Sicar()
car.download_state(State.MG, Polygon.LEGAL_RESERVE, folder="MG")
```

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

| **Attribute** | **Description**                                              |
|---------------|--------------------------------------------------------------|
| cod_estado    | Unit of the Federation in which the registration is located. |
| municipio     | Municipality in which the registration is located. |
| num_area      | Gross area of the rural property or the subject that makes up the registry, in hectare. |
| cod_imovel    | Registration number in the Rural Environmental Registry (CAR). |
| ind_status    | Status of registration in CAR, according to Normative Instruction no. 2, of May 6, 2014, of the Ministry of the Environment (https://www.car.gov.br/leis/IN_CAR.pdf), and the Resolution No. 3, of August 27, 2018, of the Brazilian Forest Service (https://imprensanacional.gov.br/materia/-/asset_publisher/Kujrw0TZC2Mb/content/id/38537086/do1-2018-08-28-resolucao-n-3-de-27-de-agos-de-2018-38536774), being AT - Active; PE - Pending; SU - Suspended; and CA - Canceled. |
| des_condic    | Condition in which the registration is in the analysis flow by the competent body. |
| ind_tipo      | Type of Rural Property, being IRU - Rural Property; AST - Agrarian Reform Settlements; PCT - Traditional Territory of Traditional Peoples and Communities. |
| mod_fiscal    | Number of rural property tax modules. |
| nom_tema      | Name of the theme that makes up the registration (Permanent Preservation Area, Path, Remnant of Native Vegetation, Restricted Use Area, Administrative Easement, Legal Reserve, Hydrography, Wetlands, Consolidated Rural Area, Areas with Altitude Higher than 1800 meters, Areas with Slopes Higher than 45 degrees, Hilltops, Plateau Edges, Fallow Areas, Mangroves and Restinga). |

---

# License

[MIT](LICENSE)
