"""
Kalibrasyon Yardımcıları — izotonik regresyon, taşınabilir (pickle'sız) format.
--------------------------------------------------------------------------------
İki kullanım yeri var, ikisi de aynı matematiği paylaşır (monotonik x->y eşleme):

  1) Olasılık kalibrasyonu (U9): ham model olasılığı -> gözlenen frekansa daha
     yakın kalibre olasılık (ECE yüksekse uygulanır; artan/increasing).
  2) Formülasyon B (U10): klasik skor bandı -> o banttaki ampirik temerrüt
     oranı ("pd_geleneksel_bant"); skor yükseldikçe risk düşer (azalan/decreasing).

Neden pickle değil: `kayit.py`'nin taşınabilirlik ilkesiyle aynı gerekçe —
`sklearn.isotonic.IsotonicRegression` nesnesini pickle'lamak yerine, fit
edilmiş adım fonksiyonunun (x_thresholds_, y_thresholds_) ham sayı dizilerini
JSON'a yazıyoruz. Model kütüphanesi/sürümünden bağımsız, düz veri.
"""
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import StratifiedKFold


def oof_proba(model_fn, X, y, n_splits=5, seed=42):
    """Out-of-fold tahmin olasılıkları — kalibrasyon fit'i için sızıntısız veri.

    `model_fn()` her fold'da taze bir model örneği döndürmeli (fit edilmemiş).
    """
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof = np.zeros(len(y))
    for tr, te in skf.split(X, y):
        m = model_fn()
        m.fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
    return oof


def ece(y, p, n_bins=10):
    """Expected Calibration Error — eşit genişlikli binlerde |gözlenen - tahmin|."""
    y, p = np.asarray(y, dtype=float), np.asarray(p, dtype=float)
    kenarlar = np.linspace(0, 1, n_bins + 1)
    toplam = 0.0
    for i in range(n_bins):
        mask = (p >= kenarlar[i]) & (p < kenarlar[i + 1]) if i < n_bins - 1 else (p >= kenarlar[i]) & (p <= kenarlar[i + 1])
        if mask.sum() == 0:
            continue
        toplam += (mask.sum() / len(p)) * abs(y[mask].mean() - p[mask].mean())
    return float(toplam)


def fit_isotonic(x, y, increasing=True):
    """x'ten y'ye monotonik adım fonksiyonu fit eder. Taşınabilir dict döner."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    iso = IsotonicRegression(increasing=increasing, out_of_bounds="clip")
    iso.fit(x, y)
    return {
        "increasing": bool(increasing),
        "x_esik": [float(v) for v in iso.X_thresholds_],
        "y_esik": [float(v) for v in iso.y_thresholds_],
    }


def apply_isotonic(x_val, kalib):
    """Fit edilmiş adım fonksiyonunu (JSON'dan yüklenmiş dict) tek/çoklu değere uygular."""
    x_esik = np.asarray(kalib["x_esik"], dtype=float)
    y_esik = np.asarray(kalib["y_esik"], dtype=float)
    tekil = np.isscalar(x_val)
    x = np.atleast_1d(np.asarray(x_val, dtype=float))
    x = np.clip(x, x_esik[0], x_esik[-1])
    sonuc = np.interp(x, x_esik, y_esik)
    return float(sonuc[0]) if tekil else sonuc
