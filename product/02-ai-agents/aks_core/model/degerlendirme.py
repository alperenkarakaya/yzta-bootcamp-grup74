"""
Değerlendirme Harness'i — RESEARCH_STRATEGY.md §4 A3 (genelleme) + A4 (kalibrasyon).
-----------------------------------------------------------------------------------
Model- ve veri-agnostik. Verilen (model_fn, X, y, persona) için tam bir istatistiksel
rapor üretir. Amaç: mandatte istenen "design the evaluation before the implementation"
ilkesi — bu harness, sentetik/gerçek veri veya XGBoost/LojistikRegresyon fark etmeksizin
aynı kalır. Döngüsellik düzeltilse de (OQ-36/37) bu modül yeniden kullanılabilir.

Ürettiği metrikler (öncelik sırasına göre):
  #2 Genelleme : tekrarlı stratified k-fold ROC-AUC & PR-AUC, bootstrap %95 CI
  #3 Kalibrasyon: Brier skoru, ECE (Expected Calibration Error), reliability eğrisi
  + Alt-grup (persona) bazında AUC & Brier — thin-file tezinin asıl test edildiği yer
  + Mandat gereği: XGBoost vs LojistikRegresyon (basit model eşitse basiti seç)

Çalıştırma:  python -m aks_core.model.degerlendirme
"""
from dataclasses import dataclass, field

import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from aks_core import paths
from aks_core.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI
from aks_core.model.etiketleme import etiketle


# ----------------------------- yardımcılar -----------------------------

def _bootstrap_ci(degerler, n_boot=2000, seed=42, alpha=0.05):
    """Fold-seviyesi metrik dizisinin bootstrap %(1-alpha) güven aralığı."""
    degerler = np.asarray(degerler, dtype=float)
    rng = np.random.default_rng(seed)
    boot = [degerler[rng.integers(0, len(degerler), len(degerler))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(degerler.mean()), float(degerler.std()), (float(lo), float(hi))


def _ece(y, p, n_bins=10):
    """Expected Calibration Error — eşit genişlikli binlerde |gözlenen - tahmin|."""
    y, p = np.asarray(y), np.asarray(p)
    kenarlar = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (p >= kenarlar[i]) & (p < kenarlar[i + 1]) if i < n_bins - 1 else (p >= kenarlar[i]) & (p <= kenarlar[i + 1])
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / len(p)) * abs(y[mask].mean() - p[mask].mean())
    return float(ece)


def _reliability(y, p, n_bins=10):
    """Reliability eğrisi: bin başına (ort_tahmin, gozlenen_frekans, adet)."""
    y, p = np.asarray(y), np.asarray(p)
    kenarlar = np.linspace(0, 1, n_bins + 1)
    satirlar = []
    for i in range(n_bins):
        mask = (p >= kenarlar[i]) & (p < kenarlar[i + 1]) if i < n_bins - 1 else (p >= kenarlar[i]) & (p <= kenarlar[i + 1])
        if mask.sum() == 0:
            continue
        satirlar.append((float(p[mask].mean()), float(y[mask].mean()), int(mask.sum())))
    return satirlar


def _fit_predict(model_fn, Xtr, ytr, Xte):
    m = model_fn()
    if isinstance(m, LogisticRegression):
        sc = StandardScaler().fit(Xtr)
        Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)
    m.fit(Xtr, ytr)
    return m.predict_proba(Xte)[:, 1]


# ----------------------------- rapor yapısı -----------------------------

@dataclass
class ModelRaporu:
    ad: str
    auc: tuple          # (mean, std, (lo, hi))
    ap: tuple
    brier_oof: float
    ece_oof: float
    reliability: list
    persona_metrik: dict = field(default_factory=dict)  # persona -> (auc, brier, n)


