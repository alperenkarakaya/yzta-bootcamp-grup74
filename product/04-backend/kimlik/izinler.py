"""Çok kiracılılık zorlaması — DRF permission sınıfı + rıza kontrolü.

Kurum kapsamlı HER view bu iki fonksiyondan geçmeli: `KurumUyesi` (kullanıcı
bir kuruma üye mi) ve `aktif_riza()` (o kurumun BU müşteriye şu an aktif
erişimi var mı). İkisi de eksikse 403 — sızıntı riski taşıyan tek nokta
burası, bu yüzden `test_kiracilik.py` her iki kontrolü de ayrı ayrı kırmaya
çalışır (execution.md §3b Phase 7 / 7.2).
"""
from django.utils import timezone
from rest_framework.permissions import BasePermission

from .models import ErisimTalebi, KurumUyeligi


class KurumUyesi(BasePermission):
    """Yalnızca en az bir kuruma üye olan kullanıcılar geçer — banka
    personeli girişi, tüketici portalinden (`portal/*`) tamamen ayrı."""
    message = "Bu uç yalnızca bir kuruma üye kullanıcılar için."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and KurumUyeligi.objects.filter(user=request.user).exists()
        )


def kullanicinin_kurumu(user):
    """Kullanıcının kurum üyeliğini döner — yoksa `None`.

    Basit senaryo: bir kullanıcı tek kuruma üye (`unique_together` bunu
    zorlamıyor ama demo/kurulum akışı böyle varsayıyor); birden fazla üyelik
    varsa ilkini döner.
    """
    uyelik = KurumUyeligi.objects.filter(user=user).select_related("kurum").first()
    return uyelik.kurum if uyelik else None


def aktif_riza(kurum, profil):
    """Bu kurumun bu profile şu an geçerli (onaylanmış VE süresi dolmamış)
    erişimi var mı — varsa ilgili `ErisimTalebi`'ni döner, yoksa `None`.

    Süresi dolmuş ya da sonradan iptal edilmiş (`durum` değişir, bkz.
    kurum_views.py) bir onay burada ASLA aktif sayılmaz — testler bunu
    ayrı ayrı doğrular.
    """
    return (
        ErisimTalebi.objects.filter(
            kurum=kurum, profil=profil, durum="onaylandi", gecerlilik_bitis__gt=timezone.now(),
        )
        .order_by("-gecerlilik_bitis")
        .first()
    )
