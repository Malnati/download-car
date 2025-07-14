# cli.py
"""Core logic for download_car operations. Contains all business logic that was previously in api.py."""

import os
import argparse
import tempfile
import zipfile
import shutil
import sys
import subprocess
import time
from datetime import datetime
from typing import Optional, Dict, List, Any, Union
from pathlib import Path as FilePath
from itertools import cycle

def get_env_config():
    """Obtém configurações das variáveis de ambiente com valores padrão."""
    config = {}
    
    # Variáveis de download com valores padrão
    config['STATE'] = os.getenv('STATE', 'SP')
    config['POLYGON'] = os.getenv('POLYGON', 'AREA_PROPERTY')
    config['FOLDER'] = os.getenv('FOLDER', 'temp/SP')
    config['TRIES'] = os.getenv('TRIES', '25')
    config['DEBUG'] = os.getenv('DEBUG', 'false')
    config['TIMEOUT'] = os.getenv('TIMEOUT', '30')
    config['MAX_RETRIES'] = os.getenv('MAX_RETRIES', '5')
    
    return config

# Restaurado de app.py (commit d13d049)
def download_state_logic(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
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

# Restaurado de app.py (commit d13d049)
def download_country_logic(polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Baixa shapefiles de dados do CAR para todos os estados do Brasil.
    """
    from download_car import State
    
    # Lista de todos os estados
    states = [state.name for state in State]
    
    # Cria a pasta base
    os.makedirs(folder, exist_ok=True)
    
    # Baixa dados para cada estado
    downloaded_files = []
    for state in states:
        try:
            file_path = download_state_logic(state, polygon, folder, tries, debug, timeout, max_retries)
            downloaded_files.append(file_path)
        except Exception as e:
            if debug:
                print(f"Erro ao baixar {state}: {e}")
            continue
    
    if not downloaded_files:
        raise Exception("Nenhum arquivo foi baixado com sucesso")
    
    # Cria um ZIP com todos os arquivos baixados
    country_zip_path = os.path.join(folder, f"brazil_{polygon}.zip")
    with zipfile.ZipFile(country_zip_path, "w", zipfile.ZIP_DEFLATED) as country_zip:
        for file_path in downloaded_files:
            country_zip.write(file_path, arcname=os.path.basename(file_path))
    
    return country_zip_path

# Restaurado de app.py (commit d13d049)
def download_property_logic(car: str, state: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int) -> str:
    """
    Baixa dados de uma propriedade pelo número do CAR.
    """
    # Verificar se o estado foi informado
    if not state:
        raise Exception("Estado deve ser informado para busca de propriedade")

    # 1. Caminho do ZIP do estado
    polygon = "AREA_IMOVEL"  # Padrão usado no download
    zip_path = os.path.join("temp", f"{state}_{polygon}.zip")
    
    if not os.path.exists(zip_path):
        raise Exception(f"Arquivo do estado {state} não encontrado. Baixe primeiro via /download_state.")

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

        return zip_filename

# Restaurado de app.py commit d13d049
def buscar_estado_por_car_logic(car: str, state: Optional[str], data_folder: str) -> Dict:
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

# Restaurado de app.py (commit d13d049)
def buscar_propriedade_por_car_logic(car: str, state: Optional[str], data_folder: str) -> Dict:
    """
    Busca uma propriedade pelo número do CAR.
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

# Restaurado de app.py commit d13d049
def get_state_status_logic(state: str, folder: str) -> Dict:
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

# Restaurado de app.py (commit d13d049)
def download_state_file_logic(state: str, polygon_type: str, folder: str) -> str:
    """
    Faz download de um arquivo específico de um estado.
    """
    filename = f"{state}_{polygon_type}.zip"
    file_path = os.path.join(folder, filename)
    
    if not os.path.exists(file_path):
        raise Exception(f"Arquivo {filename} não encontrado para o estado {state}")
    
    return file_path

# Restaurado de app.py commit d13d049
def sync_to_database_logic(sync_type: str, state: str, polygon_type: str, car_code: Optional[str], folder: str) -> Dict:
    """
    Sincroniza shapefiles com o banco de dados PostgreSQL/PostGIS.
    """
    # Esta funcionalidade ainda não está implementada
    return {
        "success": False,
        "message": "Sincronização com banco de dados ainda não implementada",
        "sync_type": sync_type,
        "state": state,
        "polygon_type": polygon_type,
        "car_code": car_code,
        "folder": folder
    }

# Restaurado de app.py commit d13d049
def database_status_logic() -> Dict:
    """
    Verifica o status da conexão com o banco de dados.
    """
    # Esta funcionalidade ainda não está implementada
    return {
        "success": False,
        "message": "Verificação de status do banco de dados ainda não implementada",
        "status": "not_configured"
    }

# Restaurado de app.py (commit d13d049)
def brasil_config_logic() -> Dict:
    """
    Retorna configurações do Brasil.
    """
    # Esta funcionalidade ainda não está implementada
    return {
        "success": False,
        "message": "Configurações do Brasil ainda não implementada",
        "config": {}
    }

# Restaurado de app.py (commit d13d049)
def car_data_logic(car_code: Optional[str], state: Optional[str], polygon_type: Optional[str], limit: int) -> Dict:
    """
    Busca dados do CAR no banco de dados.
    """
    # Esta funcionalidade ainda não está implementada
    return {
        "success": False,
        "message": "Consulta de dados do CAR ainda não implementada",
        "car_code": car_code,
        "state": state,
        "polygon_type": polygon_type,
        "limit": limit,
        "data": []
    }

# Restaurado de app.py (commit d13d049)
def delete_state_logic(state: str, folder: str, include_properties: bool) -> Dict:
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
        }

# Restaurado de app.py (commit d13d049)
def get_states_logic() -> Dict:
    """
    Retorna a lista de estados brasileiros disponíveis.
    """
    from download_car import State
    
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

# Restaurado de app.py (commit d13d049)
def get_polygons_logic() -> Dict:
    """
    Retorna a lista de tipos de polígonos disponíveis.
    """
    from download_car import Polygon
    
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

def execute_with_driver_fallback(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int, driver_type: str = "tesseract"):
    """Executa download com driver OCR específico."""
    
    from download_car.drivers import Tesseract
    from download_car import DownloadCar, Polygon, State
    
    # Converter strings para enums
    state_enum = State[state] if state in State.__members__ else State[state]
    polygon_enum = Polygon[polygon] if polygon in Polygon.__members__ else Polygon[polygon]
    
    # Selecionar driver baseado no tipo
    if driver_type == "paddle":
        try:
            from download_car.drivers import PaddleOCR
            driver_class = PaddleOCR
            print("🔍 Usando driver PaddleOCR...")
        except ImportError:
            print("⚠️  PaddleOCR não disponível, usando Tesseract...")
            driver_class = Tesseract
    else:
        driver_class = Tesseract
        print("🔍 Usando driver Tesseract...")
    
    # Criar instância com o driver selecionado (passar a classe, não instância)
    car = DownloadCar(driver=driver_class)  # type: ignore
    
    # Tentar download
    result = car.download_state(
        state=state_enum,
        polygon=polygon_enum,
        folder=folder,
        tries=tries,
        debug=debug,
        timeout=timeout,
        max_retries=max_retries,
    )
    
    return result

def execute_download_sequence(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int):
    """Executa a sequência de download seguindo as orientações especificadas."""
    
    print("🚀 Iniciando sequência de download...")
    
    # Garantir que a pasta existe
    os.makedirs(folder, exist_ok=True)
    
    # Limpar arquivos existentes
    expected_file = os.path.join(folder, f"{state}_AREA_IMOVEL.zip")
    if os.path.exists(expected_file):
        try:
            subprocess.run(['sudo', 'rm', '-f', expected_file], capture_output=True)
            print(f"🗑️  Arquivo existente removido: {expected_file}")
        except Exception as e:
            print(f"⚠️  Não foi possível remover arquivo: {e}")
    
    # ETAPA 1: Tentativa com parâmetros do .config.env
    try:
        print("🔍 Etapa 1: Tentativa com parâmetros do .config.env...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries, "tesseract")
        if result:
            print("✅ Download concluído com sucesso na primeira tentativa!")
            return result
    except Exception as e:
        error_msg = str(e).lower()
        print(f"⚠️  Etapa 1 falhou: {e}")
        
        # Verificar se é erro de timeout
        if "timeout" in error_msg or "time out" in error_msg:
            print("⏰ Erro de timeout detectado, prosseguindo para Etapa 2...")
        elif "captcha" in error_msg or "ocr" in error_msg:
            print("🤖 Erro de captcha detectado, prosseguindo para Etapa 3...")
        elif any(keyword in error_msg for keyword in ["access", "blocked", "forbidden", "rate limit"]):
            print("🚫 Erro de acesso detectado, prosseguindo para Etapa 4...")
        else:
            print("❌ Erro não reconhecido, tentando próxima etapa...")
    
    # ETAPA 2: Timeout dobrado
    try:
        doubled_timeout = timeout * 2
        print(f"🔍 Etapa 2: Tentativa com timeout dobrado ({doubled_timeout}s)...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, doubled_timeout, max_retries, "tesseract")
        if result:
            print("✅ Download concluído com timeout dobrado!")
            return result
    except Exception as e:
        error_msg = str(e).lower()
        print(f"⚠️  Etapa 2 falhou: {e}")
        
        # Verificar se é erro de captcha
        if "captcha" in error_msg or "ocr" in error_msg:
            print("🤖 Erro de captcha detectado, prosseguindo para Etapa 3...")
        elif any(keyword in error_msg for keyword in ["access", "blocked", "forbidden", "rate limit"]):
            print("🚫 Erro de acesso detectado, prosseguindo para Etapa 4...")
        else:
            print("❌ Erro não reconhecido, tentando próxima etapa...")
    
    # ETAPA 3: Trocar driver para PaddleOCR
    try:
        print("🔍 Etapa 3: Tentativa com PaddleOCR...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries, "paddle")
        if result:
            print("✅ Download concluído com PaddleOCR!")
            return result
    except Exception as e:
        error_msg = str(e).lower()
        print(f"⚠️  Etapa 3 falhou: {e}")
        
        # Verificar se é erro de acesso
        if any(keyword in error_msg for keyword in ["access", "blocked", "forbidden", "rate limit"]):
            print("🚫 Erro de acesso detectado, prosseguindo para Etapa 4...")
        else:
            print("❌ Erro não reconhecido, tentando próxima etapa...")
    
    # ETAPA 4: Ativar VPN para problemas de acesso
    try:
        print("🔍 Etapa 4: Ativando VPN para contornar bloqueio de acesso...")
        from dev.vpn_manager import setup_vpn_fallback, execute_with_vpn_fallback
        
        def download_with_vpn():
            return execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries, "tesseract")
        
        result = execute_with_vpn_fallback(download_with_vpn)
        if result:
            print("✅ Download concluído com VPN!")
            return result
    except Exception as e:
        print(f"⚠️  Etapa 4 falhou: {e}")
    
    # Se chegou aqui, todas as estratégias falharam
    raise Exception("❌ Todas as estratégias de download falharam. Tente novamente em algumas horas.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download CAR CLI")
    
    # Argumentos existentes
    parser.add_argument("--state", type=str, help="State to download")
    parser.add_argument("--polygon", type=str, help="Polygon type")
    parser.add_argument("--folder", type=str, help="Folder to save files")
    parser.add_argument("--tries", type=int, help="Number of tries")
    parser.add_argument("--debug", type=bool, help="Debug mode")
    parser.add_argument("--timeout", type=int, help="Timeout in seconds")
    parser.add_argument("--max_retries", type=int, help="Max retries")
    
    # Novos argumentos para controle de sequência
    parser.add_argument("--use-vpn", action="store_true", help="Use VPN/Tor for download")
    parser.add_argument("--driver", type=str, choices=["tesseract", "paddle"], default="tesseract", help="OCR driver to use")
    parser.add_argument("--auto-fallback", action="store_true", help="Automatic fallback sequence")
    parser.add_argument("--simple-fallback", action="store_true", help="Simple fallback: Tesseract → VPN (sem PaddleOCR)")
    
    args = parser.parse_args()
    
    # Carregar configuração das variáveis de ambiente
    config = get_env_config()
    
    # Usar valores das variáveis de ambiente se não fornecidos via argumentos
    state = args.state or config.get('STATE', 'SP')
    polygon = args.polygon or config.get('POLYGON', 'AREA_PROPERTY')
    folder = args.folder or config.get('FOLDER', 'temp/SP')
    tries = args.tries or int(config.get('TRIES', 25))
    debug = args.debug if args.debug is not None else config.get('DEBUG', 'false').lower() == 'true'
    timeout = args.timeout or int(config.get('TIMEOUT', 30))
    max_retries = args.max_retries or int(config.get('MAX_RETRIES', 5))
    
    print(f"📋 Configuração carregada:")
    print(f"   Estado: {state}")
    print(f"   Polígono: {polygon}")
    print(f"   Pasta: {folder}")
    print(f"   Tentativas: {tries}")
    print(f"   Debug: {debug}")
    print(f"   Timeout: {timeout}s")
    print(f"   Max Retries: {max_retries}")
    
    # Executar com fallback simples (recomendado para evitar crash)
    if args.simple_fallback:
        print("🚀 Modo simples ativado: Tesseract → VPN (sem PaddleOCR)")
        # Implementar fallback simples aqui se necessário
        pass
    
    # Executar com VPN se solicitado
    if args.use_vpn:
        print("🔒 Modo VPN ativado")
        from dev.vpn_manager import setup_vpn_fallback, execute_with_vpn_fallback
        
        def download_with_vpn():
            return execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries, args.driver)
        
        result = execute_with_vpn_fallback(download_with_vpn)
        return result
    
    # Execução normal com sequência automática (padrão)
    if args.auto_fallback or not any([args.use_vpn, args.simple_fallback]):
        print("🚀 Executando sequência automática de fallback...")
        execute_download_sequence(state, polygon, folder, tries, debug, timeout, max_retries)
    else:
        # Execução normal com driver específico
        print(f"🤖 Usando driver: {args.driver}")
        execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries, args.driver)

if __name__ == "__main__":
    main()

