# api.py
from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Path
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Optional

# Importa as funções de lógica do cli.py
from cli import (
    download_state_logic,
    download_country_logic,
    download_property_logic,
    buscar_estado_por_car_logic,
    buscar_propriedade_por_car_logic,
    get_state_status_logic,
    download_state_file_logic,
    sync_to_database_logic,
    database_status_logic,
    brasil_config_logic,
    car_data_logic,
    delete_state_logic,
    get_states_logic,
    get_polygons_logic
)

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
        # Delega para a lógica em cli.py
        file_path = download_state_logic(state, polygon, folder, tries, debug, timeout, max_retries)
        
        # Retorna o arquivo como resposta
        return FileResponse(
            path=file_path,
            filename=f"{state}_AREA_IMOVEL.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Delega para a lógica em cli.py
        file_path = download_country_logic(polygon, folder, tries, debug, timeout, max_retries)
        
        # Retorna o arquivo como resposta
        return FileResponse(
            path=file_path,
            filename=f"brazil_{polygon}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        # Delega para a lógica em cli.py
        result = get_states_logic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    try:
        # Delega para a lógica em cli.py
        result = get_polygons_logic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

        # Delega para a lógica em cli.py
        file_path = download_property_logic(car, state, folder, tries, debug, timeout, max_retries)
        
        # Retorna o arquivo como resposta
        return FileResponse(
            path=file_path,
            filename=f"property_{car}.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Delega para a lógica em cli.py
        result = buscar_estado_por_car_logic(car, state, data_folder)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    Busca uma propriedade pelo número do CAR.
    """
    try:
        # Delega para a lógica em cli.py
        result = buscar_propriedade_por_car_logic(car, state, data_folder)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Delega para a lógica em cli.py
        result = get_state_status_logic(state, folder)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        # Delega para a lógica em cli.py
        file_path = download_state_file_logic(state, polygon_type, folder)
        
        # Retorna o arquivo como resposta
        filename = f"{state}_{polygon_type}.zip"
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/sync_to_database",
    summary="Sincronizar shapefile com banco de dados",
    description="""
    Sincroniza um shapefile com o banco de dados PostgreSQL/PostGIS.
    
    Este endpoint permite sincronizar dados de um estado específico ou de um CAR específico
    com o banco de dados PostGIS configurado. Os dados são armazenados com geometria espacial
    e propriedades em formato JSON.
    
    **⚠️ Atenção:** Este endpoint requer que o banco de dados PostgreSQL/PostGIS esteja configurado
    e que a extensão PostGIS esteja habilitada.
    
    **Exemplo de uso:**
    ```bash
    # Sincronizar dados de um estado
    curl -X POST "http://localhost:8000/sync_to_database" \\
         -F "state=SP" \\
         -F "polygon_type=AREA_PROPERTY" \\
         -F "sync_type=state"
    
    # Sincronizar dados de um CAR específico
    curl -X POST "http://localhost:8000/sync_to_database" \\
         -F "car_code=SP12345678901234567890" \\
         -F "state=SP" \\
         -F "polygon_type=AREA_PROPERTY" \\
         -F "sync_type=car"
    ```
    
    **Retorno:**
    - JSON com informações sobre a sincronização realizada
    """,
    response_description="Resultado da sincronização com o banco de dados",
    tags=["Sincronização com Banco de Dados"]
)
async def sync_to_database_endpoint(
    sync_type: str = Form(
        ...,
        description="Tipo de sincronização: 'state' para estado completo ou 'car' para CAR específico",
        example="state",
        regex="^(state|car)$"
    ),
    state: str = Form(
        ...,
        description="Sigla do estado brasileiro (2 letras maiúsculas)",
        example="SP",
        min_length=2,
        max_length=2,
        regex="^[A-Z]{2}$"
    ),
    polygon_type: str = Form(
        "AREA_PROPERTY",
        description="Tipo de polígono a ser sincronizado (padrão: AREA_PROPERTY)",
        example="AREA_PROPERTY",
        regex="^(AREA_PROPERTY|APPS|NATIVE_VEGETATION|CONSOLIDATED_AREA|AREA_FALL|HYDROGRAPHY|RESTRICTED_USE|ADMINISTRATIVE_SERVICE|LEGAL_RESERVE)$"
    ),
    car_code: Optional[str] = Form(
        None,
        description="Código CAR específico (obrigatório quando sync_type=car)",
        example="SP12345678901234567890",
        min_length=10,
        max_length=50
    ),
    folder: str = Form(
        "temp",
        description="Pasta onde buscar os arquivos shapefile",
        example="temp"
    ),
):
    """
    Sincroniza shapefiles com o banco de dados PostgreSQL/PostGIS.
    """
    try:
        # Delega para a lógica em cli.py
        result = sync_to_database_logic(sync_type, state, polygon_type, car_code, folder)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/database_status",
    summary="Status da conexão com banco de dados",
    description="""
    Verifica o status da conexão com o banco de dados PostgreSQL/PostGIS.
    
    Este endpoint testa a conectividade com o banco de dados e retorna informações
    sobre a configuração atual.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/database_status"
    ```
    
    **Retorno:**
    - JSON com status da conexão e informações de configuração
    """,
    response_description="Status da conexão com o banco de dados",
    tags=["Sincronização com Banco de Dados"]
)
async def database_status_endpoint():
    """
    Verifica o status da conexão com o banco de dados.
    """
    try:
        # Delega para a lógica em cli.py
        result = database_status_logic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/brasil_config",
    summary="Configurações do Brasil",
    description="""
    Retorna as configurações padrão para a seção Brasil.
    
    Este endpoint fornece os valores iniciais para os campos MapBiomas e IBGE
    baseados nas variáveis de ambiente configuradas.
    
    **Exemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/brasil_config"
    ```
    
    **Retorno:**
    - JSON com configurações do Brasil
    """,
    response_description="Configurações do Brasil",
    tags=["Configurações"]
)
async def brasil_config_endpoint():
    """
    Retorna as configurações do Brasil.
    """
    try:
        # Delega para a lógica em cli.py
        result = brasil_config_logic()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/car_data",
    summary="Buscar dados do CAR no banco de dados",
    description="""
    Busca dados do CAR armazenados no banco de dados PostgreSQL/PostGIS.
    
    Este endpoint permite consultar os dados do CAR que foram sincronizados com o banco de dados,
    com filtros por código CAR, estado e tipo de polígono.
    
    **Exemplo de uso:**
    ```bash
    # Buscar todos os dados de um estado
    curl -X GET "http://localhost:8000/car_data?state=SP&limit=10"
    
    # Buscar dados de um CAR específico
    curl -X GET "http://localhost:8000/car_data?car_code=SP12345678901234567890"
    
    # Buscar dados por tipo de polígono
    curl -X GET "http://localhost:8000/car_data?polygon_type=APPS&limit=5"
    ```
    
    **Retorno:**
    - JSON com os dados do CAR encontrados
    """,
    response_description="Dados do CAR armazenados no banco de dados",
    tags=["Sincronização com Banco de Dados"]
)
async def car_data_endpoint(
    car_code: Optional[str] = Query(
        None,
        description="Código CAR específico para busca",
        example="SP12345678901234567890"
    ),
    state: Optional[str] = Query(
        None,
        description="Sigla do estado para filtrar resultados",
        example="SP",
        regex="^[A-Z]{2}$"
    ),
    polygon_type: Optional[str] = Query(
        None,
        description="Tipo de polígono para filtrar resultados",
        example="AREA_PROPERTY"
    ),
    limit: int = Query(
        100,
        description="Limite de resultados retornados",
        example=100,
        ge=1,
        le=1000
    )
):
    """
    Busca dados do CAR no banco de dados.
    """
    try:
        # Delega para a lógica em cli.py
        result = car_data_logic(car_code, state, polygon_type, limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            "property": "/property - Buscar propriedade pelo CAR",
            "sync_to_database": "/sync_to_database - Sincronizar shapefile com banco de dados",
            "database_status": "/database_status - Status da conexão com banco de dados",
            "car_data": "/car_data - Buscar dados do CAR no banco de dados"
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
        # Delega para a lógica em cli.py
        result = delete_state_logic(state, folder, include_properties)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
