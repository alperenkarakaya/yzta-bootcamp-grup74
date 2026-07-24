"""
Genelleme & Sağlamlık Testleri (R8, R10, R11 — execution.md §4)
------------------------------------------------------------------
Bağlayıcı öncelik sırası (overview.md §5): P1 doğruluk > **P2 genelleme**
> P3 kalibrasyon > **P4 sağlamlık** > ... Bu modül, mevcut CV/bootstrap
değerlendirmesinin (`degerlendirme.py`, rastgele k-fold — hâlâ AYNI
dağılımdan örnekliyor) YAPAMADIĞI iki soruyu sorar:

1. **R8 — Persona-dışı genelleme:** model HİÇ görmediği bir davranış
   profiline genelleşiyor mu? (rastgele k-fold bunu asla test edemez,
   her katmanda her personadan örnek var.)
2. **R10 — İnce dosya stres testi:** işlem geçmişi kısaldıkça (yeni/az
   işlemli müşteri) skor ZARİFÇE mi kararsızlaşıyor, yoksa GÜVENLE mi
   yanılıyor? Anomali dedektörünün (anomali.py, §5.4) bunu doğru
   yakalayıp yakalamadığı da ayrıca ölçülür — iki bileşen birbirini
   doğrulamalı.
3. **R11 — Oyunlanabilirlik duyarlılığı:** 4 nedensel özellikten (gider_
   gelir_orani, bakiye_trendi, gelir_duzenliligi, fatura_odeme_duzeni)
   hangisi, sabit bir davranış değişikliği karşılığında en fazla skor
   kazandırıyor? RQ-3'e (architecture.md §7) ilk niceliksel cevap.

**R8'in "out-of-time" kısmı bu veri setinde YAPILMADI, atlanmadı:**
`kapasite_islemler.csv`'deki her müşterinin işlemleri aynı 6 aylık
pencereye (2026-01-01 — 2026-06-29) yayılmış — üretici zamana bağlı bir
kayma (concept drift) simüle etmiyor. Müşterileri "erken" / "geç" diye
ayırmak, üretici rastgeleliğini ölçmekten başka bir şey olmaz; gerçek bir
out-of-time testi gerçek veri gerektirir (OQ-36). Sahte bir sonuç
üretmektense bunu raporun içinde açıkça `not` alanı olarak belgeliyoruz —
"no-go is a valid outcome" ilkesi.

Hiçbiri agent değildir (beş-soru testi) — `degerlendirme.py`/`is_etkisi.py`
ile aynı kategoride, deterministik araştırma betikleri.
"""
import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from aks_core import paths
from aks_core.model import anomali
from aks_core.agents.skorlama_agent import olasilik_to_aks
from aks_core.ozellik.cikarim import OZELLIK_ADLARI, ozellik_cikar

RAPOR_ADI = "genelleme_saglamlik_raporu.json"

NEDENSEL_OZELLIKLER = ["gider_gelir_orani", "bakiye_trendi", "gelir_duzenliligi", "fatura_odeme_duzeni"]
# +1: özelliği ARTIRMAK riski azaltır: -1: özelliği AZALTMAK riski azaltır
IYILESTIRME_YONU = {"gider_gelir_orani": -1, "bakiye_trendi": 1, "gelir_duzenliligi": 1, "fatura_odeme_duzeni": 1}
# Gerçekçi kırpma sınırları (aynı özellik zaten [0,1] veya benzeri sınırlı ise clip edilir)
OZELLIK_SINIRLARI = {"gelir_duzenliligi": (0.0, 1.0), "fatura_odeme_duzeni": (0.0, 1.0), "gider_gelir_orani": (0.05, None)}


def persona_disi_genelleme(musteriler, X, y, seed=42, lr_C=1.0):
    """R8a: her persona sırayla TAMAMEN test setine ayrılır, kalan personalarla
    eğitilir. Rastgele k-fold'un asla test edemediği soru: model hiç görmediği
    bir davranış profiline genelleşiyor mu?"""
    personalar = sorted(set(m["persona"] for m in musteriler))
    sonuc = {}
    for p in personalar:
        test_idx = np.array([i for i, m in enumerate(musteriler) if m["persona"] == p])
        train_idx = np.array([i for i, m in enumerate(musteriler) if m["persona"] != p])
        if len(set(y[test_idx].tolist())) < 2:
            sonuc[p] = {"n_test": int(len(test_idx)), "auc": None, "not": "test setinde tek sınıf, AUC tanımsız"}
            continue
        sc = StandardScaler().fit(X[train_idx])
        model = LogisticRegression(max_iter=2000, C=lr_C).fit(sc.transform(X[train_idx]), y[train_idx])
        p_test = model.predict_proba(sc.transform(X[test_idx]))[:, 1]
        sonuc[p] = {
            "n_test": int(len(test_idx)),
            "n_train": int(len(train_idx)),
            "auc": round(float(roc_auc_score(y[test_idx], p_test)), 4),
        }
    return sonuc


