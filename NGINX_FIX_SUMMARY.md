# Correção do Problema do Nginx - index.html não encontrado

## Problema Identificado

O problema não era que o `index.html` não estava sendo encontrado, mas sim que a configuração do nginx não estava fazendo proxy corretamente para todos os endpoints da API. O frontend estava configurado para fazer requisições para a API na porta 8787, mas quando acessado através do nginx na porta 80, as requisições para endpoints da API não estavam sendo roteadas corretamente.

## Causa Raiz

1. **Configuração incompleta do proxy**: O nginx estava configurado apenas para fazer proxy de endpoints específicos (`/api/` e alguns endpoints de download), mas não para todos os endpoints da API.

2. **Requisições 404**: Quando o frontend fazia requisições para endpoints como `/states`, `/polygons`, `/state_status/SP`, etc., o nginx não sabia como roteá-los e retornava 404.

## Solução Implementada

### 1. Atualização da Configuração do Nginx

Modificamos o arquivo `nginx.conf.template` para incluir uma regra de proxy mais abrangente:

```nginx
# Proxy para todos os endpoints da API (sem prefixo /api/)
location ~ ^/(states|polygons|state_status|database_status|brasil_config|car_data|get_states|get_polygons|download_state|download_country|download-property|sync_to_database|delete_state|reclassificar_brasil|aplicar_ibge|download_mapbiomas) {
    proxy_pass http://download-car-api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Configurações de timeout para evitar 504
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    proxy_buffering off;
    
    # Headers CORS específicos para API
    add_header Access-Control-Allow-Origin "${CORS_ALLOW_ORIGINS}" always;
    add_header Access-Control-Allow-Methods "${CORS_ALLOW_METHODS}" always;
    add_header Access-Control-Allow-Headers "*" always;
    
    # Tratar requisições OPTIONS (preflight)
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "${CORS_ALLOW_ORIGINS}";
        add_header Access-Control-Allow-Methods "${CORS_ALLOW_METHODS}";
        add_header Access-Control-Allow-Headers "*";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain; charset=utf-8";
        add_header Content-Length 0;
        return 204;
    }
}
```

### 2. Remoção de Configuração Duplicada

Removemos a seção duplicada que estava causando conflito:

```nginx
# Proxy para endpoints de status e download
location ~ ^/(state_status|download_state|download_country|download-property|delete_state) {
    # ... configuração duplicada removida
}
```

### 3. Reinicialização do Container

Reinicializamos o container nginx para aplicar as mudanças:

```bash
DOCKER_CONFIG=/tmp/docker-config-noauth docker compose restart nginx
```

## Testes Realizados

### ✅ Teste do Frontend (index.html)
```bash
curl -I http://localhost/
# Resultado: HTTP/1.1 200 OK
```

### ✅ Teste dos Endpoints da API via Nginx
```bash
curl -v http://localhost/states
# Resultado: HTTP/1.1 200 OK com dados JSON

curl -v http://localhost/polygons  
# Resultado: HTTP/1.1 200 OK com dados JSON

curl -v http://localhost/state_status/SP
# Resultado: HTTP/1.1 200 OK com dados JSON
```

### ✅ Verificação dos Logs
```bash
DOCKER_CONFIG=/tmp/docker-config-noauth docker compose logs nginx --tail=20
# Resultado: Apenas logs de sucesso (200), sem erros 404
```

## Status Final

✅ **PROBLEMA RESOLVIDO**

- O `index.html` está sendo servido corretamente na porta 80
- Todos os endpoints da API estão funcionando através do nginx
- Não há mais erros 404 para requisições da API
- O frontend pode fazer requisições para a API sem problemas
- CORS está configurado corretamente
- Headers de cache e performance estão otimizados

## Arquitetura Final

```
Cliente (Navegador)
    ↓
Nginx (Porta 80)
    ├── / → index.html (Frontend)
    ├── /assets/ → Arquivos estáticos
    ├── /api/* → Proxy para API (Porta 8000)
    └── /(endpoints) → Proxy para API (Porta 8000)
    ↓
API (Porta 8000) → Uvicorn/FastAPI
```

## Próximos Passos

1. **Monitoramento**: Acompanhar os logs do nginx para garantir que não há mais erros
2. **Performance**: Monitorar o desempenho do proxy para downloads longos
3. **Segurança**: Considerar implementar rate limiting se necessário
4. **Documentação**: Atualizar a documentação da API com os endpoints corretos

## Arquivos Modificados

- `nginx.conf.template` - Configuração do proxy nginx
- `NGINX_FIX_SUMMARY.md` - Este arquivo de documentação

## Comandos Úteis para Monitoramento

```bash
# Ver logs do nginx
DOCKER_CONFIG=/tmp/docker-config-noauth docker compose logs nginx -f

# Testar endpoints
curl http://localhost/states
curl http://localhost/polygons
curl http://localhost/state_status/SP

# Verificar status dos containers
DOCKER_CONFIG=/tmp/docker-config-noauth docker compose ps
``` 