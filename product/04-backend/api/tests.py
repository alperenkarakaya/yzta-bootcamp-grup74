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
        self.assertIn(veri["model"], ("XGBoost", "LightGBM", "LogisticRegression"))
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

    def test_metrikler_ucu_cv_raporu_donuyor(self):
        """§3b/U15/U19: degerlendirme.py'nin (U6) persist ettiği rapor erişilebilir olmalı."""
        from api import services
        if not services.metrikler_var():
            self.skipTest("degerlendirme_raporu.json henüz üretilmedi")
        r = self.client.get("/api/metrikler")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn("veri_kaynagi", veri)
        self.assertIn("modeller", veri)
        self.assertTrue(len(veri["modeller"]) >= 1)
        self.assertIn("roc_auc", veri["modeller"][0])
        self.assertIn("ci95", veri["modeller"][0]["roc_auc"])

    def test_politika_ucu_bantlari_donuyor(self):
        """§3b/U16/U19: karar mekanizması bantları tek kaynaktan (aks_core.politika) geliyor."""
        r = self.client.get("/api/politika")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn("bantlar", veri)
        esikler = [b["esik"] for b in veri["bantlar"]]
        self.assertEqual(esikler, sorted(esikler, reverse=True), "Bantlar eşiğe göre azalan sırada olmalı")

    def test_asistan_ucu_anahtarsiz_kural_moduna_duser(self):
        """§3b Phase 7/7.5/7.10: ne ANTHROPIC_API_KEY ne GEMINI_API_KEY varsa
        /api/asistan sıfır regresyonla eski kural motoruna düşmeli. İkisini de
        `patch.dict` ile boşaltıyoruz — geliştiricinin gerçek `.env`'inde bir
        anahtar dolu olsa bile bu test hermetik kalmalı (aksi halde gerçek bir
        ağ çağrısı yapıp yavaş/kırılgan hale gelir — tam olarak bu yüzden
        eklendi, bkz. execution.md §3b Phase 7/7.10)."""
        import os
        from unittest.mock import patch as mock_patch
        with mock_patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "GEMINI_API_KEY": ""}):
            r = self.client.post("/api/asistan", {
                "soru": "skorum neden düşük?",
                "baglam": {"aks_skor": 600, "risk_seviyesi": "orta risk",
                           "aciklama": {"riski_azaltan": [], "riski_artiran": []}},
            }, content_type="application/json")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn("yanit", veri)
        self.assertEqual(veri.get("mod"), "kural")

    def test_asistan_ucu_anahtar_varsa_danisman_llm_e_delege_eder(self):
        """§3b Phase 7/7.10: bir anahtar (Anthropic ya da Gemini) varsa
        `services.asistan_yanit` isteği gerçek bir ağ çağrısı yapmadan
        `danisman_llm.yanitla`'ya delege etmeli — services.py'deki yönlendirme
        koşulunun regresyon testi (bkz. `asistan_yanit`'in GEMINI_API_KEY'i de
        kontrol etmesi gerektiği bulgusu)."""
        import os
        from unittest.mock import patch as mock_patch
        with mock_patch.dict(os.environ, {"ANTHROPIC_API_KEY": "", "GEMINI_API_KEY": "sahte-anahtar"}):
            with mock_patch("aks_core.agents.danisman_llm.yanitla") as sahte_yanitla:
                sahte_yanitla.return_value = {
                    "yanit": "test yanit", "mod": "llm-arac", "saglayici": "gemini",
                    "anlati_reddedildi": False, "arac_cagrilari": [],
                }
                r = self.client.post("/api/asistan", {
                    "soru": "skorum neden düşük?",
                    "baglam": {"aks_skor": 600, "risk_seviyesi": "orta risk",
                               "aciklama": {"riski_azaltan": [], "riski_artiran": []}},
                }, content_type="application/json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["mod"], "llm-arac")
        self.assertEqual(r.json()["saglayici"], "gemini")
        sahte_yanitla.assert_called_once()

    def test_risk_istahi_ucu_uc_profil_donuyor(self):
        """§3b Phase 7/7.4: ihtiyatli/dengeli/atak profilleri, artan onay oranıyla."""
        from api import services
        if not services.risk_istahi_var():
            self.skipTest("risk_istahi_raporu.json henüz üretilmedi")
        r = self.client.get("/api/risk-istahi")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertEqual(set(veri["profiller"]), {"ihtiyatli", "dengeli", "atak"})
        onay = {k: v["onay_orani"] for k, v in veri["profiller"].items()}
        self.assertLessEqual(onay["ihtiyatli"], onay["dengeli"])
        self.assertLessEqual(onay["dengeli"], onay["atak"])

    def test_skorla_demo_formulasyon_b_alanlarini_iceriyor(self):
        """§3b/U17/U19: persona biliniyorsa pd_geleneksel_bant/pd_fark/kapasite_sinyali dönmeli."""
        from api import services
        if not services.demo_var():
            self.skipTest("Demo veri yok")
        personalar = services.demo_personalar(adet_per_persona=1)
        mid = next(iter(personalar.values()))[0]

        r = self.client.get(f"/api/skorla/{mid}")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        for alan in ("pd_geleneksel_bant", "pd_fark", "kapasite_sinyali"):
            self.assertIn(alan, veri)
        # Bant tablosu eğitilmiş bir modelden geliyorsa (normal durum) sayısal olmalı.
        if veri["pd_fark"] is not None:
            self.assertIsInstance(veri["pd_fark"], (int, float))
            self.assertEqual(veri["klasik_skor"] is not None, True)


class FormulasyonBSinirTesti(TestCase):
    """§3b/U18/U19: yeni Formülasyon B alanları klasik_skor'u ASLA etkilememeli/ezmemeli
    — bu, KlasikSkorSinirTesti'nin U17/U18 sonrası hâlâ geçerli olduğunu doğrular."""

    def setUp(self):
        from api import services
        self.services = services
        self.demo_var = services.demo_var()

    def test_pd_fark_eklenmesi_klasik_skoru_degistirmiyor(self):
        if not self.demo_var:
            self.skipTest("Demo veri yok")
        personalar = self.services.demo_personalar(adet_per_persona=1)
        persona, mid_listesi = next(iter(personalar.items()))
        mid = mid_listesi[0]
        islemler = self.services.demo_islemler(mid)

        from aks_core.model.egitim import klasik_risk_skoru
        veri = self.services.orkestrator.veri_agent.calistir(islemler)
        beklenen_klasik = klasik_risk_skoru({"persona": persona, **veri["ozellikler"]})

        sonuc, klasik = self.services.degerlendir(mid, islemler, kaynak="demo", persona=persona)
        self.assertEqual(klasik, beklenen_klasik)

        log = AuditLog.objects.filter(musteri_id=str(mid)).latest("created_at")
        self.assertEqual(log.klasik_skor, beklenen_klasik,
                          "Formülasyon B alanları eklendikten sonra bile klasik skor değişmemeli")
        # pd_fark salt-okunur türetilmiş bir alan; klasik_skor'dan bağımsız olarak var/None olabilir
        # ama asla klasik_skor kolonunun YERİNE geçmemeli (ayrı kolon).
        self.assertNotEqual(log.klasik_skor, log.aks_skor)


_ORNEK_EKSTRE_CSV = b"""tarih,islem_tipi,kategori,tutar,aciklama
2026-01-05,gelir,maas,15000,Maas Odemesi
2026-01-10,gider,market,-450.5,Migros Market
2026-01-15,gider,fatura,-320,Elektrik Faturasi
2026-02-05,gelir,maas,15000,Maas Odemesi
2026-02-12,gider,kira,-6000,Kira Odemesi
2026-02-20,gider,eglence,-149.99,Netflix Aboneligi
"""

_BASKA_EKSTRE_CSV = b"""tarih,islem_tipi,kategori,tutar,aciklama
2026-01-03,gelir,maas,9000,Maas
2026-01-08,gider,market,-200,Market
2026-01-14,gider,fatura,-150,Fatura
2026-02-02,gelir,maas,9000,Maas
2026-02-11,gider,kira,-2500,Kira
"""


class SahiplikSavunmasiTesti(TestCase):
    """§3b Phase 7/7.3: engelleme değil TESPİT — bkz. plan "Dürüstlük notu".
    Bu testler üç katmandan ikisini (parmak izi çakışması + zorunlu beyan)
    kanıtlar; davranışsal tutarlılık `kimlik` app'inin dışında, `api.sahiplik`
    modülünde ayrı test edilir."""

    def _kayit_ol_ve_giris_yap(self, email):
        r = self.client.post("/api/auth/kayit", {"email": email, "sifre": "GucluSifre123"})
        self.assertEqual(r.status_code, 201)
        return r.json()

    def _yukle(self, icerik, beyan="true", dosya_adi="ekstre.csv"):
        from django.core.files.uploadedfile import SimpleUploadedFile
        dosya = SimpleUploadedFile(dosya_adi, icerik, content_type="text/csv")
        veri = {"dosya": dosya}
        if beyan is not None:
            veri["beyan"] = beyan
        return self.client.post("/api/portal/yukle", veri)

    def test_beyan_olmadan_yukleme_reddedilir(self):
        self._kayit_ol_ve_giris_yap("beyansiz@example.com")
        r = self._yukle(_ORNEK_EKSTRE_CSV, beyan=None)
        self.assertEqual(r.status_code, 400)

    def test_beyan_ile_yukleme_kabul_edilir(self):
        self._kayit_ol_ve_giris_yap("beyanli@example.com")
        r = self._yukle(_ORNEK_EKSTRE_CSV)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json().get("sahiplik_bayraklari"), [])

    def test_ayni_belge_iki_hesapla_yuklenince_ikisi_de_bayraklanir(self):
        from audit.models import Assessment

        self._kayit_ol_ve_giris_yap("kisi1@example.com")
        r1 = self._yukle(_ORNEK_EKSTRE_CSV)
        self.assertEqual(r1.status_code, 200)
        self.assertNotIn("coklu_sahiplik_supheli", r1.json()["sahiplik_bayraklari"],
                          "İlk yükleyen için henüz çakışma yok")

        self.client.post("/api/auth/cikis")
        self._kayit_ol_ve_giris_yap("kisi2@example.com")
        r2 = self._yukle(_ORNEK_EKSTRE_CSV)  # AYNI içerik, farklı hesap
        self.assertEqual(r2.status_code, 200)
        self.assertIn("coklu_sahiplik_supheli", r2.json()["sahiplik_bayraklari"],
                       "İkinci yükleyen için çakışma bayrağı beklenir")

        # Retroaktif: ilk kaydın bayrağı da güncellenmiş olmalı
        ilk_kayit = Assessment.objects.filter(kaynak="portal").order_by("created_at").first()
        self.assertIn("coklu_sahiplik_supheli", ilk_kayit.sahiplik_bayraklari)

    def test_farkli_belge_bayrak_almiyor(self):
        self._kayit_ol_ve_giris_yap("kisi3@example.com")
        self._yukle(_ORNEK_EKSTRE_CSV)
        self.client.post("/api/auth/cikis")
        self._kayit_ol_ve_giris_yap("kisi4@example.com")
        r = self._yukle(_BASKA_EKSTRE_CSV)
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("coklu_sahiplik_supheli", r.json()["sahiplik_bayraklari"])

    def test_belge_meta_ve_ip_kaydediliyor(self):
        from audit.models import Assessment

        self._kayit_ol_ve_giris_yap("kisi5@example.com")
        self._yukle(_ORNEK_EKSTRE_CSV)
        kayit = Assessment.objects.filter(kaynak="portal").latest("created_at")
        self.assertTrue(kayit.sahiplik_beyani)
        self.assertEqual(kayit.kaynak_format, "csv")
        self.assertTrue(kayit.belge_parmak_izi)
        self.assertIsNotNone(kayit.yukleme_ip)

    def test_gelir_olceginde_ani_sicrama_tutarsizlik_bayragi_uretir(self):
        """Aynı profilin geçmiş yüklemelerine göre gelir ölçeği 3 kattan fazla
        sıçrarsa `profil_tutarsiz` üretilmeli (davranışsal tutarlılık katmanı,
        bkz. `api/sahiplik.py::davranissal_tutarlilik_kontrol`)."""
        self._kayit_ol_ve_giris_yap("tutarsiz@example.com")
        # İki normal yükleme (aynı ölçek) — medyan oluşturmak için
        self._yukle(_BASKA_EKSTRE_CSV, dosya_adi="e1.csv")
        self._yukle(_BASKA_EKSTRE_CSV.replace(b"9000", b"9100"), dosya_adi="e2.csv")

        # Üçüncü yükleme: gelir ~15x büyük (kanonik format korunarak)
        buyuk_gelirli = _BASKA_EKSTRE_CSV.replace(b"9000", b"140000")
        r = self._yukle(buyuk_gelirli, dosya_adi="e3.csv")
        self.assertEqual(r.status_code, 200)
        self.assertIn("profil_tutarsiz", r.json()["sahiplik_bayraklari"])


