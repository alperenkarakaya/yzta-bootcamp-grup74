"""
Agent 2 — Skorlama/Karar Agent
------------------------------
Sorumluluk: Özellik vektörünü eğitilmiş ML modeline verir, temerrüt
olasılığını 300-850 AKS skoruna çevirir; risk seviyesi, kredi kararı ve
ÖNERİLEN KREDİ LİMİTİ üretir.

Limit mantığı: aylık net nakit akışı (gelir - gider, aylık ortalama) taban
alınır; risk düştükçe çarpan büyür. Temerrüt olasılığı yüksekse limit 0'a iner.

Karar bantları (eşikler + limit çarpanları) artık `aks_core.politika`
içinde, tek/versiyonlanmış bir yerde (U11) — burada hardcoded değiller.
Bu, AKS'nin KENDİ tamamlayıcı skoru için konfigürasyon; bankanın klasik
skorunu asla ezmez/değiştirmez (overview.md §7).
"""
import numpy as np

from aks_core import politika


def olasilik_to_aks(p):
    return int(max(300, min(850, round(850 - 550 * p))))


def limit_oner(aks_skor, ozellikler):
    """Aylık net nakit akışına ve risk seviyesine göre önerilen kredi limiti (TL)."""
    aylik_gelir = ozellikler["toplam_gelir_hacmi"] / 6.0   # 180 gün ≈ 6 ay
    aylik_gider = ozellikler["toplam_gider_hacmi"] / 6.0
    net_akis = max(0.0, aylik_gelir - aylik_gider)
    carpan = politika.bant_bul(aks_skor)["carpan"]
    limit = net_akis * carpan
    return int(round(limit / 500) * 500)  # 500 TL'ye yuvarla


class SkorlamaAgent:
    ad = "skorlama_agent"

    def __init__(self, model_yolu=None):
        from aks_core.model import kayit
        self.model, self.model_adi, self.ozellikler = kayit.yukle(model_yolu)

    def calistir(self, vektor, ozellik_sozlugu=None, klasik_skor=None):
        """klasik_skor verilirse (Phase 2/backend zaten hesaplıyor), Formülasyon B
        alanları (pd_geleneksel_bant/pd_fark/kapasite_sinyali) da eklenir — bkz.
        architecture.md §5.3. Verilmezse bu alanlar hiç üretilmez (geriye dönük
        uyumlu; mevcut çağıranlar etkilenmez)."""
        x = np.array(vektor, dtype=float).reshape(1, -1)
        p = float(self.model.predict_proba(x)[0, 1])
        aks = olasilik_to_aks(p)
        bant = politika.bant_bul(aks)
        sonuc = {
            "aks_skor": aks,
            "temerrut_olasiligi": round(p, 4),
            "risk_seviyesi": bant["seviye"],
            "karar": bant["karar"],
            "model": self.model_adi,
        }
        if ozellik_sozlugu:
            sonuc["onerilen_limit"] = limit_oner(aks, ozellik_sozlugu)
        if klasik_skor is not None:
            from aks_core.model import formulasyon_b
            sonuc.update(formulasyon_b.hesapla(klasik_skor, p))
        return sonuc
