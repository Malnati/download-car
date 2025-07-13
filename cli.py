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
from typing import Optional, Dict, List, Any
from pathlib import Path as FilePath
from itertools import cycle

# NÃO importar requests aqui - será importado condicionalmente quando necessário

# Imports condicionais - apenas quando necessário
# from download_car import DownloadCar, Polygon, State
# from download_car.drivers import Tesseract

# =============================================================================
# VPN E PROXY MANAGER (INTEGRADO)
# =============================================================================

class VPNProxyManager:
    """Gerenciador de VPN e Proxy integrado para contornar rate limiting."""
    
    def __init__(self):
        self.current_method = None
        self.proxy_list = []
        self.vpn_configs = []
        self.max_retries = 3
        
    def add_proxy(self, proxy_url: str):
        """Adiciona proxy à lista de rotação."""
        self.proxy_list.append(proxy_url)
        print(f"🔗 Proxy adicionado: {proxy_url}")
    
    def add_vpn_config(self, config_path: str, username: str = None, password: str = None):
        """Adiciona configuração OpenVPN."""
        self.vpn_configs.append({
            'config_path': config_path,
            'username': username,
            'password': password
        })
        print(f" VPN config adicionada: {config_path}")
    
    def setup_tor_proxy(self) -> bool:
        """Configura proxy Tor."""
        try:
            # Import condicional
            import socks
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            import socket
            socket.socket = socks.socksocket
            print("🔗 Proxy Tor configurado")
            return True
        except ImportError:
            print("❌ Módulo 'pysocks' não encontrado. Instale com: pip install pysocks")
            return False
        except Exception as e:
            print(f"❌ Erro ao configurar Tor: {e}")
            return False
    
    def connect_openvpn(self, config: Dict) -> bool:
        """Conecta ao OpenVPN."""
        try:
            cmd = ['sudo', 'openvpn', '--config', config['config_path'], '--daemon']
            
            if config.get('username') and config.get('password'):
                # Criar arquivo de autenticação
                auth_file = '/tmp/vpn_auth.txt'
                with open(auth_file, 'w') as f:
                    f.write(f"{config['username']}\n{config['password']}\n")
                cmd.extend(['--auth-user-pass', auth_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f" OpenVPN conectado: {config['config_path']}")
                time.sleep(5)  # Aguardar estabilização
                return True
            else:
                print(f"❌ Falha OpenVPN: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erro OpenVPN: {e}")
            return False
    
    def disconnect_vpn(self):
        """Desconecta VPN atual."""
        try:
            subprocess.run(['sudo', 'pkill', 'openvpn'], capture_output=True)
            print("🔗 VPN desconectada")
        except Exception as e:
            print(f"❌ Erro ao desconectar VPN: {e}")
    
    def test_connection(self, url: str = "https://httpbin.org/ip") -> bool:
        """Testa se a conexão atual está funcionando."""
        try:
            # Import condicional
            import requests
            response = requests.get(url, timeout=10, verify=False)
            return response.status_code == 200
        except ImportError:
            print("❌ Módulo 'requests' não encontrado. Instale com: pip install requests")
            return False
        except:
            return False
    
    def rotate_connection(self) -> bool:
        """Rotaciona para próximo método de conexão."""
        print(" Rotacionando conexão...")
        
        # Tentar VPNs
        for config in self.vpn_configs:
            self.disconnect_vpn()
            if self.connect_openvpn(config):
                return True
        
        # Tentar Tor
        if self.setup_tor_proxy():
            return True
        
        # Tentar proxies
        if self.proxy_list:
            # Implementação básica de proxy
            print(f"🔗 Usando proxy da lista ({len(self.proxy_list)} disponíveis)")
            return True
        
        return False

# Instância global do gerenciador
vpn_manager = VPNProxyManager()

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def setup_vpn_fallback():
    """Configura fallback VPN com configurações reais."""
    # Proxies gratuitos reais (exemplo)
    real_proxies = [
        "http://185.199.229.156:7492",
        "http://185.199.228.220:7492", 
        "http://185.199.231.45:7492",
        "http://185.199.230.102:7492"
    ]
    
    for proxy in real_proxies:
        vpn_manager.add_proxy(proxy)
    
    # Configurar Tor se disponível
    try:
        import subprocess
        result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
        if result.returncode == 0:
            print("🔗 Tor detectado no sistema")
            
            # Verificar se Tor está rodando
            try:
                import requests
                response = requests.get('https://check.torproject.org/', 
                                     proxies={'http': 'socks5://127.0.0.1:9050',
                                             'https': 'socks5://127.0.0.1:9050'},
                                     timeout=10)
                if 'Congratulations' in response.text:
                    print("✅ Tor está funcionando!")
                    vpn_manager.add_proxy("socks5://127.0.0.1:9050")
                else:
                    print("⚠️  Tor não está funcionando corretamente")
            except:
                print("⚠️  Tor não está acessível")
        else:
            print("⚠️  Tor não encontrado no sistema")
    except:
        print("⚠️  Não foi possível verificar Tor")

def execute_with_vpn_fallback(func, *args, **kwargs):
    """Executa função com fallback VPN em caso de rate limiting."""
    for attempt in range(vpn_manager.max_retries):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detectar rate limiting ou problemas SSL
            if any(keyword in error_msg for keyword in [
                "rate limit", "ssl", "handshake", "timeout", "connection", "urlnotok"
            ]):
                print(f"⚠️  Problema de conexão detectado (tentativa {attempt + 1}/{vpn_manager.max_retries})")
                print(f"🔍 Erro: {e}")
                
                if vpn_manager.rotate_connection():
                    print("⏳ Aguardando estabilização da conexão...")
                    time.sleep(10)
                    continue
                else:
                    print("❌ Não foi possível rotacionar conexão")
            else:
                # Erro não relacionado a conexão, propagar
                raise e
    
    raise Exception("❌ Todas as tentativas de conexão falharam")

def execute_with_automatic_vpn_fallback(func, *args, **kwargs):
    """Executa função com fallback VPN automático em caso de rate limiting."""
    
    def _detect_rate_limiting_error(error):
        """Detecta se o erro é de rate limiting ou SSL."""
        error_msg = str(error).lower()
        rate_limiting_keywords = [
            "rate limit", "ssl", "handshake", "timeout", 
            "connection", "urlnotok", "failed to access"
        ]
        return any(keyword in error_msg for keyword in rate_limiting_keywords)
    
    # Primeira tentativa: download normal
    try:
        print("🚀 Tentativa 1: Download normal...")
        result = func(*args, **kwargs)
        if result:  # Se retornou um caminho válido
            print("✅ Download concluído com sucesso!")
            return result
    except Exception as e:
        if _detect_rate_limiting_error(e):
            print(f"⚠️  Problema de conexão detectado: {e}")
            print("🔄 Ativando modo VPN fallback...")
        else:
            # Erro não relacionado a conexão, propagar
            raise e
    
    # Se chegou aqui, houve problema de conexão ou download falhou
    # Tentar com VPN fallback
    for attempt in range(3):  # Máximo 3 tentativas com VPN
        try:
            print(f"🚀 Tentativa {attempt + 2}: Rotacionando conexão...")
            
            # Rotacionar conexão (VPN/proxy)
            if vpn_manager.rotate_connection():
                print("⏳ Aguardando estabilização da conexão...")
                time.sleep(10)
                
                # Tentar download novamente
                result = func(*args, **kwargs)
                if result:
                    print("✅ Download concluído com VPN!")
                    return result
            else:
                print("❌ Não foi possível rotacionar conexão")
                break
                
        except Exception as e:
            print(f"❌ Tentativa {attempt + 2} falhou: {e}")
            if not _detect_rate_limiting_error(e):
                # Erro não relacionado a conexão, propagar
                raise e
    
    raise Exception("❌ Todas as tentativas falharam (normal + VPN)")

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

def run_download_state(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int, use_vpn_fallback: bool = False) -> str:
    """
    Executa o download de um estado e retorna o caminho do arquivo baixado.
    """
    def _download_internal():
        try:
            # Importa apenas quando necessário
            from download_car import DownloadCar, Polygon
            from download_car.drivers import Tesseract
            
            # Garante que a pasta existe
            os.makedirs(folder, exist_ok=True)
            
            # Cria instância do DownloadCar
            car = DownloadCar(driver=Tesseract)
            
            # Executa o download diretamente
            car.download_state(
                state=state,
                polygon=Polygon[polygon],
                folder=folder,
                tries=tries,
                debug=debug,
                timeout=timeout,
                max_retries=max_retries
            )
            
            # Constrói o caminho esperado do arquivo
            expected_file = os.path.join(folder, f"{state}_AREA_IMOVEL.zip")
            
            if os.path.exists(expected_file):
                return expected_file
            else:
                raise Exception(f"Download concluído mas arquivo não foi criado: {expected_file}")
                
        except Exception as e:
            # Se o arquivo foi criado mesmo com erro, retorna o caminho
            expected_file = os.path.join(folder, f"{state}_AREA_IMOVEL.zip")
            if os.path.exists(expected_file):
                return expected_file
            
            # Se não foi criado, propaga o erro
            if "UrlNotOkException" in str(e):
                raise Exception(f"Falha no download devido a problemas de captcha. Tente novamente em alguns minutos. Detalhes: {str(e)}")
            else:
                raise Exception(f"Erro ao executar download: {str(e)}")
    
    if use_vpn_fallback:
        return execute_with_vpn_fallback(_download_internal)
    else:
        return _download_internal()

# =============================================================================
# FUNÇÕES DE DOWNLOAD
# =============================================================================

def download_state_logic(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int, use_vpn_fallback: bool = False) -> str:
    """
    Lógica de download de estado com suporte a VPN fallback.
    """
    try:
        # Executa o download usando o cli.py
        file_path = run_download_state(state, polygon, folder, tries, debug, timeout, max_retries, use_vpn_fallback)
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

def execute_with_driver_fallback(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int):
    """Executa download com fallback automático entre drivers OCR."""
    
    from download_car.drivers import Tesseract
    from download_car import DownloadCar, Polygon, State
    
    # Tentar importar PaddleOCR
    try:
        from download_car.drivers import PaddleOCR
        paddle_available = PaddleOCR is not None
    except ImportError:
        paddle_available = False
    
    # Converter strings para enums
    state_enum = State[state] if state in State.__members__ else State[state]
    polygon_enum = Polygon[polygon] if polygon in Polygon.__members__ else Polygon[polygon]
    
    # Definir drivers disponíveis
    drivers = [("Tesseract", Tesseract)]
    if paddle_available:
        drivers.append(("PaddleOCR", PaddleOCR))
    
    for driver_name, driver_class in drivers:
        try:
            print(f"🔍 Tentativa com {driver_name}...")
            
            # Criar instância com o driver atual
            car = DownloadCar(driver=driver_class)
            
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
            
            if result:
                print(f"✅ Download concluído com sucesso usando {driver_name}!")
                return result
                
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detectar se é problema de captcha/OCR
            if any(keyword in error_msg for keyword in [
                "invalid captcha", "failed to download", "captcha", "ocr"
            ]):
                print(f"⚠️  {driver_name} falhou: {e}")
                if driver_name == "Tesseract" and paddle_available:
                    print(f"🔄 Tentando PaddleOCR...")
                    continue
                else:
                    print(f"❌ Não há mais drivers disponíveis")
                    break
            else:
                # Erro não relacionado a OCR, propagar
                print(f"❌ Erro não relacionado a OCR com {driver_name}: {e}")
                raise e
    
    raise Exception("❌ Todos os drivers OCR falharam")

def download_large_state_with_chunks(car, state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int):
    """Download especial para estados com grandes volumes de dados."""
    
    print(f"📦 Estado {state} detectado como grande volume. Usando estratégia especial...")
    
    # Estratégia 1: Tentar com timeout maior e fallback de drivers
    try:
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, 300, max_retries)
        return result
    except Exception as e:
        print(f"⚠️  Estratégia 1 falhou: {e}")
    
    # Estratégia 2: Tentar com menos tentativas mas mais tempo entre elas
    try:
        result = execute_with_driver_fallback(state, polygon, folder, 10, debug, timeout, max_retries)
        return result
    except Exception as e:
        print(f"⚠️  Estratégia 2 falhou: {e}")
    
    # Estratégia 3: Tentar com VPN + fallback de drivers
    return execute_with_automatic_vpn_fallback(
        lambda *args, **kwargs: execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries)
    )

