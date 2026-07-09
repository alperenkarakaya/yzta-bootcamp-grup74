"""DRF görünümleri — eski FastAPI uç noktalarının bire bir karşılığı."""
import csv as _csv
import io

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
    return Response(services.portfoy(
        klasik_esik=_int(q, "klasik_esik", 680), aks_esik=_int(q, "aks_esik", 650),
        ort_kredi=_float(q, "ort_kredi", 25000), getiri_orani=_float(q, "getiri_orani", 0.12),
        zarar_orani=_float(q, "zarar_orani", 0.55)))


@api_view(["GET"])
def adalet(request):
    if not services.demo_var():
        return Response({"hata": "Demo verisi yüklü değil"}, status=503)
    q = request.query_params
    return Response(services.adalet(klasik_esik=_int(q, "klasik_esik", 680),
                                    aks_esik=_int(q, "aks_esik", 650)))


@api_view(["POST"])
@parser_classes([MultiPartParser])
def csv_skorla(request):
    dosya = request.FILES.get("dosya")
    if not dosya:
        return Response({"hata": "dosya alanı gerekli (multipart)"}, status=400)
    icerik = dosya.read().decode("utf-8-sig")
    okuyucu = _csv.DictReader(io.StringIO(icerik))
    gerekli = {"tarih", "islem_tipi", "kategori", "tutar"}
    if not okuyucu.fieldnames or not gerekli.issubset(set(okuyucu.fieldnames)):
        return Response({"hata": f"CSV kolonları eksik. Gerekli: {sorted(gerekli)}"}, status=400)
    islemler = []
    for i, satir in enumerate(okuyucu):
        try:
            islemler.append({"tarih": satir["tarih"].strip(), "islem_tipi": satir["islem_tipi"].strip(),
                             "kategori": satir["kategori"].strip(), "tutar": float(satir["tutar"]),
                             "aciklama": satir.get("aciklama", "")})
        except (ValueError, KeyError):
            return Response({"hata": f"Satır {i+2} okunamadı (tutar sayısal olmalı)"}, status=400)
    if len(islemler) < 5:
        return Response({"hata": "Anlamlı skor için en az 5 işlem gerekli"}, status=400)
    sonuc, _ = services.degerlendir(-1, islemler, kaynak="csv")
    return Response({
        "islem_sayisi": len(islemler), "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"], "karar": sonuc["karar"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"], "danisman": sonuc["danisman"],
    })


@api_view(["POST"])
def asistan(request):
    return Response(services.asistan_yanit(request.data.get("soru", ""), request.data.get("baglam")))


@api_view(["GET"])
def gecmis(request, musteri_id: int):
    kayitlar = services.gecmis(musteri_id)
    return Response({"musteri_id": musteri_id, "degerlendirme_sayisi": len(kayitlar), "gecmis": kayitlar})
