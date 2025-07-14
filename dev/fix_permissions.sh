#!/bin/bash

# Script para corrigir permissões do diretório data/ e arquivos
# Uso: ./dev/fix_permissions.sh

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [opções]"
    echo ""
    echo "Opções:"
    echo "  --help, -h             Mostra esta ajuda"
    echo "  --force, -f            Força correção mesmo se não houver problemas"
    echo "  --recursive, -r        Corrige permissões recursivamente em subdiretórios"
    echo ""
    echo "Este script corrige permissões do diretório data/ e arquivos .zip"
    echo "para permitir downloads do SICAR."
}

# Variáveis
FORCE=false
RECURSIVE=false

# Processar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --force|-f)
            FORCE=true
            shift
            ;;
        --recursive|-r)
            RECURSIVE=true
            shift
            ;;
        *)
            log_error "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Verificar se estamos no diretório correto
if [ ! -f "Makefile" ]; then
    log_error "Makefile não encontrado! Execute este script no diretório raiz do projeto."
    exit 1
fi

# Função principal para corrigir permissões
fix_permissions() {
    log "Iniciando verificação e correção de permissões..."
    
    # 1. Verificar/criar diretório data/
    if [ ! -d "data" ]; then
        log "Criando diretório data/..."
        if mkdir -p data; then
            log_success "Diretório data/ criado com sucesso!"
        else
            log_error "Falha ao criar diretório data/!"
            return 1
        fi
    else
        log "Diretório data/ já existe."
    fi
    
    # 2. Verificar permissões do diretório data/
    local dir_permissions_ok=true
    
    if [ ! -r "data" ]; then
        log_warning "Diretório data/ não tem permissão de leitura."
        dir_permissions_ok=false
    fi
    
    if [ ! -w "data" ]; then
        log_warning "Diretório data/ não tem permissão de escrita."
        dir_permissions_ok=false
    fi
    
    if [ ! -x "data" ]; then
        log_warning "Diretório data/ não tem permissão de execução."
        dir_permissions_ok=false
    fi
    
    # 3. Corrigir permissões do diretório se necessário
    if [ "$dir_permissions_ok" = false ] || [ "$FORCE" = true ]; then
        log "Corrigindo permissões do diretório data/..."
        
        if chmod 755 data 2>/dev/null; then
            log_success "Permissões do diretório data/ corrigidas (755)!"
        else
            log_error "Falha ao corrigir permissões do diretório data/!"
            log_error "Tente executar: sudo chmod 755 data"
            return 1
        fi
    else
        log_success "Diretório data/ já tem permissões corretas."
    fi
    
    # 4. Verificar e corrigir permissões de arquivos .zip
    local zip_files_count=0
    local zip_files_fixed=0
    
    if [ -d "data" ]; then
        # Contar arquivos .zip
        zip_files_count=$(find data -name "*.zip" 2>/dev/null | wc -l)
        
        if [ "$zip_files_count" -gt 0 ]; then
            log "Encontrados $zip_files_count arquivo(s) .zip em data/."
            
            # Verificar arquivos sem permissão de escrita
            local unwritable_files=$(find data -name "*.zip" -not -writable 2>/dev/null | wc -l)
            
            if [ "$unwritable_files" -gt 0 ] || [ "$FORCE" = true ]; then
                log "Corrigindo permissões dos arquivos .zip..."
                
                # Corrigir permissões dos arquivos .zip
                if find data -name "*.zip" -exec chmod 644 {} \; 2>/dev/null; then
                    zip_files_fixed=$zip_files_count
                    log_success "Permissões de $zip_files_fixed arquivo(s) .zip corrigidas (644)!"
                else
                    log_warning "Alguns arquivos .zip podem precisar de correção manual."
                fi
            else
                log_success "Todos os arquivos .zip já têm permissões corretas."
            fi
        else
            log "Nenhum arquivo .zip encontrado em data/."
        fi
        
        # 5. Se recursivo, verificar subdiretórios
        if [ "$RECURSIVE" = true ]; then
            log "Verificando permissões recursivamente em subdiretórios..."
            
            local subdirs=$(find data -type d 2>/dev/null | wc -l)
            if [ "$subdirs" -gt 1 ]; then  # Mais de 1 porque inclui o próprio data/
                log "Corrigindo permissões de $((subdirs - 1)) subdiretório(s)..."
                
                if find data -type d -exec chmod 755 {} \; 2>/dev/null; then
                    log_success "Permissões dos subdiretórios corrigidas!"
                else
                    log_warning "Alguns subdiretórios podem precisar de correção manual."
                fi
            fi
        fi
    fi
    
    # 6. Resumo final
    log "=========================================="
    log "RESUMO DA CORREÇÃO DE PERMISSÕES"
    log "=========================================="
    log "Diretório data/: OK"
    log "Arquivos .zip verificados: $zip_files_count"
    log "Arquivos .zip corrigidos: $zip_files_fixed"
    
    if [ "$RECURSIVE" = true ]; then
        log "Subdiretórios: Verificados e corrigidos"
    fi
    
    log_success "Verificação de permissões concluída!"
}

# Executar função principal
fix_permissions 