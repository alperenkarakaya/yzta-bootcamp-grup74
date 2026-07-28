"""
Django ayarları — AKS backend.

Ortam değişkeni yoksa güvenli yerel varsayılanlara düşer, böylece demo
Supabase/Redis olmadan da çalışır (orijinal projenin "demo her koşulda çalışır"
ilkesi). Üretimde .env doldurulur (bkz. .env.example ve architecture.md §11).
"""
import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-key-change-in-prod")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0"
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "api",
    "audit",
    "kimlik",  # §3b Phase 7/7.2 — kimlik, rıza defteri, kurum çok kiracılılığı
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

# --- Veritabanı: Supabase (DATABASE_URL) yoksa yerel SQLite ---
# `conn_max_age=0` (istek bitince bağlantıyı kapat) KASITLI bir karardır,
# ihmal değil — bir connection pooler'ın ARKASINDA kalıcı bağlantı tutmak
# anti-pattern'dir: havuzlama zaten pooler'ın işi, uygulama tarafında ikinci
# bir havuz tutmak yalnızca sınırlı istemci kotasını tüketir.
#
# İki gerçek olayla öğrenildi (execution.md §7.10 ve §7.13):
#   1. `conn_max_age=600` ile çok sayıda kısa ömürlü script/test koşusu, her
#      biri 10 dakika bağlantı açık tutunca havuz doldu → 600'den 60'a çekildi.
#   2. 60 saniye de yetmedi: §7.11'de uçlar yetkilendirildiğinden beri HER
#      korumalı istek, oturum doğrulaması (`request.user`) için DB'ye gidiyor —
#      yani artık "DB'ye dokunmayan uç" yok. Tarayıcı bir sayfada 5 paralel
#      istek atınca dev sunucusu 5 ayrı thread'de 5 ayrı bağlantı açıp 60 saniye
#      tutuyordu; Supabase ücretsiz katmanın 15 istemci sınırı birkaç sayfa
#      gezinmesinde doluyor ve `FATAL: (EMAXCONNSESSION) max clients reached`
#      ile TÜM panel 500 dönmeye başlıyordu (canlı tarayıcı denetiminde
#      yakalandı).
# Pooler tarafında bağlantı zaten hazır beklediği için 0'a çekmenin gecikme
# maliyeti ihmal edilebilir; kazanç, havuzun tükenmemesi.
DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'aks_dev.sqlite3'}",
        conn_max_age=0,
    )
}

# --- Cache: Upstash Redis (REDIS_URL) yoksa yerel bellek ---
# IGNORE_EXCEPTIONS=True: Redis erişilemezse (ağ/TLS/DNS hatası) cache
# okuma/yazma sessizce no-op olur — İSTİSNA FIRLATMAZ. Bunsuz, Redis'in kendisi
# hiçbir işlevsel değeri olmayan bir uçta (ör. DRF throttling, /api/portfoy
# cache'i) tek hata noktası olurdu: Upstash'e erişilemediği an ilgisiz uçlar
# (OTP gönderme, erişim talebi) 500 dönmeye başlardı — bu, projenin her
# yerindeki "opsiyonel bileşen çekirdek akışı asla düşürmemeli" ilkesiyle
# (bkz. AuditLog best-effort yazımı, kalibrasyon/anomali modeli opsiyonelliği)
# tutarsız olurdu. Bilinçli ödünleşim: bu, Redis çökükken DRF throttle
# limitlerinin de sessizce devre dışı kalacağı (fail-open, fail-closed değil)
# anlamına gelir — kabul edilebilir, çünkü kullanılabilirlik > kesintide
# mükemmel hız sınırlama (django-redis'in resmi önerdiği desen).
_redis_url = os.environ.get("REDIS_URL")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _redis_url,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "IGNORE_EXCEPTIONS": True},
        }
    }
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# SMS sağlayıcısı olmadığı için (açık OQ) OTP kodunun API yanıtında
# döndürülmesi — yalnızca demo/test. `DJANGO_DEBUG`'tan AYRI tutuldu: bu
# kurulumda DEBUG kapalı (üretim benzeri hata davranışı istendi) ama telefon
# doğrulama akışının denenebilmesi gerekiyor. GERÇEK DAĞITIMDA `false`.
OTP_DEMO_KOD = os.environ.get("AKS_OTP_DEMO_KOD", "false").lower() == "true"

# --- HTTPS sertleştirmesi (yalnızca DJANGO_HTTPS=true iken) ---
# `manage.py check --deploy`'un dört uyarısının (W004/W008/W012/W016) karşılığı.
# DEBUG'a DEĞİL, ayrı bir bayrağa bağlı olmaları KASITLI: `.env`'de zaten
# DJANGO_DEBUG=false, ama yerel geliştirme hâlâ düz http üzerinden
# (localhost:5173 -> :8000). Bunlar DEBUG=False ile otomatik açılsaydı,
# tarayıcı Secure işaretli çerezi http'de göndermeyeceği için giriş sessizce
# çalışmaz hâle gelirdi. Gerçek dağıtımda (TLS sonlandıran bir proxy arkasında)
# DJANGO_HTTPS=true verilir ve dördü birden devreye girer.
HTTPS_ZORUNLU = os.environ.get("DJANGO_HTTPS", "false").lower() == "true"
if HTTPS_ZORUNLU:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 yıl
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    # Proxy TLS'i sonlandırıyorsa Django isteği "güvenli" saymalı; aksi halde
    # SECURE_SSL_REDIRECT sonsuz yönlendirme döngüsü üretir.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Çerezler hiçbir koşulda JavaScript'e açılmamalı ve çapraz-site POST'larda
# gönderilmemeli — bunlar HTTPS gerektirmediği için her ortamda açık.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# Kullanıcı portalı gerçek şifreler kabul ettiğinden (§3b Phase 6) minimum uzunluk
# doğrulaması aktif — Django'nun kendisi zaten güçlü hashleme (PBKDF2) uyguluyor.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
]
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    # §3b Phase 7/7.2 — OTP/erişim-talebi uçlarının hız sınırlaması (kimlik/throttle.py)
    "DEFAULT_THROTTLE_RATES": {"otp": "5/min", "erisim_talebi": "20/hour"},
}

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
).split(",")

# §3b Phase 6 — kullanıcı portalı (giriş/kayıt) çerez tabanlı oturum + CSRF kullanıyor.
# Django 4+ CSRF middleware'i, cookie/header eşleşse bile isteğin Origin header'ını
# CSRF_TRUSTED_ORIGINS ile karşılaştırıyor — Vite dev proxy'si isteği tarayıcıdan
# (localhost:517x) sunucu tarafında Django'ya (127.0.0.1:8000) ilettiği için bu, aynı
# origin listesini paylaşır (dev'de Vite hangi porta düşerse düşsün, 5173 dolu olduğunda
# otomatik 5174'e geçebiliyor — ikisi de listede).
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
