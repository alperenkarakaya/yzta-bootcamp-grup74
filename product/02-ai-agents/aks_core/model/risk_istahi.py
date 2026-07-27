"""
Risk İştahı — 3 Seviyeli Banka Önerisi (execution.md §3b Phase 7 / 7.4)
--------------------------------------------------------------------------
"Bankalara minimum riskten yükseğe doğru 3 farklı seviyede öneri" (PO isteği).
Bantlar KEYFİ bir skor kesimiyle değil, HEDEF KÖTÜ ORANIYLA tanımlanır — her
banka kendi risk iştahına göre onay eşiğini seçer, AKS bunu ölçüp önerir:

    ihtiyatli (risksiz) — hedef kötü oran ≤ %3
    dengeli   (orta)    — hedef kötü oran ≤ %6
    atak      (riskli)  — hedef kötü oran ≤ %10

Yöntem: `egitim.py::egit()`'in AYNI train/test bölmesi (seed=42, test_size=0.25,
stratify=y) yeniden üretilir — bu, modelin train sırasında HİÇ görmediği,
gerçek bir held-out küme. Döngüsel `sentetik_islemler.csv` KULLANILMAZ; yalnızca
dekuple (`kapasite_islemler.csv` + `kapasite_etiketleri.csv`) veri kaynağı.

Her aday AKS eşiği için onay oranı, gerçekleşen kötü oran, beklenen kâr/zarar
(`is_etkisi.py` ile AYNI illüstratif varsayımlar: ort_kredi=25000,
getiri_orani=0.12, zarar_orani=0.55) hesaplanır; her profil için, kötü oran
hedefini AŞMAYAN eşikler arasından beklenen net kârı maksimize eden eşik
seçilir. Bootstrap %95 CI ile raporlanır (`degerlendirme.py::_bootstrap_ci`
ile aynı yöntem).

Dürüstlük şerhi (`_METRIK_UYARISI` ile aynı ruh, `api/services.py`): bu rapor
sentetik/dekuple veri üzerinde, OUT-OF-SAMPLE (held-out) ama sentetik bir
benchmarkta üretildi — gerçek veri (OQ-36) olmadan "doğrulanmış" diye
alıntılanmamalı.
"""
import json
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split

from aks_core import paths
from aks_core.agents.skorlama_agent import olasilik_to_aks
from aks_core.model import kayit
from aks_core.model.egitim import VERI_KAYNAKLARI, klasik_risk_skoru, veri_hazirla
from aks_core.ozellik.cikarim import OZELLIK_ADLARI

RAPOR_ADI = "risk_istahi_raporu.json"

PROFILLER = {
    "ihtiyatli": {"ad": "İhtiyatlı (risksiz)", "hedef_kotu_oran": 0.03},
    "dengeli":   {"ad": "Dengeli (orta risk)", "hedef_kotu_oran": 0.06},
    "atak":      {"ad": "Atak (riskli)",       "hedef_kotu_oran": 0.10},
}

# is_etkisi.py ile AYNI illüstratif varsayımlar — iki bağımsız modülün aynı
# senaryo üstünden konuşması, sayıların keyfi seçilmediğinin bir göstergesi.
ORT_KREDI = 25000
GETIRI_ORANI = 0.12
ZARAR_ORANI = 0.55

ESIK_ARALIGI = list(range(300, 851, 5))


