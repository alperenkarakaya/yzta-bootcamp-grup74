"""
AKS FastAPI Backend
-------------------
Üç-agent mimarisini HTTP servisi + web dashboard olarak sunar.

Uç noktalar:
    GET  /                     -> web dashboard (arayüz)
    GET  /api/bilgi            -> servis bilgisi
    GET  /api/demo-musteriler  -> demo için örnek müşteri listesi
    POST /api/skorla           -> işlemlerden AKS skoru + kredi kararı
    GET  /api/skorla/{id}      -> demo müşteriyi ID ile skorla
    POST /api/aciklama         -> skorun SHAP faktör açıklaması
    POST /api/simulasyon       -> "ya şöyle olsaydı" senaryosu
    GET  /api/portfoy          -> banka portföy analizi (kurtarılan segment + getiri)
    GET  /api/gecmis/{id}      -> müşterinin geçmiş değerlendirmeleri (hafıza)

Çalıştırma:  uvicorn src.api.main:app --reload
"""
import os
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np

from src.agents.orkestrator import Orkestrator
from src.agents.asistan import AsistanAgent
from src.agents.skorlama_agent import olasilik_to_aks
from src.ozellik.cikarim import OZELLIK_ADLARI, csv_oku, tum_musteriler
from src.model.etiketleme import etiketle
from src.model.egitim import klasik_risk_skoru
from src.model.adalet import adalet_raporu

app = FastAPI(title="AKS - Alternatif Kapasite Skoru API", version="3.0")
orkestrator = Orkestrator()
asistan = AsistanAgent()

VERI_YOLU = os.environ.get("AKS_VERI", "data/sentetik_islemler.csv")
_musteri_islemleri, _persona = ({}, {})
if os.path.exists(VERI_YOLU):
    _musteri_islemleri, _persona = csv_oku(VERI_YOLU)


class Islem(BaseModel):
    tarih: str
    islem_tipi: str
    kategori: str
    tutar: float
    aciklama: Optional[str] = ""


class SkorTalebi(BaseModel):
    musteri_id: int
    islemler: List[Islem]


class AsistanTalebi(BaseModel):
    soru: str
    baglam: Optional[Dict] = None


class SimulasyonTalebi(BaseModel):
    musteri_id: int
    islemler: Optional[List[Islem]] = None
    degisiklikler: Dict[str, float]


def _islem_dict(islemler):
    return [i.model_dump() for i in islemler]


def _demo_islemler(mid: int):
    if mid not in _musteri_islemleri:
        raise HTTPException(404, f"Demo müşteri {mid} bulunamadı")
    return [dict(i) for i in _musteri_islemleri[mid]]


# ---------- Dashboard ----------
@app.get("/")
def dashboard():
    yol = "web/index.html"
    if os.path.exists(yol):
        return FileResponse(yol)
    return {"mesaj": "Dashboard bulunamadı; /docs üzerinden API'yi kullanabilirsiniz."}


# ---------- API ----------
@app.get("/api/bilgi")
def bilgi():
    return {
        "servis": "AKS - Alternatif Kapasite Skoru",
        "surum": "3.0",
        "model": orkestrator.skorlama_agent.model_adi,
        "ozellikler": OZELLIK_ADLARI,
        "demo_musteri_sayisi": len(_musteri_islemleri),
    }


@app.get("/api/demo-musteriler")
def demo_musteriler(adet_per_persona: int = 3):
    """Dashboard için her persona'dan örnek müşteriler döner."""
    ornekler = {}
    for mid, p in _persona.items():
        ornekler.setdefault(p, [])
        if len(ornekler[p]) < adet_per_persona:
            ornekler[p].append(mid)
    return ornekler


