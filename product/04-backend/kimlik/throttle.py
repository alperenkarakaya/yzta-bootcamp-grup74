"""OTP/erişim-talebi uçları için hız sınırlama — DRF scoped throttle.

Oranlar `config/settings.py::REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]`'te
tanımlı. Amaç: bir hesabın OTP kodunu deneme-yanılmayla kırmaya çalışması ya
da bir kurumun art arda erişim talebi spam'lemesi (execution.md §3b Phase 7).
"""
from django.core.cache import caches
from rest_framework.throttling import UserRateThrottle


class OtpThrottle(UserRateThrottle):
    scope = "otp"


class ErisimTalebiThrottle(UserRateThrottle):
    scope = "erisim_talebi"


class AsistanThrottle(UserRateThrottle):
    """`/api/asistan` — projedeki TEK dış ücretli servisi (Gemini) çağıran uç.

    Diğer iki throttle güvenlik amaçlı (OTP kaba kuvvet, talep spam'i); bu ise
    MALİYET amaçlı. Uygulama herkese açık ve demo giriş bilgileri arayüzde
    yazılı olduğundan (jüri sürtünmesiz denesin diye alınmış bilinçli karar),
    isteyen herkes giriş yapıp bu ucu döngüye sokabilir ve PO'nun Gemini
    kotasını/faturasını tüketebilir. Anahtar sızmıyor — tüketilen, anahtarın
    değeri.

    Anahtar yokken uç deterministik kural motoruna düştüğü için sınır orada da
    zararsız: normal bir kullanıcı dakikada 10 soru sormaz.

    `cache`: varsayılan cache DEĞİL. Varsayılan, `REDIS_URL` doluysa Upstash'e
    gider ve `IGNORE_EXCEPTIONS=True` ile fail-open'dır — Redis erişilemezse
    sayaç hiç artmaz ve sınır SESSİZCE devre dışı kalır. (Bu tam olarak
    yaşandı: sınır yazıldıktan sonra testte 11 isteğin 11'i de 200 döndü,
    çünkü bu makinedeki Upstash erişilemez durumdaydı.) Diğer iki throttle
    güvenlik amaçlı olduğu ve kullanılabilirlik lehine bu ödünleşim bilinçli
    kabul edildiği için onlar varsayılanda bırakıldı; maliyet koruması ise
    dış bir servisin ayakta olmasına bağlanamaz.
    """
    scope = "asistan"
    cache = caches["throttle"]
