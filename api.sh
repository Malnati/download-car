#!/usr/bin/env bash
# api.sh

set -e

PYTHON_VERSION="3.11.8"

if ! command -v pyenv &> /dev/null; then
  echo "❌ pyenv não encontrado. Instale antes de continuar."
  exit 1
fi

pyenv install -s "$PYTHON_VERSION"
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install --upgrade pip
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install fastapi uvicorn httpx Pillow tqdm

echo "🚀 Servidor FastAPI pronto em http://localhost:8000"
PYENV_VERSION="$PYTHON_VERSION" pyenv exec uvicorn app:app --reload --port 8000