def ince_dosya_stres_testi(musteri_islem_map, model, anomali_model,
                            kesme_noktalari=(5, 8, 12, 20, 40), ornek_n=150, seed=42):
    """R10: her müşterinin TAM geçmişiyle skorunu taban alır; geçmişi ilk K
    işleme kırpıp skorun tam-geçmiş skorundan ne kadar SAPTIĞINI ve anomali
    bayrağının ne sıklıkla tetiklendiğini ölçer — "zarif bozulma" testi.

    NOT: `model.predict_proba()` ham (ölçeksiz) özellik vektörü bekler —
    LR sarmalayıcısı (`kayit.py::OlcekliLojistikSarmalayici`) ölçeklendirmeyi
    KENDİ İÇİNDE yapar (aynı `SkorlamaAgent.calistir()`'in yaptığı gibi).
    Burada elle `scaler.transform()` çağırmak çift ölçeklendirme olurdu."""
    rng = np.random.default_rng(seed)
    uygun = [mid for mid, isl in musteri_islem_map.items() if len(isl) > max(kesme_noktalari)]
    secili = rng.choice(uygun, size=min(ornek_n, len(uygun)), replace=False)

    def _skorla(islemler):
        oz = ozellik_cikar(islemler)
        vek = [oz[o] for o in OZELLIK_ADLARI]
        x = np.asarray(vek, dtype=float).reshape(1, -1)
        p = float(model.predict_proba(x)[0, 1])
        bayrak = None
        if anomali_model is not None:
            bayrak, _ = anomali.degerlendir(anomali_model, vek)
        return olasilik_to_aks(p), bayrak

    sonuc = {}
    for k in kesme_noktalari:
        sapmalar, bayraklar = [], []
        for mid in secili:
            islemler = sorted(musteri_islem_map[mid], key=lambda i: i["tarih_obj"])
            skor_tam, _ = _skorla(islemler)
            skor_kirpik, bayrak = _skorla(islemler[:k])
            sapmalar.append(abs(skor_kirpik - skor_tam))
            if bayrak is not None:
                bayraklar.append(bayrak)
        sonuc[f"ilk_{k}_islem"] = {
            "n": len(sapmalar),
            "ort_mutlak_sapma": round(float(np.mean(sapmalar)), 1),
            "p90_mutlak_sapma": round(float(np.percentile(sapmalar, 90)), 1),
            "anomali_bayrak_orani": round(float(np.mean(bayraklar)), 3) if bayraklar else None,
        }
    return sonuc


