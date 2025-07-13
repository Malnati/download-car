#!/bin/bash

# Script para iniciar Tor em background
echo "�� Iniciando Tor..."
sudo -u debian-tor tor --runasdaemon 1

# Aguardar Tor inicializar
echo "⏳ Aguardando Tor inicializar..."
sleep 10

# Verificar se Tor está funcionando
if curl --socks5 127.0.0.1:9050 --socks5-hostname 127.0.0.1:9050 -s https://check.torproject.org/ | grep -q "Congratulations"; then
    echo "✅ Tor está funcionando corretamente!"
else
    echo "⚠️  Tor pode não estar funcionando corretamente"
fi

# Executar o comando original
exec "$@" 