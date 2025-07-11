# app.py
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Path
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import zipfile
import shutil
import tempfile
import shutil
import os
import zipfile
from pathlib import Path as FilePath
from typing import Optional
import subprocess
import sys
from datetime import datetime

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
    
    # Constrói o caminho esperado do arquivo
    # O download_state.py cria arquivos com o nome {state}_AREA_IMOVEL.zip
    # independentemente do polígono passado (AREA_PROPERTY é mapeado para AREA_IMOVEL)
    expected_file = os.path.join(folder, f"{state}_AREA_IMOVEL.zip")
    
    # Verifica se o arquivo foi criado, mesmo que o processo tenha falhado
    if os.path.exists(expected_file):
        return expected_file
    
    # Se o arquivo não existe, verifica se houve erro
    if result.returncode != 0:
        error_msg = result.stderr.strip()
        if "UrlNotOkException" in error_msg:
            raise Exception(f"Falha no download devido a problemas de captcha. Tente novamente em alguns minutos. Detalhes: {error_msg}")
        else:
            raise Exception(f"Erro ao executar download_state.py: {error_msg}")
    
    # Se chegou aqui, o processo não falhou mas o arquivo não foi criado
    raise Exception(f"Download concluído mas arquivo não foi criado: {expected_file}")


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
            filename=f"{state}_AREA_IMOVEL.zip",
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


