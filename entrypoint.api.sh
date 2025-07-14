#!/usr/bin/env bash
set -e

# Iniciar a API
echo "🚀 Iniciando API..."
exec uvicorn api:app --host 0.0.0.0 --port 8000

