#!/usr/bin/env bash
# dev/api.sh
# api.sh

set -e

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

# \U1F9EA Verifica pyenv
if ! command -v pyenv &> /dev/null; then
  echo -e "\u274c pyenv não encontrado. Instale com:\n  brew install pyenv  # macOS\n  sudo apt install pyenv -y  # Ubuntu/Debian"
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

PYTHON_VERSION="3.11.8"

# \U1F40D Define Python version
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION$"; then
  echo -e "\u23f3 Instalando Python $PYTHON_VERSION via pyenv..."
  pyenv install $PYTHON_VERSION
fi

# \u1F680 Instala dependências via pyenv
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install --upgrade pip
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install fastapi uvicorn httpx Pillow tqdm python-multipart

echo "🚀 Servidor FastAPI pronto em http://localhost:8000"
PYENV_VERSION="$PYTHON_VERSION" pyenv exec uvicorn api:app --reload --port 8000

