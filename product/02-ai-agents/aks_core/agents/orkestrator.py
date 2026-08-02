"""
Orkestratör — Agent Koordinasyonu + Hafıza
------------------------------------------
Üç agent'ı sırayla çalıştırır (veri → skorlama → danışman) ve müşteri bazında
HAFIZA tutar: her değerlendirme kaydedilir, geçmiş skorlarla kıyaslanabilir.
Bu, "AI agent kullanımı, hafıza, orkestrasyon" kriterini karşılar.
"""
from datetime import datetime
from aks_core.agents.veri_agent import VeriAgent
from aks_core.agents.skorlama_agent import SkorlamaAgent
from aks_core.agents.danisman_agent import DanismanAgent
from aks_core.model.aciklama import Aciklayici


class Orkestrator:
    def __init__(self, model_yolu=None, llm_fonksiyonu=None):
        self.veri_agent = VeriAgent()
        self.skorlama_agent = SkorlamaAgent(model_yolu)
        self.aciklayici = Aciklayici(self.skorlama_agent.model, self.skorlama_agent.ozellikler)
        self.danisman_agent = DanismanAgent(llm_fonksiyonu)
        self.hafiza = {}  # musteri_id -> [değerlendirme kayıtları]

    def degerlendir(self, musteri_id, islemler, hafizaya_yaz=True):
        """`hafizaya_yaz=False`: bu çağrı süreç-içi hafızaya HİÇ dokunmaz.

        `self.hafiza` süreç genelinde paylaşılan bir sözlük ve `musteri_id` ile
        anahtarlanıyor. Kimliği olmayan skorlamalar (kullanıcı portalı yüklemesi,
        anonim CSV ucu) tek bir sahte kimlikle (`-1`) çağrıldığı için TÜM
        kullanıcıların yüklemeleri aynı listede birikiyordu; sonuç olarak bir
        kullanıcının `onceki_skor`/`skor_degisimi` alanları BAŞKA bir kullanıcının
        skorundan hesaplanıyordu (§7.20'de iki hesapla yeniden üretildi:
        A→850, ardından B→841 ve B'nin kaydında `onceki_skor: 850`).

        Bu alanlar veritabanına yazılmadığı ve portal yanıtında yer almadığı için
        ekrana yansımıyordu, ama yapı yanlıştı: eklenecek tek bir alan onu
        görünür kılardı. Ayrıca liste hiç temizlenmediğinden her yükleme kalıcı
        olarak bellekte birikiyordu (512 MB'lık dağıtım konteynerinde önemli).

        Kullanıcının GERÇEK geçmişi zaten kalıcı ve kullanıcıya özel:
        `Assessment.objects.filter(user=...)`. Paylaşılan hafıza yalnızca banka
        içi demo yüzeyinin (gerçek `musteri_id`'li) yedek geçmişi için var.
        """
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
            "anomali_bayrak": skor.get("anomali_bayrak"),
            "anomali_skoru": skor.get("anomali_skoru"),
            "ozellikler": veri["ozellikler"],
            "aciklama": aciklama,
            "danisman": danisman,
            "kullanilan_agentlar": [self.veri_agent.ad, self.skorlama_agent.ad, self.danisman_agent.ad],
        }
        # Hafızaya yaz + önceki skorla kıyas (yalnızca gerçek kimlikli çağrılarda)
        if hafizaya_yaz:
            gecmis = self.hafiza.setdefault(musteri_id, [])
            if gecmis:
                kayit["onceki_skor"] = gecmis[-1]["aks_skor"]
                kayit["skor_degisimi"] = skor["aks_skor"] - gecmis[-1]["aks_skor"]
            gecmis.append(kayit)
        return kayit

    def gecmis(self, musteri_id):
        return self.hafiza.get(musteri_id, [])
