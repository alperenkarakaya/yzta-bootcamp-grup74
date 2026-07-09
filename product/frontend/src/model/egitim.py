"""
Model Eğitimi: XGBoost & LightGBM vs Klasik Skor
-------------------------------------------------
Davranışsal özelliklerle temerrüt (default) tahmini yapan denetimli modeller
eğitir ve mevcut sistemi temsil eden 'klasik skor' baseline'ı ile karşılaştırır.

Ana metrik: ROC-AUC (temerrüt sıralama gücü). Hedef, davranışsal modelin
klasik skordan daha yüksek AUC almasını ve klasik skorun haksızca reddettiği
disiplinli düşük-gelirli kişileri doğru şekilde 'düşük risk' sınıflamasını
göstermektir.
"""
import argparse, csv, json, os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
import xgboost as xgb
import lightgbm as lgb
import joblib

from src.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI
from src.model.etiketleme import etiketle


def klasik_risk_skoru(m):
    """Mevcut sistemi taklit eden baseline: resmi statü (persona) + gelir hacmi.
    Yüksek skor = düşük risk. Temerrüt tahmini için risk = (850 - skor)."""
    taban = 500
    if m["persona"] == "klasik_maasli": taban += 200
    elif m["persona"] == "stajyer_degisken_gelir": taban += 40
    elif m["persona"] == "ogrenci_yuksek_hacim": taban += 10
    skor = taban + m["toplam_gelir_hacmi"] * 0.001
    return int(max(300, min(850, skor)))


def veri_hazirla(islem_csv, egitim_csv_cikti=None, hedef_oran=0.18):
    musteriler = etiketle(tum_musteriler(islem_csv), hedef_temerrut_orani=hedef_oran)
    if egitim_csv_cikti:
        alanlar = ["musteri_id", "persona"] + OZELLIK_ADLARI + ["klasik_skor", "temerrut_olasiligi_gercek", "temerrut"]
        for m in musteriler:
            m["klasik_skor"] = klasik_risk_skoru(m)
        with open(egitim_csv_cikti, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
            w.writeheader(); w.writerows(musteriler)
    return musteriler


def egit(islem_csv="data/sentetik_islemler.csv", model_cikti="models/aks_model.joblib"):
    musteriler = veri_hazirla(islem_csv, "data/egitim_verisi.csv")
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    y = np.array([m["temerrut"] for m in musteriler])
    klasik = np.array([klasik_risk_skoru(m) for m in musteriler], dtype=float)

    Xtr, Xte, ytr, yte, ktr, kte = train_test_split(X, y, klasik, test_size=0.30, random_state=42, stratify=y)

    pos = max(1, ytr.sum()); neg = len(ytr) - pos
    scale = neg / pos

    xgb_m = xgb.XGBClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.9,
        colsample_bytree=0.9, scale_pos_weight=scale, eval_metric="auc",
        random_state=42, n_jobs=-1)
    xgb_m.fit(Xtr, ytr)

    lgb_m = lgb.LGBMClassifier(
        n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.9,
        colsample_bytree=0.9, class_weight="balanced", random_state=42,
        n_jobs=-1, verbose=-1)
    lgb_m.fit(Xtr, ytr)

    p_xgb = xgb_m.predict_proba(Xte)[:, 1]
    p_lgb = lgb_m.predict_proba(Xte)[:, 1]
    # Klasik skor bir risk tahmincisi olarak: yüksek skor=düşük risk -> risk=(850-skor)
    p_klasik = (850 - kte)

    sonuc = {
        "XGBoost":      {"auc": roc_auc_score(yte, p_xgb), "ap": average_precision_score(yte, p_xgb)},
        "LightGBM":     {"auc": roc_auc_score(yte, p_lgb), "ap": average_precision_score(yte, p_lgb)},
        "Klasik skor":  {"auc": roc_auc_score(yte, p_klasik), "ap": average_precision_score(yte, p_klasik)},
    }

    print(f"\n{'Model':<16}{'ROC-AUC':<12}{'PR-AUC':<12}")
    print("-" * 40)
    for ad, s in sonuc.items():
        print(f"{ad:<16}{s['auc']:<12.4f}{s['ap']:<12.4f}")
    print("-" * 40)
    en_iyi = max([("XGBoost", xgb_m, p_xgb), ("LightGBM", lgb_m, p_lgb)], key=lambda t: roc_auc_score(yte, t[2]))
    print(f"En iyi model: {en_iyi[0]} (AUC {roc_auc_score(yte, en_iyi[2]):.4f})")
    kazanc = sonuc[en_iyi[0]]["auc"] - sonuc["Klasik skor"]["auc"]
    print(f"Klasik skora göre AUC kazancı: +{kazanc:.4f}")

    # Kaydet
    os.makedirs(os.path.dirname(model_cikti), exist_ok=True)
    joblib.dump({"model": en_iyi[1], "model_adi": en_iyi[0], "ozellikler": OZELLIK_ADLARI}, model_cikti)
    with open("models/metrikler.json", "w", encoding="utf-8") as f:
        json.dump({k: {m: round(v, 4) for m, v in val.items()} for k, val in sonuc.items()}, f, ensure_ascii=False, indent=2)
    print(f"\nModel kaydedildi -> {model_cikti}")
    return sonuc


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--girdi", default="data/sentetik_islemler.csv")
    p.add_argument("--model-cikti", default="models/aks_model.joblib")
    a = p.parse_args()
    egit(a.girdi, a.model_cikti)