def _bootstrap_ci(degerler, n_boot=1000, seed=42, alpha=0.05):
    degerler = np.asarray(degerler, dtype=float)
    if len(degerler) == 0:
        return None
    rng = np.random.default_rng(seed)
    boot = [degerler[rng.integers(0, len(degerler), len(degerler))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"ortalama": round(float(degerler.mean()), 4), "ci95": [round(float(lo), 4), round(float(hi), 4)]}


def _esik_degerlendir(aks_skorlar, y, esik):
    onaylanan = aks_skorlar >= esik
    n_onay = int(onaylanan.sum())
    if n_onay == 0:
        return {"esik": esik, "onay_orani": 0.0, "kotu_oran": None, "n_onay": 0, "net_kar": 0.0}
    iyi = onaylanan & (y == 0)
    kotu = onaylanan & (y == 1)
    kazanc = int(iyi.sum()) * ORT_KREDI * GETIRI_ORANI
    kayip = int(kotu.sum()) * ORT_KREDI * ZARAR_ORANI
    return {
        "esik": esik,
        "onay_orani": round(n_onay / len(aks_skorlar), 4),
        "kotu_oran": round(float(y[onaylanan].mean()), 4),
        "n_onay": n_onay,
        "net_kar": round(kazanc - kayip, 2),
    }


def _profil_esigi_sec(taramalar, hedef_kotu_oran):
    """Kötü oranı hedefi AŞMAYAN eşikler arasından net kârı maksimize edeni seçer.
    Hiçbir eşik hedefi sağlamıyorsa (çok agresif bir hedef) en düşük kötü oranlı
    eşiğe düşer — sessizce boş dönmek yerine dürüst bir `uyari` alanı taşır."""
    uygunlar = [t for t in taramalar if t["kotu_oran"] is not None and t["kotu_oran"] <= hedef_kotu_oran]
    if uygunlar:
        return max(uygunlar, key=lambda t: t["net_kar"]), None
    en_dusuk_kotu = min((t for t in taramalar if t["kotu_oran"] is not None), key=lambda t: t["kotu_oran"])
    return en_dusuk_kotu, (
        f"Hiçbir eşik hedef kötü oranı (%{hedef_kotu_oran*100:.0f}) sağlamadı — "
        f"en düşük ulaşılabilir kötü oranlı eşik (%{en_dusuk_kotu['kotu_oran']*100:.1f}) kullanıldı."
    )


def hesapla(veri_kaynagi="dekuple", seed=42):
    if veri_kaynagi != "dekuple":
        raise ValueError(
            "risk_istahi yalnızca 'dekuple' veri kaynağıyla çalışır — döngüsel "
            "veri üzerinde bir 'kötü oran hedefi' anlamsız olurdu (bkz. modül docstring'i)."
        )
    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"])
    musteriler = veri_hazirla(islem_csv, veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)

    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    y = np.array([m["temerrut"] for m in musteriler])

    # egitim.py::egit() ile AYNI bölme — modelin train sırasında görmediği,
    # gerçek held-out küme (bkz. modül docstring'i: sızıntı yok).
    _Xtr, Xte, _ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)

    model, model_adi, ozellikler = kayit.yukle()
    p_test = model.predict_proba(Xte)[:, 1]
    aks_skorlar = np.array([olasilik_to_aks(float(p)) for p in p_test])

    taramalar = [_esik_degerlendir(aks_skorlar, yte, esik) for esik in ESIK_ARALIGI]

    profil_sonuclari = {}
    for anahtar, tanim in PROFILLER.items():
        secilen, uyari = _profil_esigi_sec(taramalar, tanim["hedef_kotu_oran"])
        esik = secilen["esik"]
        onaylanan_mask = aks_skorlar >= esik
        onay_orani_ci = _bootstrap_ci((onaylanan_mask).astype(float), seed=seed)
        kotu_oran_ci = (
            _bootstrap_ci(yte[onaylanan_mask].astype(float), seed=seed) if onaylanan_mask.sum() > 0 else None
        )
        profil_sonuclari[anahtar] = {
            "ad": tanim["ad"],
            "hedef_kotu_oran": tanim["hedef_kotu_oran"],
            "secilen_esik": esik,
            "gerceklesen_kotu_oran": secilen["kotu_oran"],
            "gerceklesen_kotu_oran_ci95": kotu_oran_ci["ci95"] if kotu_oran_ci else None,
            "onay_orani": secilen["onay_orani"],
            "onay_orani_ci95": onay_orani_ci["ci95"] if onay_orani_ci else None,
            "n_onay": secilen["n_onay"],
            "n_test": int(len(yte)),
            "beklenen_net_kar": secilen["net_kar"],
            "uyari": uyari,
        }

    return {
        "profiller": profil_sonuclari,
        "varsayimlar": {"ort_kredi": ORT_KREDI, "getiri_orani": GETIRI_ORANI, "zarar_orani": ZARAR_ORANI},
        "n_test": int(len(yte)),
        "model_adi_referans": model_adi,
    }


def musteri_risk_istahi(aks_skor, rapor=None):
    """Verilen bir AKS skorunun 3 profilden hangilerinde onaylanacağını döner.
    `rapor` verilmezse `raporu_yukle()` ile diskteki son rapor okunur — ağır
    hesaplama TEKRARLANMAZ, yalnızca persiste edilmiş eşiklerle karşılaştırma
    yapılır (`kurum_views.py`'nin canlı istekte kullandığı yol)."""
    rapor = rapor or raporu_yukle()
    sonuc = {}
    for anahtar, veri in rapor["profiller"].items():
        sonuc[anahtar] = {
            "ad": veri["ad"], "onaylanir_mi": aks_skor >= veri["secilen_esik"],
            "esik": veri["secilen_esik"],
        }
    return sonuc


def kaydet(rapor, dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / RAPOR_ADI
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    return str(yol)


def raporu_yukle(dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / RAPOR_ADI
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def rapor_uret(veri_kaynagi="dekuple", seed=42, dosya_yolu=None):
    t0 = time.time()
    rapor = hesapla(veri_kaynagi=veri_kaynagi, seed=seed)
    rapor["zaman"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    rapor["veri_kaynagi"] = veri_kaynagi
    rapor["sure_sn"] = round(time.time() - t0, 1)
    rapor["uyari"] = (
        "Bu profiller sentetik/dekuple veri üzerinde, held-out (out-of-sample) ama sentetik bir "
        "benchmarkta üretildi. Gerçek veri doğrulaması olmadan 'nihai/doğrulanmış banka politikası' "
        "olarak alıntılanmamalı."
    )
    kaydet(rapor, dosya_yolu)
    return rapor


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--veri-kaynagi", default="dekuple", choices=["dekuple"])
    a = p.parse_args()
    r = rapor_uret(veri_kaynagi=a.veri_kaynagi)

    print(f"\n=== Risk İştahı Profilleri ({r['sure_sn']}s, n_test={r['n_test']}) ===")
    for anahtar, veri in r["profiller"].items():
        print(f"\n[{veri['ad']}] hedef kötü oran <= %{veri['hedef_kotu_oran']*100:.0f}")
        print(f"  Seçilen eşik: {veri['secilen_esik']}")
        print(f"  Gerçekleşen kötü oran: %{(veri['gerceklesen_kotu_oran'] or 0)*100:.1f} "
              f"(CI95 {veri['gerceklesen_kotu_oran_ci95']})")
        print(f"  Onay oranı: %{veri['onay_orani']*100:.1f} (CI95 {veri['onay_orani_ci95']}, n_onay={veri['n_onay']})")
        print(f"  Beklenen net kâr (bu örneklem): {veri['beklenen_net_kar']:,.0f} TL")
        if veri["uyari"]:
            print(f"  UYARI: {veri['uyari']}")
