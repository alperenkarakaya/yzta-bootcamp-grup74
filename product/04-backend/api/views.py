"""DRF görünümleri — eski FastAPI uç noktalarının bire bir karşılığı."""
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from aks_core.ozellik.cikarim import OZELLIK_ADLARI
from . import services


def _int(params, ad, varsayilan):
    try:
        return int(params.get(ad, varsayilan))
    except (TypeError, ValueError):
        return varsayilan


def _float(params, ad, varsayilan):
    try:
        return float(params.get(ad, varsayilan))
    except (TypeError, ValueError):
        return varsayilan


@api_view(["GET"])
def bilgi(request):
    return Response(services.bilgi())


@api_view(["GET"])
def metrikler(request):
    """§3b/U15: degerlendirme.py'nin (U6) persist ettiği CV+CI+kalibrasyon+alt-grup raporu."""
    if not services.metrikler_var():
        return Response({"hata": "Henüz üretilmedi — python -m aks_core.model.degerlendirme çalıştırın"}, status=503)
    return Response(services.metrikler())


@api_view(["GET"])
def politika(request):
    """§3b/U16: karar mekanizması politikası (skor bantları + limit çarpanları)."""
    return Response(services.politika())


@api_view(["GET"])
def segmentasyon(request):
    """§3b/U26: segmentasyon.py'nin (denetimsiz K-Means keşif) persist ettiği rapor."""
    if not services.segmentasyon_var():
        return Response({"hata": "Henüz üretilmedi — python -m aks_core.model.segmentasyon çalıştırın"}, status=503)
    return Response(services.segmentasyon())


@api_view(["GET"])
def genelleme_saglamlik(request):
    """§4 R8/R10/R11: persona-dışı genelleme, ince dosya stres testi, oyunlanabilirlik duyarlılığı."""
    if not services.genelleme_saglamlik_var():
        return Response({"hata": "Henüz üretilmedi — python -m aks_core.model.genelleme_saglamlik çalıştırın"}, status=503)
    return Response(services.genelleme_saglamlik())


@api_view(["GET"])
def risk_istahi(request):
    """§3b Phase 7/7.4: risk_istahi.py'nin persist ettiği 3 profil (ihtiyatli/
    dengeli/atak) raporu — hedef kötü oranına göre seçilmiş eşikler + CI."""
    if not services.risk_istahi_var():
        return Response({"hata": "Henüz üretilmedi — python -m aks_core.model.risk_istahi çalıştırın"}, status=503)
    return Response(services.risk_istahi())


@api_view(["GET"])
def demo_musteriler(request):
    return Response(services.demo_personalar(_int(request.query_params, "adet_per_persona", 3)))


@api_view(["GET"])
def skorla_demo(request, musteri_id: int):
    islemler = services.demo_islemler(musteri_id)
    if islemler is None:
        return Response({"hata": f"Demo müşteri {musteri_id} bulunamadı"}, status=404)
    persona = services._persona.get(musteri_id, "")
    sonuc, klasik = services.degerlendir(musteri_id, islemler, kaynak="demo", persona=persona)
    return Response({
        "musteri_id": musteri_id, "persona": persona or "bilinmiyor",
        "klasik_skor": klasik, "aks_skor": sonuc["aks_skor"],
        "onerilen_limit": sonuc.get("onerilen_limit"), "risk_seviyesi": sonuc["risk_seviyesi"],
        "karar": sonuc["karar"], "ozellikler": sonuc["ozellikler"],
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
        "pd_geleneksel_bant": sonuc.get("pd_geleneksel_bant"),
        "pd_fark": sonuc.get("pd_fark"),
        "kapasite_sinyali": sonuc.get("kapasite_sinyali"),
        "anomali_bayrak": sonuc.get("anomali_bayrak"),
        "anomali_skoru": sonuc.get("anomali_skoru"),
    })


@api_view(["POST"])
def skorla(request):
    islemler = request.data.get("islemler") or []
    if not islemler:
        return Response({"hata": "İşlem listesi boş olamaz"}, status=400)
    mid = request.data.get("musteri_id")
    sonuc, _ = services.degerlendir(mid, islemler, kaynak="api")
    return Response({
        "musteri_id": mid, "aks_skor": sonuc["aks_skor"], "risk_seviyesi": sonuc["risk_seviyesi"],
        "karar": sonuc["karar"], "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
        "anomali_bayrak": sonuc.get("anomali_bayrak"), "anomali_skoru": sonuc.get("anomali_skoru"),
    })


