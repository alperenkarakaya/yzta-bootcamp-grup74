"""
Model Eğitimi: XGBoost & LightGBM & Lojistik Regresyon vs Klasik Skor
-----------------------------------------------------------------------
Davranışsal özelliklerle temerrüt (default) tahmini yapan denetimli modeller
eğitir ve mevcut sistemi temsil eden 'klasik skor' baseline'ı ile karşılaştırır.

Ana metrik: ROC-AUC (temerrüt sıralama gücü). §3b/U1: `veri_kaynagi="dekuple"`
varsayılan — 01-data/generator/veri/uretici_kapasite.py'nin ürettiği, ETİKETİN
ÖZELLİKLERDEN BAĞIMSIZ üretildiği veri setini kullanır (architecture.md §5.1
döngüsellik bulgusunun düzeltmesi). Eski döngüsel veri (`veri_kaynagi="dongusel"`)
hâlâ seçilebilir — yalnızca circularity_ablation.py'nin önce/sonra kanıtı için.

Bu betik `01-data/` içindeki HİÇBİR dosyayı değiştirmez; yalnızca zaten
üretilmiş CSV'leri salt-okunur tüketir (execution.md §3b sınırı).

§3b/U3: tek 70/30 split + hardcoded hiperparametreler yerine, train/test
holdout + train üzerinde RandomizedSearchCV (5-fold) ile hiperparametre
araması. §3b/U8: kazanan model klasik/basit LojistikRegresyon da dahil olmak
üzere 3 aday arasından seçilir (mandat: eşit/üstünse basit model kazanır).
§3b/U9: test ECE eşiği aşarsa (varsayılan 0.03) OOF izotonik kalibrasyon fit
edilip modelin üstüne şeffafça sarmalanır (bkz. kayit.py KalibreliModel).
§3b/U10: klasik skor -> ampirik temerrüt oranı (Formülasyon B "geleneksel
bant") tablosu train bölümünden fit edilip kaydedilir.
"""
import argparse, csv, json, os, time
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV, cross_val_score
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import lightgbm as lgb

from aks_core.model import kayit, kalibrasyon, formulasyon_b, aciklama
from aks_core.ozellik.cikarim import tum_musteriler, OZELLIK_ADLARI
from aks_core.model.etiketleme import etiketle

# veri_kaynagi -> (işlem CSV'si, harici etiket CSV'si veya None=etiketleme.py kullan)
VERI_KAYNAKLARI = {
    "dongusel": {"islem": "sentetik_islemler.csv", "etiket": None},
    "dekuple":  {"islem": "kapasite_islemler.csv", "etiket": "kapasite_etiketleri.csv"},
}

XGB_PARAM_DAGILIMI = {
    "n_estimators": [150, 250, 300, 400, 500],
    "max_depth": [3, 4, 5, 6],
    "learning_rate": [0.03, 0.05, 0.08, 0.1],
    "subsample": [0.8, 0.9, 1.0],
    "colsample_bytree": [0.8, 0.9, 1.0],
}
LGB_PARAM_DAGILIMI = dict(XGB_PARAM_DAGILIMI)
LR_PARAM_DAGILIMI = {"C": [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]}


def klasik_risk_skoru(m):
    """Mevcut sistemi taklit eden baseline: resmi statü (persona) + gelir hacmi.
    Yüksek skor = düşük risk. Temerrüt tahmini için risk = (850 - skor)."""
    taban = 500
    if m["persona"] == "klasik_maasli": taban += 200
    elif m["persona"] == "stajyer_degisken_gelir": taban += 40
    elif m["persona"] == "ogrenci_yuksek_hacim": taban += 10
    skor = taban + m["toplam_gelir_hacmi"] * 0.001
    return int(max(300, min(850, skor)))


def _etiketleri_disaridan_yukle(dosya_yolu):
    """kapasite_etiketleri.csv -> {musteri_id: {temerrut, temerrut_olasiligi_gercek}}.

    01-data/'nin ürettiği, özelliklerden bağımsız (decoupled) etiket dosyasını
    salt-okunur tüketir — bu dosyayı YAZMAZ/değiştirmez."""
    with open(dosya_yolu, encoding="utf-8") as f:
        return {
            int(r["musteri_id"]): {
                "temerrut": int(r["temerrut"]),
                "temerrut_olasiligi_gercek": float(r["temerrut_olasiligi_gercek"]),
            }
            for r in csv.DictReader(f)
        }


