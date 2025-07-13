# cli.py
"""Core logic for download_car operations. Contains all business logic that was previously in api.py."""

import os
import argparse
import tempfile
import zipfile
import shutil
import sys
import subprocess
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path as FilePath

# Imports condicionais - apenas quando necessário
# from download_car import DownloadCar, Polygon, State
# from download_car.drivers import Tesseract

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def zip_shapefile(shp_path: str) -> str:
    """Cria um arquivo ZIP contendo todos os arquivos do shapefile."""
    base = os.path.splitext(shp_path)[0]
    exts = [".shp", ".shx", ".dbf", ".prj"]
    files = [base + ext for ext in exts if os.path.exists(base + ext)]
    zip_path = base + ".zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            zipf.write(f, arcname=os.path.basename(f))
    return zip_path


def extract_and_find_shp(upload_file, temp_dir: str) -> str:
    """Extrai um arquivo ZIP e encontra o arquivo .shp dentro dele."""
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
    Executa o download de um estado e retorna o caminho do arquivo baixado.
    """
    # Garante que a pasta existe
    os.makedirs(folder, exist_ok=True)
    
    # Constrói o comando
    cmd = [
        sys.executable, "cli.py",
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
    # O cli.py cria arquivos com o nome {state}_AREA_IMOVEL.zip
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
            raise Exception(f"Erro ao executar cli.py: {error_msg}")
    
    # Se chegou aqui, o processo não falhou mas o arquivo não foi criado
    raise Exception(f"Download concluído mas arquivo não foi criado: {expected_file}")


# =============================================================================
# FUNÇÕES DE DOWNLOAD
# =============================================================================

def download_state_logic(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Lógica de download de estado - transferida de api.py
    """
    try:
        # Executa o download usando o cli.py
        file_path = run_download_state(state, polygon, folder, tries, debug, timeout, max_retries)
        return file_path
    except Exception as e:
        raise Exception(f"Erro no download do estado {state}: {str(e)}")


