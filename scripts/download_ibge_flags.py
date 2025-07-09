#!/usr/bin/env python3
"""
Script para baixar bandeiras oficiais dos estados brasileiros do IBGE
"""

import os
import requests

URL = "https://atlasescolar.ibge.gov.br/bandeiras-das-ufs.html"
DEST_DIR = "assets/flags"

# Lista das siglas dos estados
siglas = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PR", "PB", "PA", "PE", "PI", "RN", "RS", "RJ", "RO", "RR", "SC", "SE", "SP", "TO"
]

# Padrão de URL das imagens
def get_img_url(sigla):
    return f"https://atlasescolar.ibge.gov.br/images/bandeiras/ufs/{sigla.lower()}.png"

os.makedirs(DEST_DIR, exist_ok=True)
print("Baixando bandeiras oficiais do IBGE...")

for sigla in siglas:
    url = get_img_url(sigla)
    dest = os.path.join(DEST_DIR, f"{sigla}.png")
    print(f"📥 {sigla}: {url}")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"✅ {sigla} salva em {dest} ({os.path.getsize(dest)} bytes)")
    except Exception as e:
        print(f"❌ Erro ao baixar {sigla}: {e}")

print("\n🎉 Todas as bandeiras foram processadas!")
print(f"📁 Bandeiras salvas em: {DEST_DIR}") 