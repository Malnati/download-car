from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import tempfile
import shutil
import os
import zipfile
from pathlib import Path
from typing import Optional

from download_car import DownloadCar, State, Polygon
from download_car.drivers import Tesseract

app = FastAPI(
    title="Download CAR API",
    description="""
    API para download de dados do Cadastro Ambiental Rural (CAR) do Brasil.
    
    Esta API permite baixar shapefiles contendo informações geoespaciais de propriedades rurais,
    áreas de preservação permanente, vegetação nativa e outros polígonos ambientais para todos os estados brasileiros.
    
    ## Funcionalidades
    
    - **Download por Estado**: Baixa dados de um estado específico
    - **Download Nacional**: Baixa dados de todos os estados do Brasil
    - **Múltiplos Tipos de Polígonos**: APPS, Reserva Legal, Vegetação Nativa, etc.
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
    
    - **AREA_PROPERTY**: Perímetros dos imóveis (Property perimeters)
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
         -F "polygon=APPS" \\
         -F "tries=25" \\
         -F "debug=false" \\
         --output SP_APPS.zip
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
        ...,
        description="Tipo de polígono a ser baixado",
        example="APPS",
        regex="^(AREA_PROPERTY|APPS|NATIVE_VEGETATION|CONSOLIDATED_AREA|AREA_FALL|HYDROGRAPHY|RESTRICTED_USE|ADMINISTRATIVE_SERVICE|LEGAL_RESERVE)$"
    ),
    folder: Optional[str] = Form(
        None,
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
    Baixa dados do CAR para um estado específico.
    
    **Parâmetros obrigatórios:**
    - `state`: Sigla do estado (ex: SP, RJ, MG)
    - `polygon`: Tipo de polígono (ex: APPS, AREA_PROPERTY, LEGAL_RESERVE)
    
    **Parâmetros opcionais:**
    - `folder`: Pasta de destino (padrão: pasta temporária)
    - `tries`: Tentativas de download (padrão: 25)
    - `debug`: Modo debug (padrão: False)
    - `timeout`: Timeout em segundos (padrão: 30)
    - `max_retries`: Máximo de retry (padrão: 5)
    
    **Retorna:**
    - Arquivo ZIP com shapefile do estado solicitado
    - Em caso de erro: JSON com mensagem de erro
    """
    try:
        car = DownloadCar(driver=Tesseract)
        path = car.download_state(
            state=State[state.upper()],
            polygon=Polygon[polygon.upper()],
            folder=folder or "temp",
            tries=tries,
            debug=debug,
            timeout=timeout,
        )
        zip_path = zip_shapefile(str(path))
        zip_file_handle = open(zip_path, "rb")
        return StreamingResponse(
            zip_file_handle,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{state}_{polygon}.zip"'},
        )
    except Exception as exc:
        return {"error": str(exc)}


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
         -F "polygon=APPS" \\
         -F "folder=brazil" \\
         -F "tries=25" \\
         -F "debug=false" \\
         --output brazil_APPS.zip
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
        ...,
        description="Tipo de polígono a ser baixado para todos os estados",
        example="APPS",
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
):
    """
    Baixa dados do CAR para todos os estados do Brasil.
    
    **Parâmetros obrigatórios:**
    - `polygon`: Tipo de polígono (ex: APPS, AREA_PROPERTY, LEGAL_RESERVE)
    
    **Parâmetros opcionais:**
    - `folder`: Pasta base de destino (padrão: "brazil")
    - `tries`: Tentativas por estado (padrão: 25)
    - `debug`: Modo debug (padrão: False)
    - `timeout`: Timeout em segundos (padrão: 30)
    
    **Retorna:**
    - Arquivo ZIP com shapefiles de todos os estados
    - Em caso de erro: JSON com mensagem de erro
    
    **Observações:**
    - O download pode demorar muito tempo (horas)
    - O arquivo resultante pode ser muito grande (GB)
    - Cada estado é baixado sequencialmente
    """
    try:
        car = DownloadCar(driver=Tesseract)
        result = car.download_country(
            polygon=Polygon[polygon.upper()],
            folder=folder,
            tries=tries,
            debug=debug,
            timeout=timeout,
        )
        zip_paths = []
        for _state, path in result.items():
            zip_paths.append(zip_shapefile(str(path)))
        with tempfile.NamedTemporaryFile(delete=False) as zip_file:
            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                for z in zip_paths:
                    zipf.write(z, os.path.basename(z))
            zip_file_path = zip_file.name
        zip_file_handle = open(zip_file_path, "rb")
        return StreamingResponse(
            zip_file_handle,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="brazil_{polygon}.zip"'},
        )
    except Exception as exc:
        return {"error": str(exc)}


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
    Retorna todos os estados brasileiros disponíveis.
    
    **Retorna:**
    - Lista de dicionários com sigla e nome de cada estado
    """
    states = []
    for state in State:
        states.append({
            "sigla": state.value,
            "nome": {
                "AC": "Acre",
                "AL": "Alagoas", 
                "AM": "Amazonas",
                "AP": "Amapá",
                "BA": "Bahia",
                "CE": "Ceará",
                "DF": "Distrito Federal",
                "ES": "Espírito Santo",
                "GO": "Goiás",
                "MA": "Maranhão",
                "MG": "Minas Gerais",
                "MS": "Mato Grosso do Sul",
                "MT": "Mato Grosso",
                "PA": "Pará",
                "PB": "Paraíba",
                "PE": "Pernambuco",
                "PI": "Piauí",
                "PR": "Paraná",
                "RJ": "Rio de Janeiro",
                "RN": "Rio Grande do Norte",
                "RO": "Rondônia",
                "RR": "Roraima",
                "RS": "Rio Grande do Sul",
                "SC": "Santa Catarina",
                "SE": "Sergipe",
                "SP": "São Paulo",
                "TO": "Tocantins"
            }.get(state.value, state.value)
        })
    return {"states": states}


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
    Retorna todos os tipos de polígonos disponíveis.
    
    **Retorna:**
    - Lista de dicionários com código e descrição de cada polígono
    """
    polygons = []
    for polygon in Polygon:
        descriptions = {
            "AREA_PROPERTY": "Perímetros dos imóveis (Property perimeters)",
            "APPS": "Área de Preservação Permanente (Permanent preservation area)",
            "NATIVE_VEGETATION": "Remanescente de Vegetação Nativa (Native Vegetation Remnants)",
            "CONSOLIDATED_AREA": "Área Consolidada (Consolidated Area)",
            "AREA_FALL": "Área de Pousio (Fallow Area)",
            "HYDROGRAPHY": "Hidrografia (Hydrography)",
            "RESTRICTED_USE": "Uso Restrito (Restricted Use)",
            "ADMINISTRATIVE_SERVICE": "Servidão Administrativa (Administrative Servitude)",
            "LEGAL_RESERVE": "Reserva Legal (Legal reserve)"
        }
        
        polygons.append({
            "codigo": polygon.name,
            "valor": polygon.value,
            "descricao": descriptions.get(polygon.name, polygon.name)
        })
    return {"polygons": polygons}


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
    Retorna informações gerais sobre a API.
    
    **Retorna:**
    - Informações sobre a API e links para documentação
    """
    return {
        "message": "Download CAR API",
        "version": "1.0.0",
        "description": "API para download de dados do Cadastro Ambiental Rural (CAR) do Brasil",
        "endpoints": {
            "download_state": "/download_state - Download de dados por estado",
            "download_country": "/download_country - Download de dados para todo o Brasil",
            "states": "/states - Lista de estados disponíveis",
            "polygons": "/polygons - Lista de polígonos disponíveis",
            "docs": "/docs - Documentação Swagger",
            "redoc": "/redoc - Documentação ReDoc"
        },
        "contact": {
            "name": "Download CAR API",
            "url": "https://github.com/Malnati/download-car"
        }
    }
