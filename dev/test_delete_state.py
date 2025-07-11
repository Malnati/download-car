#!/usr/bin/env python3
"""
Script de teste para o endpoint DELETE /delete_state

Este script testa o funcionamento do novo endpoint que exclui arquivos de um estado específico.
"""

import os
import tempfile
import zipfile
import requests
import json
from pathlib import Path

def create_test_files(state, folder="temp"):
    """Cria arquivos de teste para simular downloads de um estado"""
    os.makedirs(folder, exist_ok=True)
    
    # Criar arquivos de estado
    state_files = [
        f"{state}_AREA_IMOVEL.zip",
        f"{state}_APPS.zip",
        f"{state}_NATIVE_VEGETATION.zip"
    ]
    
    created_files = []
    for filename in state_files:
        file_path = os.path.join(folder, filename)
        with zipfile.ZipFile(file_path, 'w') as zipf:
            zipf.writestr('test.txt', f'Test file for {state}')
        created_files.append(file_path)
        print(f"✅ Criado: {file_path}")
    
    # Criar arquivos de propriedade
    property_folder = "PROPERTY"
    os.makedirs(property_folder, exist_ok=True)
    
    property_files = [
        f"property_{state}-123456-ABCDEF.zip",
        f"property_{state}-789012-GHIJKL.zip"
    ]
    
    for filename in property_files:
        file_path = os.path.join(property_folder, filename)
        with zipfile.ZipFile(file_path, 'w') as zipf:
            zipf.writestr('property.txt', f'Property file for {state}')
        created_files.append(file_path)
        print(f"✅ Criado: {file_path}")
    
    return created_files

def test_delete_state_endpoint(api_url="http://localhost:8000", state="SP", folder="temp", include_properties=True):
    """Testa o endpoint DELETE /delete_state"""
    
    print(f"\n🧪 Testando exclusão do estado {state}")
    print(f"📁 Pasta: {folder}")
    print(f"🏠 Incluir propriedades: {include_properties}")
    
    # Criar arquivos de teste
    print(f"\n📝 Criando arquivos de teste para {state}...")
    test_files = create_test_files(state, folder)
    
    # Verificar se os arquivos foram criados
    print(f"\n🔍 Verificando arquivos criados...")
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"✅ Arquivo existe: {file_path}")
        else:
            print(f"❌ Arquivo não encontrado: {file_path}")
    
    # Fazer a requisição para o endpoint
    print(f"\n🚀 Fazendo requisição DELETE para /delete_state...")
    
    try:
        response = requests.delete(
            f"{api_url}/delete_state",
            data={
                "state": state,
                "folder": folder,
                "include_properties": str(include_properties).lower()
            }
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso!")
            print(f"📋 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Verificar se os arquivos foram realmente excluídos
            print(f"\n🔍 Verificando se os arquivos foram excluídos...")
            for file_path in test_files:
                if os.path.exists(file_path):
                    print(f"❌ Arquivo ainda existe: {file_path}")
                else:
                    print(f"✅ Arquivo excluído: {file_path}")
            
            return True
        else:
            print(f"❌ Erro na requisição:")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE DO ENDPOINT DELETE /delete_state")
    print("=" * 50)
    
    # Teste 1: Excluir apenas arquivos de estado
    print("\n📋 TESTE 1: Excluir apenas arquivos de estado")
    print("-" * 40)
    test_delete_state_endpoint(state="SP", include_properties=False)
    
    # Teste 2: Excluir arquivos de estado e propriedades
    print("\n📋 TESTE 2: Excluir arquivos de estado e propriedades")
    print("-" * 40)
    test_delete_state_endpoint(state="RJ", include_properties=True)
    
    # Teste 3: Estado inexistente
    print("\n📋 TESTE 3: Estado inexistente")
    print("-" * 40)
    test_delete_state_endpoint(state="XX", include_properties=True)
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main() 