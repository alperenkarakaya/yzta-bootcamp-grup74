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

# --workers 2 --threads 4  => en fazla 8 eşzamanlı istek, yani en fazla 8
# eşzamanlı Postgres bağlantısı (settings.py: conn_max_age=0, bağlantı istek
# bitince kapanır). Supabase ücretsiz katmanın 15 istemci sınırının altında
# kalır — bu sınır §7.13'te canlıda TÜM panelin 500 dönmesine yol açmıştı.
# Worker başına ~335 MB yerleşik bellek (shap/xgboost/lightgbm import zinciri).
echo "==> Gunicorn başlıyor (port ${PORT:-7860})"
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-7860}" \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