def oyunlanabilirlik_duyarliligi(musteriler, model, oran=0.25, ornek_n=200, seed=42):
    """R11: 4 nedensel özelliği tek tek, sabit bir göreli miktarda (varsayılan
    %25) 'iyileştirme' yönünde değiştirip ortalama skor kazancını ölçer —
    hangi özellik, aynı büyüklükteki davranış değişikliği için en çok skor
    'satın alıyor' (RQ-3'e ilk niceliksel cevap, architecture.md §7)."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(musteriler), size=min(ornek_n, len(musteriler)), replace=False)
    ornekler = [musteriler[i] for i in idx]

    def _skorla(oz_sozluk):
        vek = [oz_sozluk[o] for o in OZELLIK_ADLARI]
        x = np.asarray(vek, dtype=float).reshape(1, -1)
        p = float(model.predict_proba(x)[0, 1])
        return olasilik_to_aks(p)

    sonuc = {}
    for feat in NEDENSEL_OZELLIKLER:
        kazanclar = []
        for m in ornekler:
            baz = _skorla(m)
            degisim = abs(m[feat]) * oran * IYILESTIRME_YONU[feat]
            if degisim == 0:
                degisim = 0.1 * IYILESTIRME_YONU[feat]
            yeni_deger = m[feat] + degisim
            lo, hi = OZELLIK_SINIRLARI.get(feat, (None, None))
            if lo is not None:
                yeni_deger = max(lo, yeni_deger)
            if hi is not None:
                yeni_deger = min(hi, yeni_deger)
            yeni_oz = dict(m)
            yeni_oz[feat] = yeni_deger
            kazanclar.append(_skorla(yeni_oz) - baz)
        sonuc[feat] = {
            "ort_skor_kazanci": round(float(np.mean(kazanclar)), 1),
            "p90_skor_kazanci": round(float(np.percentile(kazanclar, 90)), 1),
            "degisim_orani": oran,
        }
    return sonuc


def rapor_uret(veri_kaynagi="dekuple", seed=42, dosya_yolu=None):
    from aks_core.model.egitim import VERI_KAYNAKLARI, veri_hazirla
    from aks_core.ozellik.cikarim import csv_oku
    from aks_core.model import kayit

    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"]) if kaynak["etiket"] else None
    musteriler = veri_hazirla(islem_csv, veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    y = np.array([m["temerrut"] for m in musteriler])

    model, model_adi, ozellikler = kayit.yukle()
    anomali_model = anomali.yukle()

    musteri_islem_map, _ = csv_oku(islem_csv)

    t0 = time.time()
    r8 = persona_disi_genelleme(musteriler, X, y, seed=seed)
    r10 = ince_dosya_stres_testi(musteri_islem_map, model, anomali_model, seed=seed)
    r11 = oyunlanabilirlik_duyarliligi(musteriler, model, seed=seed)
    sure_sn = round(time.time() - t0, 1)

    rapor = {
        "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "veri_kaynagi": veri_kaynagi,
        "n_musteri": len(musteriler),
        "model_adi_referans": model_adi,
        "sure_sn": sure_sn,
        "persona_disi_genelleme": {
            "aciklama": "Her persona sırayla eğitim setinden tamamen çıkarılıp kalan 3 personayla eğitilen "
                         "ayrı bir LogisticRegression(C=1.0) ile test edildi — üretim modeliyle aynı hiperparametre "
                         "(egitim_manifest.json), ama rastgele k-fold DEĞİL: gerçek 'hiç görmedim' testi.",
            "sonuc": r8,
        },
        "out_of_time_split": {
            "durum": "YAPILMADI (atlanmadı, gerekçeli)",
            "gerekce": "kapasite_islemler.csv'deki her müşterinin işlemleri aynı 6 aylık pencereye "
                       "(2026-01-01–2026-06-29) yayılmış; üretici zamana bağlı bir kayma (concept drift) "
                       "simüle etmiyor. Müşterileri tarihe göre erken/geç ayırmak üretici rastgeleliğini "
                       "ölçmekten başka bir şey olmazdı — sahte bir sonuç yerine bu boşluk açıkça bırakıldı. "
                       "Gerçek bir out-of-time testi gerçek veri gerektirir (OQ-36).",
        },
        "ince_dosya_stres_testi": {
            "aciklama": "150 rastgele müşterinin TAM geçmişiyle skoru taban alınıp, geçmiş ilk K işleme "
                         "kırpıldığında skorun ne kadar SAPTIĞI ve anomali bayrağının ne sıklıkla tetiklendiği "
                         "ölçüldü. K küçüldükçe sapma artıyor VE anomali oranı artıyorsa, model 'zarifçe' "
                         "bozuluyor demektir (güvenle yanılmak yerine daha az güvenilir olduğunu işaretliyor).",
            "sonuc": r10,
        },
        "oyunlanabilirlik_duyarliligi": {
            "aciklama": "4 nedensel özellik tek tek %25 'iyileştirme' yönünde değiştirilip ortalama skor "
                         "kazancı ölçüldü — sabit büyüklükteki bir davranış değişikliği için hangi özellik "
                         "en çok skor 'satın alıyor'. Yüksek kazanç + düşük gerçek-dünya maliyeti olan bir "
                         "özellik, oyunlanabilirlik riski taşır (RQ-3).",
            "sonuc": r11,
        },
    }
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / RAPOR_ADI
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    return rapor


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--veri-kaynagi", default="dekuple", choices=["dongusel", "dekuple"])
    a = p.parse_args()
    r = rapor_uret(veri_kaynagi=a.veri_kaynagi)

    print(f"\n=== R8: Persona-dışı genelleme ({r['sure_sn']}s) ===")
    for persona, s in r["persona_disi_genelleme"]["sonuc"].items():
        print(f"  {persona:<26} n_test={s['n_test']:<5} AUC={s['auc']}")

    print("\n=== R8: Out-of-time split ===")
    print(f"  {r['out_of_time_split']['durum']}")

    print("\n=== R10: İnce dosya stres testi ===")
    for k, s in r["ince_dosya_stres_testi"]["sonuc"].items():
        print(f"  {k:<14} n={s['n']:<4} ort_sapma={s['ort_mutlak_sapma']:<6} p90={s['p90_mutlak_sapma']:<6} anomali_orani={s['anomali_bayrak_orani']}")

    print("\n=== R11: Oyunlanabilirlik duyarlılığı (%25 iyileştirme) ===")
    for feat, s in sorted(r["oyunlanabilirlik_duyarliligi"]["sonuc"].items(), key=lambda kv: -kv[1]["ort_skor_kazanci"]):
        print(f"  {feat:<22} ort_kazanc={s['ort_skor_kazanci']:<7} p90={s['p90_skor_kazanci']}")
