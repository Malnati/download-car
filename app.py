from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import shutil
import os
import zipfile
from pathlib import Path
from typing import Optional
import os

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
    
    - **AREA_IMOVEL**: Perímetros dos imóveis (Property perimeters) - **PADRÃO**
    - **APPS**: Área de Preservação Permanente (Permanent preservation area)
    - **VEGETACAO_NATIVA**: Remanescente de Vegetação Nativa (Native Vegetation Remnants)
    - **AREA_CONSOLIDADA**: Área Consolidada (Consolidated Area)
    - **AREA_POUSIO**: Área de Pousio (Fallow Area)
    - **HIDROGRAFIA**: Hidrografia (Hydrography)
    - **USO_RESTRITO**: Uso Restrito (Restricted Use)
    - **SERVIDAO_ADMINISTRATIVA**: Servidão Administrativa (Administrative Servitude)
    - **RESERVA_LEGAL**: Reserva Legal (Legal reserve)
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
         -F "polygon=AREA_IMOVEL" \\
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
        "AREA_IMOVEL",
        description="Tipo de polígono a ser baixado (padrão: AREA_IMOVEL)",
        example="AREA_IMOVEL",
        regex="^(AREA_IMOVEL|APPS|VEGETACAO_NATIVA|AREA_CONSOLIDADA|AREA_POUSIO|HIDROGRAFIA|USO_RESTRITO|SERVIDAO_ADMINISTRATIVA|RESERVA_LEGAL)$"
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
    
    **Parâmetros opcionais:**
    - `polygon`: Tipo de polígono (padrão: AREA_IMOVEL)
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
        car = DownloadCar(driver=Tesseract())
        
        # Mapear o valor do polígono para o enum correto
        polygon_mapping = {
            "AREA_IMOVEL": Polygon.AREA_PROPERTY,
            "APPS": Polygon.APPS,
            "VEGETACAO_NATIVA": Polygon.NATIVE_VEGETATION,
            "AREA_CONSOLIDADA": Polygon.CONSOLIDATED_AREA,
            "AREA_POUSIO": Polygon.AREA_FALL,
            "HIDROGRAFIA": Polygon.HYDROGRAPHY,
            "USO_RESTRITO": Polygon.RESTRICTED_USE,
            "SERVIDAO_ADMINISTRATIVA": Polygon.ADMINISTRATIVE_SERVICE,
            "RESERVA_LEGAL": Polygon.LEGAL_RESERVE
        }
        
        polygon_enum = polygon_mapping.get(polygon.upper())
        if not polygon_enum:
            return {"error": f"Polígono '{polygon}' não reconhecido"}
        
        path = car.download_state(
            state=State[state.upper()],
            polygon=polygon_enum,
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
         -F "polygon=AREA_IMOVEL" \\
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
        "AREA_IMOVEL",
        description="Tipo de polígono a ser baixado para todos os estados (padrão: AREA_IMOVEL)",
        example="AREA_IMOVEL",
        regex="^(AREA_IMOVEL|APPS|VEGETACAO_NATIVA|AREA_CONSOLIDADA|AREA_POUSIO|HIDROGRAFIA|USO_RESTRITO|SERVIDAO_ADMINISTRATIVA|RESERVA_LEGAL)$"
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
    - `polygon`: Tipo de polígono (padrão: AREA_IMOVEL)
    
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
        car = DownloadCar(driver=Tesseract())
        
        # Mapear o valor do polígono para o enum correto
        polygon_mapping = {
            "AREA_IMOVEL": Polygon.AREA_PROPERTY,
            "APPS": Polygon.APPS,
            "VEGETACAO_NATIVA": Polygon.NATIVE_VEGETATION,
            "AREA_CONSOLIDADA": Polygon.CONSOLIDATED_AREA,
            "AREA_POUSIO": Polygon.AREA_FALL,
            "HIDROGRAFIA": Polygon.HYDROGRAPHY,
            "USO_RESTRITO": Polygon.RESTRICTED_USE,
            "SERVIDAO_ADMINISTRATIVA": Polygon.ADMINISTRATIVE_SERVICE,
            "RESERVA_LEGAL": Polygon.LEGAL_RESERVE
        }
        
        polygon_enum = polygon_mapping.get(polygon.upper())
        if not polygon_enum:
            return {"error": f"Polígono '{polygon}' não reconhecido"}
        
        result = car.download_country(
            polygon=polygon_enum,
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
        state_names = {
            "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
            "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
            "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
            "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
            "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí",
            "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
            "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"
        }
        
        states.append({
            "sigla": state.value,
            "nome": state_names.get(state.value, state.value)
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
            "AREA_PROPERTY": "Perímetros dos imóveis (Property perimeters) - PADRÃO",
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
    
    **Parâmetros obrigatórios:**
    - `car`: Número do CAR do imóvel
    
    **Parâmetros opcionais:**
    - `state`: Sigla do estado para limitar a busca
    - `data_folder`: Pasta com os dados baixados (padrão: "data")
    
    **Retorna:**
    - JSON com informações do imóvel e estado encontrado
    - Em caso de erro: JSON com mensagem de erro
    """
    try:
        import geopandas as gpd
        from pathlib import Path
        import glob
        
        # Verificar se a pasta de dados existe
        data_path = Path(data_folder)
        if not data_path.exists():
            return {
                "error": f"Pasta de dados '{data_folder}' não encontrada. Baixe os dados primeiro usando /download_state ou /download_country."
            }
        
        # Buscar shapefiles de área de imóvel
        found_imovel = None
        found_state = None
        found_file = None
        
        # Definir estados para buscar
        states_to_search = [State[state.upper()]] if state else list(State)
        
        # Procurar em cada estado
        for state_enum in states_to_search:
            state_folder = data_path / state_enum.value
            if not state_folder.exists():
                continue
                
            # Procurar por arquivos de área de imóvel
            shp_files = list(state_folder.glob("*AREA_IMOVEL*.shp"))
            if not shp_files:
                continue
                
            for shp_file in shp_files:
                try:
                    # Ler o shapefile
                    gdf = gpd.read_file(shp_file)
                    
                    # Verificar se existe a coluna cod_imovel
                    if 'cod_imovel' not in gdf.columns:
                        continue
                    
                    # Buscar o CAR
                    mask = gdf['cod_imovel'] == car
                    if mask.any():
                        found_imovel = gdf[mask].iloc[0]
                        found_state = state_enum.value
                        found_file = str(shp_file)
                        break
                        
                except Exception as e:
                    print(f"Erro ao ler {shp_file}: {e}")
                    continue
            
            if found_imovel is not None:
                break
        
        if found_imovel is None:
            return {
                "error": f"Imóvel com CAR '{car}' não encontrado em nenhum estado.",
                "suggestion": "Verifique se o número do CAR está correto e se os dados dos estados foram baixados."
            }
        
        # Preparar resposta com informações do imóvel
        imovel_info = {}
        for col in found_imovel.index:
            if col != 'geometry':
                imovel_info[col] = str(found_imovel[col])
        
        # Buscar informações do estado
        state_names = {
            "AC": "Acre", "AL": "Alagoas", "AM": "Amazonas", "AP": "Amapá",
            "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
            "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
            "MG": "Minas Gerais", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
            "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco", "PI": "Piauí",
            "PR": "Paraná", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
            "RO": "Rondônia", "RR": "Roraima", "RS": "Rio Grande do Sul",
            "SC": "Santa Catarina", "SE": "Sergipe", "SP": "São Paulo", "TO": "Tocantins"
        }
        
        return {
            "success": True,
            "car": car,
            "estado": {
                "sigla": found_state,
                "nome": state_names.get(str(found_state), str(found_state))
            },
            "imovel": imovel_info,
            "arquivo_origem": found_file,
            "message": f"Imóvel encontrado no estado {found_state} ({state_names.get(str(found_state), str(found_state))})"
        }
        
    except ImportError:
        return {
            "error": "Biblioteca geopandas não encontrada. Instale com: pip install geopandas"
        }
    except Exception as exc:
        return {
            "error": f"Erro ao buscar imóvel: {str(exc)}"
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
    Busca uma propriedade pelo número do CAR e retorna o shape da propriedade.
    
    **Parâmetros obrigatórios:**
    - `car`: Número do CAR da propriedade
    
    **Parâmetros opcionais:**
    - `state`: Sigla do estado para limitar a busca
    - `data_folder`: Pasta com os dados baixados (padrão: "data")
    
    **Retorna:**
    - Shape da propriedade encontrada
    - Em caso de erro: JSON com mensagem de erro
    """
    try:
        import geopandas as gpd
        from pathlib import Path
        import glob
        
        # Verificar se a pasta de dados existe
        data_path = Path(data_folder)
        if not data_path.exists():
            return {
                "error": f"Pasta de dados '{data_folder}' não encontrada. Baixe os dados primeiro usando /download_state ou /download_country."
            }
        
        # Buscar shapefiles de área de imóvel
        found_imovel = None
        found_state = None
        found_file = None
        
        # Definir estados para buscar
        states_to_search = [State[state.upper()]] if state else list(State)
        
        # Procurar em cada estado
        for state_enum in states_to_search:
            state_folder = data_path / state_enum.value
            if not state_folder.exists():
                continue
                
            # Procurar por arquivos de área de imóvel
            shp_files = list(state_folder.glob("*AREA_IMOVEL*.shp"))
            if not shp_files:
                continue
                
            for shp_file in shp_files:
                try:
                    # Ler o shapefile
                    gdf = gpd.read_file(shp_file)
                    
                    # Verificar se existe a coluna cod_imovel
                    if 'cod_imovel' not in gdf.columns:
                        continue
                    
                    # Buscar o CAR
                    mask = gdf['cod_imovel'] == car
                    if mask.any():
                        found_imovel = gdf[mask].iloc[0]
                        found_state = state_enum.value
                        found_file = str(shp_file)
                        break
                        
                except Exception as e:
                    print(f"Erro ao ler {shp_file}: {e}")
                    continue
            
            if found_imovel is not None:
                break
        
        if found_imovel is None:
            return {
                "error": f"Propriedade com CAR '{car}' não encontrada em nenhum estado.",
                "suggestion": "Verifique se o número do CAR está correto e se os dados dos estados foram baixados."
            }
        
        # Criar GeoDataFrame apenas com a propriedade encontrada
        property_gdf = gpd.GeoDataFrame([found_imovel], crs=gdf.crs)
        
        # Salvar shape da propriedade em arquivo temporário
        temp_shp_path = f"temp_property_{car}.shp"
        property_gdf.to_file(temp_shp_path)
        
        # Criar ZIP com o shape da propriedade
        zip_path = zip_shapefile(temp_shp_path)
        zip_file_handle = open(zip_path, "rb")
        
        return StreamingResponse(
            zip_file_handle,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="property_{car}.zip"'},
        )
        
    except ImportError:
        return {
            "error": "Biblioteca geopandas não encontrada. Instale com: pip install geopandas"
        }
    except Exception as exc:
        return {
            "error": f"Erro ao buscar propriedade: {str(exc)}"
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
            "state": "/state - Buscar estado de um imóvel pelo CAR",
            "property": "/property - Buscar propriedade pelo CAR",
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
