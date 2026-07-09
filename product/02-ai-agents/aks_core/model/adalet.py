"""
Adalet / Önyargı Analizi (Fairness)
-----------------------------------
Modelin farklı gruplara (persona'lara) adil davranıp davranmadığını ölçer.
Sorumlu YZ prensibi: model, kişinin RESMİ STATÜSÜNE göre değil, GERÇEK
riskine göre karar vermeli.

Ölçülen metrikler (grup bazında):
- Onay oranı (AKS >= eşik)
- Gerçek pozitif oranı / TPR (kredibl olanların onaylanma oranı — equal opportunity)
- Yanlış onay oranı (temerrüde düşecek olanların yanlışlıkla onaylanması)

Ana adalet ölçüsü: kredibl kişiler arasında onaylanma oranı gruplar arasında
yakın olmalı (equal opportunity). Klasik skor bunu ihlal eder; AKS düzeltir.
"""
import numpy as np
from collections import defaultdict


def grup_metrikleri(musteriler, skor_alani="aks_skor", esik=650):
    """Persona bazında onay/TPR/yanlış-onay oranları."""
    gruplar = defaultdict(list)
    for m in musteriler:
        gruplar[m["persona"]].append(m)
    sonuc = {}
    for persona, uyeler in gruplar.items():
        onayli = [m for m in uyeler if m[skor_alani] >= esik]
        kredibl = [m for m in uyeler if m["temerrut"] == 0]
        kredibl_onayli = [m for m in kredibl if m[skor_alani] >= esik]
        temerrutlu = [m for m in uyeler if m["temerrut"] == 1]
        yanlis = [m for m in temerrutlu if m[skor_alani] >= esik]
        sonuc[persona] = {
            "n": len(uyeler),
            "onay_orani": round(len(onayli) / max(1, len(uyeler)), 3),
            "kredibl_onay_orani_tpr": round(len(kredibl_onayli) / max(1, len(kredibl)), 3),
            "yanlis_onay_orani": round(len(yanlis) / max(1, len(temerrutlu)), 3),
        }
    return sonuc


def adalet_raporu(musteriler, esikler={"klasik_skor": 680, "aks_skor": 650}):
    """Klasik vs AKS için equal-opportunity karşılaştırması.
    Boşluk (gap) = kredibl onay oranının gruplar arası max-min farkı; düşük = adil."""
    rapor = {}
    for alan, esik in esikler.items():
        gm = grup_metrikleri(musteriler, alan, esik)
        tprler = [v["kredibl_onay_orani_tpr"] for v in gm.values()]
        rapor[alan] = {
            "gruplar": gm,
            "equal_opportunity_boslugu": round(max(tprler) - min(tprler), 3),
        }
    return rapor