class HamIslemSaklamaTesti(TestCase):
    """PO kararı: müşteri tarafından yüklenen ham işlemler müşteri bazlı
    saklanmalı, yalnızca türetilmiş özellikler değil — böylece müşteri kendi
    geçmiş yüklemesinin detayını (hangi işlem, hangi tarih/tutar) görebilir."""

    def _kayit_ol_ve_giris_yap(self, email):
        r = self.client.post("/api/auth/kayit", {"email": email, "sifre": "GucluSifre123"})
        self.assertEqual(r.status_code, 201)
        return r.json()

    def _yukle(self, icerik=_ORNEK_EKSTRE_CSV, dosya_adi="ekstre.csv"):
        from django.core.files.uploadedfile import SimpleUploadedFile
        dosya = SimpleUploadedFile(dosya_adi, icerik, content_type="text/csv")
        return self.client.post("/api/portal/yukle", {"dosya": dosya, "beyan": "true"})

    def test_portal_yuklemesi_ham_islemleri_saklar(self):
        from audit.models import Assessment
        self._kayit_ol_ve_giris_yap("hamveri1@example.com")
        r = self._yukle()
        self.assertEqual(r.status_code, 200)
        kayit = Assessment.objects.filter(kaynak="portal").latest("created_at")
        self.assertTrue(kayit.ham_islemler, "Yüklenen işlemler saklanmalı")
        self.assertEqual(len(kayit.ham_islemler), r.json()["islem_sayisi"])
        ilk = kayit.ham_islemler[0]
        self.assertIn("tarih", ilk)
        self.assertIn("tutar", ilk)

    def test_musteri_kendi_gecmis_detayini_gorebilir(self):
        self._kayit_ol_ve_giris_yap("hamveri2@example.com")
        self._yukle()
        liste = self.client.get("/api/portal/gecmis").json()["gecmis"]
        self.assertEqual(len(liste), 1)
        kayit_id = liste[0]["id"]

        detay = self.client.get(f"/api/portal/gecmis/{kayit_id}")
        self.assertEqual(detay.status_code, 200)
        gövde = detay.json()
        self.assertTrue(gövde["islemler"], "Detay uç noktası ham işlemleri döndürmeli")
        self.assertEqual(len(gövde["islemler"]), liste[0]["islem_sayisi"])

    def test_baska_kullanicinin_gecmis_detayina_erisilemez(self):
        self._kayit_ol_ve_giris_yap("sahip@example.com")
        self._yukle()
        from audit.models import Assessment
        kayit_id = Assessment.objects.filter(kaynak="portal").latest("created_at").id

        self.client.post("/api/auth/cikis")
        self._kayit_ol_ve_giris_yap("baskasi@example.com")
        r = self.client.get(f"/api/portal/gecmis/{kayit_id}")
        self.assertEqual(r.status_code, 404, "Başka hesabın kaydı asla görünmemeli")

    def test_demo_skorlama_ham_islem_saklamaz(self):
        """Bankanın demo/anonim skorlaması (profilsiz) — veri zaten kaynak
        CSV'de duruyor, ikinci kez saklamaya gerek yok (kişisel veri ayak izi
        büyümesin)."""
        from audit.models import Assessment
        r = self.client.get("/api/skorla/1")
        self.assertEqual(r.status_code, 200)
        kayit = Assessment.objects.filter(kaynak="demo").latest("created_at")
        self.assertEqual(kayit.ham_islemler, [])