@app.post(
    "/download-property",
    summary="Download de propriedade pelo número do CAR",
    description="""
    Baixa dados de uma propriedade específica pelo seu número do CAR.
    
    Este endpoint busca uma propriedade pelo número do CAR nos shapefiles
    já baixados dos estados e retorna os dados da propriedade em formato ZIP.
    
    **Exemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/download-property" \\
         -F "car=MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4" \\
         -F "state=MA" \\
         -F "folder=PROPERTY" \\
         -F "tries=25" \\
         -F "debug=false" \\
         --output property_MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4.zip
    ```
    
    **Arquivo de retorno:**
    - Formato: ZIP contendo shapefile da propriedade
    - Nome: `property_{car}.zip`
    """,
    response_description="Arquivo ZIP contendo os dados da propriedade",
    tags=["Download por Propriedade"]
)
async def download_property_endpoint(
    car: str = Form(
        ...,
        description="Número do CAR da propriedade a ser baixada",
        example="MA-2114007-FFFE73B6633D4199ACB914F4DFCCEEE4",
        min_length=10,
        max_length=50
    ),
    state: Optional[str] = Form(
        None,
        description="Sigla do estado para limitar a busca (opcional)",
        example="MA",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    folder: str = Form(
        os.getenv("PROPERTY_FOLDER", "PROPERTY"),
        description="Pasta para armazenamento dos arquivos da propriedade",
        example="PROPERTY"
    ),
    tries: int = Form(
        int(os.getenv("PROPERTY_TRIES", "25")),
        description="Número máximo de tentativas em caso de falha no download",
        example=25,
        ge=1,
        le=100
    ),
    debug: bool = Form(
        os.getenv("PROPERTY_DEBUG", "false").lower() == "true",
        description="Ativa modo debug com mensagens detalhadas de progresso",
        example=False
    ),
    timeout: int = Form(
        int(os.getenv("PROPERTY_TIMEOUT", "30")),
        description="Timeout em segundos para cada tentativa de download",
        example=30,
        ge=10,
        le=300
    ),
    max_retries: int = Form(
        int(os.getenv("PROPERTY_MAX_RETRIES", "5")),
        description="Número máximo de tentativas para download de cada arquivo",
        example=5,
        ge=1,
        le=20
    ),
):
    """
    Baixa dados de uma propriedade pelo número do CAR.
    """
    try:
        # Verificar se o estado foi informado
        if not state:
            raise HTTPException(
                status_code=400,
                detail="Estado deve ser informado para busca de propriedade"
            )

        # 1. Caminho do ZIP do estado
        polygon = "AREA_IMOVEL"  # Padrão usado no download
        zip_path = os.path.join("temp", f"{state}_{polygon}.zip")
        
        if not os.path.exists(zip_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Arquivo do estado {state} não encontrado. Baixe primeiro via /download_state."
            )

        # 2. Extrair o ZIP para um diretório temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            # 3. Encontrar o arquivo .shp extraído
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_files:
                raise HTTPException(
                    status_code=500, 
                    detail="Shapefile não encontrado no ZIP do estado."
                )
            shp_path = os.path.join(tmpdir, shp_files[0])

            # 4. Ler o shapefile com geopandas
            try:
                import geopandas as gpd
                gdf = gpd.read_file(shp_path)
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="Geopandas não disponível. Instale com: pip install geopandas"
                )

            # 5. Procurar o CAR (tentar diferentes nomes de campo)
            car_fields = ["CAR", "cod_imovel", "COD_IMOVEL", "car", "codigo_car"]
            car_field = None
            
            for field in car_fields:
                if field in gdf.columns:
                    car_field = field
                    break
            
            if car_field is None:
                # Se não encontrar, mostrar as colunas disponíveis para debug
                available_columns = list(gdf.columns)
                raise HTTPException(
                    status_code=500,
                    detail=f"Campo do CAR não encontrado. Colunas disponíveis: {available_columns}"
                )

            # 6. Buscar o CAR (case insensitive)
            result_gdf = gdf[gdf[car_field].astype(str).str.upper() == car.upper()]
            
            if result_gdf.empty:
                raise HTTPException(
                    status_code=404,
                    detail=f"CAR {car} não encontrado no estado {state}."
                )

            # 7. Salvar o resultado em um novo shapefile temporário
            out_dir = tempfile.mkdtemp()
            out_shp = os.path.join(out_dir, f"property_{car}.shp")
            result_gdf.to_file(out_shp)

            # 8. Empacotar o shapefile em um ZIP
            zip_filename = os.path.join(out_dir, f"property_{car}.zip")
            with zipfile.ZipFile(zip_filename, "w") as zipf:
                for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
                    f = out_shp.replace(".shp", ext)
                    if os.path.exists(f):
                        zipf.write(f, arcname=os.path.basename(f))

            # 9. Retornar o arquivo ZIP como download
            return FileResponse(
                path=zip_filename,
                filename=f"property_{car}.zip",
                media_type="application/zip"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar propriedade {car}: {str(e)}"
        )


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
    "/state_status/{state}",
    summary="Verificar status de arquivo de estado",
    description="""
    Verifica se existe arquivo baixado para um estado específico e retorna informações para download.
    
    Este endpoint verifica se há arquivos ZIP disponíveis para o estado informado e retorna
    informações sobre os arquivos encontrados, incluindo links para download.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/state_status/SP"
    ```
    
    **Retorno:**
    - JSON com informações sobre os arquivos disponíveis para o estado
    - Links para download dos arquivos encontrados
    """,
    response_description="Informações sobre arquivos disponíveis para o estado",
    tags=["Status de Estados"]
)
async def get_state_status(
    state: str = Path(...),
    folder: str = Query(
        "temp",
        description="Pasta onde buscar os arquivos do estado",
        example="temp"
    )
):
    """
    Verifica se existe arquivo baixado para um estado específico.
    """
    try:
        # Lista de possíveis arquivos para o estado
        state_files_patterns = [
            f"{state}_AREA_IMOVEL.zip",
            f"{state}_APPS.zip",
            f"{state}_NATIVE_VEGETATION.zip",
            f"{state}_CONSOLIDATED_AREA.zip",
            f"{state}_AREA_FALL.zip",
            f"{state}_HYDROGRAPHY.zip",
            f"{state}_RESTRICTED_USE.zip",
            f"{state}_ADMINISTRATIVE_SERVICE.zip",
            f"{state}_LEGAL_RESERVE.zip"
        ]
        
        available_files = []
        total_size = 0
        
        for pattern in state_files_patterns:
            file_path = os.path.join(folder, pattern)
            if os.path.exists(file_path):
                try:
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)
                    
                    # Extrair tipo de polígono do nome do arquivo
                    polygon_type = pattern.replace(f"{state}_", "").replace(".zip", "")
                    
                    available_files.append({
                        "filename": pattern,
                        "file_path": file_path,
                        "size_bytes": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(file_mtime).isoformat(),
                        "polygon_type": polygon_type,
                        "download_url": f"/download_state_file/{state}/{polygon_type}"
                    })
                    
                    total_size += file_size
                except Exception as e:
                    continue
        
        # Verificar se há arquivos do estado em ZIPs nacionais
        national_files_containing_state = []
        national_zip_patterns = [
            "brazil_AREA_IMOVEL.zip",
            "brazil_APPS.zip",
            "brazil_NATIVE_VEGETATION.zip",
            "brazil_CONSOLIDATED_AREA.zip",
            "brazil_AREA_FALL.zip",
            "brazil_HYDROGRAPHY.zip",
            "brazil_RESTRICTED_USE.zip",
            "brazil_ADMINISTRATIVE_SERVICE.zip",
            "brazil_LEGAL_RESERVE.zip"
        ]
        
        for pattern in national_zip_patterns:
            zip_path = os.path.join(folder, pattern)
            if os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        state_files_in_zip = [f for f in zip_ref.namelist() if f.startswith(f"{state}_")]
                        if state_files_in_zip:
                            national_files_containing_state.append({
                                "national_zip": pattern,
                                "state_files": state_files_in_zip
                            })
                except Exception as e:
                    continue
        
        return {
            "state": state,
            "has_files": len(available_files) > 0,
            "available_files": available_files,
            "total_files": len(available_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "national_files_containing_state": national_files_containing_state,
            "folder": folder,
            "message": f"Encontrados {len(available_files)} arquivo(s) para o estado {state}" if available_files else f"Nenhum arquivo encontrado para o estado {state}"
        }
        
    except Exception as e:
        return {
            "state": state,
            "has_files": False,
            "error": str(e),
            "message": f"Erro ao verificar arquivos do estado {state}"
        }


@app.get(
    "/download_state_file/{state}/{polygon_type}",
    summary="Download de arquivo específico de estado",
    description="""
    Faz download de um arquivo específico de um estado e tipo de polígono.
    
    Este endpoint permite baixar um arquivo ZIP específico de um estado e tipo de polígono
    que já foi baixado anteriormente.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/download_state_file/SP/AREA_IMOVEL" --output SP_AREA_IMOVEL.zip
    ```
    
    **Retorno:**
    - Arquivo ZIP do estado solicitado
    """,
    response_description="Arquivo ZIP do estado solicitado",
    tags=["Download por Estado"]
)
async def download_state_file(
    state: str = Path(...),
    polygon_type: str = Path(...),
    folder: str = Query(
        "temp",
        description="Pasta onde buscar o arquivo",
        example="temp"
    )
):
    """
    Faz download de um arquivo específico de um estado.
    """
    try:
        filename = f"{state}_{polygon_type}.zip"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Arquivo {filename} não encontrado para o estado {state}"
            )
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao baixar arquivo: {str(e)}"
        )


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
            "download_property": "/download-property - Download de propriedade pelo CAR",
            "delete_state": "/delete_state - Excluir downloads de um estado",
            "states": "/states - Lista de estados disponíveis",
            "polygons": "/polygons - Lista de polígonos disponíveis",
            "state": "/state - Buscar estado de um imóvel pelo CAR",
            "property": "/property - Buscar propriedade pelo CAR"
        },
        "documentation": "/docs",
        "repository": "https://github.com/Malnati/download-car",
        "license": "MIT License"
    }


