#!/bin/bash

# Script de teste para as novas funcionalidades
# Testa os novos endpoints e funcionalidades implementadas

set -e

echo "🧪 Testando novas funcionalidades..."

# Configurações
API_URL="http://localhost:8000"
TEST_CAR="SP12345678901234567890"

echo "📋 Testando endpoint /polygons..."
curl -s "${API_URL}/polygons" | jq '.polygons[] | select(.valor == "AREA_PROPERTY")' || echo "❌ Falha no teste de polígonos"

echo "📋 Testando endpoint /states..."
curl -s "${API_URL}/states" | jq '.states | length' || echo "❌ Falha no teste de estados"

echo "📋 Testando endpoint /state (busca por CAR)..."
curl -s "${API_URL}/state?car=${TEST_CAR}" | jq '.' || echo "❌ Falha no teste de busca por CAR"

echo "📋 Testando endpoint /property (download de propriedade)..."
curl -s "${API_URL}/property?car=${TEST_CAR}" -o /dev/null || echo "❌ Falha no teste de download de propriedade"

echo "📋 Testando endpoint /download_state com polígono padrão..."
curl -s -X POST "${API_URL}/download_state" \
  -F "state=DF" \
  -F "polygon=AREA_PROPERTY" \
  -F "tries=1" \
  -F "debug=false" \
  -o /dev/null || echo "❌ Falha no teste de download_state"

echo "✅ Testes concluídos!" 