# Sistema de Variáveis de Ambiente - Download CAR

Este documento explica como configurar e usar o sistema de variáveis de ambiente implementado no projeto Download CAR.

## Arquitetura

O sistema segue a seguinte cadeia de configuração:

```
.env → docker-compose.yml → container → nginx → frontend
```

### 1. Arquivo .env

Arquivo principal de configuração com todas as variáveis do sistema (padrão do Docker Compose):

```bash
# URL do endpoint da API
API_ENDPOINT_URL=http://192.168.5.179:8787

# Configuração padrão de polígono
DEFAULT_POLYGON=AREA_PROPERTY

# Configurações de timeout (em milissegundos)
DEFAULT_TIMEOUT=800000
TIMEOUT_INCREMENT=10000
MIN_TIMEOUT=10000
MAX_TIMEOUT=300000

# Timeouts específicos por estado
STATE_TIMEOUT_AC=60000
STATE_TIMEOUT_AL=120000
# ... outros estados

# Configurações CORS
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_METHODS=GET,POST,OPTIONS
CORS_ALLOW_HEADERS=*
```

### 2. Docker Compose

O `docker-compose.yml` carrega automaticamente as variáveis do arquivo `.env` (padrão do Docker Compose):

```yaml
# O Docker Compose carrega automaticamente o arquivo .env
# Não é necessário especificar env_file para o arquivo .env padrão

services:
  nginx:
    environment:
      - API_ENDPOINT_URL
      - DEFAULT_POLYGON
      # ... outras variáveis
```

### 3. Container Nginx

O container nginx usa um Dockerfile customizado que:
- Instala Node.js
- Executa script de entrypoint que substitui variáveis
- Gera configuração do frontend dinamicamente

### 4. Frontend

O frontend recebe as configurações através de:
- Substituição de variáveis no `nginx.conf.template`
- Geração dinâmica do `index.html` com valores corretos

## Como Usar

### 1. Configuração Inicial

```bash
# O Docker Compose carrega automaticamente o arquivo .env
# Não é necessário carregar manualmente

# Ou definir manualmente se necessário
export API_ENDPOINT_URL=http://seu-servidor:8787
```

### 2. Modificar Configurações

Edite o arquivo `.env` para alterar qualquer configuração:

```bash
# Alterar timeout padrão
DEFAULT_TIMEOUT=600000

# Alterar timeout específico de um estado
STATE_TIMEOUT_SP=600000

# Alterar URL da API
API_ENDPOINT_URL=http://novo-servidor:8787
```

### 3. Reconstruir e Executar

```bash
# Parar containers
docker-compose down

# Reconstruir com novas configurações
docker-compose up --build

# Ou apenas reiniciar
docker-compose up -d
```

## Variáveis Disponíveis

### Configurações Gerais
- `API_ENDPOINT_URL`: URL completa da API
- `DEFAULT_POLYGON`: Tipo de polígono padrão
- `DEFAULT_TIMEOUT`: Timeout padrão em milissegundos
- `TIMEOUT_INCREMENT`: Incremento de timeout em caso de erro
- `MIN_TIMEOUT`: Timeout mínimo
- `MAX_TIMEOUT`: Timeout máximo

### Timeouts por Estado
- `STATE_TIMEOUT_AC`: Timeout para Acre
- `STATE_TIMEOUT_AL`: Timeout para Alagoas
- `STATE_TIMEOUT_AM`: Timeout para Amazonas
- ... (todos os 27 estados)

### Configurações CORS
- `CORS_ALLOW_ORIGINS`: Origens permitidas
- `CORS_ALLOW_METHODS`: Métodos HTTP permitidos
- `CORS_ALLOW_HEADERS`: Headers permitidos
- `CORS_ALLOW_CREDENTIALS`: Permitir credenciais

### Configurações do Servidor
- `API_HOST`: Host da API
- `API_PORT`: Porta da API
- `API_PATH`: Caminho da API
- `NETWORK_TIMEOUT`: Timeout de rede
- `MAX_RETRIES`: Máximo de tentativas

## Scripts Disponíveis

### generate-config.nginx.js
Gera configuração do frontend com variáveis de ambiente:
```bash
node generate-config.nginx.js
```

### entrypoint.nginx.sh
Script executado no container nginx para:
- Substituir variáveis no nginx.conf
- Gerar configuração do frontend
- Iniciar o nginx

## Exemplos de Uso

### Alterar Timeout de São Paulo
```bash
# Editar .env
echo "STATE_TIMEOUT_SP=300000" >> .env

# Reconstruir
docker-compose up --build
```

### Alterar URL da API
```bash
# Editar .env
sed -i 's|API_ENDPOINT_URL=.*|API_ENDPOINT_URL=http://novo-servidor:8787|' .env

# Reiniciar
docker-compose restart nginx
```

### Configurar para Desenvolvimento
```bash
# Criar .env.dev
cp .env .env.dev

# Editar para desenvolvimento
sed -i 's|API_ENDPOINT_URL=.*|API_ENDPOINT_URL=http://localhost:8787|' .env.dev

# Usar arquivo específico
docker-compose --env-file .env.dev up
```

## Troubleshooting

### Variáveis não estão sendo aplicadas
1. Verifique se o arquivo `.env` existe
2. Confirme que as variáveis estão no formato correto
3. Reconstrua o container: `docker-compose up --build`

### Frontend não atualiza
1. Verifique se o Node.js está instalado no container
2. Confirme que o script `generate-config.js` está sendo executado
3. Verifique os logs: `docker-compose logs nginx`

### Nginx não inicia
1. Verifique se o `nginx.conf.template` está correto
2. Confirme que as variáveis CORS estão definidas
3. Verifique os logs: `docker-compose logs nginx`

## Benefícios

1. **Flexibilidade**: Configurações podem ser alteradas sem modificar código
2. **Portabilidade**: Fácil adaptação para diferentes ambientes
3. **Manutenibilidade**: Centralização de configurações
4. **Segurança**: Separação de configurações sensíveis
5. **Automação**: Configuração automática durante deploy 