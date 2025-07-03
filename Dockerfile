# Dockerfile
ARG VARIANT="3.10"
FROM python:${VARIANT}

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install tesseract-ocr python3-opencv

RUN pip install --upgrade pip

RUN pip install 'download_car[paddle]@git+https://github.com/Malnati/download-car'

WORKDIR /download-car

# Optionally download PaddleOCR models during build.
# This step may fail on CPUs without AVX support, so it is disabled by default.
ARG PRELOAD_MODELS=0
RUN if [ "$PRELOAD_MODELS" = "1" ]; then \
        python - <<'EOF'
from paddleocr import PaddleOCR
PaddleOCR(lang="en")
EOF
    ; fi

ENTRYPOINT ["python"]
