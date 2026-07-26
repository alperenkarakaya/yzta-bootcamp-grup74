"""Telefon doğrulama — HMAC-SHA256 hash'li numara + tek kullanımlık OTP kodu.

Ham telefon numarası HİÇBİR ZAMAN diske yazılmaz — yalnızca
`HMAC-SHA256(AKS_PEPPER, E.164)` saklanır (bkz. `models.Profil.telefon_hash`,
`unique=True` — bir numara yalnızca bir hesaba bağlanabilir, PO'nun seçtiği
Sybil-direnci mekanizması, execution.md §3b Phase 7).

SMS sağlayıcısı henüz kurulu değil (yeni OQ, execution.md'ye eklendi) —
`DEBUG=True` iken kod hem sunucu logunda hem API yanıtında görünür
(yalnızca geliştirme/demo; üretimde bu satır kaldırılmalı).
"""
import hashlib
import hmac
import os
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

OTP_GECERLILIK_DK = 5
OTP_UZUNLUK = 6
MAKS_DENEME = 5


def _pepper() -> bytes:
    # AKS_PEPPER ayrı bir sırdır (SECRET_KEY'den bağımsız rotasyon için) —
    # tanımlı değilse SECRET_KEY'e düşer (demo/geliştirmede .env doldurulmamış
    # olabilir; paths.py/settings.py'deki "boş env -> varsayılan" deseniyle tutarlı).
    return os.environ.get("AKS_PEPPER", settings.SECRET_KEY).encode("utf-8")


def hashle(deger: str) -> str:
    return hmac.new(_pepper(), deger.encode("utf-8"), hashlib.sha256).hexdigest()


def otp_uret() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_UZUNLUK))


def otp_son_gecerlilik():
    return timezone.now() + timedelta(minutes=OTP_GECERLILIK_DK)
