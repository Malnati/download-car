# 🗄️ Banco de Dados PostgreSQL/PostGIS

Este documento descreve a configuração e uso do banco de dados PostgreSQL/PostGIS para o projeto download-car.

## 📋 Visão Geral

O projeto agora suporta sincronização de shapefiles com um banco de dados PostgreSQL/PostGIS, permitindo:

- Armazenamento persistente dos dados do CAR
- Consultas espaciais otimizadas
- Análises geoespaciais avançadas
- Integração com ferramentas GIS

## 🏗️ Estrutura do Banco de Dados

### Tabela Principal: `car_data`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | SERIAL | Chave primária auto-incrementada |
| `car_code` | VARCHAR(100) | Código único do CAR |
| `state` | VARCHAR(2) | Sigla do estado (ex: SP, MG, BA) |
| `polygon_type` | VARCHAR(50) | Tipo de polígono (ex: AREA_PROPERTY, APPS) |
| `geometry` | GEOMETRY(MULTIPOLYGON, 4326) | Geometria espacial em WGS84 |
| `properties` | JSONB | Propriedades do shapefile em formato JSON |
| `created_at` | TIMESTAMP | Data/hora de criação do registro |
| `updated_at` | TIMESTAMP | Data/hora da última atualização |

### Índices Criados

- `idx_car_data_car_code` - Índice no código do CAR
- `idx_car_data_state` - Índice no estado
- `idx_car_data_polygon_type` - Índice no tipo de polígono
- `idx_car_data_geometry` - Índice espacial GIST na geometria

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Configure as seguintes variáveis no arquivo `.env`:

```bash
# Configurações do Banco de Dados PostgreSQL/PostGIS
DB_HOST=postgres
DB_PORT=5432
DB_NAME=download_car
DB_USER=postgres
DB_PASSWORD=postgres
DB_SCHEMA=public
DB_POOL_SIZE=5
DB_TIMEOUT=30
```

### 2. Inicialização do Banco

```bash
# Inicializar banco de dados
make init-db

# Ou executar diretamente
python init_database.py
```

### 3. Verificar Status

```bash
# Verificar status da conexão
make db-status

# Ou via curl
curl -X GET "http://localhost:8000/database_status"
```

## 🚀 Uso da API

### Endpoints Disponíveis

#### 1. Sincronizar com Banco de Dados

**POST** `/sync_to_database`

Sincroniza shapefiles com o banco de dados.

**Parâmetros:**
- `sync_type` (obrigatório): "state" ou "car"
- `state` (obrigatório): Sigla do estado
- `polygon_type` (opcional): Tipo de polígono (padrão: AREA_PROPERTY)
- `car_code` (opcional): Código CAR específico
- `folder` (opcional): Pasta dos shapefiles (padrão: temp)
- `create_tables` (opcional): Criar tabelas automaticamente (padrão: true)

**Exemplos:**

```bash
# Sincronizar estado completo
curl -X POST "http://localhost:8000/sync_to_database" \
     -F "sync_type=state" \
     -F "state=SP" \
     -F "polygon_type=AREA_PROPERTY"

# Sincronizar CAR específico
curl -X POST "http://localhost:8000/sync_to_database" \
     -F "sync_type=car" \
     -F "car_code=SP12345678901234567890" \
     -F "state=SP" \
     -F "polygon_type=AREA_PROPERTY"
```

#### 2. Verificar Status do Banco

**GET** `/database_status`

Retorna informações sobre a conexão e configuração do banco.

```bash
curl -X GET "http://localhost:8000/database_status"
```

#### 3. Consultar Dados

**GET** `/car_data`

Consulta dados do CAR armazenados no banco.

**Parâmetros:**
- `car_code` (opcional): Código CAR específico
- `state` (opcional): Filtrar por estado
- `polygon_type` (opcional): Filtrar por tipo de polígono
- `limit` (opcional): Limite de resultados (padrão: 100, máximo: 1000)

**Exemplos:**

```bash
# Buscar todos os dados de um estado
curl -X GET "http://localhost:8000/car_data?state=SP&limit=10"

# Buscar CAR específico
curl -X GET "http://localhost:8000/car_data?car_code=SP12345678901234567890"

# Buscar por tipo de polígono
curl -X GET "http://localhost:8000/car_data?polygon_type=APPS&limit=5"
```

## 🛠️ Comandos Makefile

O projeto inclui comandos Makefile para facilitar o uso:

```bash
# Inicializar banco de dados
make init-db

# Verificar status
make db-status

# Sincronizar estado
make sync-state state=SP polygon=AREA_PROPERTY

# Sincronizar CAR específico
make sync-car car=SP12345678901234567890 state=SP polygon=AREA_PROPERTY

# Consultar CAR
make query-car car=SP12345678901234567890

# Consultar estado
make query-state state=SP limit=10
```

## 📊 Consultas SQL Úteis

### Consultas Básicas

```sql
-- Contar total de registros por estado
SELECT state, COUNT(*) as total
FROM car_data
GROUP BY state
ORDER BY total DESC;

-- Contar por tipo de polígono
SELECT polygon_type, COUNT(*) as total
FROM car_data
GROUP BY polygon_type
ORDER BY total DESC;

-- Buscar CAR específico
SELECT car_code, state, polygon_type, 
       ST_AsText(geometry) as geometry,
       properties
FROM car_data
WHERE car_code = 'SP12345678901234567890';
```

### Consultas Espaciais

```sql
-- Calcular área total por estado
SELECT state, 
       SUM(ST_Area(geometry::geography)) / 10000 as area_hectares
FROM car_data
GROUP BY state
ORDER BY area_hectares DESC;

-- Buscar propriedades dentro de uma área
SELECT car_code, state, polygon_type
FROM car_data
WHERE ST_Intersects(
    geometry,
    ST_GeomFromText('POLYGON((...))', 4326)
);

-- Calcular centroide das propriedades
SELECT car_code, 
       ST_AsText(ST_Centroid(geometry)) as centroid
FROM car_data
WHERE state = 'SP';
```

### Consultas Avançadas

```sql
-- Propriedades com maior área
SELECT car_code, state, polygon_type,
       ST_Area(geometry::geography) / 10000 as area_hectares
FROM car_data
ORDER BY area_hectares DESC
LIMIT 10;

-- Estatísticas por município (se disponível nas propriedades)
SELECT properties->>'municipio' as municipio,
       COUNT(*) as total_propriedades,
       AVG(ST_Area(geometry::geography) / 10000) as area_media_hectares
FROM car_data
WHERE properties->>'municipio' IS NOT NULL
GROUP BY properties->>'municipio'
ORDER BY total_propriedades DESC;
```

## 🔧 Manutenção

### Backup do Banco

```bash
# Backup completo
pg_dump -h localhost -U postgres -d download_car > backup_$(date +%Y%m%d).sql

# Backup apenas dados (sem estrutura)
pg_dump -h localhost -U postgres -d download_car --data-only > data_backup_$(date +%Y%m%d).sql
```

### Restaurar Backup

```bash
# Restaurar backup completo
psql -h localhost -U postgres -d download_car < backup_20231201.sql

# Restaurar apenas dados
psql -h localhost -U postgres -d download_car < data_backup_20231201.sql
```

### Limpeza de Dados

```sql
-- Remover registros duplicados
DELETE FROM car_data
WHERE id NOT IN (
    SELECT MIN(id)
    FROM car_data
    GROUP BY car_code
);

-- Remover registros antigos
DELETE FROM car_data
WHERE created_at < NOW() - INTERVAL '1 year';
```

## 🐳 Docker Compose

O projeto inclui configuração Docker Compose com PostgreSQL/PostGIS:

```yaml
services:
  postgis:
    image: postgis/postgis:15-3.3
    environment:
      - POSTGRES_DB=${DB_NAME:-download_car}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    ports:
      - "${DB_PORT:-5432}:5432"
    volumes:
      - postgis_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-download_car}"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de conexão**
   - Verifique se o PostgreSQL está rodando
   - Confirme as variáveis de ambiente
   - Teste a conexão: `make db-status`

2. **Erro de PostGIS**
   - Verifique se a extensão PostGIS está instalada
   - Execute: `CREATE EXTENSION IF NOT EXISTS postgis;`

3. **Erro de permissões**
   - Verifique se o usuário tem permissões no banco
   - Execute: `GRANT ALL PRIVILEGES ON DATABASE download_car TO postgres;`

4. **Erro de memória**
   - Aumente o pool de conexões: `DB_POOL_SIZE=10`
   - Aumente o timeout: `DB_TIMEOUT=60`

### Logs

```bash
# Ver logs do PostgreSQL
docker compose logs postgis

# Ver logs da API
docker compose logs download-car-api

# Ver logs específicos
docker compose logs -f download-car-api | grep -i database
```

## 📚 Recursos Adicionais

- [Documentação PostgreSQL](https://www.postgresql.org/docs/)
- [Documentação PostGIS](https://postgis.net/documentation/)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/) 