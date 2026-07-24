"""
Anomali / Dağılım-Dışı (OOD) Tespiti
-------------------------------------
Denetimsiz bir İzolasyon Ormanı (Isolation Forest), bir müşterinin
davranışsal profilinin EĞİTİM DAĞILIMININ dışında kalıp kalmadığını
işaretler — "modelin hiç görmediği türden bir profile ne kadar
güvenilmeli" sorusuna, etiket gerektirmeyen bir şeffaflık sinyali ekler.

Sınır (boundary, overview.md §7): bu bir karar mekanizması DEĞİLDİR — skoru
veya kararı hiçbir şekilde değiştirmez, yalnızca ek bir bayrak/skor üretir.
Beş-soru testi (overview.md §6): LLM/agent değil, SHAP açıklayıcısıyla aynı
kategoride deterministik bir yardımcı istatistiksel bileşen.

Neden İzolasyon Ormanı: ölçeklendirme gerektirmez (ağaç-tabanlı), az
parametre, aykırı-değer tespitinde standart/yorumlanabilir bir başlangıç
noktası. Bu veri boyutunda (9 özellik, ~2000 satır) bir autoencoder vb.
gerekçelendirilemeyecek bir karmaşıklık artışı olurdu (mandat: eşitse/
yeterliyse basit yöntem kazanır).

Kalıcılık: IsolationForest saf NumPy/sklearn durumu tutar (XGBoost'un C++
buffer sorunu yok — kayit.py'deki LogisticRegression ile aynı gerekçe),
joblib ile taşınabilir şekilde kaydedilir.
"""
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest

from aks_core import paths

ANOMALI_ADI = "anomali_model.joblib"
KONTAMINASYON = 0.05  # eğitim verisinin ~%5'i "olağan dışı" kabul edilir


def egit(X, seed=42, kontaminasyon=KONTAMINASYON):
    model = IsolationForest(n_estimators=200, contamination=kontaminasyon, random_state=seed, n_jobs=-1)
    model.fit(np.asarray(X, dtype=float))
    return model


def kaydet(model, dosya_yolu=None):
    import joblib
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / ANOMALI_ADI
    yol.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, yol)
    return str(yol)


def yukle(dosya_yolu=None):
    """Model dosyası yoksa None döner — bu bileşen opsiyoneldir; eksikliği
    skorlamayı asla engellemez (kayit.py'deki kalibrasyon dosyasıyla aynı desen)."""
    import joblib
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / ANOMALI_ADI
    if not yol.exists():
        return None
    return joblib.load(yol)


def degerlendir(model, vektor):
    """Tek bir müşteri için (bayrak, tipiklik_skoru) döner.

    tipiklik_skoru: sklearn `score_samples()` ham çıktısı — negatife
    yaklaştıkça daha aykırı, 0'a yaklaştıkça daha tipik. KALİBRE BİR
    OLASILIK DEĞİLDİR, yalnızca göreli bir sıralama sinyalidir."""
    x = np.asarray(vektor, dtype=float).reshape(1, -1)
    bayrak = bool(model.predict(x)[0] == -1)
    skor = float(model.score_samples(x)[0])
    return bayrak, round(skor, 4)
