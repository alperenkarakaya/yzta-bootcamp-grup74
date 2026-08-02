# AKS — dağıtım imajı (sağlayıcıdan bağımsız)
#
# TEK SERVİS: Django hem /api'yi hem derlenmiş React arayüzünü servis eder.
# Gerekçe settings.py'deki SPA_DIR bloğunda: arayüz ayrı bir alan adına
# konsaydı `credentials: "same-origin"` yüzünden oturum çerezi hiç gönderilmez
# ve giriş komple çalışmazdı.
#
# Build bağlamı DEPO KÖKÜDÜR (COPY yolları `product/...` ile başlar).
#   Render : render.yaml `dockerfilePath: ./deploy/Dockerfile` ile bunu kullanır.
#   HF     : `deploy/hf/yayinla.sh` bunu Space deposunun köküne taşır.
# Dinlenen port `PORT` env'inden gelir (Render bunu kendi atar), yoksa 7860.

# ---- 1) Arayüz derlemesi ----
FROM node:20-slim AS arayuz
WORKDIR /arayuz
# package*.json ayrı katmanda: kaynak değişince npm ci yeniden çalışmasın.
COPY product/03-frontend/package.json product/03-frontend/package-lock.json ./
RUN npm ci
COPY product/03-frontend/ ./
# `npm run build` = `tsc --noEmit && vite build` — tip hatası varsa imaj
# üretilmez. Bu KASITLI: bozuk bir arayüzün canlıya çıkmasındansa build patlasın.
RUN npm run build

# ---- 2) Çalışma imajı ----
FROM python:3.11-slim

# libgomp1: LightGBM'in manylinux wheel'i OpenMP çalışma zamanını İÇERMEZ,
# sisteme kurulu olmasını bekler. Yoksa `import lightgbm` şu hatayla patlar:
# "libgomp.so.1: cannot open shared object file". aks_core.model.kayit bunu
# import ettiği için skorlama uçlarının tamamı çöker.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# HF Spaces konteyneri UID 1000 ile çalıştırmayı öneriyor; root olarak yazılan
# dosyalar çalışma anında izin hatası verebiliyor.
RUN useradd -m -u 1000 user

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=7860

WORKDIR /app

# Kaynaklar önce, kurulum sonra. Bağımlılıkları ayrı bir katmana çıkarıp
# (yalnızca pyproject.toml + requirements.txt kopyalayarak) ~1 GB'lık ML
# kurulumunu cache'lemek CAZİP ama denenmedi: aks_core'u kaynağı yokken
# editable kurmak, setuptools'un editable-finder davranışına bel bağlar.
# Sadelik ve kesin doğruluk, build süresine tercih edildi.
COPY --chown=user:user product/02-ai-agents/ product/02-ai-agents/
COPY --chown=user:user product/01-data/ product/01-data/
COPY --chown=user:user product/04-backend/ product/04-backend/

# aks_core EDITABLE kurulur: paths.py veri dizinini `__file__`'a göre
# (`_PKG.parents[2]/product/01-data/datasets`) çözüyor — site-packages'a
# kopyalansaydı bu yol imajda yanlış yere işaret ederdi. AKS_DATA_DIR yine de
# aşağıda açıkça veriliyor (kemer + askı).
RUN pip install -e product/02-ai-agents \
    && pip install -r product/04-backend/requirements.txt
# Derlenmiş arayüz -> settings.SPA_DIR
COPY --chown=user:user --from=arayuz /arayuz/dist/ product/04-backend/spa/
COPY --chown=user:user deploy/baslat.sh /app/baslat.sh
RUN chmod +x /app/baslat.sh

ENV AKS_DATA_DIR=/app/product/01-data/datasets

USER user
WORKDIR /app/product/04-backend

# Build sırasında toplanır (yalnızca Django admin'inin statikleri; SPA
# varlıklarını WhiteNoise doğrudan spa/ dizininden servis ediyor).
# Çalışma anında yapılmıyor: her konteyner başlangıcını yavaşlatırdı.
RUN python manage.py collectstatic --noinput

EXPOSE 7860
CMD ["/app/baslat.sh"]