@app.get("/api/skorla/{musteri_id}")
def skorla_demo(musteri_id: int):
    islemler = _demo_islemler(musteri_id)
    sonuc = orkestrator.degerlendir(musteri_id, islemler)
    # Klasik skor kıyası için
    veri = orkestrator.veri_agent.calistir(_demo_islemler(musteri_id))
    klasik = klasik_risk_skoru({"persona": _persona[musteri_id], **veri["ozellikler"]})
    return {
        "musteri_id": musteri_id,
        "persona": _persona.get(musteri_id, "bilinmiyor"),
        "klasik_skor": klasik,
        "aks_skor": sonuc["aks_skor"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "risk_seviyesi": sonuc["risk_seviyesi"],
        "karar": sonuc["karar"],
        "ozellikler": sonuc["ozellikler"],
        "aciklama": sonuc["aciklama"],
        "danisman": sonuc["danisman"],
    }


@app.post("/api/skorla")
def skorla(talep: SkorTalebi):
    if not talep.islemler:
        raise HTTPException(400, "İşlem listesi boş olamaz")
    sonuc = orkestrator.degerlendir(talep.musteri_id, _islem_dict(talep.islemler))
    return {
        "musteri_id": talep.musteri_id,
        "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"],
        "karar": sonuc["karar"],
        "aciklama": sonuc["aciklama"],
        "danisman": sonuc["danisman"],
    }


@app.post("/api/aciklama")
def aciklama(talep: SkorTalebi):
    veri = orkestrator.veri_agent.calistir(_islem_dict(talep.islemler))
    skor = orkestrator.skorlama_agent.calistir(veri["vektor"])
    acikla = orkestrator.aciklayici.acikla(veri["vektor"])
    return {"musteri_id": talep.musteri_id, "aks_skor": skor["aks_skor"], "aciklama": acikla}


@app.post("/api/simulasyon")
def simulasyon(talep: SimulasyonTalebi):
    if talep.islemler:
        islemler = _islem_dict(talep.islemler)
    else:
        islemler = _demo_islemler(talep.musteri_id)
    veri = orkestrator.veri_agent.calistir(islemler)
    mevcut = orkestrator.skorlama_agent.calistir(veri["vektor"])
    ozellikler = dict(veri["ozellikler"])
    gecersiz = [k for k in talep.degisiklikler if k not in ozellikler]
    if gecersiz:
        raise HTTPException(400, f"Geçersiz özellik(ler): {gecersiz}")
    ozellikler.update(talep.degisiklikler)
    yeni_vektor = [ozellikler[o] for o in OZELLIK_ADLARI]
    senaryo = orkestrator.skorlama_agent.calistir(yeni_vektor)
    return {
        "musteri_id": talep.musteri_id,
        "mevcut_skor": mevcut["aks_skor"],
        "senaryo_skor": senaryo["aks_skor"],
        "skor_degisimi": senaryo["aks_skor"] - mevcut["aks_skor"],
        "uygulanan_degisiklikler": talep.degisiklikler,
        "senaryo_karar": senaryo["karar"],
    }


@app.get("/api/portfoy")
def portfoy(klasik_esik: int = 680, aks_esik: int = 650,
            ort_kredi: float = 25000, getiri_orani: float = 0.12, zarar_orani: float = 0.55):
    """Banka portföy analizi: klasik skorun reddettiği kredibl segmenti
    modelin ne kadar kurtardığı + illüstratif getiri hesabı."""
    if not _musteri_islemleri:
        raise HTTPException(503, "Demo verisi yüklü değil")
    musteriler = etiketle(tum_musteriler(VERI_YOLU), hedef_temerrut_orani=0.18)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    p = orkestrator.skorlama_agent.model.predict_proba(X)[:, 1]
    for m, pi in zip(musteriler, p):
        m["klasik_skor"] = klasik_risk_skoru(m)
        m["aks_skor"] = olasilik_to_aks(float(pi))

    red = [m for m in musteriler if m["klasik_skor"] < klasik_esik]
    kredibl = [m for m in red if m["temerrut"] == 0]
    kurtarilan = [m for m in kredibl if m["aks_skor"] >= aks_esik]
    temerrutler = [m for m in red if m["temerrut"] == 1]
    yanlis_onay = [m for m in temerrutler if m["aks_skor"] >= aks_esik]

    from collections import Counter
    kirilim = Counter(m["persona"] for m in kurtarilan)
    kazanc = len(kurtarilan) * ort_kredi * getiri_orani
    kayip = len(yanlis_onay) * ort_kredi * zarar_orani
    return {
        "toplam_musteri": len(musteriler),
        "klasik_red": len(red),
        "kredibl_red": len(kredibl),
        "kurtarilan": len(kurtarilan),
        "kurtarma_orani": round(len(kurtarilan) / max(1, len(kredibl)), 3),
        "yanlis_onay": len(yanlis_onay),
        "yanlis_onay_orani": round(len(yanlis_onay) / max(1, len(temerrutler)), 3),
        "persona_kirilimi": dict(kirilim),
        "illustratif_getiri": {
            "varsayimlar": {"ort_kredi": ort_kredi, "getiri_orani": getiri_orani, "zarar_orani": zarar_orani},
            "potansiyel_kazanc": round(kazanc), "beklenen_kayip": round(kayip), "net": round(kazanc - kayip),
        },
    }




