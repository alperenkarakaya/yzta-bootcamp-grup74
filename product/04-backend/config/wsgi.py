import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()

# --- §7.18: demo popülasyonunu arka planda ısıt ---
# `services._skorla_hepsi()` 2000 müşteriyi CSV'den okuyup skorluyor ve sonucu
# süreç ömrü boyunca saklıyor. Bu ilk hesap Render'ın ücretsiz katmanında ~78
# saniye sürüyor; ısıtılmazsa bu bedeli İLK ZİYARETÇİ öder (jüri olabilir).
#
# Neden burada: `wsgi.py` yalnızca gerçek sunucu (gunicorn) altında çalışır —
# `manage.py migrate` / `collectstatic` / `test` bu dosyayı hiç import etmez,
# dolayısıyla build ve testler yavaşlamaz. `AppConfig.ready()` bu ayrımı
# yapamazdı, her yönetim komutunda da tetiklenirdi.
#
# Neden DAEMON THREAD: senkron yapılsaydı worker ~78 saniye boyunca hiçbir
# isteği karşılayamaz, Render'ın sağlık kontrolü (`/api/bilgi`) zaman aşımına
# uğrar ve dağıtım başarısız sayılırdı. Bu haliyle worker anında hazır olur,
# ağır hesap arkada tamamlanır.
#
# Hata yutulur (`_skorla_hepsi_isit` içinde loglanır): ısınma bir optimizasyon,
# çekirdek akışın önkoşulu değil — başarısız olursa yalnızca ilk /portfoy
# isteği yavaş olur.
if os.environ.get("AKS_ISINMA", "true").lower() == "true":
    from api import services

    threading.Thread(
        target=services._skorla_hepsi_isit,
        name="aks-demo-isinma",
        daemon=True,
    ).start()
