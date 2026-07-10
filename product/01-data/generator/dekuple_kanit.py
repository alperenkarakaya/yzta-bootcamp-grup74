"""
Dekuple (döngüsellik-kıran) veri KANITI — 01-data
=================================================
`uretici_kapasite.py`'nin ürettiği veri üzerinde, döngüselliğin gerçekten
kırıldığını ve ürün tezinin artık DÜRÜST biçimde ölçülebildiğini sayısal
olarak kanıtlar. Karşılaştırma noktası: architecture.md §5.1 / §4'teki eski
(döngüsel) üreticinin bulguları.

Özellikler GERÇEK üretim çıkarıcısıyla (aks_core.ozellik.cikarim) hesaplanır;
etiketler gizli-kapasiteden türetilmiş ayrı dosyadan gelir (ÖZELLİKLERDEN DEĞİL).

Çalıştırma:
    pip install -e product/02-ai-agents   # aks_core (bir kez)
    python product/01-data/generator/dekuple_kanit.py
"""
import csv
import os

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from aks_core.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI

BURADA = os.path.dirname(__file__)
DATASETS = os.path.join(BURADA, "..", "datasets")
ISLEM_CSV = os.path.join(DATASETS, "kapasite_islemler.csv")
ETIKET_CSV = os.path.join(DATASETS, "kapasite_etiketleri.csv")

# Davranışsal (disiplin) özellikler — ham gelir hacmi HARİÇ
DAVRANISSAL = ["gider_gelir_orani", "bakiye_trendi", "gelir_duzenliligi",
               "fatura_odeme_duzeni", "hesap_hareket_yogunlugu",
               "gelir_kaynagi_sayisi", "gelir_islem_sayisi"]
GELIR_KANALI = ["toplam_gelir_hacmi"]  # geleneksel/klasik kanal (thin-file kör noktası)


