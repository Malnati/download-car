#!/usr/bin/env python3
"""
Script para incrementar automaticamente a versão no pyproject.toml
"""

import re
import sys
from pathlib import Path

def bump_version(version_type='patch'):
    """
    Incrementa a versão no pyproject.toml
    
    Args:
        version_type (str): Tipo de incremento ('major', 'minor', 'patch')
    """
    pyproject_path = Path('pyproject.toml')
    
    if not pyproject_path.exists():
        print("❌ pyproject.toml não encontrado!")
        sys.exit(1)
    
    # Lê o conteúdo do arquivo
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    # Encontra a linha da versão
    version_pattern = r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)
    
    if not match:
        print("❌ Não foi possível encontrar a versão no pyproject.toml!")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    # Incrementa a versão conforme o tipo
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch (padrão)
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    old_version = f"{major}.{minor}.{patch-1}" if version_type == 'patch' else match.group(0)
    
    # Substitui a versão no conteúdo
    new_content = re.sub(version_pattern, f'version = "{new_version}"', content)
    
    # Escreve o arquivo atualizado
    with open(pyproject_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Versão incrementada: {match.group(1)}.{match.group(2)}.{match.group(3)} → {new_version}")
    return new_version

if __name__ == "__main__":
    version_type = sys.argv[1] if len(sys.argv) > 1 else 'patch'
    bump_version(version_type) 