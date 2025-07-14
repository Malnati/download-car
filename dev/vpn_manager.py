# dev/vpn_manager.py
"""
VPN Manager Module.

This module provides VPN and proxy management functionality for the download-car project.
"""

import os
import subprocess
import time
from typing import Dict, List, Any

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
    
    def setup_tor_proxy(self) -> bool:
        """Configura proxy Tor."""
        try:
            import socks
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            import socket
            socket.socket = socks.socksocket
            print("🔗 Proxy Tor configurado")
            return True
        except ImportError:
            print("❌ Módulo 'pysocks' não encontrado")
            return False
        except Exception as e:
            print(f"❌ Erro ao configurar Tor: {e}")
            return False
    
    def test_connection(self, url: str = "https://httpbin.org/ip") -> bool:
        """Testa se a conexão atual está funcionando."""
        try:
            import requests
            response = requests.get(url, timeout=10, verify=False)
            return response.status_code == 200
        except ImportError:
            print("❌ Módulo 'requests' não encontrado")
            return False
        except:
            return False
    
    def rotate_connection(self) -> bool:
        """Rotaciona para próximo método de conexão."""
        print(" Rotacionando conexão...")
        
        # Tentar Tor
        if self.setup_tor_proxy():
            return True
        
        # Tentar proxies
        if self.proxy_list:
            print(f"🔗 Usando proxy da lista ({len(self.proxy_list)} disponíveis)")
            return True
        
        return False

def setup_vpn_fallback():
    """Configura fallback VPN com configurações reais."""
    manager = VPNProxyManager()
    
    # Proxies gratuitos reais (exemplo)
    real_proxies = [
        "http://185.199.229.156:7492",
        "http://185.199.228.220:7492", 
        "http://185.199.231.45:7492",
        "http://185.199.230.102:7492"
    ]
    
    for proxy in real_proxies:
        manager.add_proxy(proxy)
    
    # Configurar Tor se disponível
    try:
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
                    manager.add_proxy("socks5://127.0.0.1:9050")
                else:
                    print("⚠️  Tor não está funcionando corretamente")
            except:
                print("⚠️  Tor não está acessível")
        else:
            print("⚠️  Tor não encontrado no sistema")
    except:
        print("⚠️  Não foi possível verificar Tor")
    
    return manager

def execute_with_vpn_fallback(func, *args, **kwargs):
    """Executa função com fallback VPN em caso de rate limiting."""
    manager = setup_vpn_fallback()
    
    for attempt in range(manager.max_retries):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            error_msg = str(e).lower()
            
            # Detectar rate limiting ou problemas SSL
            if any(keyword in error_msg for keyword in [
                "rate limit", "ssl", "handshake", "timeout", "connection", "urlnotok"
            ]):
                print(f"⚠️  Problema de conexão detectado (tentativa {attempt + 1}/{manager.max_retries})")
                print(f"🔍 Erro: {e}")
                
                if manager.rotate_connection():
                    print("⏳ Aguardando estabilização da conexão...")
                    time.sleep(10)
                    continue
                else:
                    print("❌ Não foi possível rotacionar conexão")
            else:
                # Erro não relacionado a conexão, propagar
                raise e
    
    raise Exception("❌ Todas as tentativas de conexão falharam") 