@app.delete(
    "/delete_state",
    summary="Excluir downloads de um estado",
    description="""
    Exclui todos os arquivos relacionados a um estado específico.
    
    Este endpoint remove:
    - Arquivos de download do estado (shapefiles baixados do sistema CAR)
    - Arquivos de propriedades extraídas do estado
    - Arquivos temporários relacionados ao estado
    
    **⚠️ Atenção:** Esta operação é irreversível e excluirá permanentemente todos os dados do estado.
    
    **Exemplo de uso:**
    ```bash
    curl -X DELETE "http://localhost:8000/delete_state" \\
         -F "state=SP" \\
         -F "folder=temp" \\
         -F "include_properties=true"
    ```
    
    **Parâmetros:**
    - `state`: Sigla do estado a ser excluído (obrigatório)
    - `folder`: Pasta onde estão os arquivos do estado (opcional, padrão: "temp")
    - `include_properties`: Se deve excluir também arquivos de propriedades (opcional, padrão: true)
    
    **Retorno:**
    - JSON com informações sobre os arquivos excluídos
    """,
    response_description="Informações sobre os arquivos excluídos",
    tags=["Gerenciamento de Arquivos"]
)
async def delete_state_endpoint(
    state: str = Form(
        ...,
        description="Sigla do estado brasileiro a ser excluído (2 letras maiúsculas)",
        example="SP",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    folder: str = Form(
        "temp",
        description="Pasta onde estão os arquivos do estado (opcional)",
        example="temp"
    ),
    include_properties: bool = Form(
        True,
        description="Se deve excluir também arquivos de propriedades extraídas do estado",
        example=True
    ),
):
    """
    Exclui todos os arquivos relacionados a um estado específico.
    """
    try:
        deleted_files = []
        deleted_dirs = []
        errors = []
        
        # 1. Excluir arquivos de download do estado
        state_files_patterns = [
            f"{state}_AREA_IMOVEL.zip",
            f"{state}_APPS.zip",
            f"{state}_NATIVE_VEGETATION.zip",
            f"{state}_CONSOLIDATED_AREA.zip",
            f"{state}_AREA_FALL.zip",
            f"{state}_HYDROGRAPHY.zip",
            f"{state}_RESTRICTED_USE.zip",
            f"{state}_ADMINISTRATIVE_SERVICE.zip",
            f"{state}_LEGAL_RESERVE.zip"
        ]
        
        for pattern in state_files_patterns:
            file_path = os.path.join(folder, pattern)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                except Exception as e:
                    errors.append(f"Erro ao excluir {file_path}: {str(e)}")
        
        # 2. Excluir arquivos de propriedades do estado (se solicitado)
        if include_properties:
            # Buscar em pastas comuns onde propriedades podem estar
            property_folders = [
                "PROPERTY",
                "properties",
                "temp",
                folder
            ]
            
            for prop_folder in property_folders:
                if os.path.exists(prop_folder):
                    try:
                        # Buscar arquivos de propriedade que contenham o estado no nome
                        for root, dirs, files in os.walk(prop_folder):
                            for file in files:
                                if file.startswith("property_") and state in file:
                                    file_path = os.path.join(root, file)
                                    try:
                                        os.remove(file_path)
                                        deleted_files.append(file_path)
                                    except Exception as e:
                                        errors.append(f"Erro ao excluir propriedade {file_path}: {str(e)}")
                    except Exception as e:
                        errors.append(f"Erro ao buscar propriedades em {prop_folder}: {str(e)}")
        
        # 3. Excluir diretórios temporários vazios relacionados ao estado
        temp_dirs_to_check = [
            os.path.join(folder, state),
            os.path.join("temp", state),
            os.path.join("PROPERTY", state)
        ]
        
        for temp_dir in temp_dirs_to_check:
            if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                try:
                    # Verificar se o diretório está vazio
                    if not os.listdir(temp_dir):
                        os.rmdir(temp_dir)
                        deleted_dirs.append(temp_dir)
                except Exception as e:
                    errors.append(f"Erro ao excluir diretório {temp_dir}: {str(e)}")
        
        # 4. Verificar se há arquivos do estado em ZIPs nacionais
        national_zip_patterns = [
            "brazil_AREA_IMOVEL.zip",
            "brazil_APPS.zip",
            "brazil_NATIVE_VEGETATION.zip",
            "brazil_CONSOLIDATED_AREA.zip",
            "brazil_AREA_FALL.zip",
            "brazil_HYDROGRAPHY.zip",
            "brazil_RESTRICTED_USE.zip",
            "brazil_ADMINISTRATIVE_SERVICE.zip",
            "brazil_LEGAL_RESERVE.zip"
        ]
        
        national_files_containing_state = []
        for pattern in national_zip_patterns:
            zip_path = os.path.join(folder, pattern)
            if os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        state_files_in_zip = [f for f in zip_ref.namelist() if f.startswith(f"{state}_")]
                        if state_files_in_zip:
                            national_files_containing_state.append({
                                "zip_file": zip_path,
                                "state_files": state_files_in_zip
                            })
                except Exception as e:
                    errors.append(f"Erro ao verificar ZIP nacional {zip_path}: {str(e)}")
        
        return {
            "success": True,
            "state": state,
            "message": f"Exclusão de arquivos do estado {state} concluída",
            "deleted_files": deleted_files,
            "deleted_directories": deleted_dirs,
            "total_files_deleted": len(deleted_files),
            "total_dirs_deleted": len(deleted_dirs),
            "include_properties": include_properties,
            "national_files_containing_state": national_files_containing_state,
            "warnings": [
                "Arquivos em ZIPs nacionais não foram excluídos automaticamente",
                "Para excluir completamente, recrie os ZIPs nacionais sem o estado"
            ] if national_files_containing_state else [],
            "errors": errors if errors else None
        }
        
    except Exception as e:
        return {
            "success": False,
            "state": state,
            "error": str(e),
            "message": f"Erro ao excluir arquivos do estado {state}"
        }, 500
