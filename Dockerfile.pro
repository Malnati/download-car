# Dockerfile.pro
FROM download-car-base:latest

WORKDIR /download-car

# Copiar requirements.txt (gerado previamente pelo poetry export)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Renomear app.py para api.py se existir
RUN if [ -f app.py ]; then mv app.py api.py; fi
