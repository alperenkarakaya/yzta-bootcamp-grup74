"""
Açıklanabilirlik (SHAP)
-----------------------
Bir kişinin AKS skorunu HANGİ davranışsal faktörlerin ne yönde etkilediğini
SHAP değerleriyle çıkarır. Çıktı, hem son kullanıcıya ("skorun neden böyle")
hem de danışman agent'a (öneri üretmek için) girdi olur.

Model-agnostik açıklayıcı (§3b/U8 düzeltmesi): `shap.TreeExplainer` yalnızca
kütüphanenin tanıdığı ham ağaç nesnelerini (ör. `xgboost.Booster`) kabul eder
— `kayit.py`'nin taşınabilirlik/kalibrasyon sarmalayıcıları (`KalibreliModel`,
`OlcekliLojistikSarmalayici`, `LGBMSarmalayici`) veya doğrusal bir model
(LogisticRegression, mandat gereği kazanabilir — architecture.md §5.2) ile
sessizce/açıkça patlar. Bu gizli bir kusurdu: XGBoost her zaman kazandığı
sürece görünmüyordu. Artık sarmalayıcı katmanları açılıp gerçek model tipine
göre doğru SHAP algoritması seçiliyor (ağaç -> TreeExplainer, tam/kesin;
doğrusal -> LinearExplainer, arka plan örneğiyle).

İzotonik kalibrasyon (U9) MONOTONİK olduğundan, kalibrasyon öncesi ham model
üzerinden hesaplanan SHAP katkılarının YÖNÜ ve SIRASI değişmez — yalnızca son
olasılık ölçeği değişir. Reason-code amaçlı (en etkili N faktör) bu nedenle
kalibrasyon öncesi (taban) modeli açıklamak yeterli ve doğrudur.
"""
import json
import numpy as np
import shap

from aks_core import paths
from aks_core.model.kayit import KalibreliModel, OlcekliLojistikSarmalayici, LGBMSarmalayici

# Özellik -> insan-okur açıklama ve yön (pozitif SHAP = riski artırır)
OZELLIK_ETIKET = {
    "toplam_gelir_hacmi": "toplam gelir hacmi",
    "toplam_gider_hacmi": "toplam gider hacmi",
    "gelir_islem_sayisi": "gelir işlem sıklığı",
    "gelir_kaynagi_sayisi": "gelir kaynağı çeşitliliği",
    "gelir_duzenliligi": "gelir düzenliliği",
    "gider_gelir_orani": "gider/gelir oranı",
    "bakiye_trendi": "bakiye trendi (tasarruf eğilimi)",
    "fatura_odeme_duzeni": "fatura ödeme düzeni",
    "hesap_hareket_yogunlugu": "hesap hareket yoğunluğu",
}

ARKA_PLAN_ADI = "arka_plan_ornek.json"


def arka_plan_kaydet(X_ornek, dosya_yolu=None):
    """Eğitimden (egitim.py) küçük, temsili bir ham-özellik örneği kaydeder —
    doğrusal modeller için SHAP arka planı (ağaç modelleri buna ihtiyaç duymaz)."""
    yol = dosya_yolu or (paths.ARTIFACTS_DIR / ARKA_PLAN_ADI)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(np.asarray(X_ornek, dtype=float).tolist(), f)
    return str(yol)


def _arka_plan_yukle(ozellik_sayisi, dosya_yolu=None):
    yol = dosya_yolu or (paths.ARTIFACTS_DIR / ARKA_PLAN_ADI)
    try:
        with open(yol, encoding="utf-8") as f:
            return np.array(json.load(f), dtype=float)
    except FileNotFoundError:
        # Geriye dönük uyumluluk: arka plan artifact'i olmayan eski bir model.
        # Sıfır-vektör arka plan; kalite düşer ama patlamaz.
        return np.zeros((1, ozellik_sayisi))


def _taban_model(model):
    return model.taban_model if isinstance(model, KalibreliModel) else model


class Aciklayici:
    def __init__(self, model, ozellikler):
        self.model = model
        self.ozellikler = ozellikler
        self._olcekleyici = None

        taban = _taban_model(model)
        if isinstance(taban, OlcekliLojistikSarmalayici):
            arka_plan = _arka_plan_yukle(len(ozellikler))
            self._olcekleyici = taban.scaler
            self.explainer = shap.LinearExplainer(taban.model, taban.scaler.transform(arka_plan))
        elif isinstance(taban, LGBMSarmalayici):
            self.explainer = shap.TreeExplainer(taban.booster)
        else:
            self.explainer = shap.TreeExplainer(taban)  # XGBoost — doğrudan destekleniyor

    def acikla(self, ozellik_vektoru, ilk_n=4):
        """Tek kişi için SHAP katkılarını döndürür.
        Dönüş: riski artıran ve azaltan ilk_n faktör (etiket + katkı)."""
        x = np.array(ozellik_vektoru, dtype=float).reshape(1, -1)
        x_acikla = self._olcekleyici.transform(x) if self._olcekleyici is not None else x
        sv = self.explainer.shap_values(x_acikla)
        if isinstance(sv, list):  # bazı sürümlerde liste
            sv = sv[1] if len(sv) > 1 else sv[0]
        katkilar = list(zip(self.ozellikler, np.asarray(sv)[0]))
        # Pozitif SHAP = temerrüt riskini artırır (skoru düşürür)
        artiranlar = sorted([k for k in katkilar if k[1] > 0], key=lambda t: -t[1])[:ilk_n]
        azaltanlar = sorted([k for k in katkilar if k[1] < 0], key=lambda t: t[1])[:ilk_n]
        return {
            "riski_artiran": [{"faktor": OZELLIK_ETIKET.get(a, a), "kod": a, "etki": round(float(v), 4)} for a, v in artiranlar],
            "riski_azaltan": [{"faktor": OZELLIK_ETIKET.get(a, a), "kod": a, "etki": round(float(v), 4)} for a, v in azaltanlar],
        }
