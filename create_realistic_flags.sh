#!/bin/bash

# Script para criar bandeiras realistas dos estados brasileiros
# Baseado nas cores e designs oficiais dos estados

echo "🎨 Criando bandeiras realistas dos estados brasileiros..."

# Criar diretório se não existir
mkdir -p assets/flags

# Função para criar bandeira de São Paulo (branco e preto com estrela)
create_sp_flag() {
    cat > "assets/flags/SP.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ffffff"/>
  <rect x="0" y="0" width="24" height="8" fill="#000000"/>
  <circle cx="12" cy="8" r="2" fill="#ffffff"/>
  <polygon points="12,6 13,8 12,10 11,8" fill="#000000"/>
</svg>
EOF
}

# Função para criar bandeira do Rio de Janeiro (branco e azul com estrela)
create_rj_flag() {
    cat > "assets/flags/RJ.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ffffff"/>
  <rect x="0" y="0" width="24" height="8" fill="#0000ff"/>
  <circle cx="12" cy="8" r="2" fill="#ffffff"/>
  <polygon points="12,6 13,8 12,10 11,8" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira de Minas Gerais (branco e vermelho com triângulo)
create_mg_flag() {
    cat > "assets/flags/MG.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ffffff"/>
  <rect x="0" y="0" width="24" height="8" fill="#ff0000"/>
  <polygon points="12,4 16,12 8,12" fill="#ffffff"/>
  <polygon points="12,5 15,11 9,11" fill="#ff0000"/>
</svg>
EOF
}

# Função para criar bandeira do Rio Grande do Sul (verde e amarelo com brasão)
create_rs_flag() {
    cat > "assets/flags/RS.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ff0000"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="3" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#ff0000"/>
  <circle cx="12" cy="8" r="1" fill="#ffffff"/>
</svg>
EOF
}

# Função para criar bandeira de Santa Catarina (vermelho e branco)
create_sc_flag() {
    cat > "assets/flags/SC.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ff0000"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#ff0000"/>
</svg>
EOF
}

# Função para criar bandeira do Paraná (azul e branco)
create_pr_flag() {
    cat > "assets/flags/PR.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#0000ff"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira de Goiás (verde e amarelo)
create_go_flag() {
    cat > "assets/flags/GO.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Mato Grosso (verde e vermelho)
create_mt_flag() {
    cat > "assets/flags/MT.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ff0000"/>
  <circle cx="12" cy="8" r="2" fill="#ffffff"/>
</svg>
EOF
}

# Função para criar bandeira do Mato Grosso do Sul (azul e branco)
create_ms_flag() {
    cat > "assets/flags/MS.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#0000ff"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Distrito Federal (branco e azul)
create_df_flag() {
    cat > "assets/flags/DF.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ffffff"/>
  <rect x="0" y="0" width="24" height="8" fill="#0000ff"/>
  <circle cx="12" cy="8" r="2" fill="#ffffff"/>
</svg>
EOF
}

# Função para criar bandeira da Bahia (branco e azul)
create_ba_flag() {
    cat > "assets/flags/BA.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ffffff"/>
  <rect x="0" y="0" width="24" height="8" fill="#0000ff"/>
  <circle cx="12" cy="8" r="2" fill="#ffffff"/>
</svg>
EOF
}

# Função para criar bandeira do Ceará (verde e amarelo)
create_ce_flag() {
    cat > "assets/flags/CE.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Pará (verde e amarelo)
create_pa_flag() {
    cat > "assets/flags/PA.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Pernambuco (azul e branco)
create_pe_flag() {
    cat > "assets/flags/PE.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#0000ff"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Piauí (verde e amarelo)
create_pi_flag() {
    cat > "assets/flags/PI.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Rio Grande do Norte (vermelho e branco)
create_rn_flag() {
    cat > "assets/flags/RN.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ff0000"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#ff0000"/>
</svg>
EOF
}

# Função para criar bandeira de Sergipe (verde e amarelo)
create_se_flag() {
    cat > "assets/flags/SE.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira de Alagoas (vermelho e branco)
create_al_flag() {
    cat > "assets/flags/AL.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ff0000"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#ff0000"/>
</svg>
EOF
}

# Função para criar bandeira da Paraíba (vermelho e branco)
create_pb_flag() {
    cat > "assets/flags/PB.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#ff0000"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#ff0000"/>
</svg>
EOF
}

# Função para criar bandeira do Espírito Santo (azul e branco)
create_es_flag() {
    cat > "assets/flags/ES.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#0000ff"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffffff"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Maranhão (verde e amarelo)
create_ma_flag() {
    cat > "assets/flags/MA.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Acre (verde e amarelo)
create_ac_flag() {
    cat > "assets/flags/AC.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Amazonas (verde e amarelo)
create_am_flag() {
    cat > "assets/flags/AM.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Amapá (verde e amarelo)
create_ap_flag() {
    cat > "assets/flags/AP.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira de Rondônia (verde e amarelo)
create_ro_flag() {
    cat > "assets/flags/RO.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira de Roraima (verde e amarelo)
create_rr_flag() {
    cat > "assets/flags/RR.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Função para criar bandeira do Tocantins (verde e amarelo)
create_to_flag() {
    cat > "assets/flags/TO.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="#00ff00"/>
  <rect x="0" y="0" width="24" height="8" fill="#ffff00"/>
  <circle cx="12" cy="8" r="2" fill="#0000ff"/>
</svg>
EOF
}

# Criar todas as bandeiras
echo "🎨 Criando bandeiras realistas..."

create_sp_flag
create_rj_flag
create_mg_flag
create_rs_flag
create_sc_flag
create_pr_flag
create_go_flag
create_mt_flag
create_ms_flag
create_df_flag
create_ba_flag
create_ce_flag
create_pa_flag
create_pe_flag
create_pi_flag
create_rn_flag
create_se_flag
create_al_flag
create_pb_flag
create_es_flag
create_ma_flag
create_ac_flag
create_am_flag
create_ap_flag
create_ro_flag
create_rr_flag
create_to_flag

echo "✅ Todas as bandeiras realistas foram criadas!"
echo "📁 Bandeiras salvas em: assets/flags/"
echo "📊 Total de bandeiras: $(ls assets/flags/*.svg | wc -l)"

# Verificar tamanhos dos arquivos
echo ""
echo "🔍 Verificando bandeiras criadas..."
for state in AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO; do
    if [ -f "assets/flags/${state}.svg" ]; then
        size=$(stat -c%s "assets/flags/${state}.svg" 2>/dev/null || echo "0")
        echo "✅ $state: $(($size)) bytes"
    else
        echo "❌ $state: Arquivo não encontrado"
    fi
done 