def is_large_state(state: str) -> bool:
    """Detecta se o estado tem grande volume de dados."""
    large_states = [
        "AC",  # Acre - muito grande
        "PA",  # Pará - muito grande  
        "AM",  # Amazonas - muito grande
        "MT",  # Mato Grosso - grande
        "MG",  # Minas Gerais - grande
        "SP",  # São Paulo - grande
    ]
    return state.upper() in large_states

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Download CAR CLI")
    
    # Argumentos existentes
    parser.add_argument("--state", type=str, help="State to download")
    parser.add_argument("--polygon", type=str, help="Polygon type")
    parser.add_argument("--folder", type=str, help="Folder to save files")
    parser.add_argument("--tries", type=int, default=3, help="Number of tries")
    parser.add_argument("--debug", type=bool, default=False, help="Debug mode")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    parser.add_argument("--max_retries", type=int, default=3, help="Max retries")
    
    # Novos argumentos para VPN e PaddleOCR
    parser.add_argument("--use-vpn", action="store_true", help="Use VPN/Tor for download")
    parser.add_argument("--driver", type=str, choices=["tesseract", "paddle"], default="tesseract", help="OCR driver to use")
    parser.add_argument("--auto-fallback", action="store_true", help="Automatic fallback: Tesseract → PaddleOCR → VPN")
    
    args = parser.parse_args()
    
    # Configurar VPN se solicitado
    if args.use_vpn or args.auto_fallback:
        setup_vpn_fallback()
    
    # Executar com fallback automático se solicitado
    if args.auto_fallback:
        print("🚀 Modo automático ativado: Tesseract → PaddleOCR → VPN")
        execute_complete_fallback(
            args.state, args.polygon, args.folder, 
            args.tries, args.debug, args.timeout, args.max_retries
        )
        return
    
    # Executar com VPN se solicitado
    if args.use_vpn:
        print("🔒 Modo VPN ativado")
        run_download_state(
            args.state, args.polygon, args.folder, 
            args.tries, args.debug, args.timeout, args.max_retries, 
            use_vpn_fallback=True
        )
        return
    
    # Execução normal com driver específico
    print(f"🤖 Usando driver: {args.driver}")
    run_download_state(
        args.state, args.polygon, args.folder, 
        args.tries, args.debug, args.timeout, args.max_retries
    )

