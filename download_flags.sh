#!/bin/bash

# Script para baixar bandeiras dos estados brasileiros
# Criado por: Download CAR System

echo "🚩 Baixando bandeiras dos estados brasileiros..."

# Criar diretório se não existir
mkdir -p assets/flags

# Array com as URLs das bandeiras (usando URLs alternativas)
declare -A flags=(
    ["AC"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/AC.svg"
    ["AL"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/AL.svg"
    ["AM"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/AM.svg"
    ["AP"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/AP.svg"
    ["BA"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/BA.svg"
    ["CE"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/CE.svg"
    ["DF"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/DF.svg"
    ["ES"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/ES.svg"
    ["GO"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/GO.svg"
    ["MA"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/MA.svg"
    ["MG"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/MG.svg"
    ["MS"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/MS.svg"
    ["MT"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/MT.svg"
    ["PA"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/PA.svg"
    ["PB"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/PB.svg"
    ["PE"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/PE.svg"
    ["PI"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/PI.svg"
    ["PR"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/PR.svg"
    ["RJ"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/RJ.svg"
    ["RN"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/RN.svg"
    ["RO"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/RO.svg"
    ["RR"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/RR.svg"
    ["RS"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/RS.svg"
    ["SC"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/SC.svg"
    ["SE"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/SE.svg"
    ["SP"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/SP.svg"
    ["TO"]="https://raw.githubusercontent.com/rafaelbotazini/flags-workspace/master/TO.svg"
)

# Função para criar bandeira SVG simples como fallback
create_simple_flag() {
    local state=$1
    local color1="#009c3b"  # Verde
    local color2="#ffdf00"  # Amarelo
    local color3="#002776"  # Azul
    
    # Cores específicas para alguns estados
    case $state in
        "SP") color1="#ffffff"; color2="#000000" ;;  # SP: branco e preto
        "RJ") color1="#ffffff"; color2="#0000ff" ;;  # RJ: branco e azul
        "MG") color1="#ffffff"; color2="#ff0000" ;;  # MG: branco e vermelho
        "RS") color1="#ff0000"; color2="#ffff00" ;;  # RS: vermelho e amarelo
        "SC") color1="#ff0000"; color2="#ffffff" ;;  # SC: vermelho e branco
        "PR") color1="#0000ff"; color2="#ffffff" ;;  # PR: azul e branco
        "GO") color1="#00ff00"; color2="#ffff00" ;;  # GO: verde e amarelo
        "MT") color1="#ff0000"; color2="#00ff00" ;;  # MT: vermelho e verde
        "MS") color1="#0000ff"; color2="#ffffff" ;;  # MS: azul e branco
        "DF") color1="#ffffff"; color2="#0000ff" ;;  # DF: branco e azul
    esac
    
    cat > "assets/flags/${state}.svg" << EOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 16" width="24" height="16">
  <rect width="24" height="16" fill="${color1}"/>
  <rect x="0" y="0" width="24" height="8" fill="${color2}"/>
  <text x="12" y="10" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" font-weight="bold" fill="${color3}">${state}</text>
</svg>
EOF
}

# Baixar ou criar bandeiras
for state in "${!flags[@]}"; do
    echo "📥 Baixando bandeira de $state..."
    
    # Tentar baixar
    if wget -q -O "assets/flags/${state}.svg" "${flags[$state]}" 2>/dev/null; then
        echo "✅ $state baixado com sucesso"
    else
        echo "⚠️  Falha ao baixar $state, criando bandeira simples..."
        create_simple_flag "$state"
        echo "✅ $state criado como fallback"
    fi
done

echo "🎉 Todas as bandeiras foram processadas!"
echo "📁 Bandeiras salvas em: assets/flags/"
echo "📊 Total de bandeiras: $(ls assets/flags/*.svg | wc -l)" 