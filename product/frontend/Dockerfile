FROM python:3.12-slim

WORKDIR /app

# LightGBM için gerekli sistem kütüphanesi
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY web/ web/
COPY models/ models/
COPY data/sentetik_islemler.csv data/sentetik_islemler.csv

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
