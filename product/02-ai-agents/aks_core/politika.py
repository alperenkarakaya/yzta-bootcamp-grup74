"""
Karar Mekanizması Politikası (U11)
-----------------------------------
AKS skorunu (300-850) risk seviyesi + karar + limit çarpanına çeviren bantlar,
tek, versiyonlanmış bir yerde. Öncesinde bu eşikler (720/620/540) ve limit
çarpanları (8/5/2/0) `skorlama_agent.py` içinde hardcoded'du, `is_etkisi.py`
de kendi `olasilik_to_aks()` kopyasını tutuyordu (drift riski).

Bu modül "karar mekanizması" değişikliği: kararın KENDİSİ değişmiyor (aynı
bantlar, aynı davranış), yalnızca tek, denetlenebilir/versiyonlanmış bir
kaynağa taşınıyor. Bankanın klasik skorunu asla ezmez/değiştirmez — bu
sadece AKS'nin KENDİ tamamlayıcı skoru için karar bandı konfigürasyonudur
(overview.md §7 sınırı burada değişmez).
"""

POLITIKA_SURUMU = "v1"

# Sıra önemli: yüksekten düşüğe, ilk eşleşen bant kullanılır.
SKOR_BANTLARI = [
    {"esik": 720, "seviye": "düşük risk",       "karar": "onaylanabilir (yüksek limit)",             "carpan": 8},
    {"esik": 620, "seviye": "orta-düşük risk",   "karar": "onaylanabilir (standart limit)",           "carpan": 5},
    {"esik": 540, "seviye": "orta risk",         "karar": "koşullu / düşük limitle onaylanabilir",    "carpan": 2},
    {"esik": 300, "seviye": "yüksek risk",       "karar": "ek teminat/gözden geçirme önerilir",       "carpan": 0},
]


def bant_bul(aks_skor):
    """AKS skoruna karşılık gelen politika bandını döner (seviye/karar/çarpan)."""
    for bant in SKOR_BANTLARI:
        if aks_skor >= bant["esik"]:
            return bant
    return SKOR_BANTLARI[-1]


def olarak_sozluk():
    """API/frontend'e taşınabilir, JSON-uyumlu politika özeti (Phase 2'de /api/politika)."""
    return {"surum": POLITIKA_SURUMU, "bantlar": SKOR_BANTLARI}