def download_country_logic(polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Lógica de download de país - transferida de api.py
    """
    try:
        # Importa apenas quando necessário
        from download_car import DownloadCar, Polygon
        from download_car.drivers import Tesseract
        
        # Garante que a pasta existe
        os.makedirs(folder, exist_ok=True)
        
        # Cria instância do DownloadCar
        car = DownloadCar(driver=Tesseract)
        
        # Download para todos os estados
        car.download_country(
            polygon=Polygon[polygon],
            folder=folder,
            tries=tries,
            debug=debug,
            timeout=timeout,
            max_retries=max_retries
        )
        
        # Constrói o caminho do arquivo nacional
        national_file = os.path.join(folder, f"brazil_{polygon}.zip")
        
        if os.path.exists(national_file):
            return national_file
        else:
            raise Exception(f"Arquivo nacional não foi criado: {national_file}")
            
    except Exception as e:
        raise Exception(f"Erro no download nacional: {str(e)}")


def download_property_logic(car: str, state: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Lógica de download de propriedade - transferida de api.py
    """
    try:
        # Verificar se o estado foi informado
        if not state:
            raise Exception("Estado deve ser informado para busca de propriedade")

        # 1. Caminho do ZIP do estado
        polygon = "AREA_IMOVEL"  # Padrão usado no download
        zip_path = os.path.join("temp", f"{state}_{polygon}.zip")
        
        if not os.path.exists(zip_path):
            raise Exception(f"Arquivo do estado {state} não encontrado. Baixe primeiro via download_state.")

        # 2. Extrair o ZIP para um diretório temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)

            # 3. Encontrar o arquivo .shp extraído
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_files:
                raise Exception("Shapefile não encontrado no ZIP do estado.")
            shp_path = os.path.join(tmpdir, shp_files[0])

            # 4. Ler o shapefile com geopandas
            try:
                import geopandas as gpd
                gdf = gpd.read_file(shp_path)
            except ImportError:
                raise Exception("Geopandas não disponível. Instale com: pip install geopandas")

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
                raise Exception(f"Campo do CAR não encontrado. Colunas disponíveis: {available_columns}")

            # 6. Buscar o CAR (case insensitive)
            result_gdf = gdf[gdf[car_field].astype(str).str.upper() == car.upper()]
            
            if result_gdf.empty:
                raise Exception(f"CAR {car} não encontrado no estado {state}.")

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

            # 9. Retornar o caminho do arquivo ZIP
            return zip_filename
            
    except Exception as e:
        raise Exception(f"Erro ao processar propriedade {car}: {str(e)}")


# =============================================================================
# FUNÇÕES DE BUSCA
# =============================================================================

def buscar_estado_por_car_logic(car: str, state: Optional[str], data_folder: str) -> Dict[str, Any]:
    """
    Lógica de busca de estado por CAR - transferida de api.py
    """
    try:
        # Esta funcionalidade ainda não está implementada na classe DownloadCar
        # Por enquanto, retorna uma mensagem informativa
        return {
            "success": False,
            "message": "Funcionalidade de busca de estado por CAR ainda não implementada",
            "car": car,
            "state": state,
            "data_folder": data_folder
        }
    except Exception as e:
        raise Exception(f"Erro ao buscar estado por CAR: {str(e)}")


def buscar_propriedade_por_car_logic(car: str, state: Optional[str], data_folder: str) -> Dict[str, Any]:
    """
    Lógica de busca de propriedade por CAR - transferida de api.py
    """
    try:
        # Esta funcionalidade ainda não está implementada na classe DownloadCar
        # Por enquanto, retorna uma mensagem informativa
        return {
            "success": False,
            "message": "Funcionalidade de busca de propriedade por CAR ainda não implementada",
            "car": car,
            "state": state,
            "data_folder": data_folder
        }
    except Exception as e:
        raise Exception(f"Erro ao buscar propriedade por CAR: {str(e)}")


# =============================================================================
# FUNÇÕES DE STATUS E GERENCIAMENTO
# =============================================================================

def get_state_status_logic(state: str, folder: str) -> Dict[str, Any]:
    """
    Lógica de verificação de status de estado - transferida de api.py
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


def download_state_file_logic(state: str, polygon_type: str, folder: str) -> str:
    """
    Lógica de download de arquivo específico de estado - transferida de api.py
    """
    try:
        filename = f"{state}_{polygon_type}.zip"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            raise Exception(f"Arquivo {filename} não encontrado para o estado {state}")
        
        return file_path
        
    except Exception as e:
        raise Exception(f"Erro ao baixar arquivo: {str(e)}")


def delete_state_logic(state: str, folder: str, include_properties: bool) -> Dict[str, Any]:
    """
    Lógica de exclusão de estado - transferida de api.py
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
        }


# =============================================================================
# FUNÇÕES DE BANCO DE DADOS
# =============================================================================

def sync_to_database_logic(sync_type: str, state: str, polygon_type: str, car_code: Optional[str], folder: str) -> Dict[str, Any]:
    """
    Lógica de sincronização com banco de dados - transferida de api.py
    """
    try:
        # Importa db_manager apenas quando necessário
        from database import db_manager
        
        # Verificar se o banco de dados está configurado
        if not db_manager.test_connection():
            raise Exception("Não foi possível conectar ao banco de dados. Verifique as configurações.")
        
        # Verificar se PostGIS está disponível
        if not db_manager.check_postgis_extension():
            raise Exception("PostGIS não está disponível no banco de dados.")
        
        # Verificar parâmetros baseados no tipo de sincronização
        if sync_type == "car" and not car_code:
            raise Exception("Código CAR é obrigatório quando sync_type=car")
        
        # Caminho do arquivo shapefile
        polygon = "AREA_IMOVEL"  # Padrão usado no download
        zip_path = os.path.join(folder, f"{state}_{polygon}.zip")
        
        if not os.path.exists(zip_path):
            raise Exception(f"Arquivo do estado {state} não encontrado. Baixe primeiro via download_state.")
        
        # Extrair o ZIP para um diretório temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Encontrar o arquivo .shp extraído
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_files:
                raise Exception("Shapefile não encontrado no ZIP do estado.")
            
            shp_path = os.path.join(tmpdir, shp_files[0])
            
            # Sincronizar com o banco de dados
            result = db_manager.sync_shapefile_to_db(
                shapefile_path=shp_path,
                state=state,
                polygon_type=polygon_type,
                car_code=car_code
            )
            
            if not result["success"]:
                raise Exception(result["message"])
            
            return {
                "success": True,
                "message": "Sincronização concluída com sucesso",
                "sync_type": sync_type,
                "state": state,
                "polygon_type": polygon_type,
                "car_code": car_code,
                "records_processed": result.get("records_processed", 0),
                "details": result
            }
            
    except Exception as e:
        raise Exception(f"Erro ao sincronizar com banco de dados: {str(e)}")


