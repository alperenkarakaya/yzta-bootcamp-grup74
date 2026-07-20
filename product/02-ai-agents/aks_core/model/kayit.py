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

Lojistik Regresyon (U8): XGBoost/LightGBM'in aksine LR saf NumPy/sklearn
durumu tutar, C++ bellek buffer'ı gömmez — joblib/pickle ile taşınabilir
şekilde kaydedilebilir (mandat: architecture.md §5.2, klasik model tercih
edilirse). Özellikleri standardize etmek için kullanılan `StandardScaler`
modelle BİRLİKTE kaydedilir; aksi halde canlı skorlamada ham (ölçeksiz)
vektör verilirse model sessizce yanlış tahmin üretir.
"""
import json
import os
from pathlib import Path

import numpy as np

from aks_core import paths

META_ADI = "aks_model_meta.json"
XGB_ADI = "aks_model.json"
LGB_ADI = "aks_model.txt"
LR_ADI = "aks_model_lr.joblib"
KALIB_ADI = "kalibrasyon.json"


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


class OlcekliLojistikSarmalayici:
    """LogisticRegression + fit edilmiş StandardScaler'ı tek `predict_proba` arayüzünde birleştirir.

    Skorlama katmanı (skorlama_agent.py) ham özellik vektörü verir; LR eğitim
    sırasında standardize edilmiş özelliklerle fit edildiği için, aynı ölçekleme
    tahmin anında da uygulanmalı — aksi halde sessiz/yanlış tahmin riski var.
    """

    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def predict_proba(self, X):
        return self.model.predict_proba(self.scaler.transform(X))


class KalibreliModel:
    """Temel modelin ham `predict_proba` çıktısına izotonik kalibrasyon uygular (U9).

    Kalibrasyon eğitim setinde (OOF) ölçülen ECE eşiği aşıldığında egitim.py
    tarafından fit edilir ve `kalibrasyon.json` olarak kaydedilir; burada
    varsa şeffafça sarmalanır. Yoksa `yukle()` temel modeli olduğu gibi döner.
    """

    def __init__(self, taban_model, kalib_tablo):
        self.taban_model = taban_model
        self.kalib_tablo = kalib_tablo

    def predict_proba(self, X):
        from aks_core.model import kalibrasyon
        ham = self.taban_model.predict_proba(np.asarray(X))[:, 1]
        p = kalibrasyon.apply_isotonic(ham, self.kalib_tablo)
        p = np.atleast_1d(p)
        return np.column_stack([1.0 - p, p])


def _artifacts_dizini() -> Path:
    d = Path(paths.ARTIFACTS_DIR)
    d.mkdir(parents=True, exist_ok=True)
    return d


def kalibrasyon_kaydet(tablo, dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else _artifacts_dizini() / KALIB_ADI
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(tablo, f, ensure_ascii=False, indent=2)
    return str(yol)


def kalibrasyon_yukle(dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else _artifacts_dizini() / KALIB_ADI
    if not yol.exists():
        return None
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def kaydet(model, model_adi: str, ozellikler: list, scaler=None) -> str:
    """Eğitilmiş modeli taşınabilir formatta kaydeder. Yazılan dosyanın yolunu döner.

    `scaler` yalnızca model_adi="LogisticRegression" için gerekli (fit edilmiş
    StandardScaler; tahmin anında aynı ölçekleme uygulanabilsin diye modelle
    birlikte kaydedilir).
    """
    d = _artifacts_dizini()

    if model_adi == "XGBoost":
        yol = d / XGB_ADI
        model.save_model(str(yol))          # XGBClassifier -> UBJSON/JSON
        bicim = "xgboost_json"
    elif model_adi == "LightGBM":
        yol = d / LGB_ADI
        model.booster_.save_model(str(yol))  # LGBMClassifier -> metin formatı
        bicim = "lightgbm_txt"
    elif model_adi == "LogisticRegression":
        import joblib
        if scaler is None:
            raise ValueError("LogisticRegression kaydı için `scaler` zorunlu")
        yol = d / LR_ADI
        joblib.dump({"model": model, "scaler": scaler}, yol)  # saf NumPy/sklearn -> platformdan bağımsız
        bicim = "logistic_joblib"
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
            taban = xgb.XGBClassifier()
            taban.load_model(str(dosya))
        elif meta["bicim"] == "lightgbm_txt":
            import lightgbm as lgb
            taban = LGBMSarmalayici(lgb.Booster(model_file=str(dosya)))
        elif meta["bicim"] == "logistic_joblib":
            import joblib
            paket = joblib.load(dosya)
            taban = OlcekliLojistikSarmalayici(paket["model"], paket["scaler"])
        else:
            raise ValueError(f"Bilinmeyen model biçimi: {meta['bicim']}")

        kalib = kalibrasyon_yukle()
        model = KalibreliModel(taban, kalib) if kalib is not None else taban
        return model, meta["model_adi"], meta["ozellikler"]

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
