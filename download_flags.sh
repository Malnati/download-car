#!/bin/bash

# Script para baixar bandeiras oficiais dos estados brasileiros
# Criado por: Download CAR System

echo "🚩 Baixando bandeiras oficiais dos estados brasileiros..."

# Criar diretório se não existir
mkdir -p assets/flags

# Array com as URLs das bandeiras oficiais dos estados brasileiros
declare -A flags=(
    ["AC"]="https://upload.wikimedia.org/wikipedia/commons/0/0c/Flag_of_Acre.svg"
    ["AL"]="https://upload.wikimedia.org/wikipedia/commons/4/4c/Flag_of_Alagoas.svg"
    ["AM"]="https://upload.wikimedia.org/wikipedia/commons/6/6b/Flag_of_Amazonas.svg"
    ["AP"]="https://upload.wikimedia.org/wikipedia/commons/0/0c/Flag_of_Amap%C3%A1.svg"
    ["BA"]="https://upload.wikimedia.org/wikipedia/commons/7/7c/Flag_of_Bahia.svg"
    ["CE"]="https://upload.wikimedia.org/wikipedia/commons/2/2e/Flag_of_Cear%C3%A1.svg"
    ["DF"]="https://upload.wikimedia.org/wikipedia/commons/6/6f/Flag_of_the_Federal_District.svg"
    ["ES"]="https://upload.wikimedia.org/wikipedia/commons/4/4e/Flag_of_Esp%C3%ADrito_Santo.svg"
    ["GO"]="https://upload.wikimedia.org/wikipedia/commons/b/be/Flag_of_Goi%C3%A1s.svg"
    ["MA"]="https://upload.wikimedia.org/wikipedia/commons/4/45/Flag_of_Maranh%C3%A3o.svg"
    ["MG"]="https://upload.wikimedia.org/wikipedia/commons/f/f4/Flag_of_Minas_Gerais.svg"
    ["MS"]="https://upload.wikimedia.org/wikipedia/commons/6/64/Flag_of_Mato_Grosso_do_Sul.svg"
    ["MT"]="https://upload.wikimedia.org/wikipedia/commons/0/0f/Flag_of_Mato_Grosso.svg"
    ["PA"]="https://upload.wikimedia.org/wikipedia/commons/0/02/Flag_of_Par%C3%A1.svg"
    ["PB"]="https://upload.wikimedia.org/wikipedia/commons/b/bb/Flag_of_Para%C3%ADba.svg"
    ["PE"]="https://upload.wikimedia.org/wikipedia/commons/5/59/Flag_of_Pernambuco.svg"
    ["PI"]="https://upload.wikimedia.org/wikipedia/commons/3/33/Flag_of_Piau%C3%AD.svg"
    ["PR"]="https://upload.wikimedia.org/wikipedia/commons/9/93/Flag_of_Paran%C3%A1.svg"
    ["RJ"]="https://upload.wikimedia.org/wikipedia/commons/7/7d/Flag_of_Rio_de_Janeiro.svg"
    ["RN"]="https://upload.wikimedia.org/wikipedia/commons/3/3e/Flag_of_Rio_Grande_do_Norte.svg"
    ["RO"]="https://upload.wikimedia.org/wikipedia/commons/f/fa/Flag_of_Rond%C3%B4nia.svg"
    ["RR"]="https://upload.wikimedia.org/wikipedia/commons/9/98/Flag_of_Roraima.svg"
    ["RS"]="https://upload.wikimedia.org/wikipedia/commons/6/63/Flag_of_Rio_Grande_do_Sul.svg"
    ["SC"]="https://upload.wikimedia.org/wikipedia/commons/1/1a/Flag_of_Santa_Catarina.svg"
    ["SE"]="https://upload.wikimedia.org/wikipedia/commons/b/bb/Flag_of_Sergipe.svg"
    ["SP"]="https://upload.wikimedia.org/wikipedia/commons/2/2b/Flag_of_S%C3%A3o_Paulo.svg"
    ["TO"]="https://upload.wikimedia.org/wikipedia/commons/f/ff/Flag_of_Tocantins.svg"
)

# URLs alternativas caso a primeira falhe
declare -A flags_alt=(
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

# Função para criar bandeira SVG simples como fallback (apenas se tudo falhar)
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

# Baixar bandeiras oficiais
for state in "${!flags[@]}"; do
    echo "📥 Baixando bandeira oficial de $state..."
    
    # Tentar URL principal (Wikimedia)
    if wget -q -O "assets/flags/${state}.svg" "${flags[$state]}" 2>/dev/null; then
        echo "✅ $state baixado com sucesso (Wikimedia)"
    else
        echo "⚠️  Falha na URL principal, tentando alternativa..."
        
        # Tentar URL alternativa
        if wget -q -O "assets/flags/${state}.svg" "${flags_alt[$state]}" 2>/dev/null; then
            echo "✅ $state baixado com sucesso (GitHub)"
        else
            echo "❌ Falha em todas as URLs, criando bandeira simples..."
            create_simple_flag "$state"
            echo "✅ $state criado como fallback"
        fi
    fi
done

echo "🎉 Todas as bandeiras foram processadas!"
echo "📁 Bandeiras salvas em: assets/flags/"
echo "📊 Total de bandeiras: $(ls assets/flags/*.svg | wc -l)"

# Verificar se as bandeiras foram baixadas corretamente
echo ""
echo "🔍 Verificando bandeiras baixadas..."
for state in "${!flags[@]}"; do
    if [ -f "assets/flags/${state}.svg" ]; then
        size=$(stat -c%s "assets/flags/${state}.svg" 2>/dev/null || echo "0")
        if [ "$size" -gt 100 ]; then
            echo "✅ $state: $(($size)) bytes"
        else
            echo "⚠️  $state: Arquivo muito pequeno ($(($size)) bytes)"
        fi
    else
        echo "❌ $state: Arquivo não encontrado"
    fi
done 