@api_view(["POST"])
def aciklama(request):
    islemler = request.data.get("islemler") or []
    if not islemler:
        return Response({"hata": "İşlem listesi boş olamaz"}, status=400)
    veri = services.orkestrator.veri_agent.calistir(islemler)
    skor = services.orkestrator.skorlama_agent.calistir(veri["vektor"])
    acikla = services.orkestrator.aciklayici.acikla(veri["vektor"])
    return Response({"musteri_id": request.data.get("musteri_id"),
                     "aks_skor": skor["aks_skor"], "aciklama": acikla})


@api_view(["POST"])
def simulasyon(request):
    mid = request.data.get("musteri_id")
    islemler = request.data.get("islemler")
    if not islemler:
        islemler = services.demo_islemler(mid)
        if islemler is None:
            return Response({"hata": f"Demo müşteri {mid} bulunamadı"}, status=404)
    degisiklikler = request.data.get("degisiklikler") or {}
    veri = services.orkestrator.veri_agent.calistir(islemler)
    mevcut = services.orkestrator.skorlama_agent.calistir(veri["vektor"])
    ozellikler = dict(veri["ozellikler"])
    gecersiz = [k for k in degisiklikler if k not in ozellikler]
    if gecersiz:
        return Response({"hata": f"Geçersiz özellik(ler): {gecersiz}"}, status=400)
    ozellikler.update(degisiklikler)
    yeni_vektor = [ozellikler[o] for o in OZELLIK_ADLARI]
    senaryo = services.orkestrator.skorlama_agent.calistir(yeni_vektor)
    return Response({
        "musteri_id": mid, "mevcut_skor": mevcut["aks_skor"], "senaryo_skor": senaryo["aks_skor"],
        "skor_degisimi": senaryo["aks_skor"] - mevcut["aks_skor"],
        "uygulanan_degisiklikler": degisiklikler, "senaryo_karar": senaryo["karar"],
    })


@api_view(["GET"])
def portfoy(request):
    if not services.demo_var():
        return Response({"hata": "Demo verisi yüklü değil"}, status=503)
    q = request.query_params
    varsayilan = services.PORTFOY_ESIK_VARSAYILAN
    return Response(services.portfoy(
        klasik_esik=_int(q, "klasik_esik", varsayilan["klasik_esik"]),
        aks_esik=_int(q, "aks_esik", varsayilan["aks_esik"]),
        ort_kredi=_float(q, "ort_kredi", 25000), getiri_orani=_float(q, "getiri_orani", 0.12),
        zarar_orani=_float(q, "zarar_orani", 0.55)))


@api_view(["GET"])
def adalet(request):
    if not services.demo_var():
        return Response({"hata": "Demo verisi yüklü değil"}, status=503)
    q = request.query_params
    varsayilan = services.PORTFOY_ESIK_VARSAYILAN
    return Response(services.adalet(klasik_esik=_int(q, "klasik_esik", varsayilan["klasik_esik"]),
                                    aks_esik=_int(q, "aks_esik", varsayilan["aks_esik"])))


@api_view(["POST"])
@parser_classes([MultiPartParser])
def csv_skorla(request):
    """§3b Phase 7 / 7.1: adı tarihsel nedenlerle "csv_skorla" (URL/frontend geriye
    dönük uyumluluğu) ama artık CSV/XLSX/PDF'in üçünü de kabul eder — format
    tespiti `aks_core.belge.okuyucu.ayristir()`'de uzantıya göre yapılır."""
    from aks_core.belge.hatalar import BelgeHatasi
    dosya = request.FILES.get("dosya")
    if not dosya:
        return Response({"hata": "dosya alanı gerekli (multipart)"}, status=400)
    try:
        islemler, meta = services.belge_ayristir(dosya)
    except BelgeHatasi as e:
        return Response({"hata": str(e)}, status=400)
    sonuc, _ = services.degerlendir(-1, islemler, kaynak="csv", belge_meta=meta)
    return Response({
        "islem_sayisi": len(islemler), "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"], "karar": sonuc["karar"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
        "anomali_bayrak": sonuc.get("anomali_bayrak"), "anomali_skoru": sonuc.get("anomali_skoru"),
        "belge_meta": meta,
    })


@api_view(["POST"])
def asistan(request):
    return Response(services.asistan_yanit(request.data.get("soru", ""), request.data.get("baglam")))


@api_view(["GET"])
def gecmis(request, musteri_id: int):
    kayitlar = services.gecmis(musteri_id)
    return Response({"musteri_id": musteri_id, "degerlendirme_sayisi": len(kayitlar), "gecmis": kayitlar})
