"""Çok kiracılılık zorlaması — DRF permission sınıfı + rıza kontrolü.

Kurum kapsamlı HER view bu iki fonksiyondan geçmeli: `KurumUyesi` (kullanıcı
bir kuruma üye mi) ve `aktif_riza()` (o kurumun BU müşteriye şu an aktif
erişimi var mı). İkisi de eksikse 403 — sızıntı riski taşıyan tek nokta
burası, bu yüzden `test_kiracilik.py` her iki kontrolü de ayrı ayrı kırmaya
çalışır (execution.md §3b Phase 7 / 7.2).
"""
from django.utils import timezone
from rest_framework.permissions import BasePermission

from .models import ErisimTalebi, KurumUyeligi, Profil


class ProfilSahibi(BasePermission):
    """Yalnızca bir `Profil`'i (AKS numarası) olan kullanıcılar geçer.

    Kurum personeli hesaplarının `Profil`'i yoktur (`bootstrap_kurum` yalnızca
    `KurumUyeligi` açar). Bu izin olmadan müşteri-taraflı uçlar `request.user.
    profil` üzerinde `RelatedObjectDoesNotExist` fırlatıp 500 dönüyordu — kurum
    kullanıcısı portal sayfalarına girdiğinde tetiklenen gerçek bir hataydı.
    """
    message = "Bu uç yalnızca AKS numarası olan müşteri hesapları için."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and Profil.objects.filter(user=request.user).exists()
        )


class YoneticiKullanici(BasePermission):
    """Banka içi demo/araştırma yüzeyi (`api/views.py`) — yalnızca `is_staff`.

    Bu yüzey TÜM demo popülasyonunu, portföy/adalet toplu istatistiklerini ve
    değerlendirme geçmişini gösterir; yani doğası gereği "herkesi görebilen"
    tek yüzeydir. Phase 7'ye kadar hiçbir izin kontrolü yoktu (DRF varsayılanı
    `AllowAny`) — sonuç: kayıt olan HERHANGİ bir son kullanıcı, hatta anonim
    bir istemci, `/api/demo-musteriler`, `/api/portfoy`, `/api/gecmis/<id>`
    uçlarına doğrudan erişebiliyordu. Ürünün "kullanıcı yalnızca kendi
    içeriğini, kurum yalnızca rıza verileni görür" sözünü ihlal eden yer
    burasıydı (portal ve kurum katmanları zaten `ProfilSahibi` / `KurumUyesi`
    ile doğru kapsamlanmıştı).

    `is_staff` kasıtlı: yeni bir rol modeli/tablo eklemek yerine Django'nun
    kendi yönetici bayrağı kullanılıyor — bu yüzey zaten "banka içi araç"
    olduğundan admin paneline erişimle aynı güven seviyesini gerektirir.
    """
    message = "Bu uç yalnızca yönetici (banka içi araştırma) hesapları için."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


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
