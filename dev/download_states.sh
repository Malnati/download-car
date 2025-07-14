#!/bin/bash

# Script para download de estados específicos ou todos os estados
# Uso: ./dev/download_states.sh [estado1 estado2 ...]
# Se nenhum estado for especificado, baixa todos os estados

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
    echo "Uso: $0 [estado1 estado2 ...]"
    echo ""
    echo "Argumentos:"
    echo "  estado1, estado2, ...  Estados específicos para download (ex: SP MG RJ)"
    echo "  --help, -h             Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                     # Baixa todos os estados"
    echo "  $0 SP MG RJ            # Baixa apenas SP, MG e RJ"
    echo "  $0 AC AL AM            # Baixa apenas AC, AL e AM"
    echo ""
    echo "Estados disponíveis:"
    echo "  AC, AL, AM, AP, BA, CE, DF, ES, GO, MA, MG, MS, MT,"
    echo "  PA, PB, PE, PI, PR, RJ, RN, RO, RR, RS, SC, SE, SP, TO"
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

# Lista de todos os estados brasileiros válidos
ALL_STATES=(
    "AC" "AL" "AM" "AP" "BA" "CE" "DF" "ES" "GO" "MA"
    "MG" "MS" "MT" "PA" "PB" "PE" "PI" "PR" "RJ" "RN"
    "RO" "RR" "RS" "SC" "SE" "SP" "TO"
)

# Função para validar estado
is_valid_state() {
    local state=$1
    for valid_state in "${ALL_STATES[@]}"; do
        if [ "$state" = "$valid_state" ]; then
            return 0
        fi
    done
    return 1
}

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

# Função para executar download de um estado
download_state() {
    local state=$1
    local timeout=$(get_state_timeout $state)
    
    log "Iniciando download do estado: $state (timeout: ${timeout}s)"
    
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
    local states_to_download=()
    
    # Processar argumentos
    if [ $# -eq 0 ]; then
        # Se nenhum argumento, usar todos os estados
        states_to_download=("${ALL_STATES[@]}")
        log "Nenhum estado especificado. Baixando todos os estados..."
    else
        # Validar estados especificados
        for state in "$@"; do
            if [ "$state" = "--help" ] || [ "$state" = "-h" ]; then
                show_help
                exit 0
            elif is_valid_state "$state"; then
                states_to_download+=("$state")
            else
                log_error "Estado inválido: $state"
                log "Estados válidos: ${ALL_STATES[*]}"
                exit 1
            fi
        done
    fi
    
    log "Estados para download: ${states_to_download[*]}"
    log "Total de estados: ${#states_to_download[@]}"
    
    local success_count=0
    local error_count=0
    local start_time=$(date +%s)
    
    # Array para armazenar estados com erro
    local failed_states=()
    
    for state in "${states_to_download[@]}"; do
        log "=========================================="
        log "Processando estado: $state"
        log "=========================================="
        
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
    log "RESUMO FINAL"
    log "=========================================="
    log "Tempo total de execução: ${minutes}m ${seconds}s"
    log "Estados processados com sucesso: $success_count"
    log "Estados com erro: $error_count"
    
    if [ ${#failed_states[@]} -gt 0 ]; then
        log_warning "Estados que falharam: ${failed_states[*]}"
    fi
    
    if [ $error_count -eq 0 ]; then
        log_success "Todos os estados foram processados com sucesso!"
        exit 0
    else
        log_warning "Alguns estados falharam, mas o processo foi concluído."
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
    
    # Verificar se há arquivos com permissões incorretas
    if [ -d "data" ] && [ "$(find data -name "*.zip" -not -writable 2>/dev/null | wc -l)" -gt 0 ]; then
        log_warning "Encontrados arquivos .zip sem permissão de escrita em data/."
        log "Tentando corrigir permissões dos arquivos..."
        
        if find data -name "*.zip" -exec chmod 644 {} \; 2>/dev/null; then
            log_success "Permissões dos arquivos .zip corrigidas!"
        else
            log_warning "Alguns arquivos podem precisar de correção manual de permissões."
        fi
    fi
}

# Executar verificação de permissões
check_and_fix_permissions

# Executar função principal
main "$@" 