def database_status_logic() -> Dict[str, Any]:
    """
    Lógica de verificação de status do banco de dados - transferida de api.py
    """
    try:
        # Importa db_manager apenas quando necessário
        from database import db_manager
        
        # Testar conexão
        connection_ok = db_manager.test_connection()
        
        # Obter informações de configuração
        config = {
            "db_host": os.getenv("DB_HOST", "localhost"),
            "db_port": os.getenv("DB_PORT", "5432"),
            "db_name": os.getenv("DB_NAME", "download_car"),
            "db_user": os.getenv("DB_USER", "postgres"),
            "db_schema": os.getenv("DB_SCHEMA", "public"),
            "db_pool_size": os.getenv("DB_POOL_SIZE", "5"),
            "db_timeout": os.getenv("DB_TIMEOUT", "30")
        }
        
        return {
            "success": connection_ok,
            "connection_status": "connected" if connection_ok else "disconnected",
            "configuration": config,
            "message": "Conexão com banco de dados funcionando" if connection_ok else "Erro na conexão com banco de dados"
        }
        
    except Exception as e:
        return {
            "success": False,
            "connection_status": "error",
            "error": str(e),
            "message": "Erro ao verificar status do banco de dados"
        }


def car_data_logic(car_code: Optional[str], state: Optional[str], polygon_type: Optional[str], limit: int) -> Dict[str, Any]:
    """
    Lógica de busca de dados do CAR no banco de dados - transferida de api.py
    """
    try:
        # Importa db_manager apenas quando necessário
        from database import db_manager
        
        result = db_manager.get_car_data(
            car_code=car_code,
            state=state,
            polygon_type=polygon_type,
            limit=limit
        )
        
        if not result["success"]:
            raise Exception(result["message"])
        
        return result
        
    except Exception as e:
        raise Exception(f"Erro ao buscar dados do CAR: {str(e)}")


# =============================================================================
# FUNÇÕES DE CONFIGURAÇÃO
# =============================================================================

def brasil_config_logic() -> Dict[str, Any]:
    """
    Lógica de configurações do Brasil - transferida de api.py
    """
    try:
        config = {
            "mapbiomas_url": os.getenv("MAPBIOMAS_URL", "https://storage.googleapis.com/mapbiomas-public/initiative/collection-7/brasil/coverage/mapbiomas-brasil-coverage-2022.tif"),
            "ibge_url": os.getenv("IBGE_URL", "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Municipios_2022.zip")
        }
        
        return {
            "success": True,
            "configuration": config,
            "message": "Configurações do Brasil carregadas com sucesso"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao carregar configurações do Brasil"
        }


def get_states_logic() -> Dict[str, Any]:
    """
    Lógica de obtenção da lista de estados - transferida de api.py
    """
    try:
        # Importa apenas quando necessário
        from download_car import State
        
        states = []
        for state in State:
            states.append({
                "code": state.name,
                "name": state.value
            })
        
        return {
            "success": True,
            "states": states,
            "total": len(states),
            "message": f"Lista de {len(states)} estados brasileiros"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao obter lista de estados"
        }


