#!/bin/bash

# Script para download apenas dos estados que falharam anteriormente
# Utiliza os novos timeouts específicos definidos em .config.env

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

# Carregar variáveis do .config.env
if [ -f ".config.env" ]; then
    log "Carregando configurações do .config.env..."
    # Carregar apenas variáveis simples (sem espaços ou caracteres especiais)
    while IFS='=' read -r key value; do
        # Ignorar linhas vazias, comentários e linhas com espaços
        if [[ -n "$key" && ! "$key" =~ ^[[:space:]]*# && ! "$key" =~ [[:space:]] ]]; then
            # Remover espaços em branco
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            # Exportar apenas se a chave for válida
            if [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
                export "$key=$value"
            fi
        fi
    done < .config.env
else
    log_error "Arquivo .config.env não encontrado!"
    exit 1
fi

# Lista dos estados que falharam na execução anterior
FAILED_STATES=(
    "AC" "AM" "AP" "CE" "ES" "MA" "MS" "PB"
)

# Função para obter timeout específico do estado
get_state_timeout() {
    local state=$1
    local timeout_var="STATE_TIMEOUT_${state}"
    local timeout_value=${!timeout_var}
    
    if [ -n "$timeout_value" ]; then
        # Converte de milissegundos para segundos
        echo $((timeout_value / 1000))
    else
        # Timeout padrão se não especificado
        echo 180
    fi
}

# Função para verificar se o arquivo já existe
file_exists() {
    local state=$1
    local file="data/${state}_AREA_IMOVEL.zip"
    
    if [ -f "$file" ]; then
        local size=$(stat -c%s "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt 1000 ]; then  # Arquivo maior que 1KB
            return 0  # Arquivo existe e tem tamanho válido
        fi
    fi
    return 1  # Arquivo não existe ou é muito pequeno
}

# Função para executar download de um estado
download_state() {
    local state=$1
    local timeout=$(get_state_timeout $state)
    
    log "Iniciando download do estado: $state (timeout: ${timeout}s)"
    
    # Verificar se o arquivo já existe
    if file_exists "$state"; then
        log_warning "Arquivo para estado $state já existe. Pulando..."
        return 0
    fi
    
    # Executar o comando make com timeout específico
    if timeout ${timeout} make download state=$state polygon=AREA_PROPERTY folder=data debug=true timeout=180 max_retries=1; then
        log_success "Download do estado $state concluído com sucesso!"
        return 0
    else
        log_error "Download do estado $state falhou ou atingiu timeout!"
        return 1
    fi
}

# Função principal
main() {
    log "Iniciando download dos estados que falharam anteriormente..."
    log "Estados com novos timeouts: ${FAILED_STATES[*]}"
    log "Total de estados: ${#FAILED_STATES[@]}"
    
    local success_count=0
    local error_count=0
    local skipped_count=0
    local start_time=$(date +%s)
    
    # Array para armazenar estados com erro
    local failed_states=()
    local skipped_states=()
    
    for state in "${FAILED_STATES[@]}"; do
        log "=========================================="
        log "Processando estado: $state"
        log "=========================================="
        
        # Verificar se o arquivo já existe
        if file_exists "$state"; then
            log_warning "Arquivo para estado $state já existe. Pulando..."
            ((skipped_count++))
            skipped_states+=("$state")
            continue
        fi
        
        if download_state "$state"; then
            ((success_count++))
        else
            ((error_count++))
            failed_states+=("$state")
        fi
        
        # Pequena pausa entre downloads para não sobrecarregar
        sleep 2
    done
    
    # Resumo final
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    log "=========================================="
    log "RESUMO FINAL - ESTADOS QUE FALHARAM"
    log "=========================================="
    log "Tempo total de execução: ${minutes}m ${seconds}s"
    log "Estados processados com sucesso: $success_count"
    log "Estados pulados (já existem): $skipped_count"
    log "Estados com erro: $error_count"
    
    if [ ${#skipped_states[@]} -gt 0 ]; then
        log_warning "Estados pulados: ${skipped_states[*]}"
    fi
    
    if [ ${#failed_states[@]} -gt 0 ]; then
        log_error "Estados que ainda falharam: ${failed_states[*]}"
    fi
    
    if [ $error_count -eq 0 ]; then
        log_success "Todos os estados foram processados com sucesso!"
        exit 0
    else
        log_warning "Alguns estados ainda falharam. Considere aumentar ainda mais os timeouts."
        exit 1
    fi
}

# Verificar se estamos no diretório correto
if [ ! -f "Makefile" ]; then
    log_error "Makefile não encontrado! Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar e corrigir permissões do diretório data/
check_and_fix_permissions() {
    log "Verificando permissões do diretório data/..."
    
    # Criar diretório data/ se não existir
    if [ ! -d "data" ]; then
        log "Criando diretório data/..."
        mkdir -p data
    fi
    
    # Verificar se o diretório data/ tem permissão de escrita
    if [ ! -w "data" ]; then
        log_warning "Diretório data/ não tem permissão de escrita. Tentando corrigir..."
        
        # Tentar corrigir permissões
        if chmod 755 data 2>/dev/null; then
            log_success "Permissões do diretório data/ corrigidas com sucesso!"
        else
            log_error "Não foi possível corrigir permissões do diretório data/."
            log_error "Execute: sudo chmod 755 data"
            exit 1
        fi
    else
        log_success "Diretório data/ tem permissões corretas."
    fi
}

# Executar verificação de permissões
check_and_fix_permissions

# Executar função principal
main "$@" 