"""OTP/erişim-talebi uçları için hız sınırlama — DRF scoped throttle.

Oranlar `config/settings.py::REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`'te
tanımlı. Amaç: bir hesabın OTP kodunu deneme-yanılmayla kırmaya çalışması ya
da bir kurumun art arda erişim talebi spam'lemesi (execution.md §3b Phase 7).
"""
from rest_framework.throttling import UserRateThrottle


class OtpThrottle(UserRateThrottle):
    scope = "otp"


class ErisimTalebiThrottle(UserRateThrottle):
    scope = "erisim_talebi"
