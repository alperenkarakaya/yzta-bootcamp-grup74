"""
Kurum-taraflı (banka) uçlar — çok kiracılılığın zorlandığı yer. Her view
`KurumUyesi` (kullanıcı bir kuruma üye mi) VE `izinler.aktif_riza()` (o
kurumun BU müşteriye şu an aktif erişimi var mı) kontrolünden geçer
(execution.md §3b Phase 7 / 7.2). Bankanın kendi demo/araştırma sayfaları
(`api/views.py`) bundan tamamen ayrı — bu modül yalnızca rıza-tabanlı,
gerçek-müşteri erişim akışı için.
"""
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response

from . import aks_no as aks_no_modul
from . import izinler
from .models import ErisimTalebi, Profil
from .throttle import ErisimTalebiThrottle
from .views import _riza_yaz


@api_view(["GET"])
@permission_classes([izinler.KurumUyesi])
def ben(request):
    kurum = izinler.kullanicinin_kurumu(request.user)
    return Response({"kurum": kurum.ad, "kurum_kod": kurum.kod})


@api_view(["POST"])
@permission_classes([izinler.KurumUyesi])
@throttle_classes([ErisimTalebiThrottle])
def erisim_talebi_olustur(request):
    kurum = izinler.kullanicinin_kurumu(request.user)
    aks_numarasi = (request.data.get("aks_no") or "").strip().upper()
    amac = (request.data.get("amac") or "").strip()

    if not aks_no_modul.gecerli_mi(aks_numarasi):
        return Response({"hata": "Geçersiz AKS numarası formatı"}, status=400)
    if not amac:
        return Response({"hata": "Erişim amacı belirtilmeli"}, status=400)
    try:
        profil = Profil.objects.get(aks_no=aks_numarasi)
    except Profil.DoesNotExist:
        return Response({"hata": "Bu AKS numarasına kayıtlı müşteri bulunamadı"}, status=404)

    var_olan = ErisimTalebi.objects.filter(kurum=kurum, profil=profil, durum="bekliyor").first()
    if var_olan:
        return Response({"hata": "Bu müşteri için zaten bekleyen bir talep var"}, status=409)

    talep = ErisimTalebi.objects.create(kurum=kurum, profil=profil, talep_eden=request.user, amac=amac)
    _riza_yaz(talep, "talep_olusturuldu", request)
    return Response({"talep_id": talep.id, "durum": talep.durum}, status=201)


@api_view(["GET"])
@permission_classes([izinler.KurumUyesi])
def musteriler(request):
    """Yalnızca bu kurumun ŞU AN aktif rızası olan müşteriler — süresi
    dolmuş/iptal edilmiş rızalar burada GÖRÜNMEZ (izinler.aktif_riza ile
    aynı sorgu mantığı)."""
    kurum = izinler.kullanicinin_kurumu(request.user)
    aktif_talepler = (
        ErisimTalebi.objects.filter(kurum=kurum, durum="onaylandi", gecerlilik_bitis__gt=timezone.now())
        .select_related("profil")
    )
    return Response({"musteriler": [
        {"aks_no": t.profil.aks_no, "amac": t.amac, "gecerlilik_bitis": t.gecerlilik_bitis.isoformat()}
        for t in aktif_talepler
    ]})


@api_view(["GET"])
@permission_classes([izinler.KurumUyesi])
def musteri_detay(request, aks_numarasi: str):
    kurum = izinler.kullanicinin_kurumu(request.user)
    try:
        profil = Profil.objects.get(aks_no=aks_numarasi.strip().upper())
    except Profil.DoesNotExist:
        return Response({"hata": "Müşteri bulunamadı"}, status=404)

    talep = izinler.aktif_riza(kurum, profil)
    if talep is None:
        return Response(
            {"hata": "Bu müşteriye erişim yetkiniz yok (rıza yok, süresi dolmuş ya da iptal edilmiş)"},
            status=403,
        )
    _riza_yaz(talep, "erisim_kullanildi", request)

    from audit.models import Assessment
    son_degerlendirme = Assessment.objects.filter(profil=profil).order_by("-created_at").first()
    if son_degerlendirme is None:
        return Response({
            "aks_no": profil.aks_no, "degerlendirme_var": False,
            "not": "Bu müşteri henüz bir belge yüklememiş.",
        })

    a = son_degerlendirme
    from api import services
    risk_istahi = services.musteri_risk_istahi(a.aks_skor) if services.risk_istahi_var() else None

    return Response({
        "aks_no": profil.aks_no, "degerlendirme_var": True,
        "aks_skor": a.aks_skor, "risk_seviyesi": a.risk_seviyesi, "karar": a.karar,
        "onerilen_limit": a.onerilen_limit, "kaynak_format": a.kaynak_format,
        "sahiplik_bayraklari": a.sahiplik_bayraklari,
        "created_at": a.created_at.isoformat(timespec="seconds"),
        # §3b Phase 7/7.4: bankanın 3 risk-iştahı profilinden hangilerinde
        # bu müşteri onaylanır — persiste edilmiş eşiklerle karşılaştırma,
        # ağır hesaplama yok.
        "risk_istahi": risk_istahi,
    })
