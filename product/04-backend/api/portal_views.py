"""
Kullanıcı portalı — giriş yapmış bir son kullanıcının KENDİ ekstresini
yükleyip analiz sonucu görmesi + geçmiş yüklemelerini listelemesi
(execution.md §3b Phase 6). Banka tarafının gördüğü hiçbir veriyi/akışı
etkilemez — ayrı, `IsAuthenticated` ile korunan uç noktalar.

`csv_skorla` (anonim, `/api/csv-skorla`) ile aynı ayrıştırma mantığını
(`services.csv_ayristir`) paylaşır; tek fark, sonucun `Assessment.user`'a
bağlanması (kaynak="portal") — bu da yalnızca kullanıcının kendi "Geçmişim"
listesini besler.
"""
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services


@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def portal_yukle(request):
    dosya = request.FILES.get("dosya")
    if not dosya:
        return Response({"hata": "dosya alanı gerekli (multipart)"}, status=400)
    try:
        islemler = services.csv_ayristir(dosya)
    except ValueError as e:
        return Response({"hata": str(e)}, status=400)
    sonuc, _ = services.degerlendir(-1, islemler, kaynak="portal", user=request.user)
    return Response({
        "islem_sayisi": len(islemler), "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"], "karar": sonuc["karar"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
        "anomali_bayrak": sonuc.get("anomali_bayrak"), "anomali_skoru": sonuc.get("anomali_skoru"),
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
