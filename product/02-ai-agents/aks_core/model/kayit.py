"""
Model Kaydetme / Yükleme — platformlar arası taşınabilir format
---------------------------------------------------------------
Neden bu modül var:

Model önceden `joblib.dump(...)` ile kaydediliyordu. joblib/pickle, XGBoost
booster'ını kaydederken kütüphanenin ham C++ bellek buffer'ını gömer. Bu buffer
platforma ve derleme ayarlarına bağlıdır: Linux'ta eğitilen bir model Windows'ta
açılmaya çalışıldığında `XGBoostError: input stream corrupted` verir. Yani repoyu
klonlayan bir Windows kullanıcısı ürünü çalıştıramıyordu.

Çözüm: her kütüphaneyi kendi resmî serileştirme formatıyla kaydetmek.
  - XGBoost  -> aks_model.json   (save_model / load_model)
  - LightGBM -> aks_model.txt    (Booster.save_model / Booster(model_file=...))
Yanına da hangi formatın kullanıldığını ve özellik sırasını tutan
`aks_model_meta.json` yazılır.

Bu formatlar sürümler arasında da geriye dönük uyumludur; pickle değildir.

Geriye dönük uyumluluk: eski `aks_model.joblib` duruyorsa ve yeni format yoksa,
`yukle()` onu okumayı dener (aynı platformda eğitildiyse çalışır).
"""
import json
import os
from pathlib import Path

import numpy as np

from aks_core import paths

META_ADI = "aks_model_meta.json"
XGB_ADI = "aks_model.json"
LGB_ADI = "aks_model.txt"


class LGBMSarmalayici:
    """LightGBM Booster'a sklearn benzeri `predict_proba` arayüzü verir.

    Booster.predict() ikili sınıflandırmada doğrudan pozitif sınıf olasılığını
    döndürür; kodun geri kalanı `predict_proba(X)[:, 1]` beklediği için iki
    kolonlu diziye çeviriyoruz.
    """

    def __init__(self, booster):
        self.booster = booster

    def predict_proba(self, X):
        p = np.asarray(self.booster.predict(X), dtype=float).ravel()
        return np.column_stack([1.0 - p, p])


def _artifacts_dizini() -> Path:
    d = Path(paths.ARTIFACTS_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def kaydet(model, model_adi: str, ozellikler: list) -> str:
    """Eğitilmiş modeli taşınabilir formatta kaydeder. Yazılan dosyanın yolunu döner."""
    d = _artifacts_dizini()

    if model_adi == "XGBoost":
        yol = d / XGB_ADI
        model.save_model(str(yol))          # XGBClassifier -> UBJSON/JSON
        bicim = "xgboost_json"
    elif model_adi == "LightGBM":
        yol = d / LGB_ADI
        model.booster_.save_model(str(yol))  # LGBMClassifier -> metin formatı
        bicim = "lightgbm_txt"
    else:
        raise ValueError(f"Bilinmeyen model adı: {model_adi}")

    meta = {"model_adi": model_adi, "bicim": bicim, "dosya": yol.name, "ozellikler": list(ozellikler)}
    with open(d / META_ADI, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return str(yol)


def yukle(model_yolu=None):
    """Modeli diskten yükler.

    Döner: (model, model_adi, ozellikler)
    `model` nesnesi her durumda `predict_proba(X)` destekler.
    """
    d = _artifacts_dizini()
    meta_yolu = d / META_ADI

    if meta_yolu.exists():
        with open(meta_yolu, encoding="utf-8") as f:
            meta = json.load(f)
        dosya = Path(model_yolu) if model_yolu else d / meta["dosya"]

        if meta["bicim"] == "xgboost_json":
            import xgboost as xgb
            m = xgb.XGBClassifier()
            m.load_model(str(dosya))
            return m, meta["model_adi"], meta["ozellikler"]

        if meta["bicim"] == "lightgbm_txt":
            import lightgbm as lgb
            booster = lgb.Booster(model_file=str(dosya))
            return LGBMSarmalayici(booster), meta["model_adi"], meta["ozellikler"]

        raise ValueError(f"Bilinmeyen model biçimi: {meta['bicim']}")

    # --- Geriye dönük uyumluluk: eski pickle formatı ---
    eski = Path(model_yolu) if model_yolu else Path(paths.model_path())
    if eski.exists():
        import joblib
        paket = joblib.load(eski)   # aynı platformda eğitildiyse çalışır
        return paket["model"], paket["model_adi"], paket["ozellikler"]

    raise FileNotFoundError(
        f"Model bulunamadı. Önce eğitin:\n"
        f"    cd product/02-ai-agents && python -m aks_core.model.egitim\n"
        f"(aranan: {meta_yolu} veya {eski})"
    )
