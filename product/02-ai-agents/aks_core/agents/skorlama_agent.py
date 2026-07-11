"""
Agent 2 — Skorlama/Karar Agent
------------------------------
Sorumluluk: Özellik vektörünü eğitilmiş ML modeline verir, temerrüt
olasılığını 300-850 AKS skoruna çevirir; risk seviyesi, kredi kararı ve
ÖNERİLEN KREDİ LİMİTİ üretir.

Limit mantığı: aylık net nakit akışı (gelir - gider, aylık ortalama) taban
alınır; risk düştükçe çarpan büyür. Temerrüt olasılığı yüksekse limit 0'a iner.
"""
import numpy as np


def olasilik_to_aks(p):
    return int(max(300, min(850, round(850 - 550 * p))))


def limit_oner(aks_skor, ozellikler):
    """Aylık net nakit akışına ve risk seviyesine göre önerilen kredi limiti (TL)."""
    aylik_gelir = ozellikler["toplam_gelir_hacmi"] / 6.0   # 180 gün ≈ 6 ay
    aylik_gider = ozellikler["toplam_gider_hacmi"] / 6.0
    net_akis = max(0.0, aylik_gelir - aylik_gider)
    if aks_skor >= 720:   carpan = 8
    elif aks_skor >= 620: carpan = 5
    elif aks_skor >= 540: carpan = 2
    else:                 carpan = 0
    limit = net_akis * carpan
    return int(round(limit / 500) * 500)  # 500 TL'ye yuvarla


class SkorlamaAgent:
    ad = "skorlama_agent"

    def __init__(self, model_yolu=None):
        from aks_core.model import kayit
        self.model, self.model_adi, self.ozellikler = kayit.yukle(model_yolu)

    def calistir(self, vektor, ozellik_sozlugu=None):
        x = np.array(vektor, dtype=float).reshape(1, -1)
        p = float(self.model.predict_proba(x)[0, 1])
        aks = olasilik_to_aks(p)
        if aks >= 720:
            seviye, karar = "düşük risk", "onaylanabilir (yüksek limit)"
        elif aks >= 620:
            seviye, karar = "orta-düşük risk", "onaylanabilir (standart limit)"
        elif aks >= 540:
            seviye, karar = "orta risk", "koşullu / düşük limitle onaylanabilir"
        else:
            seviye, karar = "yüksek risk", "ek teminat/gözden geçirme önerilir"
        sonuc = {
            "aks_skor": aks,
            "temerrut_olasiligi": round(p, 4),
            "risk_seviyesi": seviye,
            "karar": karar,
            "model": self.model_adi,
        }
        if ozellik_sozlugu:
            sonuc["onerilen_limit"] = limit_oner(aks, ozellik_sozlugu)
        return sonuc
