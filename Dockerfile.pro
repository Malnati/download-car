# Dockerfile.pro
FROM download-car-base:latest

WORKDIR /download-car

# Copiar requirements.txt (gerado previamente pelo poetry export)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
