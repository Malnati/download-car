#!/bin/bash
# dev/cli.sh

set -e

# \U1F9E0 Uso:
# ./cli.sh --state DF --polygon APPS --folder data/DF --tries 25 --debug True

# \U1F9EA Verifica pyenv
if ! command -v pyenv &> /dev/null; then
  echo -e "\u274c pyenv não encontrado. Instale com:\n  brew install pyenv  # macOS\n  sudo apt install pyenv -y  # Ubuntu/Debian"
  exit 2
fi

# 🔍 Detecta o sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
  OS="macos"
  PACKAGE_MANAGER="brew"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  OS="linux"
  PACKAGE_MANAGER="apt"
else
  echo -e "\u274c Sistema operacional não suportado: $OSTYPE"
  exit 2
fi

# 📷 Verifica e instala Tesseract OCR
if ! command -v tesseract &> /dev/null; then
  echo -e "\u23f3 Tesseract OCR não encontrado. Instalando..."
  
  if [[ "$OS" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
      echo -e "\u274c Homebrew não encontrado. Instale com:\n  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
      exit 2
    fi
    brew install tesseract
  elif [[ "$OS" == "linux" ]]; then
    sudo apt update
    sudo apt install tesseract-ocr -y
  fi
  
  # Verifica se a instalação foi bem-sucedida
  if ! command -v tesseract &> /dev/null; then
    echo -e "\u274c Falha na instalação do Tesseract OCR"
    exit 2
  fi
  
  echo -e "\u2705 Tesseract OCR instalado com sucesso!"
fi

# \U1F40D Define Python version
PYTHON_VERSION="3.10.12"
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
  echo -e "\u23f3 Instalando Python $PYTHON_VERSION via pyenv..."
  pyenv install $PYTHON_VERSION
fi

# \u1F680 Instala dependências via pyenv
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install --upgrade pip
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install --editable .[paddle]

# \u1F6E0 Define variáveis de ambiente para passar os parâmetros para o script Python
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --state)
      STATE="$2"
      shift 2
      ;;
    --polygon)
      POLYGON="$2"
      shift 2
      ;;
    --folder)
      FOLDER="$2"
      shift 2
      ;;
    --debug)
      DEBUG="$2"
      shift 2
      ;;
    --tries)
      TRIES="$2"
      shift 2
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    --max_retries)
      MAX_RETRIES="$2"
      shift 2
      ;;
    *)
      echo "Erro: Parâmetro desconhecido $1"
      echo "Uso: ./cli.sh --state <state> --polygon <polygon> --folder <folder> --tries <tries> --debug <debug> --timeout <timeout> --max_retries <max_retries>"
      exit 1
      ;;
  esac
done

# Verifica se os parâmetros obrigatórios foram passados
if [ -z "$STATE" ] || [ -z "$POLYGON" ] || [ -z "$FOLDER" ]; then
  echo "❌ Erro: Parâmetros obrigatórios faltando."
  echo ""
  echo "📋 Uso: ./cli.sh --state <state> --polygon <polygon> --folder <folder> [--tries <tries>] [--debug <debug>] [--timeout <timeout>] [--max_retries <max_retries>]"
  echo ""
  echo "💡 Exemplo de chamada correta:"
  echo "   ./cli.sh --state DF --polygon APPS --folder data/DF --tries 25 --debug True"
  echo ""
  echo "📝 Parâmetros obrigatórios:"
  echo "   --state: Sigla do estado (ex: DF, SP, RJ)"
  echo "   --polygon: Nome do polígono (ex: APPS, URBANO)"
  echo "   --folder: Pasta de destino para os dados"
  echo ""
  echo "📝 Parâmetros opcionais:"
  echo "   --tries: Número de tentativas (padrão: 25)"
  echo "   --debug: Modo debug True/False (padrão: False)"
  echo "   --timeout: Timeout em segundos (padrão: 30)"
  echo "   --max_retries: Máximo de retry (padrão: 5)"
  exit 1
fi

TRIES="${TRIES:-25}"
TIMEOUT="${TIMEOUT:-30}"
MAX_RETRIES="${MAX_RETRIES:-5}"
DEBUG="${DEBUG:-False}"

# \U1F4D1 Exemplo de parâmetros passados para o script
echo "Executando download para o estado $STATE, polígono $POLYGON, na pasta $FOLDER com tries=$TRIES, debug=$DEBUG, timeout=$TIMEOUT e max_retries=$MAX_RETRIES..."

# \u25B6️ Executa o script cli.py com os parâmetros fornecidos
PYENV_VERSION="$PYTHON_VERSION" pyenv exec python cli.py \
  --state "$STATE" \
  --polygon "$POLYGON" \
  --folder "$FOLDER" \
  --tries "$TRIES" \
  --debug "$DEBUG" \
  --timeout "$TIMEOUT" \
  --max_retries "$MAX_RETRIES"

