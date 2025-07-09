#!/usr/bin/env bash
# entrypoint.download.sh

set -e

PYTHON_VERSION="3.11.8"

if ! command -v pyenv &> /dev/null; then
  echo "pyenv não encontrado"
  exit 1
fi

pyenv install -s "$PYTHON_VERSION"

STATE=${STATE:-DF}
FOLDER=${FOLDER:-data/$STATE}
POLYGON=${POLYGON:-APPS}
TRIES=${TRIES:-25}
DEBUG=${DEBUG:-False}
TIMEOUT=${TIMEOUT:-30}
MAX_RETRIES=${MAX_RETRIES:-5}
mkdir -p "$FOLDER"

PYENV_VERSION="$PYTHON_VERSION" pyenv exec python download_state.py \
  --state "$STATE" \
  --polygon "$POLYGON" \
  --folder "$FOLDER" \
  --tries "$TRIES" \
  --debug "$DEBUG" \
  --timeout "$TIMEOUT" \
  --max_retries "$MAX_RETRIES"



