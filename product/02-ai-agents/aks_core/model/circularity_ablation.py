"""
Döngüsellik (circularity) tanı testi — RESEARCH_STRATEGY.md §4 A1.
--------------------------------------------------------------------
Bu bir üretim modülü DEĞİLDİR; ana tez şu iddiayı sayısal olarak sınar:

  "gider_gelir_orani, bakiye_trendi, gelir_duzenliligi, fatura_odeme_duzeni"
  etiketin (temerrut) doğrudan nedensel girdileridir (etiketleme.py) ve model
  bu 4 değişkeni ham/bozulmamış halde görüyor — bu yüzden XGBoost'un AUC
  üstünlüğü "davranışsal sinyal keşfi" değil, bilinen bir doğrusal kuralın
  yeniden inşasıdır.

Ölçülen:
  1) Aynı 9 özellikle Lojistik Regresyon vs XGBoost  (yakın performans bekleniyor)
  2) Sadece 4 nedensel özellik ile Lojistik Regresyon (neredeyse aynı AUC bekleniyor)
  3) Sadece 5 nedensel-olmayan özellik ile Lojistik Regresyon (şansa yakın AUC bekleniyor)
  4) Oracle/Bayes-optimal AUC: gerçek üretim olasılığı (temerrut_olasiligi_gercek)
     ile gerçekleşen temerrut arasındaki AUC — teorik tavan.
  5-fold stratified CV + %95 bootstrap CI ile.

Çalıştırma:  python -m aks_core.model.circularity_ablation
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from aks_core import paths
from aks_core.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI
from aks_core.model.etiketleme import etiketle

NEDENSEL = ["gider_gelir_orani", "bakiye_trendi", "gelir_duzenliligi", "fatura_odeme_duzeni"]
NEDENSEL_OLMAYAN = [o for o in OZELLIK_ADLARI if o not in NEDENSEL]


def _cv_auc(X, y, model_fn, n_splits=5, n_boot=1000, seed=42):
    """Stratified k-fold AUC + fold-level bootstrap %95 CI."""
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
    aucs = np.array(aucs)
    rng = np.random.default_rng(seed)
    boot = [aucs[rng.integers(0, len(aucs), len(aucs))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return aucs.mean(), aucs.std(), (lo, hi)


def calistir(islem_csv=None, hedef_oran=0.18, seed=42):
    islem_csv = islem_csv or paths.data("sentetik_islemler.csv")
    musteriler = etiketle(tum_musteriler(islem_csv), hedef_temerrut_orani=hedef_oran)

    y = np.array([m["temerrut"] for m in musteriler])
    p_gercek = np.array([m["temerrut_olasiligi_gercek"] for m in musteriler])
    X_tum = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    X_nedensel = np.array([[m[o] for o in NEDENSEL] for m in musteriler], dtype=float)
    X_olmayan = np.array([[m[o] for o in NEDENSEL_OLMAYAN] for m in musteriler], dtype=float)

    sonuclar = {}

    oracle_auc = roc_auc_score(y, p_gercek)
    sonuclar["0_Oracle (Bayes-optimal, teorik tavan)"] = (oracle_auc, 0.0, (oracle_auc, oracle_auc))

    sonuclar["1_XGBoost (9 ozellik, dahil: 4 nedensel)"] = _cv_auc(
        X_tum, y, lambda: xgb.XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.9,
            colsample_bytree=0.9, eval_metric="logloss", random_state=seed, n_jobs=-1))

    sonuclar["2_LojistikRegresyon (ayni 9 ozellik)"] = _cv_auc(
        X_tum, y, lambda: LogisticRegression(max_iter=1000))

    sonuclar["3_LojistikRegresyon (SADECE 4 nedensel ozellik)"] = _cv_auc(
        X_nedensel, y, lambda: LogisticRegression(max_iter=1000))

    sonuclar["4_LojistikRegresyon (SADECE 5 nedensel-olmayan ozellik)"] = _cv_auc(
        X_olmayan, y, lambda: LogisticRegression(max_iter=1000))

    print(f"\n{'Model':<48}{'AUC (ort)':<12}{'std':<10}{'%95 CI'}")
    print("-" * 90)
    for ad, (mean, std, ci) in sonuclar.items():
        etiket = ad.split("_", 1)[1]
        print(f"{etiket:<48}{mean:<12.4f}{std:<10.4f}[{ci[0]:.4f}, {ci[1]:.4f}]")
    print("-" * 90)
    xgb_auc = sonuclar["1_XGBoost (9 ozellik, dahil: 4 nedensel)"][0]
    lr9_auc = sonuclar["2_LojistikRegresyon (ayni 9 ozellik)"][0]
    lr4_auc = sonuclar["3_LojistikRegresyon (SADECE 4 nedensel ozellik)"][0]
    lr5_auc = sonuclar["4_LojistikRegresyon (SADECE 5 nedensel-olmayan ozellik)"][0]
    print(f"\nXGBoost / Oracle oranı: {xgb_auc/oracle_auc:.3f}  (1.0'a ne kadar yakinsa, model o kadar Bayes-optimale ulasmis)")
    print(f"LR(9 ozellik) vs XGBoost farki: {abs(lr9_auc-xgb_auc):.4f}  (kucukse: ensemble karmasikligi gereksiz)")
    print(f"LR(sadece 4 nedensel) vs LR(9 ozellik) farki: {abs(lr4_auc-lr9_auc):.4f}  (kucukse: diger 5 ozellik ~sifir katki)")
    print(f"LR(sadece 5 nedensel-olmayan) AUC: {lr5_auc:.4f}  (0.50'ye yakinsa: bu ozellikler etikete gore sansa yakin)")
    return sonuclar


if __name__ == "__main__":
    calistir()
