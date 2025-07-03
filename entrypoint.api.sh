#!/usr/bin/env bash
# entrypoint.api.sh
set -e

PYTHON_VERSION="3.11.8"

if ! command -v pyenv &> /dev/null; then
  echo "pyenv não encontrado"
  exit 1
fi

pyenv install -s "$PYTHON_VERSION"
PYENV_VERSION="$PYTHON_VERSION" pyenv exec pip install --upgrade pip
PYENV_VERSION="$PYTHON_VERSION" pyenv exec \
  pip install fastapi uvicorn httpx Pillow tqdm python-multipart

exec PYENV_VERSION="$PYTHON_VERSION" pyenv exec \
  uvicorn app:app --host 0.0.0.0 --port 8000