def get_polygons_logic() -> Dict[str, Any]:
    """
    Lógica de obtenção da lista de polígonos - transferida de api.py
    """
    try:
        polygons = [
            {
                "code": "AREA_PROPERTY",
                "name": "Perímetros dos imóveis",
                "description": "Property perimeters - PADRÃO"
            },
            {
                "code": "APPS",
                "name": "Área de Preservação Permanente",
                "description": "Permanent preservation area"
            },
            {
                "code": "NATIVE_VEGETATION",
                "name": "Remanescente de Vegetação Nativa",
                "description": "Native Vegetation Remnants"
            },
            {
                "code": "CONSOLIDATED_AREA",
                "name": "Área Consolidada",
                "description": "Consolidated Area"
            },
            {
                "code": "AREA_FALL",
                "name": "Área de Pousio",
                "description": "Fallow Area"
            },
            {
                "code": "HYDROGRAPHY",
                "name": "Hidrografia",
                "description": "Hydrography"
            },
            {
                "code": "RESTRICTED_USE",
                "name": "Uso Restrito",
                "description": "Restricted Use"
            },
            {
                "code": "ADMINISTRATIVE_SERVICE",
                "name": "Servidão Administrativa",
                "description": "Administrative Servitude"
            },
            {
                "code": "LEGAL_RESERVE",
                "name": "Reserva Legal",
                "description": "Legal reserve"
            }
        ]
        
        return {
            "success": True,
            "polygons": polygons,
            "total": len(polygons),
            "message": f"Lista de {len(polygons)} tipos de polígonos disponíveis"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao obter lista de polígonos"
        }


# =============================================================================
# FUNÇÃO PRINCIPAL CLI (MANTIDA PARA COMPATIBILIDADE)
# =============================================================================

def main():
    """Função principal do CLI - mantida para compatibilidade com o código original."""
    # Importa apenas quando necessário
    from download_car import DownloadCar, Polygon, State
    from download_car.drivers import Tesseract
    
    parser = argparse.ArgumentParser(description="Download SICAR state polygon.")
    parser.add_argument("--state", type=str, default=os.getenv("STATE", "DF"))
    parser.add_argument("--polygon", type=str, default=os.getenv("POLYGON", "AREA_PROPERTY"))
    parser.add_argument("--folder", type=str, default=os.getenv("FOLDER", "data/DF"))
    parser.add_argument("--tries", type=int, default=int(os.getenv("TRIES", "25")))
    parser.add_argument("--debug", type=lambda x: str(x).lower() == "true", default=os.getenv("DEBUG", "False"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("TIMEOUT", "30")))
    parser.add_argument("--max_retries", type=int, default=int(os.getenv("MAX_RETRIES", "5")))
    args = parser.parse_args()

    # Read parameters from environment variables with reasonable defaults
    state = State[args.state] if args.state in State.__members__ else State[os.getenv("STATE", "DF")]
    polygon = Polygon[args.polygon] if args.polygon in Polygon.__members__ else Polygon[os.getenv("POLYGON", "AREA_PROPERTY")]
    folder = args.folder
    tries = args.tries
    debug = args.debug
    chunk_size = 1024
    timeout = args.timeout
    max_retries = args.max_retries

    # Create DownloadCar instance (using Tesseract as default driver)
    car = DownloadCar(driver=Tesseract)

    # Download polygon for the selected state
    car.download_state(
        state=state,
        polygon=polygon,
        folder=folder,
        tries=tries,
        debug=debug,
        chunk_size=chunk_size,
        timeout=timeout,
        max_retries=max_retries,
    )

    # Download polygons for all states (uncomment if needed)
    # car.download_country(polygon=polygon, folder="/Brazil")

    # Get release date for all states and print the one for the chosen state
    release_dates = car.get_release_dates()
    print(f"Release date for {state.name} is: {release_dates.get(state)}")


if __name__ == "__main__":
    # Quando executado diretamente, apenas executa a função main original
    # sem importar as funções de lógica que dependem de módulos externos
    main()

