#!/usr/bin/env bash
# AKS — Tek komutla tüm testler + build doğrulaması.
# Kullanım:  bash dogrula.sh
# Push öncesi çalıştırın; her üç paket de yeşilse teslime hazırsınız.
set -uo pipefail
KOK="$(cd "$(dirname "$0")" && pwd)"
HATA=0
baslik() { echo; echo "==================== $1 ===================="; }

baslik "1/3  aks_core (pytest)"
cd "$KOK/product/02-ai-agents" || exit 1
python -m pip install -q -e ".[test]" 2>/dev/null
if python -m pytest -q; then echo "aks_core: OK"; else echo "aks_core: BAŞARISIZ"; HATA=1; fi

baslik "2/3  Django backend (manage.py test)"
cd "$KOK/product/04-backend" || exit 1
python -m pip install -q -r requirements.txt 2>/dev/null
if python manage.py test; then echo "backend: OK"; else echo "backend: BAŞARISIZ"; HATA=1; fi

baslik "3/3  Frontend (tsc + vite build)"
cd "$KOK/product/03-frontend" || exit 1
npm install --no-audit --no-fund >/dev/null 2>&1
if npm run build >/dev/null 2>&1; then echo "frontend: OK (build temiz)"; else echo "frontend: BAŞARISIZ"; HATA=1; fi

baslik "SONUÇ"
if [ "$HATA" -eq 0 ]; then
  echo "✅ Tüm paketler geçti — push'a hazır."
else
  echo "❌ En az bir paket başarısız — yukarıdaki çıktıya bakın."
fi
exit "$HATA"
