# Dockerfile.pro
FROM download-car-base:latest

# Instalar dependências do sistema necessárias para produção
RUN apt-get update && apt-get install -y --no-install-recommends \
        # Dependências para geopandas e postgresql (apenas para produção)
        libgdal-dev \
        libproj-dev \
        libgeos-dev \
        libspatialindex-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /download-car

# Copiar requirements.txt (gerado previamente pelo poetry export)
COPY requirements.txt .

# Instalar apenas dependências de produção
RUN pip install --no-cache-dir -r requirements.txt

# Copiar apenas arquivos necessários para produção
COPY download_car/ ./download_car/
COPY cli.py .
COPY api.py .
COPY database.py .
COPY entrypoint.*.sh ./

# Renomear app.py para api.py se existir
RUN if [ -f app.py ]; then mv app.py api.py; fi

# Script para iniciar Tor junto com a aplicação
COPY dev/start-tor.sh /usr/local/bin/start-tor.sh
RUN chmod +x /usr/local/bin/start-tor.sh
