"""
Servis katmanı — aks_core'u Django'ya bağlar.

- Orkestrator + AsistanAgent tekil (singleton) örnekleri
- Demo veri yüklemesi (01-data/datasets)
- portföy / adalet hesapları (eski FastAPI main.py'den taşındı)
- Her skorlamadan sonra DEĞİŞTİRİLEMEZ denetim kaydı yazımı (boundary hikâyesi)
"""
from collections import Counter

import numpy as np
from django.core.cache import cache

from aks_core import paths
from aks_core.agents.orkestrator import Orkestrator
from aks_core.agents.asistan import AsistanAgent
from aks_core.agents.skorlama_agent import olasilik_to_aks
from aks_core.ozellik.cikarim import OZELLIK_ADLARI, csv_oku, tum_musteriler
from aks_core.model.etiketleme import etiketle
from aks_core.model.egitim import klasik_risk_skoru
from aks_core.model.adalet import adalet_raporu

# --- Tekil çekirdek nesneleri (model bir kez yüklensin) ---
orkestrator = Orkestrator()
asistan = AsistanAgent()

VERI_YOLU = paths.data("sentetik_islemler.csv")
try:
    _musteri_islemleri, _persona = csv_oku(VERI_YOLU)
except FileNotFoundError:
    _musteri_islemleri, _persona = {}, {}


def demo_islemler(mid):
    if mid not in _musteri_islemleri:
        return None
    return [dict(i) for i in _musteri_islemleri[mid]]


def demo_var():
    return bool(_musteri_islemleri)


def demo_personalar(adet_per_persona=3):
    ornekler = {}
    for mid, p in _persona.items():
        ornekler.setdefault(p, [])
        if len(ornekler[p]) < adet_per_persona:
            ornekler[p].append(mid)
    return ornekler


def bilgi():
    return {
        "servis": "AKS - Alternatif Kapasite Skoru",
        "surum": "3.0-django",
        "model": orkestrator.skorlama_agent.model_adi,
        "ozellikler": OZELLIK_ADLARI,
        "demo_musteri_sayisi": len(_musteri_islemleri),
    }


def degerlendir(musteri_id, islemler, kaynak="api", persona=""):
    """aks_core ile skorla + denetim izi yaz."""
    sonuc = orkestrator.degerlendir(musteri_id, islemler)
    klasik = None
    if persona:
        veri = orkestrator.veri_agent.calistir(islemler)
        klasik = klasik_risk_skoru({"persona": persona, **veri["ozellikler"]})
    _denetim_yaz(musteri_id, klasik, sonuc, kaynak)
    return sonuc, klasik


def _denetim_yaz(musteri_id, klasik, sonuc, kaynak):
    """Best-effort: denetim yazımı skorlamayı asla düşürmemeli."""
    try:
        from audit.models import AuditLog, Assessment, Customer
        cust = None
        if kaynak == "demo":
            cust, _ = Customer.objects.get_or_create(
                external_id=str(musteri_id),
                defaults={"persona": _persona.get(musteri_id, "")},
            )
        Assessment.objects.create(
            customer=cust, musteri_id=str(musteri_id), klasik_skor=klasik,
            aks_skor=sonuc["aks_skor"], risk_seviyesi=sonuc["risk_seviyesi"],
            karar=sonuc["karar"], onerilen_limit=sonuc.get("onerilen_limit"),
            ozellikler=sonuc.get("ozellikler", {}), kaynak=kaynak,
        )
        AuditLog.objects.create(
            musteri_id=str(musteri_id), klasik_skor=klasik, aks_skor=sonuc["aks_skor"],
            karar=sonuc["karar"], onerilen_limit=sonuc.get("onerilen_limit"),
            ajanlar=sonuc.get("kullanilan_agentlar", []), kaynak=kaynak,
        )
    except Exception:  # tablo yoksa / DB yoksa demo yine çalışsın
        pass


def gecmis(musteri_id):
    """DB'den (kalıcı) geçmiş; yoksa orkestratör hafızasına düş."""
    try:
        from audit.models import Assessment
        qs = Assessment.objects.filter(musteri_id=str(musteri_id)).order_by("created_at")
        if qs.exists():
            return [{"zaman": a.created_at.isoformat(timespec="seconds"),
                     "aks_skor": a.aks_skor, "risk_seviyesi": a.risk_seviyesi} for a in qs]
    except Exception:
        pass
    return [{"zaman": k["zaman"], "aks_skor": k["aks_skor"], "risk_seviyesi": k["risk_seviyesi"]}
            for k in orkestrator.gecmis(musteri_id)]


def _skorla_hepsi():
    musteriler = etiketle(tum_musteriler(VERI_YOLU), hedef_temerrut_orani=0.18)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    p = orkestrator.skorlama_agent.model.predict_proba(X)[:, 1]
    for m, pi in zip(musteriler, p):
        m["klasik_skor"] = klasik_risk_skoru(m)
        m["aks_skor"] = olasilik_to_aks(float(pi))
    return musteriler


def portfoy(klasik_esik=680, aks_esik=650, ort_kredi=25000, getiri_orani=0.12, zarar_orani=0.55):
    key = f"portfoy:{klasik_esik}:{aks_esik}:{ort_kredi}:{getiri_orani}:{zarar_orani}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    musteriler = _skorla_hepsi()
    red = [m for m in musteriler if m["klasik_skor"] < klasik_esik]
    kredibl = [m for m in red if m["temerrut"] == 0]
    kurtarilan = [m for m in kredibl if m["aks_skor"] >= aks_esik]
    temerrutler = [m for m in red if m["temerrut"] == 1]
    yanlis_onay = [m for m in temerrutler if m["aks_skor"] >= aks_esik]
    kirilim = Counter(m["persona"] for m in kurtarilan)
    kazanc = len(kurtarilan) * ort_kredi * getiri_orani
    kayip = len(yanlis_onay) * ort_kredi * zarar_orani
    sonuc = {
        "toplam_musteri": len(musteriler), "klasik_red": len(red), "kredibl_red": len(kredibl),
        "kurtarilan": len(kurtarilan), "kurtarma_orani": round(len(kurtarilan) / max(1, len(kredibl)), 3),
        "yanlis_onay": len(yanlis_onay), "yanlis_onay_orani": round(len(yanlis_onay) / max(1, len(temerrutler)), 3),
        "persona_kirilimi": dict(kirilim),
        "illustratif_getiri": {
            "varsayimlar": {"ort_kredi": ort_kredi, "getiri_orani": getiri_orani, "zarar_orani": zarar_orani},
            "potansiyel_kazanc": round(kazanc), "beklenen_kayip": round(kayip), "net": round(kazanc - kayip),
        },
    }
    cache.set(key, sonuc, timeout=600)
    return sonuc


def adalet(klasik_esik=680, aks_esik=650):
    key = f"adalet:{klasik_esik}:{aks_esik}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    musteriler = _skorla_hepsi()
    sonuc = adalet_raporu(musteriler, {"klasik_skor": klasik_esik, "aks_skor": aks_esik})
    cache.set(key, sonuc, timeout=600)
    return sonuc


def asistan_yanit(soru, baglam):
    return asistan.yanitla(soru, baglam or {})
