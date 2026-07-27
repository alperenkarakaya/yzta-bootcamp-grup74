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
        # Çağıranın listesini/sözlüklerini MUTATE ETMEZ — kopya üzerinde çalışır.
        # (Bulundu: bu fonksiyon eskiden `islemler` içindeki her dict'e doğrudan
        # `tarih_obj` (bir `datetime` nesnesi) yazıyordu; çağıran taraf aynı
        # referansı sonradan ham veri olarak saklamaya/serialize etmeye çalışınca
        # "datetime is not JSON serializable" hatasıyla patlıyordu — bkz.
        # api/services.py::_denetim_yaz, Assessment.ham_islemler.)
        calisma = [dict(i) for i in islemler]
        for i in calisma:
            i["tarih_obj"] = datetime.strptime(i["tarih"], "%Y-%m-%d")
            i["tutar"] = float(i["tutar"])
        ozellikler = ozellik_cikar(calisma)
        return {
            "ozellikler": ozellikler,
            "vektor": [ozellikler[o] for o in OZELLIK_ADLARI],
            "islem_sayisi": len(islemler),
        }
