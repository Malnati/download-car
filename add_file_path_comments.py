#!/usr/bin/env python3
# add_file_path_comments.py

import os
import re
import mimetypes
from pathlib import Path
from typing import Set, Dict, List, Tuple

class FilePathCommenter:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.ignored_patterns = self._load_gitignore_patterns()
        
    def _load_gitignore_patterns(self) -> Set[str]:
        """Carrega padrões do .gitignore para excluir arquivos"""
        patterns = set()
        gitignore_path = self.root_dir / ".gitignore"
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.add(line)
        
        # Adicionar padrões padrão para pastas sensíveis
        default_patterns = {
            '.git/', 'node_modules/', 'venv/', '__pycache__/', 
            '.venv/', '.env', '.vscode/', '.cursor/', 'temp/',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe',
            '*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.ico',
            '*.zip', '*.tar', '*.gz', '*.rar', '*.7z',
            '*.pdf', '*.doc', '*.docx', '*.xls', '*.xlsx',
            '*.log', '*.tmp', '*.temp'
        }
        patterns.update(default_patterns)
        
        return patterns
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Verifica se o arquivo deve ser ignorado baseado nos padrões do .gitignore"""
        rel_path = file_path.relative_to(self.root_dir)
        rel_path_str = str(rel_path)
        
        for pattern in self.ignored_patterns:
            if pattern.endswith('/'):
                # Padrão de diretório
                if rel_path_str.startswith(pattern) or f"/{pattern}" in f"/{rel_path_str}":
                    return True
            elif pattern.startswith('*'):
                # Padrão de extensão
                if rel_path_str.endswith(pattern[1:]):
                    return True
            else:
                # Padrão exato
                if rel_path_str == pattern or rel_path_str.endswith(f"/{pattern}"):
                    return True
        
        return False
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """Verifica se o arquivo é binário"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
    
    def _get_comment_syntax(self, file_path: Path) -> Tuple[str, str]:
        """Retorna a sintaxe de comentário apropriada para o tipo de arquivo"""
        extension = file_path.suffix.lower()
        
        comment_syntax = {
            # Python
            '.py': ('#', '#'),
            '.pyx': ('#', '#'),
            '.pyi': ('#', '#'),
            
            # JavaScript/TypeScript
            '.js': ('//', '//'),
            '.jsx': ('//', '//'),
            '.ts': ('//', '//'),
            '.tsx': ('//', '//'),
            
            # Shell/Bash
            '.sh': ('#', '#'),
            '.bash': ('#', '#'),
            '.zsh': ('#', '#'),
            
            # HTML/XML
            '.html': ('<!--', '-->'),
            '.htm': ('<!--', '-->'),
            '.xml': ('<!--', '-->'),
            '.svg': ('<!--', '-->'),
            
            # CSS
            '.css': ('/*', '*/'),
            '.scss': ('/*', '*/'),
            '.sass': ('/*', '*/'),
            '.less': ('/*', '*/'),
            
            # C/C++
            '.c': ('//', '//'),
            '.cpp': ('//', '//'),
            '.cc': ('//', '//'),
            '.cxx': ('//', '//'),
            '.h': ('//', '//'),
            '.hpp': ('//', '//'),
            
            # Java
            '.java': ('//', '//'),
            
            # Go
            '.go': ('//', '//'),
            
            # Rust
            '.rs': ('//', '//'),
            
            # Ruby
            '.rb': ('#', '#'),
            
            # PHP
            '.php': ('//', '//'),
            
            # Perl
            '.pl': ('#', '#'),
            '.pm': ('#', '#'),
            
            # Lua
            '.lua': ('--', '--'),
            
            # SQL
            '.sql': ('--', '--'),
            
            # YAML
            '.yml': ('#', '#'),
            '.yaml': ('#', '#'),
            
            # JSON (não suporta comentários, mas podemos usar // para compatibilidade)
            '.json': ('//', '//'),
            
            # Markdown
            '.md': ('<!--', '-->'),
            '.markdown': ('<!--', '-->'),
            
            # Docker
            'Dockerfile': ('#', '#'),
            'dockerfile': ('#', '#'),
            
            # Makefile
            'Makefile': ('#', '#'),
            'makefile': ('#', '#'),
            
            # Configurações
            '.toml': ('#', '#'),
            '.ini': ('#', '#'),
            '.cfg': ('#', '#'),
            '.conf': ('#', '#'),
            
            # Outros
            '.txt': ('#', '#'),
            '.log': ('#', '#'),
        }
        
        # Verificar por nome de arquivo específico
        filename = file_path.name
        if filename in comment_syntax:
            return comment_syntax[filename]
        
        # Verificar por extensão
        if extension in comment_syntax:
            return comment_syntax[extension]
        
        # Fallback para comentário padrão
        return ('#', '#')
    
    def _has_shebang(self, content: str) -> bool:
        """Verifica se o arquivo tem shebang na primeira linha"""
        lines = content.split('\n')
        if not lines:
            return False
        return lines[0].startswith('#!')
    
    def _has_xml_declaration(self, content: str) -> bool:
        """Verifica se o arquivo tem declaração XML na primeira linha"""
        lines = content.split('\n')
        if not lines:
            return False
        first_line = lines[0].strip()
        return first_line.startswith('<?xml')
    
    def _has_doctype(self, content: str) -> bool:
        """Verifica se o arquivo tem DOCTYPE na primeira linha"""
        lines = content.split('\n')
        if not lines:
            return False
        first_line = lines[0].strip()
        return first_line.startswith('<!DOCTYPE')
    
    def _comment_already_exists(self, content: str, rel_path: str, comment_start: str, comment_end: str) -> bool:
        """Verifica se o comentário com o caminho já existe"""
        lines = content.split('\n')
        
        # Verificar apenas as primeiras linhas para comentários existentes
        for i, line in enumerate(lines[:3]):  # Verificar apenas as 3 primeiras linhas
            line = line.strip()
            if comment_start == '<!--' and comment_end == '-->':
                # Para HTML/XML, procurar por comentário com o caminho
                if f'<!-- {rel_path} -->' in line or f'<!--{rel_path}-->' in line:
                    return True
            elif comment_start == '/*' and comment_end == '*/':
                # Para CSS, procurar por comentário com o caminho
                if f'/* {rel_path} */' in line or f'/*{rel_path}*/' in line:
                    return True
            else:
                # Para comentários de linha única
                if line.startswith(f'{comment_start} {rel_path}') or line == f'{comment_start} {rel_path}':
                    return True
        
        return False
    
    def _insert_comment(self, content: str, rel_path: str, comment_start: str, comment_end: str, 
                       has_special_first_line: bool = False) -> str:
        """Insere o comentário com o caminho relativo no local apropriado"""
        lines = content.split('\n')
        
        if comment_start == '<!--' and comment_end == '-->':
            # Para HTML/XML
            if has_special_first_line:
                # Inserir após a primeira linha (DOCTYPE ou XML declaration)
                lines.insert(1, f'{comment_start} {rel_path} {comment_end}')
            else:
                # Inserir no início
                lines.insert(0, f'{comment_start} {rel_path} {comment_end}')
        elif comment_start == '/*' and comment_end == '*/':
            # Para CSS
            if has_special_first_line:
                # Inserir após a primeira linha
                lines.insert(1, f'{comment_start} {rel_path} {comment_end}')
            else:
                # Inserir no início
                lines.insert(0, f'{comment_start} {rel_path} {comment_end}')
        else:
            # Para comentários de linha única
            comment_line = f'{comment_start} {rel_path}'
            if has_special_first_line:
                # Inserir após a primeira linha (shebang)
                lines.insert(1, comment_line)
            else:
                # Inserir no início
                lines.insert(0, comment_line)
        
        return '\n'.join(lines)
    
    def process_file(self, file_path: Path) -> bool:
        """Processa um arquivo individual, adicionando o comentário se necessário"""
        try:
            # Verificar se deve ser ignorado
            if self._should_ignore_file(file_path):
                return False
            
            # Verificar se é arquivo binário
            if self._is_binary_file(file_path):
                return False
            
            # Obter caminho relativo
            rel_path = file_path.relative_to(self.root_dir)
            rel_path_str = str(rel_path)
            
            # Obter sintaxe de comentário
            comment_start, comment_end = self._get_comment_syntax(file_path)
            
            # Ler conteúdo do arquivo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Verificar se o comentário já existe
            if self._comment_already_exists(content, rel_path_str, comment_start, comment_end):
                return False
            
            # Verificar se tem linha especial na primeira linha
            has_special_first_line = (
                self._has_shebang(content) or 
                self._has_xml_declaration(content) or 
                self._has_doctype(content)
            )
            
            # Inserir comentário
            new_content = self._insert_comment(content, rel_path_str, comment_start, comment_end, has_special_first_line)
            
            # Escrever arquivo de volta
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            return False
    
    def process_all_files(self) -> Dict[str, int]:
        """Processa todos os arquivos do projeto"""
        stats = {
            'processed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                try:
                    if self.process_file(file_path):
                        stats['processed'] += 1
                        print(f"✓ Processado: {file_path.relative_to(self.root_dir)}")
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    stats['errors'] += 1
                    print(f"✗ Erro: {file_path.relative_to(self.root_dir)} - {e}")
        
        return stats

def main():
    """Função principal"""
    print("=== Adicionando comentários com caminho relativo aos arquivos ===")
    print()
    
    commenter = FilePathCommenter()
    stats = commenter.process_all_files()
    
    print()
    print("=== Resumo ===")
    print(f"Arquivos processados: {stats['processed']}")
    print(f"Arquivos ignorados: {stats['skipped']}")
    print(f"Erros: {stats['errors']}")
    print()
    print("Concluído!")

if __name__ == "__main__":
    main() 