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

