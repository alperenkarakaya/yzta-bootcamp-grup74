"""
Agent 1 — Veri/Özellik Agent
----------------------------
Sorumluluk: Ham banka işlem (transaction) kayıtlarını alır, davranışsal
özellik vektörüne dönüştürür. Pipeline'ın giriş katmanı.
"""
from aks_core.ozellik.cikarim import ozellik_cikar, OZELLIK_ADLARI
from datetime import datetime


class VeriAgent:
    ad = "veri_agent"

    def calistir(self, islemler):
        # Tarih alanını normalize et (API'den string gelebilir)
        for i in islemler:
            if "tarih_obj" not in i:
                i["tarih_obj"] = datetime.strptime(i["tarih"], "%Y-%m-%d")
            i["tutar"] = float(i["tutar"])
        ozellikler = ozellik_cikar(islemler)
        return {
            "ozellikler": ozellikler,
            "vektor": [ozellikler[o] for o in OZELLIK_ADLARI],
            "islem_sayisi": len(islemler),
        }
