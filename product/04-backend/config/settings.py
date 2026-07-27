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
# conn_max_age düşük tutulur (SQLite'ta zaten anlamsız, Supabase'te KASITLI):
# Supabase'in Session pooler'ı zaten kendi tarafında havuzluyor ve ücretsiz
# katmanda sert bir istemci sınırı var (execution.md §7.10'da bulunan gerçek
# olay: `FATAL: max clients reached ... pool_size: 15` — çok sayıda kısa ömürlü
# script/test koşusu, her biri conn_max_age=600 ile 10 dakika bağlantı açık
# tutunca havuzu doldurdu). Django tarafında UZUN ömürlü bağlantı tutmanın
# pooler zaten var olduğu için ek faydası yok, yalnızca havuzu daha çabuk
# doldurma riski var — bu yüzden kısa tutuluyor.
DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'aks_dev.sqlite3'}",
        conn_max_age=60,
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