def degerlendir_model(ad, model_fn, X, y, persona, n_splits=5, n_repeats=5, seed=42):
    # --- #2 Genelleme: tekrarlı stratified k-fold AUC/AP + bootstrap CI ---
    rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    aucs, aps = [], []
    for tr, te in rskf.split(X, y):
        p = _fit_predict(model_fn, X[tr], y[tr], X[te])
        aucs.append(roc_auc_score(y[te], p))
        aps.append(average_precision_score(y[te], p))

    # --- #3 Kalibrasyon: tek k-fold pass ile OOF tahminleri ---
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(y))
    for tr, te in skf.split(X, y):
        oof[te] = _fit_predict(model_fn, X[tr], y[tr], X[te])

    # --- Alt-grup (persona) bazında OOF metrikleri ---
    persona_metrik = {}
    for pj in sorted(set(persona)):
        mask = persona == pj
        if mask.sum() < 10 or len(set(y[mask])) < 2:
            continue
        persona_metrik[pj] = (
            float(roc_auc_score(y[mask], oof[mask])),
            float(brier_score_loss(y[mask], oof[mask])),
            int(mask.sum()),
        )

    return ModelRaporu(
        ad=ad,
        auc=_bootstrap_ci(aucs, seed=seed),
        ap=_bootstrap_ci(aps, seed=seed),
        brier_oof=float(brier_score_loss(y, oof)),
        ece_oof=_ece(y, oof),
        reliability=_reliability(y, oof),
        persona_metrik=persona_metrik,
    )


# ----------------------------- yazdırma -----------------------------

def _yazdir(rapor: ModelRaporu):
    a_m, a_s, (a_lo, a_hi) = rapor.auc
    p_m, p_s, (p_lo, p_hi) = rapor.ap
    print(f"\n=== {rapor.ad} ===")
    print(f"  ROC-AUC : {a_m:.4f} ± {a_s:.4f}   %95 CI [{a_lo:.4f}, {a_hi:.4f}]")
    print(f"  PR-AUC  : {p_m:.4f} ± {p_s:.4f}   %95 CI [{p_lo:.4f}, {p_hi:.4f}]")
    print(f"  Brier   : {rapor.brier_oof:.4f}   (dusuk=iyi; referans: sabit taban orani icin ~p(1-p))")
    print(f"  ECE     : {rapor.ece_oof:.4f}   (dusuk=iyi kalibre)")
    print(f"  Reliability (ort_tahmin -> gozlenen [adet]):")
    for pt, obs, n in rapor.reliability:
        print(f"      {pt:.3f} -> {obs:.3f}   [{n}]")
    if rapor.persona_metrik:
        print(f"  Persona bazinda (OOF):")
        for pj, (auc, brier, n) in rapor.persona_metrik.items():
            print(f"      {pj:<26} AUC {auc:.4f}  Brier {brier:.4f}  [n={n}]")


def calistir(islem_csv=None, hedef_oran=0.18, seed=42):
    islem_csv = islem_csv or paths.data("sentetik_islemler.csv")
    musteriler = etiketle(tum_musteriler(islem_csv), hedef_temerrut_orani=hedef_oran)
    y = np.array([m["temerrut"] for m in musteriler])
    persona = np.array([m["persona"] for m in musteriler])
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)

    print(f"Veri: {len(y)} musteri, taban temerrut orani {y.mean():.3f}, {X.shape[1]} ozellik")
    print(f"Referans Brier (sabit p=taban): {y.mean()*(1-y.mean()):.4f}")

    adaylar = {
        "XGBoost (uretimdeki model)": lambda: xgb.XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.9,
            colsample_bytree=0.9, eval_metric="logloss", random_state=seed, n_jobs=-1),
        "LojistikRegresyon (mandat: basit baseline)": lambda: LogisticRegression(max_iter=1000),
    }
    raporlar = [degerlendir_model(ad, fn, X, y, persona, seed=seed) for ad, fn in adaylar.items()]
    for r in raporlar:
        _yazdir(r)

    xgb_auc = raporlar[0].auc[0]
    lr_auc = raporlar[1].auc[0]
    print(f"\nKarar notu (mandat #1/#8): XGBoost AUC {xgb_auc:.4f} vs LR AUC {lr_auc:.4f} — "
          f"fark {abs(xgb_auc-lr_auc):.4f}. CI'lar orortusuyorsa, basit model (LR) tercih edilmeli.")
    return raporlar


if __name__ == "__main__":
    calistir()
