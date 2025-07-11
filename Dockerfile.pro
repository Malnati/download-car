# Dockerfile.pro
FROM download-car-base:latest

# Instalar o download-car sem paddle (mais leve)
RUN pip install 'download_car@git+https://github.com/Malnati/download-car'
