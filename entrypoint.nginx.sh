#!/bin/sh
# entrypoint.nginx.sh

# Script para substituir variáveis de ambiente no nginx.conf e gerar configuração do frontend
# Este script é executado antes de iniciar o nginx

echo "Substituindo variáveis de ambiente no nginx.conf..."

# Substituir variáveis de ambiente no arquivo de configuração
envsubst '${CORS_ALLOW_ORIGINS} ${CORS_ALLOW_METHODS} ${CORS_ALLOW_HEADERS}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Configuração do nginx atualizada com as variáveis de ambiente."

# Gerar configuração do frontend se Node.js estiver disponível
if command -v node >/dev/null 2>&1; then
    echo "Gerando configuração do frontend..."
    node /usr/share/nginx/html/generate-config.js
else
    echo "Node.js não disponível, pulando geração da configuração do frontend"
fi

# Iniciar o nginx
exec nginx -g 'daemon off;' 