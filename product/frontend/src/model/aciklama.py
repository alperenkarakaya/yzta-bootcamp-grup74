"""
Açıklanabilirlik (SHAP)
-----------------------
Bir kişinin AKS skorunu HANGİ davranışsal faktörlerin ne yönde etkilediğini
SHAP değerleriyle çıkarır. Çıktı, hem son kullanıcıya ("skorun neden böyle")
hem de danışman agent'a (öneri üretmek için) girdi olur.
"""
import numpy as np
import shap

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


class Aciklayici:
    def __init__(self, model, ozellikler):
        self.model = model
        self.ozellikler = ozellikler
        self.explainer = shap.TreeExplainer(model)

    def acikla(self, ozellik_vektoru, ilk_n=4):
        """Tek kişi için SHAP katkılarını döndürür.
        Dönüş: riski artıran ve azaltan ilk_n faktör (etiket + katkı)."""
        x = np.array(ozellik_vektoru, dtype=float).reshape(1, -1)
        sv = self.explainer.shap_values(x)
        if isinstance(sv, list):  # bazı sürümlerde liste
            sv = sv[1] if len(sv) > 1 else sv[0]
        katkilar = list(zip(self.ozellikler, sv[0]))
        # Pozitif SHAP = temerrüt riskini artırır (skoru düşürür)
        artiranlar = sorted([k for k in katkilar if k[1] > 0], key=lambda t: -t[1])[:ilk_n]
        azaltanlar = sorted([k for k in katkilar if k[1] < 0], key=lambda t: t[1])[:ilk_n]
        return {
            "riski_artiran": [{"faktor": OZELLIK_ETIKET.get(a, a), "kod": a, "etki": round(float(v), 4)} for a, v in artiranlar],
            "riski_azaltan": [{"faktor": OZELLIK_ETIKET.get(a, a), "kod": a, "etki": round(float(v), 4)} for a, v in azaltanlar],
        }
