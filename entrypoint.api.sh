#!/usr/bin/env bash
set -e

# Não utilizar pyenv, todas as dependências já estão instaladas
exec uvicorn api:app --host 0.0.0.0 --port 8000

