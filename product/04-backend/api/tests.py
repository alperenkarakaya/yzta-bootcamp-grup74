"""
SINIR TESTLERİ — ürünün ana vaadinin kanıtı.

README ve overview.md şunu iddia ediyor:

    "AKS, bankanın klasik skorunu veya segmentini asla ezmez, değiştirmez —
     yalnızca tamamlar. Bu bir vaat değil, kodda zorlanan bir kısıt."

Kodda zorlanan bir kısıt, testle kanıtlanmıyorsa sadece bir yorum satırıdır.
Bu dosya o kısıtı kanıtlar. Kısıt bozulursa buradaki testler kırmızıya döner.

Çalıştırmak için:
    cd product/04-backend
    python manage.py test
"""
from django.test import TestCase
from django.urls import reverse

from audit.models import Assessment, AuditLog, Customer


class KlasikSkorSinirTesti(TestCase):
    """AKS'in klasik skora dokunmadığını kanıtlar."""

    def setUp(self):
        from api import services
        self.services = services
        # Demo veri yoksa testlerin çoğu anlamsız olur; erkenden görelim.
        self.demo_var = services.demo_var()

    def _demo_musteri(self):
        personalar = self.services.demo_personalar(adet_per_persona=1)
        # Odak grubumuz: klasik skorun haksızca cezalandırdığı öğrenci
        for tercih in ("ogrenci_yuksek_hacim", "klasik_maasli"):
            if personalar.get(tercih):
                return personalar[tercih][0], tercih
        ilk = next(iter(personalar.items()))
        return ilk[1][0], ilk[0]

    def test_denetim_kaydi_klasik_skoru_degistirmeden_saklıyor(self):
        """Skorlama, klasik skoru olduğu gibi denetim iznine yazmalı."""
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        mid, persona = self._demo_musteri()

        from aks_core.model.egitim import klasik_risk_skoru
        islemler = self.services.demo_islemler(mid)
        veri = self.services.orkestrator.veri_agent.calistir(islemler)
        beklenen_klasik = klasik_risk_skoru({"persona": persona, **veri["ozellikler"]})

        self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)

        log = AuditLog.objects.filter(musteri_id=str(mid)).latest("created_at")
        self.assertEqual(
            log.klasik_skor, beklenen_klasik,
            "Klasik skor denetim izine değiştirilmiş halde yazılmış — SINIR İHLALİ",
        )

    def test_aks_skoru_klasik_skorun_yerine_gecmiyor(self):
        """İki skor ayrı kolonlarda tutulmalı; AKS klasiği ezmemeli."""
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        mid, persona = self._demo_musteri()
        islemler = self.services.demo_islemler(mid)
        sonuc, klasik = self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)

        kayit = Assessment.objects.filter(musteri_id=str(mid)).latest("created_at")
        self.assertEqual(kayit.klasik_skor, klasik)
        self.assertEqual(kayit.aks_skor, sonuc["aks_skor"])
        self.assertNotEqual(
            kayit.klasik_skor, kayit.aks_skor,
            "Klasik skor AKS ile aynı değere gelmiş — üzerine yazılmış olabilir",
        )

    def test_tekrarlanan_skorlama_klasik_skoru_kaydirmiyor(self):
        """Aynı müşteri 3 kez skorlansa da klasik skor sabit kalmalı."""
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        mid, persona = self._demo_musteri()
        islemler = self.services.demo_islemler(mid)

        for _ in range(3):
            self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)

        klasikler = list(
            AuditLog.objects.filter(musteri_id=str(mid)).values_list("klasik_skor", flat=True)
        )
        self.assertEqual(len(set(klasikler)), 1, f"Klasik skor kaymış: {klasikler}")

    def test_her_skorlama_denetim_izi_birakiyor(self):
        """Denetlenebilirlik: skorlanan her müşteri için bir AuditLog satırı."""
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        mid, persona = self._demo_musteri()
        islemler = self.services.demo_islemler(mid)

        once = AuditLog.objects.count()
        self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)
        self.assertEqual(AuditLog.objects.count(), once + 1)

    def test_denetim_kaydi_kullanilan_agentlari_yaziyor(self):
        """Kararın hangi agent zincirinden çıktığı iz bırakmalı."""
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        mid, persona = self._demo_musteri()
        islemler = self.services.demo_islemler(mid)
        self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)

        log = AuditLog.objects.filter(musteri_id=str(mid)).latest("created_at")
        self.assertIn("skorlama_agent", log.ajanlar)


class DenetimIziDegistirilemezlikTesti(TestCase):
    """AuditLog append-only olmalı: güncellenemez, silinemez."""

    def _log(self):
        return AuditLog.objects.create(
            musteri_id="test-1", klasik_skor=600, aks_skor=780,
            karar="onaylanabilir", ajanlar=["skorlama_agent"], kaynak="api",
        )

    def test_denetim_kaydi_guncellenemiyor(self):
        log = self._log()
        log.klasik_skor = 999
        with self.assertRaises(Exception, msg="AuditLog güncellenebiliyor — değiştirilemez olmalı"):
            log.save()

    def test_denetim_kaydi_silinemiyor(self):
        log = self._log()
        with self.assertRaises(Exception, msg="AuditLog silinebiliyor — değiştirilemez olmalı"):
            log.delete()


class ApiUclariTesti(TestCase):
    """Uçlar ayakta mı ve sözleşmeye uyuyor mu."""

    def test_bilgi_ucu_model_adini_donuyor(self):
        r = self.client.get("/api/bilgi")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn(veri["model"], ("XGBoost", "LightGBM"))
        self.assertEqual(len(veri["ozellikler"]), 9)

    def test_demo_musteri_ucu_persona_listeliyor(self):
        r = self.client.get("/api/demo-musteriler")
        self.assertEqual(r.status_code, 200)

    def test_skorla_ucu_iki_skoru_da_donuyor(self):
        from api import services
        if not services.demo_var():
            self.skipTest("Demo veri yok")
        personalar = services.demo_personalar(adet_per_persona=1)
        mid = next(iter(personalar.values()))[0]

        r = self.client.get(f"/api/skorla/{mid}")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn("klasik_skor", veri)
        self.assertIn("aks_skor", veri)
        self.assertIn("aciklama", veri)

    def test_gecmis_ucu_calisiyor(self):
        r = self.client.get("/api/gecmis/1")
        self.assertEqual(r.status_code, 200)
        self.assertIn("gecmis", r.json())