@app.post("/api/csv-skorla")
async def csv_skorla(dosya: UploadFile = File(...)):
    """Kullanıcının kendi hesap dökümü CSV'sini skorlar.
    Beklenen kolonlar: tarih (YYYY-AA-GG), islem_tipi (gelir/gider), kategori, tutar."""
    import csv as _csv, io
    icerik = (await dosya.read()).decode("utf-8-sig")
    okuyucu = _csv.DictReader(io.StringIO(icerik))
    gerekli = {"tarih", "islem_tipi", "kategori", "tutar"}
    if not okuyucu.fieldnames or not gerekli.issubset(set(okuyucu.fieldnames)):
        raise HTTPException(400, f"CSV kolonları eksik. Gerekli: {sorted(gerekli)}")
    islemler = []
    for i, satir in enumerate(okuyucu):
        try:
            islemler.append({"tarih": satir["tarih"].strip(), "islem_tipi": satir["islem_tipi"].strip(),
                             "kategori": satir["kategori"].strip(), "tutar": float(satir["tutar"]),
                             "aciklama": satir.get("aciklama", "")})
        except (ValueError, KeyError):
            raise HTTPException(400, f"Satır {i+2} okunamadı (tutar sayısal olmalı)")
    if len(islemler) < 5:
        raise HTTPException(400, "Anlamlı skor için en az 5 işlem gerekli")
    sonuc = orkestrator.degerlendir(-1, islemler)
    return {
        "islem_sayisi": len(islemler),
        "aks_skor": sonuc["aks_skor"],
        "risk_seviyesi": sonuc["risk_seviyesi"],
        "karar": sonuc["karar"],
        "onerilen_limit": sonuc.get("onerilen_limit"),
        "aciklama": sonuc["aciklama"],
        "danisman": sonuc["danisman"],
    }


@app.get("/api/adalet")
def adalet(klasik_esik: int = 680, aks_esik: int = 650):
    """Adalet/önyargı raporu: klasik skor vs AKS için grup bazlı equal-opportunity."""
    if not _musteri_islemleri:
        raise HTTPException(503, "Demo verisi yüklü değil")
    musteriler = etiketle(tum_musteriler(VERI_YOLU), hedef_temerrut_orani=0.18)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    p = orkestrator.skorlama_agent.model.predict_proba(X)[:, 1]
    for m, pi in zip(musteriler, p):
        m["klasik_skor"] = klasik_risk_skoru(m)
        m["aks_skor"] = olasilik_to_aks(float(pi))
    return adalet_raporu(musteriler, {"klasik_skor": klasik_esik, "aks_skor": aks_esik})




@app.post("/api/asistan")
def asistan_yanit(talep: AsistanTalebi):
    baglam = talep.baglam or {}
    return asistan.yanitla(talep.soru, baglam)


@app.get("/api/gecmis/{musteri_id}")
def gecmis(musteri_id: int):
    kayitlar = orkestrator.gecmis(musteri_id)
    return {
        "musteri_id": musteri_id,
        "degerlendirme_sayisi": len(kayitlar),
        "gecmis": [{"zaman": k["zaman"], "aks_skor": k["aks_skor"], "risk_seviyesi": k["risk_seviyesi"]} for k in kayitlar],
    }
