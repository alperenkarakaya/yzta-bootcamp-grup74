"""
Kullanıcı portalı — giriş yapmış bir son kullanıcının KENDİ ekstresini
(CSV/XLSX/PDF) yükleyip analiz sonucu görmesi + geçmiş yüklemelerini
listelemesi (execution.md §3b Phase 6/7). Banka tarafının gördüğü hiçbir
veriyi/akışı etkilemez — ayrı, `IsAuthenticated` ile korunan uç noktalar.

`csv_skorla` (anonim, `/api/csv-skorla`) ile aynı ayrıştırma mantığını
(`services.belge_ayristir`) paylaşır; tek fark, sonucun `Assessment.user`'a
bağlanması (kaynak="portal") — bu da yalnızca kullanıcının kendi "Geçmişim"
listesini besler. Sahiplik-çakışma tespiti (parmak izi) §7.3'te eklenecek.
"""
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services


def _dogru_mu(deger):
    return str(deger).strip().lower() in ("true", "1", "on", "evet")


@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def portal_yukle(request):
    """§3b Phase 7/7.3: `beyan` alanı ZORUNLU — "bu ekstre bana ait" onayı
    olmadan yükleme kabul edilmez (sahiplik savunmasının 3. katmanı; diğer
    ikisi — parmak izi çakışması + davranışsal tutarlılık — `services.degerlendir`
    içinde otomatik çalışır, bkz. `api/sahiplik.py`)."""
    from aks_core.belge.hatalar import BelgeHatasi
    dosya = request.FILES.get("dosya")
    if not dosya:
        return Response({"hata": "dosya alanı gerekli (multipart)"}, status=400)
    if not _dogru_mu(request.data.get("beyan")):
        return Response({"hata": "Bu ekstrenin size ait olduğunu onaylamanız gerekiyor"}, status=400)
    try:
        islemler, meta = services.belge_ayristir(dosya)
    except BelgeHatasi as e:
        return Response({"hata": str(e)}, status=400)
    sonuc, _ = services.degerlendir(
        -1, islemler, kaynak="portal", user=request.user, belge_meta=meta,
        sahiplik_beyani=True, ip=request.META.get("REMOTE_ADDR"),
    )
    return Response({
        "islem_sayisi": len(islemler), "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"], "karar": sonuc["karar"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
        "anomali_bayrak": sonuc.get("anomali_bayrak"), "anomali_skoru": sonuc.get("anomali_skoru"),
        "sahiplik_bayraklari": sonuc.get("sahiplik_bayraklari", []),
        "belge_meta": meta,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def portal_gecmis(request):
    from audit.models import Assessment
    kayitlar = Assessment.objects.filter(user=request.user).order_by("-created_at")[:50]
    return Response({
        "gecmis": [
            {
                "id": a.id,
                "zaman": a.created_at.isoformat(timespec="seconds"),
                "aks_skor": a.aks_skor,
                "risk_seviyesi": a.risk_seviyesi,
                "karar": a.karar,
                "onerilen_limit": a.onerilen_limit,
            }
            for a in kayitlar
        ]
    })
