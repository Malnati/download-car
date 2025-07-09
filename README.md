<!-- README.md -->
# Download CAR files (shape) 

Ferramenta que automatiza o download de arquivos do [Cadastro Ambiental Rural (SICAR)](https://car.gov.br/publico/imoveis/index). Ela é voltada para estudantes, pesquisadores e analistas que precisam acessar shapefiles do sistema de maneira simples.

## Badges

[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Malnati/download-car/blob/main/colab.ipynb)
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
> This project automates downloads of SICAR shapefiles (Brazilian Rural Environmental Registry), with CLI, Python, Docker, API and Jupyter/Colab support. See below for parameter examples, references and data sources.

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

O repositório já possui um `docker-compose.yml` configurado com três serviços:

```yaml
version: "3.8"
services:
  download-car-download:
    build:
      context: .
      dockerfile: Dockerfile.download-car
    volumes:
      - .:/download-car
    entrypoint: ./entrypoint.download.sh
  download-car-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    volumes:
      - .:/download-car
    ports:
      - "8000:8000"
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - download-car-api
      - download-car-download
```

* **download-car-download** – roda o script `entrypoint.download.sh` para baixar os arquivos
  desejados. Defina as variáveis `STATE`, `POLYGON` e `FOLDER` conforme a
  necessidade.
* **download-car-api** – executa o `uvicorn` servindo a aplicação FastAPI em
  `http://localhost:8000`.
* **nginx** – expõe a porta `80` e redireciona `/download` para o serviço de download,
  encaminhando o restante para a API.

Assim, requisições para `http://localhost/download` são atendidas pelo
container `download-car-download`, enquanto os demais caminhos passam para
`download-car-api`.

Primeiro, construa a imagem base:

```bash
make build
```

Se desejar baixar os modelos do PaddleOCR durante a construção,
habilite a variável `PRELOAD_MODELS`:

```bash
PRELOAD_MODELS=1 make build
```

Alguns processadores não possuem suporte a AVX, o que pode causar falha
na instalação desses modelos. Deixe a opção desabilitada nesses casos.

Em seguida, suba os serviços:

```bash
docker compose up
```

Os logs do container de download indicarão o progresso do script, enquanto a
API poderá ser acessada em `http://localhost` via Nginx (porta `80`).

## 4️⃣ Execução via Google Colab (Notebook Interativo)

[![Open In Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Malnati/download-car/blob/main/colab.ipynb)

O notebook permite baixar os shapefiles diretamente no navegador sem instalar nada.

## 5️⃣ Execução via API

Uma API pública de demonstração está disponível em [GitHub.com/Malnati/download-car-api](https://GitHub.com/Malnati/download-car-api/). O endpoint `/download` aceita requisições `POST` contendo o estado e o tipo de polígono desejado.

### Campos esperados (multipart/form)

| Campo    | Tipo  | Obrigatório | Descrição                                           |
|----------|-------|-------------|-----------------------------------------------------|
| `state`  | str   | ✅          | Sigla do estado (ex.: `SP`).                         |
| `polygon`| str   | ✅          | Tipo de camada (`APPS`, `AREA_PROPERTY`, etc.).      |

### Exemplo via curl

```bash
curl -X POST https://GitHub.com/Malnati/download-car-api/download \
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

Após instalar com `pip install git+https://github.com/Malnati/download-car`, basta importar e usar:

```python
from download_car import DownloadCar, State, Polygon

car = DownloadCar()
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

# ❓ FAQ

**Como faço para baixar todos os estados automaticamente?**
- Use um loop shell com o script, ou modifique os exemplos para percorrer todos os códigos de estado.

**Como saber se o download terminou corretamente?**
- O script gera logs e arquivos zip por estado. Verifique os diretórios de saída.

**Posso contribuir?**
- Sim! Veja a seção "Contributing". Issues e pull requests são bem-vindos.

# License

[MIT](LICENSE)

Se utilizar este projeto, cite: **Urbano, Gilson**. *download-car Package*. Consulte o arquivo [CITATION.cff](CITATION.cff) para mais detalhes.
