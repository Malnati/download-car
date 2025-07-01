<!-- README.md -->
# Download CAR files (shape) 

Ferramenta que automatiza o download de arquivos do [Cadastro Ambiental Rural (SICAR)](https://car.gov.br/publico/imoveis/index). Ela é voltada para estudantes, pesquisadores e analistas que precisam acessar shapefiles do sistema de maneira simples.

## Badges

[![Open In Collab](.github/colab-badge.svg)](https://colab.research.google.com/github/Malnati/download-car/blob/main/examples/colab.ipynb)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Pulls](https://img.shields.io/docker/pulls/urbanogilson/sicar)](https://hub.docker.com/r/urbanogilson/sicar)
[![Coverage Status](https://coveralls.io/repos/github/Malnati/download-car/badge.svg?branch=main)](https://coveralls.io/github/Malnati/download-car?branch=main)
[![interrogate](.github/interrogate_badge.svg)](https://interrogate.readthedocs.io/)

# ✨ Objetivo

Permitir o download programático dos dados públicos do SICAR. O projeto inclui drivers para reconhecimento de captcha via **Tesseract** (padrão) ou **PaddleOCR**.

---

# Índice

- [⚙️ Funções principais](#️-funções-principais)
- [📥 Parâmetros disponíveis](#-parâmetros-disponíveis)
- [🚀 Como usar](#-como-usar)
  - [1️⃣ Execução via Python (direto)](#1️⃣-execução-via-python-direto)
  - [2️⃣ Execução via Shell Script](#2️⃣-execução-via-shell-script)
  - [3️⃣ Execução via Docker Compose](#3️⃣-execução-via-docker-compose)
  - [4️⃣ Execução via Google Colab (Notebook Interativo)](#4️⃣-execução-via-google-colab-notebook-interativo)
  - [5️⃣ Execução via API](#5️⃣-execução-via-api)
    - [Campos esperados (multipart/form)](#campos-esperados-multipartform)
    - [Exemplo via curl](#exemplo-via-curl)
    - [Rodando localmente com FastAPI](#rodando-localmente-com-fastapi)
  - [6️⃣ Importação como módulo Python](#6️⃣-importação-como-módulo-python)
- [📦 Resultados e arquivos de saída](#-resultados-e-arquivos-de-saída)
- [📊 Data dictionary](#data-dictionary)
- [📝 Licença](#license)

```bash
pip install git+https://github.com/Malnati/download-car
```

Prerequisite:

---

# ⚙️ Funções principais

A classe central deste pacote é `Sicar`, que disponibiliza três métodos principais:

- `download_state(state, polygon, folder="temp", tries=25, debug=False, chunk_size=1024, timeout=30)`
- `download_country(polygon, folder="brazil", tries=25, debug=False, chunk_size=1024, timeout=30)`
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
| `timeout`   | int         | ❌          | `30`    | Tempo máximo em segundos para cada tentativa de download.                         | `timeout=60`                     |

Esses parâmetros se aplicam principalmente ao método `download_state`. O método `download_country` utiliza a mesma assinatura (exceto pelo parâmetro `state`).

---

# 🚀 Como usar

## 1️⃣ Execução via Python (direto)

```python
from SICAR import Sicar, State, Polygon

car = Sicar()
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

Crie um arquivo `docker-compose.yml` simples apontando para este repositório:

```yaml
version: "3.8"
services:
  sicar:
    build: .
    volumes:
      - .:/download-car
    command: python examples/docker.py
```

```bash
pip install 'SICAR[paddle] @  git+https://github.com/Malnati/download-car'
```

Execute:

```bash
docker compose up --build
```

## 4️⃣ Execução via Google Colab (Notebook Interativo)

[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Malnati/download-car/blob/main/examples/colab.ipynb)

O notebook permite baixar os shapefiles diretamente no navegador sem instalar nada.

## 5️⃣ Execução via API

Uma API pública de demonstração está disponível em [GitHub.com/Malnati/sicar-api](https://GitHub.com/Malnati/sicar-api/). O endpoint `/download` aceita requisições `POST` contendo o estado e o tipo de polígono desejado.

### Campos esperados (multipart/form)

| Campo    | Tipo  | Obrigatório | Descrição                                           |
|----------|-------|-------------|-----------------------------------------------------|
| `state`  | str   | ✅          | Sigla do estado (ex.: `SP`).                         |
| `polygon`| str   | ✅          | Tipo de camada (`APPS`, `AREA_PROPERTY`, etc.).      |

### Exemplo via curl

```bash
curl -X POST https://GitHub.com/Malnati/sicar-api/download \
  -F "state=SP" \
  -F "polygon=APPS" \
  --output SP_APPS.zip
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

## 6️⃣ Importação como módulo Python

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

# License

[MIT](LICENSE)

Se utilizar este projeto, cite: **Urbano, Gilson**. *SICAR Package*. Consulte o arquivo [CITATION.cff](CITATION.cff) para mais detalhes.
