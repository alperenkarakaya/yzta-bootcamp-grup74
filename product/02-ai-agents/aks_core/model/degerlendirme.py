"""
Değerlendirme Harness'i — architecture.md §6 (genelleme + kalibrasyon).
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

§3b/U6: bu betiğin çıktısı önceden yalnızca stdout'a yazdırılıyordu; `egitim.py`nin
tek-split point-estimate'i (`metrikler.json`) "resmi" rapor gibi kalıyordu. Artık
`json_yaz()` bu tam CV+CI+kalibrasyon+alt-grup raporunu `degerlendirme_raporu.json`
olarak diske de yazıyor — D5'in çözümü ("headline numbers... do not cite as
validated" uyarısının somut karşılığı): raporlanan sayı artık bu dosyadan gelmeli.

Çalıştırma:  python -m aks_core.model.degerlendirme [--veri-kaynagi dekuple|dongusel]
"""
import json
import time
from dataclasses import dataclass, field, asdict

import numpy as np
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from aks_core import paths
from aks_core.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI
from aks_core.model.etiketleme import etiketle

RAPOR_DOSYA_ADI = "degerlendirme_raporu.json"


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


def _rapor_json(rapor: ModelRaporu):
    a_m, a_s, (a_lo, a_hi) = rapor.auc
    p_m, p_s, (p_lo, p_hi) = rapor.ap
    return {
        "ad": rapor.ad,
        "roc_auc": {"ortalama": round(a_m, 4), "std": round(a_s, 4), "ci95": [round(a_lo, 4), round(a_hi, 4)]},
        "pr_auc": {"ortalama": round(p_m, 4), "std": round(p_s, 4), "ci95": [round(p_lo, 4), round(p_hi, 4)]},
        "brier_oof": round(rapor.brier_oof, 4),
        "ece_oof": round(rapor.ece_oof, 4),
        "reliability": [{"tahmin": round(p, 4), "gozlenen": round(o, 4), "n": n} for p, o, n in rapor.reliability],
        "persona_metrik": {
            pj: {"auc": round(auc, 4), "brier": round(brier, 4), "n": n}
            for pj, (auc, brier, n) in rapor.persona_metrik.items()
        },
    }


def json_yaz(raporlar, veri_kaynagi, n_musteri, taban_oran, dosya_yolu=None):
    """§3b/U6: tam CV+CI+kalibrasyon+alt-grup raporunu diske yazar — bu, artık
    "resmi" (raporlanabilir) metrik kaynağıdır; `egitim.py`'nin `metrikler.json`'ı
    yalnızca hızlı bir tek-split sağlık kontrolüdür, headline sayı değildir."""
    yol = dosya_yolu or (paths.ARTIFACTS_DIR / RAPOR_DOSYA_ADI)
    icerik = {
        "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "veri_kaynagi": veri_kaynagi,
        "n_musteri": n_musteri,
        "taban_temerrut_orani": round(taban_oran, 4),
        "yontem": "RepeatedStratifiedKFold(5x5) AUC/PR-AUC + bootstrap %95 CI; 5-fold OOF Brier/ECE/reliability/persona",
        "modeller": [_rapor_json(r) for r in raporlar],
    }
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(icerik, f, ensure_ascii=False, indent=2)
    return str(yol)


def calistir(islem_csv=None, hedef_oran=0.18, seed=42, veri_kaynagi="dekuple", yaz=True):
    from aks_core.model.egitim import veri_hazirla, VERI_KAYNAKLARI
    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = islem_csv or paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"]) if kaynak["etiket"] else None
    musteriler = veri_hazirla(islem_csv, hedef_oran=hedef_oran, veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)
    y = np.array([m["temerrut"] for m in musteriler])
    persona = np.array([m["persona"] for m in musteriler])
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)

    print(f"Veri kaynagi: {veri_kaynagi} — {len(y)} musteri, taban temerrut orani {y.mean():.3f}, {X.shape[1]} ozellik")
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

    if yaz:
        yol = json_yaz(raporlar, veri_kaynagi, len(y), float(y.mean()))
        print(f"\nRapor yazildi -> {yol}")
    return raporlar


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--veri-kaynagi", default="dekuple", choices=["dekuple", "dongusel"])
    a = p.parse_args()
    calistir(veri_kaynagi=a.veri_kaynagi)
