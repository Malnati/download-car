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

# Imports condicionais - apenas quando necessário
# from download_car import DownloadCar, Polygon, State
# from download_car.drivers import Tesseract

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

def execute_simple_fallback(state: str, polygon: str, folder: str, tries: int, debug: bool, timeout: int, max_retries: int):
    """Executa download com fallback simples: Tesseract → VPN → Timeout aumentado."""
    
    print("🔄 Iniciando sequência de fallback simples (apenas Tesseract)...")
    
    # Limpar arquivos existentes
    expected_file = os.path.join(folder, f"{state}_AREA_IMOVEL.zip")
    if os.path.exists(expected_file):
        try:
            import subprocess
            subprocess.run(['sudo', 'rm', '-f', expected_file], capture_output=True)
            print(f"🗑️  Arquivo existente removido: {expected_file}")
        except Exception as e:
            print(f"⚠️  Não foi possível remover arquivo: {e}")
    
    # Garantir que a pasta existe
    os.makedirs(folder, exist_ok=True)
    
    # Estratégia 1: Tesseract com timeout normal
    try:
        print("🔍 Tentativa 1: Tesseract com timeout normal...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries)
        if result:
            print("✅ Download concluído com Tesseract!")
            return result
    except Exception as e:
        print(f"⚠️  Tesseract falhou: {e}")
    
    # Estratégia 2: Tesseract com timeout aumentado
    try:
        print("🔍 Tentativa 2: Tesseract com timeout aumentado (300s)...")
        result = execute_with_driver_fallback(state, polygon, folder, tries, debug, 300, max_retries)
        if result:
            print("✅ Download concluído com Tesseract (timeout aumentado)!")
            return result
    except Exception as e:
        print(f"⚠️  Tesseract com timeout aumentado falhou: {e}")
    
    # Estratégia 3: VPN + Tesseract
    try:
        print(" Tentativa 3: VPN + Tesseract...")
        from dev.vpn_manager import setup_vpn_fallback, execute_with_vpn_fallback
        setup_vpn_fallback()
        result = execute_with_vpn_fallback(
            lambda: execute_with_driver_fallback(state, polygon, folder, tries, debug, timeout, max_retries)
        )
        if result:
            print("✅ Download concluído com VPN + Tesseract!")
            return result
    except Exception as e:
        print(f"⚠️  VPN + Tesseract falhou: {e}")
    
    # Se chegou aqui, todas as estratégias falharam
    raise Exception("❌ Todas as estratégias de fallback falharam. Tente novamente em algumas horas.")

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
    parser.add_argument("--simple-fallback", action="store_true", help="Simple fallback: Tesseract → VPN (sem PaddleOCR)")
    
    args = parser.parse_args()
    
    # Executar com fallback simples (recomendado para evitar crash)
    if args.simple_fallback:
        print("🚀 Modo simples ativado: Tesseract → VPN (sem PaddleOCR)")
        execute_simple_fallback(
            args.state, args.polygon, args.folder, 
            args.tries, args.debug, args.timeout, args.max_retries
        )
        return
    
    # Executar com VPN se solicitado
    if args.use_vpn:
        print("🔒 Modo VPN ativado")
        from dev.vpn_manager import setup_vpn_fallback, execute_with_vpn_fallback
        setup_vpn_fallback()
        result = execute_with_vpn_fallback(
            lambda: execute_with_driver_fallback(args.state, args.polygon, args.folder, 
                                               args.tries, args.debug, args.timeout, args.max_retries)
        )
        return result
    
    # Execução normal com driver específico
    print(f"🤖 Usando driver: {args.driver}")
    execute_with_driver_fallback(
        args.state, args.polygon, args.folder, 
        args.tries, args.debug, args.timeout, args.max_retries
    )

if __name__ == "__main__":
    main()

