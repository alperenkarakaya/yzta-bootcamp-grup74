"""
Birim ve entegrasyon testleri
-----------------------------
Çalıştırma: python -m pytest tests/ -v
Kapsam: özellik çıkarımı, etiketleme, skorlama agent'ı, orkestratör hafızası, API uç noktaları.
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.ozellik.cikarim import ozellik_cikar, OZELLIK_ADLARI
from src.model.etiketleme import etiketle
from src.agents.skorlama_agent import olasilik_to_aks
from src.agents.orkestrator import Orkestrator
from src.api.main import app


def _ornek_islemler(gelir_tutari=10000, gider_tutari=6000):
    """Basit, deterministik işlem seti: 3 aylık düzenli gelir + gider + fatura."""
    islemler = []
    for ay in range(3):
        islemler.append({"tarih": f"2026-0{ay+1}-05", "islem_tipi": "gelir",
                         "kategori": "maas_odemesi", "tutar": gelir_tutari, "aciklama": "maas"})
        islemler.append({"tarih": f"2026-0{ay+1}-10", "islem_tipi": "gider",
                         "kategori": "fatura", "tutar": -gider_tutari * 0.2, "aciklama": "fatura"})
        islemler.append({"tarih": f"2026-0{ay+1}-15", "islem_tipi": "gider",
                         "kategori": "market", "tutar": -gider_tutari * 0.8, "aciklama": "market"})
    for i in islemler:
        i["tarih_obj"] = datetime.strptime(i["tarih"], "%Y-%m-%d")
        i["tutar"] = float(i["tutar"])
    return islemler


# ---------- Özellik çıkarımı ----------
class TestOzellikCikarimi:
    def test_tum_ozellikler_donuyor(self):
        oz = ozellik_cikar(_ornek_islemler())
        assert set(OZELLIK_ADLARI).issubset(oz.keys())

    def test_gider_gelir_orani_dogru(self):
        oz = ozellik_cikar(_ornek_islemler(gelir_tutari=10000, gider_tutari=6000))
        assert oz["gider_gelir_orani"] == pytest.approx(0.6, abs=0.01)

    def test_duzenli_gelir_yuksek_duzenlilik(self):
        oz = ozellik_cikar(_ornek_islemler())
        assert oz["gelir_duzenliligi"] > 0.7  # ~30 gün aralıklı düzenli maaş


# ---------- Etiketleme ----------
class TestEtiketleme:
    def _musteri(self, gider_orani):
        return {"gider_gelir_orani": gider_orani, "bakiye_trendi": 1.0 if gider_orani < 1 else -1.0,
                "gelir_duzenliligi": 0.8, "fatura_odeme_duzeni": 0.8,
                "toplam_gelir_hacmi": 60000, "gelir_kaynagi_sayisi": 2}

    def test_hedef_oran_kalibrasyonu(self):
        musteriler = [self._musteri(0.5 + 0.01 * i) for i in range(100)]
        etiketle(musteriler, hedef_temerrut_orani=0.2)
        oranlar = [m["temerrut_olasiligi_gercek"] for m in musteriler]
        assert 0.05 < sum(oranlar) / len(oranlar) < 0.40  # kalibrasyon makul aralıkta

    def test_disiplinli_daha_dusuk_risk(self):
        iyi, kotu = self._musteri(0.5), self._musteri(1.2)
        etiketle([iyi, kotu], hedef_temerrut_orani=0.2)
        assert iyi["temerrut_olasiligi_gercek"] < kotu["temerrut_olasiligi_gercek"]


# ---------- Skorlama ----------
class TestSkorlama:
    def test_olasilik_to_aks_sinirlar(self):
        assert olasilik_to_aks(0.0) == 850
        assert olasilik_to_aks(1.0) == 300
        assert 300 <= olasilik_to_aks(0.5) <= 850

    def test_dusuk_olasilik_yuksek_skor(self):
        assert olasilik_to_aks(0.05) > olasilik_to_aks(0.6)


# ---------- Orkestratör ----------
class TestOrkestrator:
    def test_uctan_uca_ve_hafiza(self):
        ork = Orkestrator()
        islemler = _ornek_islemler()
        s1 = ork.degerlendir(999, islemler)
        assert 300 <= s1["aks_skor"] <= 850
        assert s1["kullanilan_agentlar"] == ["veri_agent", "skorlama_agent", "danisman_agent"]
        s2 = ork.degerlendir(999, islemler)
        assert s2["onceki_skor"] == s1["aks_skor"]
        assert len(ork.gecmis(999)) == 2


# ---------- API ----------
class TestAPI:
    client = TestClient(app)

    def test_bilgi(self):
        r = self.client.get("/api/bilgi")
        assert r.status_code == 200 and r.json()["model"] in ("XGBoost", "LightGBM")

    def test_skorla_post(self):
        islemler = [{"tarih": i["tarih"], "islem_tipi": i["islem_tipi"], "kategori": i["kategori"],
                     "tutar": i["tutar"], "aciklama": i["aciklama"]} for i in _ornek_islemler()]
        r = self.client.post("/api/skorla", json={"musteri_id": 1, "islemler": islemler})
        assert r.status_code == 200 and 300 <= r.json()["aks_skor"] <= 850

    def test_bos_islem_reddi(self):
        r = self.client.post("/api/skorla", json={"musteri_id": 1, "islemler": []})
        assert r.status_code == 400

    def test_gecersiz_simulasyon_ozelligi(self):
        islemler = [{"tarih": i["tarih"], "islem_tipi": i["islem_tipi"], "kategori": i["kategori"],
                     "tutar": i["tutar"], "aciklama": i["aciklama"]} for i in _ornek_islemler()]
        r = self.client.post("/api/simulasyon", json={"musteri_id": 1, "islemler": islemler,
                                                      "degisiklikler": {"olmayan_ozellik": 1.0}})
        assert r.status_code == 400

    def test_portfoy(self):
        r = self.client.get("/api/portfoy")
        assert r.status_code == 200
        d = r.json()
        assert d["kurtarilan"] > 0 and 0 <= d["kurtarma_orani"] <= 1


# ---------- Limit önerisi ----------
class TestLimit:
    def test_yuksek_skor_yuksek_limit(self):
        from src.agents.skorlama_agent import limit_oner
        oz = {"toplam_gelir_hacmi": 90000, "toplam_gider_hacmi": 54000}
        assert limit_oner(800, oz) > limit_oner(650, oz) > limit_oner(500, oz) == 0

    def test_limit_negatif_olamaz(self):
        from src.agents.skorlama_agent import limit_oner
        oz = {"toplam_gelir_hacmi": 10000, "toplam_gider_hacmi": 20000}
        assert limit_oner(800, oz) == 0  # negatif nakit akışı -> limit 0


# ---------- Adalet ----------
class TestAdalet:
    def test_adalet_raporu_yapisi(self):
        from src.model.adalet import adalet_raporu
        musteriler = []
        for i in range(40):
            musteriler.append({"persona": "a" if i < 20 else "b",
                               "temerrut": i % 5 == 0,
                               "klasik_skor": 700 if i < 20 else 500,
                               "aks_skor": 700})
        r = adalet_raporu(musteriler)
        assert "equal_opportunity_boslugu" in r["aks_skor"]
        # AKS herkese aynı skoru verdi -> boşluk 0 (tam adil)
        assert r["aks_skor"]["equal_opportunity_boslugu"] == 0.0


# ---------- CSV upload ----------
class TestCSVUpload:
    client = TestClient(app)

    def _csv(self):
        s = "tarih,islem_tipi,kategori,tutar\n"
        for ay in range(1, 7):
            s += f"2026-0{ay}-05,gelir,maas_odemesi,15000\n2026-0{ay}-12,gider,fatura,-1500\n"
        return s

    def test_csv_skorla(self):
        r = self.client.post("/api/csv-skorla", files={"dosya": ("h.csv", self._csv(), "text/csv")})
        assert r.status_code == 200
        d = r.json()
        assert 300 <= d["aks_skor"] <= 850 and d["onerilen_limit"] >= 0

    def test_eksik_kolon_reddi(self):
        r = self.client.post("/api/csv-skorla", files={"dosya": ("h.csv", "a,b\n1,2\n", "text/csv")})
        assert r.status_code == 400

    def test_az_islem_reddi(self):
        s = "tarih,islem_tipi,kategori,tutar\n2026-01-05,gelir,maas,1000\n"
        r = self.client.post("/api/csv-skorla", files={"dosya": ("h.csv", s, "text/csv")})
        assert r.status_code == 400


# ---------- Asistan ----------
class TestAsistan:
    client = TestClient(app)

    def test_kural_modu_yanit(self):
        from src.agents.asistan import AsistanAgent
        a = AsistanAgent(llm_fonksiyonu=None)
        baglam = {"aks_skor": 597, "risk_seviyesi": "orta risk", "onerilen_limit": 8000,
                  "danisman": {"oneriler": ["Gider oranını düşür"], "ozet": "Skor 597."},
                  "aciklama": {"riski_azaltan": [], "riski_artiran": []}}
        r = a.yanitla("Skorumu nasıl yükseltirim?", baglam)
        assert r["mod"] == "kural" and "Gider" in r["yanit"]

    def test_baglamsiz_uyari(self):
        from src.agents.asistan import AsistanAgent
        r = AsistanAgent().yanitla("selam", {})
        assert "profil" in r["yanit"].lower() or "yükle" in r["yanit"].lower()

    def test_asistan_api(self):
        r = self.client.post("/api/asistan", json={"soru": "ne kadar limit",
             "baglam": {"aks_skor": 720, "onerilen_limit": 30000, "risk_seviyesi": "düşük risk"}})
        assert r.status_code == 200 and "30" in r.json()["yanit"]
