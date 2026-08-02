#!/bin/sh
# AKS konteyner giriş noktası (Hugging Face Spaces).
set -e

echo "==> Göç (migrate) uygulanıyor"
python manage.py migrate --noinput

# Demo hesapları idempotent: her açılışta güvenle çalışır, varsa dokunmaz.
# `|| true` KASITLI — DB geçici olarak erişilemezse (Supabase pooler doluysa)
# servis hiç açılmamaktansa demo hesapsız açılsın; bir sonraki yeniden
# başlatma tamamlar.
echo "==> Demo hesapları hazırlanıyor"
python manage.py bootstrap_demo_hesaplar || echo "!! demo hesap bootstrap atlandı"

# WORKER SAYISI BELLEKLE SINIRLI, CPU'YLA DEĞİL. Worker başına ~285 MB yerleşik
# bellek (shap/xgboost/lightgbm import zinciri) — her worker uygulamayı ayrı
# import eder. 512 MB'lık bir katmanda 2 worker ÖLÇÜLEREK elendi: konteyner
# 512 MB'a hapsedilip yük verildiğinde gunicorn 6 kez
# "Worker was sent SIGKILL! Perhaps out of memory?" bastı ve worker'lar sürekli
# yeniden doğdu. Aynı test 1 worker ile 286 MB tepe, 0 SIGKILL verdi.
# Bu yüzden varsayılan 1: dar katmanda ÇALIŞIR, geniş katmanda
# GUNICORN_WORKERS ile yükseltilir (bellek/worker ~285 MB'a göre hesaplayın).
#
# --threads 4 => worker x thread = eşzamanlı istek tavanı = eşzamanlı Postgres
# bağlantısı tavanı (settings.py: conn_max_age=0, bağlantı istek bitince
# kapanır). Supabase ücretsiz katmanın 15 istemci sınırının altında kalmalı —
# bu sınır §7.13'te canlıda TÜM panelin 500 dönmesine yol açmıştı.
ISCILER="${GUNICORN_WORKERS:-1}"
echo "==> Gunicorn başlıyor (port ${PORT:-7860}, worker: $ISCILER)"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-7860}" \
    --workers "$ISCILER" \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