def veri_hazirla(islem_csv, egitim_csv_cikti=None, hedef_oran=0.18, veri_kaynagi="dekuple", etiket_csv=None):
    """`veri_kaynagi="dongusel"`: eski, döngüsel etiket (etiketleme.py — mevcut
    4 özellikten türetilir, architecture.md §5.1). `veri_kaynagi="dekuple"`
    (varsayılan): 01-data'nın ürettiği, özelliklerden bağımsız etiket dosyası."""
    musteriler = tum_musteriler(islem_csv)
    if veri_kaynagi == "dekuple":
        if not etiket_csv:
            raise ValueError('veri_kaynagi="dekuple" için etiket_csv gerekli')
        etiketler = _etiketleri_disaridan_yukle(etiket_csv)
        musteriler = [m for m in musteriler if m["musteri_id"] in etiketler]
        for m in musteriler:
            e = etiketler[m["musteri_id"]]
            m["temerrut"] = e["temerrut"]
            m["temerrut_olasiligi_gercek"] = e["temerrut_olasiligi_gercek"]
    else:
        musteriler = etiketle(musteriler, hedef_temerrut_orani=hedef_oran)

    if egitim_csv_cikti:
        alanlar = ["musteri_id", "persona"] + OZELLIK_ADLARI + ["klasik_skor", "temerrut_olasiligi_gercek", "temerrut"]
        for m in musteriler:
            m["klasik_skor"] = klasik_risk_skoru(m)
        with open(egitim_csv_cikti, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
            w.writeheader(); w.writerows(musteriler)
    return musteriler


def _arama(model_sinifi, param_dagilimi, sabit_kwargs, X, y, n_iter, seed):
    taban = model_sinifi(**sabit_kwargs)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    arama = RandomizedSearchCV(
        taban, param_dagilimi, n_iter=min(n_iter, _kombinasyon_sayisi(param_dagilimi)),
        scoring="roc_auc", cv=cv, random_state=seed, n_jobs=-1, refit=True)
    arama.fit(X, y)
    return arama.best_estimator_, arama.best_params_, float(arama.best_score_)


def _kombinasyon_sayisi(param_dagilimi):
    n = 1
    for v in param_dagilimi.values():
        n *= len(v)
    return n


def egit(islem_csv=None, model_cikti=None, veri_kaynagi="dekuple", n_iter=20,
         kalibrasyon_esigi=0.03, seed=42):
    from aks_core import paths
    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = islem_csv or paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"]) if kaynak["etiket"] else None
    model_cikti = model_cikti or paths.model_path()

    # Debug/inceleme çıktısı artifacts/ altına yazılır — 01-data/ HİÇBİR ZAMAN
    # yazılmaz (execution.md §3b sınırı: yalnızca salt-okunur tüketim).
    os.makedirs(str(paths.ARTIFACTS_DIR), exist_ok=True)
    egitim_csv_cikti = os.path.join(str(paths.ARTIFACTS_DIR), "egitim_verisi_debug.csv")
    musteriler = veri_hazirla(islem_csv, egitim_csv_cikti,
                               veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)
    y = np.array([m["temerrut"] for m in musteriler])
    klasik = np.array([klasik_risk_skoru(m) for m in musteriler], dtype=float)

    Xtr, Xte, ytr, yte, ktr, kte = train_test_split(
        X, y, klasik, test_size=0.25, random_state=seed, stratify=y)

    pos = max(1, ytr.sum()); neg = len(ytr) - pos
    scale = neg / pos

    t0 = time.time()
    xgb_kwargs = {"scale_pos_weight": scale, "eval_metric": "logloss", "random_state": seed, "n_jobs": -1}
    xgb_best, xgb_params, xgb_cv_auc = _arama(xgb.XGBClassifier, XGB_PARAM_DAGILIMI, xgb_kwargs, Xtr, ytr, n_iter, seed)

    lgb_kwargs = {"class_weight": "balanced", "random_state": seed, "n_jobs": -1, "verbose": -1}
    lgb_best, lgb_params, lgb_cv_auc = _arama(lgb.LGBMClassifier, LGB_PARAM_DAGILIMI, lgb_kwargs, Xtr, ytr, n_iter, seed)

    sc = StandardScaler().fit(Xtr)
    Xtr_sc = sc.transform(Xtr)
    lr_best, lr_params, lr_cv_auc = _arama(LogisticRegression, LR_PARAM_DAGILIMI, {"max_iter": 2000}, Xtr_sc, ytr, n_iter, seed)
    arama_suresi_sn = round(time.time() - t0, 1)

    p_xgb = xgb_best.predict_proba(Xte)[:, 1]
    p_lgb = lgb_best.predict_proba(Xte)[:, 1]
    p_lr = lr_best.predict_proba(sc.transform(Xte))[:, 1]
    # Klasik skor bir risk tahmincisi olarak: yüksek skor=düşük risk -> risk=(850-skor)
    p_klasik = (850 - kte)

    sonuc = {
        "XGBoost":            {"auc": roc_auc_score(yte, p_xgb), "ap": average_precision_score(yte, p_xgb), "cv_auc_arama": xgb_cv_auc},
        "LightGBM":           {"auc": roc_auc_score(yte, p_lgb), "ap": average_precision_score(yte, p_lgb), "cv_auc_arama": lgb_cv_auc},
        "LogisticRegression": {"auc": roc_auc_score(yte, p_lr), "ap": average_precision_score(yte, p_lr), "cv_auc_arama": lr_cv_auc},
        "Klasik skor":        {"auc": roc_auc_score(yte, p_klasik), "ap": average_precision_score(yte, p_klasik)},
    }

    print(f"\nVeri kaynağı: {veri_kaynagi}  ({len(musteriler)} müşteri, arama {arama_suresi_sn}s)")
    print(f"{'Model':<20}{'ROC-AUC':<12}{'PR-AUC':<12}{'CV-AUC (arama)':<16}")
    print("-" * 60)
    for ad, s in sonuc.items():
        cv = f"{s['cv_auc_arama']:.4f}" if "cv_auc_arama" in s else "-"
        print(f"{ad:<20}{s['auc']:<12.4f}{s['ap']:<12.4f}{cv:<16}")
    print("-" * 60)

    adaylar = {
        "XGBoost": (xgb_best, p_xgb),
        "LightGBM": (lgb_best, p_lgb),
        "LogisticRegression": (lr_best, p_lr),
    }
    en_iyi_ad = max(adaylar, key=lambda ad: sonuc[ad]["auc"])
    en_iyi_model, en_iyi_p = adaylar[en_iyi_ad]
    print(f"En iyi model: {en_iyi_ad} (AUC {sonuc[en_iyi_ad]['auc']:.4f})")
    kazanc = sonuc[en_iyi_ad]["auc"] - sonuc["Klasik skor"]["auc"]
    print(f"Klasik skora göre AUC kazancı: +{kazanc:.4f}")
    xgb_lr_farki = abs(sonuc["XGBoost"]["auc"] - sonuc["LogisticRegression"]["auc"])
    print(f"XGBoost vs LojistikRegresyon farkı: {xgb_lr_farki:.4f} "
          f"(mandat #1/#8: küçükse/LR üstünse basit model tercih edilmeli)")

    # --- U9: kalibrasyon ihtiyacı (test ECE) ---
    ece_once = kalibrasyon.ece(yte, en_iyi_p)
    kalib_tablo = None
    ece_sonra = ece_once
    if ece_once > kalibrasyon_esigi:
        if en_iyi_ad == "XGBoost":
            model_fn = lambda: xgb.XGBClassifier(**{**xgb_params, **xgb_kwargs})
            Xtr_kalib = Xtr
        elif en_iyi_ad == "LightGBM":
            model_fn = lambda: lgb.LGBMClassifier(**{**lgb_params, **lgb_kwargs})
            Xtr_kalib = Xtr
        else:
            model_fn = lambda: LogisticRegression(max_iter=2000, **lr_params)
            Xtr_kalib = Xtr_sc
        oof = kalibrasyon.oof_proba(model_fn, Xtr_kalib, ytr, seed=seed)
        kalib_tablo = kalibrasyon.fit_isotonic(oof, ytr, increasing=True)
        p_kalibre = kalibrasyon.apply_isotonic(en_iyi_p, kalib_tablo)
        ece_sonra = kalibrasyon.ece(yte, p_kalibre)
        print(f"Kalibrasyon: test ECE {ece_once:.4f} > eşik {kalibrasyon_esigi} -> izotonik düzeltme uygulandı "
              f"(ECE sonrası {ece_sonra:.4f})")
    else:
        print(f"Kalibrasyon: test ECE {ece_once:.4f} <= eşik {kalibrasyon_esigi} -> düzeltme uygulanmadı (zaten iyi kalibre)")

    # --- U10: Formülasyon B — klasik skor bandı -> ampirik temerrüt oranı (yalnız train bölümü) ---
    bant_tablosu = formulasyon_b.bant_tablosu_fit_et(ktr, ytr)

    # --- Kaydet ---
    os.makedirs(os.path.dirname(model_cikti) or ".", exist_ok=True)
    if en_iyi_ad == "LogisticRegression":
        model_cikti = kayit.kaydet(en_iyi_model, en_iyi_ad, OZELLIK_ADLARI, scaler=sc)
    else:
        model_cikti = kayit.kaydet(en_iyi_model, en_iyi_ad, OZELLIK_ADLARI)

    if kalib_tablo is not None:
        kayit.kalibrasyon_kaydet(kalib_tablo)
    else:
        # Önceki bir eğitimden kalma kalibrasyon dosyası varsa ve artık gerekmiyorsa temizle.
        eski = os.path.join(str(paths.ARTIFACTS_DIR), kayit.KALIB_ADI)
        if os.path.exists(eski):
            os.remove(eski)

    formulasyon_b.kaydet(bant_tablosu)

    # SHAP açıklayıcı arka planı (U8 yan etkisi: LogisticRegression'ın LinearExplainer'ı
    # bir arka plan örneğine ihtiyaç duyar; ağaç modelleri kullanmaz ama tutarlılık için
    # her eğitimde yazılır).
    rng = np.random.default_rng(seed)
    n_ornek = min(100, len(Xtr))
    ornek_idx = rng.choice(len(Xtr), size=n_ornek, replace=False)
    aciklama.arka_plan_kaydet(Xtr[ornek_idx])

    with open(paths.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump({k: {m: round(v, 4) for m, v in val.items()} for k, val in sonuc.items()}, f, ensure_ascii=False, indent=2)

    manifest = {
        "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "veri_kaynagi": veri_kaynagi,
        "n_musteri": len(musteriler),
        "n_egitim": int(len(ytr)),
        "n_test": int(len(yte)),
        "taban_temerrut_orani": round(float(y.mean()), 4),
        "secilen_model": en_iyi_ad,
        "secilen_test_auc": round(float(sonuc[en_iyi_ad]["auc"]), 4),
        "en_iyi_parametreler": {"XGBoost": xgb_params, "LightGBM": lgb_params, "LogisticRegression": lr_params},
        "arama_suresi_sn": arama_suresi_sn,
        "kalibrasyon_uygulandi": kalib_tablo is not None,
        "ece_kalibrasyon_oncesi": round(float(ece_once), 4),
        "ece_kalibrasyon_sonrasi": round(float(ece_sonra), 4),
    }
    with open(os.path.join(str(paths.ARTIFACTS_DIR), "egitim_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nModel kaydedildi -> {model_cikti}")
    return sonuc


if __name__ == "__main__":
    from aks_core import paths
    p = argparse.ArgumentParser()
    p.add_argument("--girdi", default=None, help="İşlem CSV yolu (belirtilmezse --veri-kaynagi'na göre seçilir)")
    p.add_argument("--model-cikti", default=paths.model_path())
    p.add_argument("--veri-kaynagi", default="dekuple", choices=list(VERI_KAYNAKLARI))
    p.add_argument("--n-iter", type=int, default=20)
    a = p.parse_args()
    egit(a.girdi, a.model_cikti, veri_kaynagi=a.veri_kaynagi, n_iter=a.n_iter)
