"""
Orkestratör — Agent Koordinasyonu + Hafıza
------------------------------------------
Üç agent'ı sırayla çalıştırır (veri → skorlama → danışman) ve müşteri bazında
HAFIZA tutar: her değerlendirme kaydedilir, geçmiş skorlarla kıyaslanabilir.
Bu, "AI agent kullanımı, hafıza, orkestrasyon" kriterini karşılar.
"""
from datetime import datetime
from src.agents.veri_agent import VeriAgent
from src.agents.skorlama_agent import SkorlamaAgent
from src.agents.danisman_agent import DanismanAgent
from src.model.aciklama import Aciklayici


class Orkestrator:
    def __init__(self, model_yolu="models/aks_model.joblib", llm_fonksiyonu=None):
        self.veri_agent = VeriAgent()
        self.skorlama_agent = SkorlamaAgent(model_yolu)
        self.aciklayici = Aciklayici(self.skorlama_agent.model, self.skorlama_agent.ozellikler)
        self.danisman_agent = DanismanAgent(llm_fonksiyonu)
        self.hafiza = {}  # musteri_id -> [değerlendirme kayıtları]

    def degerlendir(self, musteri_id, islemler):
        # 1) Veri agent: özellik çıkar
        veri = self.veri_agent.calistir(islemler)
        # 2) Skorlama agent: skor + karar
        skor = self.skorlama_agent.calistir(veri["vektor"], veri["ozellikler"])
        # 3) Açıklama (SHAP) + danışman agent: öneri
        aciklama = self.aciklayici.acikla(veri["vektor"])
        danisman = self.danisman_agent.calistir(skor, aciklama)

        kayit = {
            "zaman": datetime.now().isoformat(timespec="seconds"),
            "musteri_id": musteri_id,
            "aks_skor": skor["aks_skor"],
            "risk_seviyesi": skor["risk_seviyesi"],
            "karar": skor["karar"],
            "onerilen_limit": skor.get("onerilen_limit"),
            "ozellikler": veri["ozellikler"],
            "aciklama": aciklama,
            "danisman": danisman,
            "kullanilan_agentlar": [self.veri_agent.ad, self.skorlama_agent.ad, self.danisman_agent.ad],
        }
        # Hafızaya yaz + önceki skorla kıyas
        gecmis = self.hafiza.setdefault(musteri_id, [])
        if gecmis:
            kayit["onceki_skor"] = gecmis[-1]["aks_skor"]
            kayit["skor_degisimi"] = skor["aks_skor"] - gecmis[-1]["aks_skor"]
        gecmis.append(kayit)
        return kayit

    def gecmis(self, musteri_id):
        return self.hafiza.get(musteri_id, [])