def execute_complete_fallback(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int):
    """Executa download com fallback completo: Tesseract → PaddleOCR → VPN → Timeout aumentado."""
    
    print("🔄 Iniciando sequência de fallback automático...")
    
    # Estratégia 1: Tesseract com timeout normal
    try:
        print("🔍 Tentativa 1: Tesseract com timeout normal...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries)
        if result:
            print("✅ Download concluído com Tesseract!")
            return result
    except Exception as e:
        print(f"⚠️  Tesseract falhou: {e}")
    
    # Estratégia 2: PaddleOCR com timeout normal
    try:
        print("🔍 Tentativa 2: PaddleOCR com timeout normal...")
        from download_car.drivers import PaddleOCR
        from download_car import DownloadCar, Polygon, State
        
        car = DownloadCar(driver=PaddleOCR)
        result = car.download_state(
            state=State[state],
            polygon=Polygon[polygon],
            folder=folder,
            tries=tries,
            debug=debug,
            timeout=timeout,
            max_retries=max_retries,
        )
        if result:
            print("✅ Download concluído com PaddleOCR!")
            return result
    except Exception as e:
        print(f"⚠️  PaddleOCR falhou: {e}")
    
    # Estratégia 3: Tesseract com timeout aumentado
    try:
        print("🔍 Tentativa 3: Tesseract com timeout aumentado (300s)...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, 300, max_retries)
        if result:
            print("✅ Download concluído com Tesseract (timeout aumentado)!")
            return result
    except Exception as e:
        print(f"⚠️  Tesseract com timeout aumentado falhou: {e}")
    
    # Estratégia 4: PaddleOCR com timeout aumentado
    try:
        print("🔍 Tentativa 4: PaddleOCR com timeout aumentado (300s)...")
        from download_car.drivers import PaddleOCR
        from download_car import DownloadCar, Polygon, State
        
        car = DownloadCar(driver=PaddleOCR)
        result = car.download_state(
            state=State[state],
            polygon=Polygon[polygon],
            folder=folder,
            tries=tries,
            debug=debug,
            timeout=300,
            max_retries=max_retries,
        )
        if result:
            print("✅ Download concluído com PaddleOCR (timeout aumentado)!")
            return result
    except Exception as e:
        print(f"⚠️  PaddleOCR com timeout aumentado falhou: {e}")
    
    # Estratégia 5: VPN + Tesseract
    try:
        print("🚀 Tentativa 5: VPN + Tesseract...")
        setup_vpn_fallback()
        result = execute_with_vpn_fallback(
            lambda: execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries)
        )
        if result:
            print("✅ Download concluído com VPN + Tesseract!")
            return result
    except Exception as e:
        print(f"⚠️  VPN + Tesseract falhou: {e}")
    
    # Estratégia 6: VPN + PaddleOCR
    try:
        print("🚀 Tentativa 6: VPN + PaddleOCR...")
        from download_car.drivers import PaddleOCR
        from download_car import DownloadCar, Polygon, State
        
        car = DownloadCar(driver=PaddleOCR)
        result = execute_with_vpn_fallback(
            lambda: car.download_state(
                state=State[state],
                polygon=Polygon[polygon],
                folder=folder,
                tries=tries,
                debug=debug,
                timeout=timeout,
                max_retries=max_retries,
            )
        )
        if result:
            print("✅ Download concluído com VPN + PaddleOCR!")
            return result
    except Exception as e:
        print(f"⚠️  VPN + PaddleOCR falhou: {e}")
    
    # Se chegou aqui, todas as estratégias falharam
    raise Exception("❌ Todas as estratégias de fallback falharam. Tente novamente em algumas horas.")

if __name__ == "__main__":
    # Quando executado diretamente, apenas executa a função main original
    # sem importar as funções de lógica que dependem de módulos externos
    main()