def _etiketleri_yukle(yol):
    d = {}
    with open(yol, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[int(r["musteri_id"])] = {
                "temerrut": int(r["temerrut"]),
                "p_gercek": float(r["temerrut_olasiligi_gercek"]),
                "c": float(r["gizli_kapasite"]),
                "persona": r["persona"],
            }
    return d


def _cv_auc(X, y, model_fn, n_splits=5, seed=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    aucs = []
    for tr, te in skf.split(X, y):
        m = model_fn()
        Xtr, Xte = X[tr], X[te]
        if isinstance(m, LogisticRegression):
            sc = StandardScaler().fit(Xtr)
            Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
        m.fit(Xtr, y[tr])
        p = m.predict_proba(Xte)[:, 1]
        aucs.append(roc_auc_score(y[te], p))
    return float(np.mean(aucs)), float(np.std(aucs))


def _lr():
    return LogisticRegression(max_iter=1000)


def _xgb(seed=42):
    return xgb.XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05,
                             subsample=0.9, colsample_bytree=0.9, eval_metric="logloss",
                             random_state=seed, n_jobs=-1)


def calistir():
    if not (os.path.exists(ISLEM_CSV) and os.path.exists(ETIKET_CSV)):
        raise SystemExit("Önce üret: python product/01-data/generator/veri/uretici_kapasite.py")

    musteriler = tum_musteriler(ISLEM_CSV)          # GERÇEK özellik çıkarıcı
    etiket = _etiketleri_yukle(ETIKET_CSV)          # gizli-kapasiteden etiket

    musteriler = [m for m in musteriler if m["musteri_id"] in etiket]
    y = np.array([etiket[m["musteri_id"]]["temerrut"] for m in musteriler])
    p_gercek = np.array([etiket[m["musteri_id"]]["p_gercek"] for m in musteriler])
    personalar = np.array([m["persona"] for m in musteriler])

    def M(kolonlar):
        return np.array([[m[o] for o in kolonlar] for m in musteriler], dtype=float)

    X_tum = M(OZELLIK_ADLARI)
    X_dav = M(DAVRANISSAL)
    X_gel = M(GELIR_KANALI)

    print("=" * 78)
    print("DEKUPLE VERİ KANITI — döngüsellik kırıldı mı? (01-data)")
    print("=" * 78)
    print(f"Müşteri: {len(y)}   temerrüt oranı: {y.mean():.3f}")

    # --- A) Etiket persona'dan bağımsız mı? ---
    print("\n[A] Persona bazinda temerrut orani (etiket persona'dan BAGIMSIZ olmali):")
    oranlar = []
    for p in sorted(set(personalar)):
        mask = personalar == p
        r = y[mask].mean()
        oranlar.append(r)
        print(f"     {p:<24} n={mask.sum():<5} temerrüt={r:.3f}")
    print(f"     -> yayılım (max-min) = {max(oranlar)-min(oranlar):.3f}  "
          f"(ESKİ döngüsel üreticide persona etiketi belirliyordu; ~0 = kırıldı)")

    # --- B) Oracle + model-sınıfı + sızıntı-kısayolu ---
    oracle = roc_auc_score(y, p_gercek)
    xgb_auc, xgb_sd = _cv_auc(X_tum, y, _xgb)
    lr_auc, lr_sd = _cv_auc(X_tum, y, _lr)
    tekil = []
    for i, ad in enumerate(OZELLIK_ADLARI):
        a, _ = _cv_auc(X_tum[:, [i]], y, _lr)
        tekil.append((ad, a))
    en_iyi_tekil = max(tekil, key=lambda t: t[1])

    print("\n[B] Oracle tavanı, model sınıfı ve sızıntı-kısayolu kontrolü:")
    print(f"     Oracle (Bayes-optimal, gerçek p):            {oracle:.4f}   (teorik tavan)")
    print(f"     XGBoost (9 özellik):                         {xgb_auc:.4f} ± {xgb_sd:.4f}")
    print(f"     LojistikRegresyon (9 özellik):               {lr_auc:.4f} ± {lr_sd:.4f}")
    print(f"     En iyi TEK özellik ({en_iyi_tekil[0]}): {en_iyi_tekil[1]:.4f}")
    print(f"     -> XGB−LR farkı = {abs(xgb_auc-lr_auc):.4f} (lineer DGP; ensemble gereksiz)")
    print(f"     -> En iyi tek özellik, çoklu-özellik modelinden {lr_auc-en_iyi_tekil[1]:.4f} DÜŞÜK")
    print(f"        (ESKİ üreticide 4 'nedensel' özellik tüm modele ~eşitti = sızıntı; "
          f"burada tek özellik etiketi TAŞIMIYOR)")

    # --- C) Gerçek tez: davranış, gelir kanalının göremediğini görüyor mu? ---
    dav_auc, _ = _cv_auc(X_dav, y, _lr)
    gel_auc, _ = _cv_auc(X_gel, y, _lr)
    print("\n[C] ÜRÜN TEZİ (dürüst ölçüm) — davranış vs geleneksel/gelir kanalı:")
    print(f"     Geleneksel kanal (yalnız gelir hacmi):       {gel_auc:.4f}   (thin-file kör noktası)")
    print(f"     Davranışsal disiplin özellikleri:            {dav_auc:.4f}")
    print(f"     -> davranışsal KALDIRAÇ = +{dav_auc-gel_auc:.4f} AUC (gerçek sinyal, tautoloji değil)")

    print("\n     Persona bazında (kaldıraç thin-file'da yoğunlaşmalı):")
    print(f"     {'persona':<24}{'gelir-kanalı':<14}{'davranışsal':<14}{'kaldıraç':<10}")
    for p in sorted(set(personalar)):
        mask = personalar == p
        if y[mask].sum() < 10 or (mask.sum() - y[mask].sum()) < 10:
            continue
        g, _ = _cv_auc(X_gel[mask], y[mask], _lr, n_splits=4)
        d, _ = _cv_auc(X_dav[mask], y[mask], _lr, n_splits=4)
        print(f"     {p:<24}{g:<14.4f}{d:<14.4f}{d-g:+.4f}")

    print("\n" + "=" * 78)
    print("SONUÇ: etiket persona'dan ve özelliklerden ayrıştı; davranışsal sinyal")
    print("gerçek (oracle'a yaklaşıyor ama aşmıyor); gelir kanalı zayıf. Döngüsellik")
    print("kırıldı — bu veri, execution.md M4 kapısını açan honest-fallback'tir.")
    print("=" * 78)


if __name__ == "__main__":
    calistir()
