from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import os
import zipfile
from pathlib import Path
from typing import Optional
import subprocess
import sys

from download_car import DownloadCar, State, Polygon
from download_car.drivers import Tesseract

# Configurações CORS baseadas em variáveis de ambiente
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET,POST,OPTIONS").split(",")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

app = FastAPI(
    title="Download CAR API",
    description="""
    API para download de dados do Cadastro Ambiental Rural (CAR) do Brasil.
    
    Esta API permite baixar shapefiles contendo informações geoespaciais de propriedades rurais,
    áreas de preservação permanente, vegetação nativa e outros polígonos ambientais para todos os estados brasileiros.
    
    ## Funcionalidades
    
    - **Download por Estado**: Baixa dados de um estado específico
    - **Download Nacional**: Baixa dados de todos os estados do Brasil
    - **Busca por CAR**: Localiza o estado de um imóvel pelo número do CAR
    - **Múltiplos Tipos de Polígonos**: AREA_IMOVEL, APPS, Reserva Legal, Vegetação Nativa, etc.
    - **Formato Shapefile**: Arquivos compatíveis com sistemas GIS
    
    ## Estados Disponíveis
    
    - AC: Acre
    - AL: Alagoas
    - AM: Amazonas
    - AP: Amapá
    - BA: Bahia
    - CE: Ceará
    - DF: Distrito Federal
    - ES: Espírito Santo
    - GO: Goiás
    - MA: Maranhão
    - MG: Minas Gerais
    - MS: Mato Grosso do Sul
    - MT: Mato Grosso
    - PA: Pará
    - PB: Paraíba
    - PE: Pernambuco
    - PI: Piauí
    - PR: Paraná
    - RJ: Rio de Janeiro
    - RN: Rio Grande do Norte
    - RO: Rondônia
    - RR: Roraima
    - RS: Rio Grande do Sul
    - SC: Santa Catarina
    - SE: Sergipe
    - SP: São Paulo
    - TO: Tocantins
    
    ## Tipos de Polígonos Disponíveis
    
    - **AREA_PROPERTY**: Perímetros dos imóveis (Property perimeters) - **PADRÃO**
    - **APPS**: Área de Preservação Permanente (Permanent preservation area)
    - **NATIVE_VEGETATION**: Remanescente de Vegetação Nativa (Native Vegetation Remnants)
    - **CONSOLIDATED_AREA**: Área Consolidada (Consolidated Area)
    - **AREA_FALL**: Área de Pousio (Fallow Area)
    - **HYDROGRAPHY**: Hidrografia (Hydrography)
    - **RESTRICTED_USE**: Uso Restrito (Restricted Use)
    - **ADMINISTRATIVE_SERVICE**: Servidão Administrativa (Administrative Servitude)
    - **LEGAL_RESERVE**: Reserva Legal (Legal reserve)
    """,
    version="1.0.0",
    contact={
        "name": "Download CAR API",
        "url": "https://github.com/Malnati/download-car",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configuração CORS baseada em variáveis de ambiente
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)


def zip_shapefile(shp_path: str) -> str:
    base = os.path.splitext(shp_path)[0]
    exts = [".shp", ".shx", ".dbf", ".prj"]
    files = [base + ext for ext in exts if os.path.exists(base + ext)]
    zip_path = base + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            zipf.write(f, arcname=os.path.basename(f))
    return zip_path


def extract_and_find_shp(upload_file: UploadFile, temp_dir: str) -> str:
    zip_path = os.path.join(temp_dir, upload_file.filename)
    with open(zip_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    shp_path = None
    for root, _dirs, files in os.walk(temp_dir):
        for file in files:
            if file.lower().endswith(".shp"):
                shp_path = os.path.join(root, file)
    if shp_path:
        return shp_path
    raise ValueError(f"No .shp file found in zip '{upload_file.filename}'.")


def run_download_state(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Executa o download_state.py como subprocess e retorna o caminho do arquivo baixado.
    """
    # Garante que a pasta existe
    os.makedirs(folder, exist_ok=True)
    
    # Constrói o comando
    cmd = [
        sys.executable, "download_state.py",
        "--state", state,
        "--polygon", polygon,
        "--folder", folder,
        "--tries", str(tries),
        "--debug", str(debug).lower(),
        "--timeout", str(timeout),
        "--max_retries", str(max_retries)
    ]
    
    # Executa o comando
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    
    if result.returncode != 0:
        raise Exception(f"Erro ao executar download_state.py: {result.stderr}")
    
    # Constrói o caminho esperado do arquivo
    expected_file = os.path.join(folder, f"{state}_{polygon}.zip")
    
    if not os.path.exists(expected_file):
        raise Exception(f"Arquivo não foi criado: {expected_file}")
    
    return expected_file


@app.post(
    "/download_state",
    summary="Download de dados por estado",
    description="""
    Baixa shapefiles de dados do CAR para um estado específico do Brasil.
    
    Este endpoint permite baixar dados geoespaciais de propriedades rurais, áreas de preservação
    permanente, vegetação nativa e outros polígonos ambientais para um estado selecionado.
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/download_state" \\
         -F "state=SP" \\
         -F "polygon=AREA_PROPERTY" \\
         -F "tries=25" \\
         -F "debug=false" \\
         --output SP_AREA_IMOVEL.zip
    ```
    
    **Arquivo de retorno:**
    - Formato: ZIP contendo shapefile (.shp, .shx, .dbf, .prj)
    - Nome: `{state}_{polygon}.zip`
    """,
    response_description="Arquivo ZIP contendo o shapefile do estado solicitado",
    tags=["Download por Estado"]
)
async def download_state_endpoint(
    state: str = Form(
        ...,
        description="Sigla do estado brasileiro (2 letras maiúsculas)",
        example="SP",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    polygon: str = Form(
        "AREA_PROPERTY",
        description="Tipo de polígono a ser baixado (padrão: AREA_PROPERTY)",
        example="AREA_PROPERTY",
        regex="^(AREA_PROPERTY|APPS|NATIVE_VEGETATION|CONSOLIDATED_AREA|AREA_FALL|HYDROGRAPHY|RESTRICTED_USE|ADMINISTRATIVE_SERVICE|LEGAL_RESERVE)$"
    ),
    folder: str = Form(
        "temp",
        description="Pasta temporária para armazenamento dos arquivos (opcional)",
        example="temp/sp_data"
    ),
    tries: int = Form(
        25,
        description="Número máximo de tentativas em caso de falha no download",
        example=25,
        ge=1,
        le=100
    ),
    debug: bool = Form(
        False,
        description="Ativa modo debug com mensagens detalhadas de progresso",
        example=False
    ),
    timeout: int = Form(
        30,
        description="Timeout em segundos para cada tentativa de download",
        example=30,
        ge=10,
        le=300
    ),
    max_retries: int = Form(
        5,
        description="Número máximo de tentativas para download de cada arquivo",
        example=5,
        ge=1,
        le=20
    ),
):
    """
    Baixa shapefiles de dados do CAR para um estado específico.
    """
    try:
        # Executa o download usando o download_state.py
        file_path = run_download_state(state, polygon, folder, tries, debug, timeout, max_retries)
        
        # Retorna o arquivo como resposta
        return FileResponse(
            path=file_path,
            filename=f"{state}_{polygon}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        return {"error": str(e)}, 500


@app.post(
    "/download_country",
    summary="Download de dados para todo o Brasil",
    description="""
    Baixa shapefiles de dados do CAR para todos os estados do Brasil.
    
    Este endpoint permite baixar dados geoespaciais de propriedades rurais, áreas de preservação
    permanente, vegetação nativa e outros polígonos ambientais para todos os 27 estados brasileiros.
    
    **⚠️ Atenção:** Este download pode demorar muito tempo e gerar um arquivo muito grande.
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/download_country" \\
         -F "polygon=AREA_PROPERTY" \\
         -F "folder=brazil" \\
         -F "tries=25" \\
         -F "debug=false" \\
         --output brazil_AREA_IMOVEL.zip
    ```
    
    **Arquivo de retorno:**
    - Formato: ZIP contendo shapefiles de todos os estados
    - Nome: `brazil_{polygon}.zip`
    - Estrutura: Cada estado em um arquivo separado dentro do ZIP
    """,
    response_description="Arquivo ZIP contendo shapefiles de todos os estados brasileiros",
    tags=["Download Nacional"]
)
async def download_country_endpoint(
    polygon: str = Form(
        "AREA_PROPERTY",
        description="Tipo de polígono a ser baixado para todos os estados (padrão: AREA_PROPERTY)",
        example="AREA_PROPERTY",
        regex="^(AREA_PROPERTY|APPS|NATIVE_VEGETATION|CONSOLIDATED_AREA|AREA_FALL|HYDROGRAPHY|RESTRICTED_USE|ADMINISTRATIVE_SERVICE|LEGAL_RESERVE)$"
    ),
    folder: str = Form(
        "brazil",
        description="Pasta base para armazenamento dos arquivos de todos os estados",
        example="brazil"
    ),
    tries: int = Form(
        25,
        description="Número máximo de tentativas por estado em caso de falha no download",
        example=25,
        ge=1,
        le=100
    ),
    debug: bool = Form(
        False,
        description="Ativa modo debug com mensagens detalhadas de progresso para cada estado",
        example=False
    ),
    timeout: int = Form(
        30,
        description="Timeout em segundos para cada tentativa de download",
        example=30,
        ge=10,
        le=300
    ),
    max_retries: int = Form(
        5,
        description="Número máximo de tentativas para download de cada arquivo",
        example=5,
        ge=1,
        le=20
    ),
):
    """
    Baixa shapefiles de dados do CAR para todos os estados do Brasil.
    """
    try:
        # Lista de todos os estados
        states = [state.name for state in State]
        
        # Cria a pasta base
        os.makedirs(folder, exist_ok=True)
        
        # Baixa dados para cada estado
        downloaded_files = []
        for state in states:
            try:
                file_path = run_download_state(state, polygon, folder, tries, debug, timeout, max_retries)
                downloaded_files.append(file_path)
            except Exception as e:
                if debug:
                    print(f"Erro ao baixar {state}: {e}")
                continue
        
        if not downloaded_files:
            return {"error": "Nenhum arquivo foi baixado com sucesso"}, 500
        
        # Cria um ZIP com todos os arquivos baixados
        country_zip_path = os.path.join(folder, f"brazil_{polygon}.zip")
        with zipfile.ZipFile(country_zip_path, "w", zipfile.ZIP_DEFLATED) as country_zip:
            for file_path in downloaded_files:
                country_zip.write(file_path, arcname=os.path.basename(file_path))
        
        # Retorna o arquivo ZIP do país
        return FileResponse(
            path=country_zip_path,
            filename=f"brazil_{polygon}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        return {"error": str(e)}, 500


@app.get(
    "/states",
    summary="Lista de estados disponíveis",
    description="""
    Retorna a lista completa de estados brasileiros disponíveis para download.
    
    Cada estado é retornado com sua sigla e nome completo.
    """,
    response_description="Lista de estados brasileiros com siglas e nomes",
    tags=["Informações"]
)
async def get_states():
    """
    Retorna a lista de estados brasileiros disponíveis.
    """
    states = []
    for state in State:
        states.append({
            "code": state.name,
            "name": state.value,
            "description": f"Estado de {state.value}"
        })
    
    return {
        "states": states,
        "total": len(states),
        "description": "Lista completa dos 27 estados brasileiros disponíveis para download"
    }


@app.get(
    "/polygons",
    summary="Lista de polígonos disponíveis",
    description="""
    Retorna a lista completa de tipos de polígonos disponíveis para download.
    
    Cada polígono é retornado com seu código e descrição detalhada.
    """,
    response_description="Lista de tipos de polígonos com códigos e descrições",
    tags=["Informações"]
)
async def get_polygons():
    """
    Retorna a lista de tipos de polígonos disponíveis.
    """
    polygons = []
    for polygon in Polygon:
        description = {
            "AREA_PROPERTY": "Perímetros dos imóveis (Property perimeters)",
            "APPS": "Área de Preservação Permanente (Permanent preservation area)",
            "NATIVE_VEGETATION": "Remanescente de Vegetação Nativa (Native Vegetation Remnants)",
            "CONSOLIDATED_AREA": "Área Consolidada (Consolidated Area)",
            "AREA_FALL": "Área de Pousio (Fallow Area)",
            "HYDROGRAPHY": "Hidrografia (Hydrography)",
            "RESTRICTED_USE": "Uso Restrito (Restricted Use)",
            "ADMINISTRATIVE_SERVICE": "Servidão Administrativa (Administrative Servitude)",
            "LEGAL_RESERVE": "Reserva Legal (Legal reserve)"
        }.get(polygon.name, "Polígono não documentado")
        
        polygons.append({
            "code": polygon.name,
            "value": polygon.value,
            "description": description
        })
    
    return {
        "polygons": polygons,
        "total": len(polygons),
        "description": "Lista completa dos tipos de polígonos disponíveis para download"
    }


@app.get(
    "/state",
    summary="Buscar estado de um imóvel pelo número do CAR",
    description="""
    Busca o estado onde está cadastrado um imóvel específico pelo seu número do CAR.
    
    Este endpoint analisa os shapefiles baixados de todos os estados para encontrar
    o imóvel com o número do CAR informado e retorna o shape do estado correspondente.
    
    **⚠️ Atenção:** Este endpoint requer que os dados dos estados estejam baixados.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/state?car=SP12345678901234567890"
    ```
    
    **Retorno:**
    - JSON com informações do imóvel encontrado
    - Shape do estado onde o imóvel está cadastrado
    """,
    response_description="Informações do imóvel e shape do estado",
    tags=["Busca por CAR"]
)
async def buscar_estado_por_car(
    car: str = Query(
        ...,
        description="Número do CAR do imóvel a ser buscado",
        example="SP12345678901234567890",
        min_length=10,
        max_length=50
    ),
    state: Optional[str] = Query(
        None,
        description="Sigla do estado para limitar a busca (opcional)",
        example="SP",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    data_folder: str = Query(
        "data",
        description="Pasta onde estão os dados baixados dos estados",
        example="data"
    )
):
    """
    Busca o estado de um imóvel pelo número do CAR.
    """
    try:
        # Esta funcionalidade ainda não está implementada na classe DownloadCar
        return {
            "success": False,
            "car_number": car,
            "message": "Funcionalidade de busca por CAR ainda não implementada. Use /download_state ou /download_country para baixar os dados primeiro."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "car_number": car
        }


@app.get(
    "/property",
    summary="Buscar propriedade pelo número do CAR",
    description="""
    Busca uma propriedade específica pelo seu número do CAR e retorna o shape da propriedade.
    
    Este endpoint analisa os shapefiles baixados de todos os estados para encontrar
    a propriedade com o número do CAR informado e retorna o shape da propriedade.
    
    **⚠️ Atenção:** Este endpoint requer que os dados dos estados estejam baixados.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/property?car=SP12345678901234567890"
    ```
    
    **Retorno:**
    - Shape da propriedade encontrada
    - Em caso de erro: JSON com mensagem de erro
    """,
    response_description="Shape da propriedade encontrada",
    tags=["Busca por CAR"]
)
async def buscar_propriedade_por_car(
    car: str = Query(
        ...,
        description="Número do CAR da propriedade a ser buscada",
        example="SP12345678901234567890",
        min_length=10,
        max_length=50
    ),
    state: Optional[str] = Query(
        None,
        description="Sigla do estado para limitar a busca (opcional)",
        example="SP",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    data_folder: str = Query(
        "data",
        description="Pasta onde estão os dados baixados dos estados",
        example="data"
    )
):
    """
    Busca uma propriedade pelo número do CAR e retorna o shape.
    """
    try:
        # Esta funcionalidade ainda não está implementada na classe DownloadCar
        return {
            "success": False,
            "car_number": car,
            "message": "Funcionalidade de busca por CAR ainda não implementada. Use /download_state ou /download_country para baixar os dados primeiro."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "car_number": car
        }


@app.get(
    "/",
    summary="Informações da API",
    description="""
    Página inicial da API com informações gerais e links úteis.
    """,
    response_description="Informações gerais da API",
    tags=["Informações"]
)
async def root():
    """
    Página inicial da API.
    """
    return {
        "title": "Download CAR API",
        "version": "1.0.0",
        "description": "API para download de dados do Cadastro Ambiental Rural (CAR) do Brasil",
        "endpoints": {
            "download_state": "/download_state - Download de dados por estado",
            "download_country": "/download_country - Download de dados para todo o Brasil",
            "states": "/states - Lista de estados disponíveis",
            "polygons": "/polygons - Lista de polígonos disponíveis",
            "state": "/state - Buscar estado de um imóvel pelo CAR",
            "property": "/property - Buscar propriedade pelo CAR"
        },
        "documentation": "/docs",
        "repository": "https://github.com/Malnati/download-car",
        "license": "MIT License"
    }
