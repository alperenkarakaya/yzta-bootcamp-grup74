"""
Kiracılık ve rıza sınır testleri — execution.md §3b Phase 7 / 7.2.

Bu dosya `api/tests.py`'nin (KlasikSkorSinirTesti vb.) aynı ruhunu taşır:
ürünün "müşteri onayı olmadan hiçbir kurum hiçbir müşteriyi göremez" vaadi
kodda zorlanmıyorsa yalnızca bir yorum satırıdır — burada kanıtlanır.

Çalıştırmak için:
    cd product/04-backend
    python manage.py test kimlik
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import Assessment
from kimlik import aks_no as aks_no_modul
from kimlik.models import ErisimTalebi, Kurum, KurumUyeligi, Profil, RizaIhlali, RizaKaydi


class AksNoTesti(TestCase):
    def test_uretilen_numara_gecerli_checksum_tasiyor(self):
        for _ in range(50):
            numara = aks_no_modul.uret()
            self.assertTrue(aks_no_modul.gecerli_mi(numara), numara)

    def test_bozuk_numara_gecersiz(self):
        numara = aks_no_modul.uret()
        bozuk = numara[:-1] + ("0" if numara[-1] != "0" else "1")
        self.assertFalse(aks_no_modul.gecerli_mi(bozuk))

    def test_numaralar_benzersiz(self):
        numaralar = {aks_no_modul.uret() for _ in range(200)}
        self.assertEqual(len(numaralar), 200)

    def test_numaradan_kisisel_veri_cikarilamaz(self):
        """Format doğrulaması dışında numara hiçbir kişisel veri taşımamalı —
        yalnızca alfabe kümesinden karakterler içermeli."""
        numara = aks_no_modul.uret()
        govde = numara.replace("AKS-", "").replace("-", "")
        self.assertTrue(all(c in aks_no_modul._ALFABE for c in govde))


class KayitProfilOlusturmaTesti(TestCase):
    """§3b Phase 7/7.2: her kayıt otomatik bir Profil + AKS no üretmeli —
    isim/soyisim/TCKN YOK."""

    def test_kayit_profil_ve_aks_no_uretir(self):
        r = self.client.post("/api/auth/kayit", {"email": "test1@example.com", "sifre": "GucluSifre123"})
        self.assertEqual(r.status_code, 201)
        veri = r.json()
        self.assertIn("aks_no", veri)
        self.assertTrue(aks_no_modul.gecerli_mi(veri["aks_no"]))

        user = User.objects.get(username="test1@example.com")
        self.assertTrue(Profil.objects.filter(user=user).exists())

    def test_farkli_kullanicilar_farkli_aks_no_alir(self):
        r1 = self.client.post("/api/auth/kayit", {"email": "a@example.com", "sifre": "GucluSifre123"})
        self.client.post("/api/auth/cikis")
        r2 = self.client.post("/api/auth/kayit", {"email": "b@example.com", "sifre": "GucluSifre123"})
        self.assertNotEqual(r1.json()["aks_no"], r2.json()["aks_no"])


class KiracilikSinirTesti(TestCase):
    """Ana vaat: bir kurum, rızası olmayan hiçbir müşteriyi göremez."""

    def setUp(self):
        self.musteri_user = User.objects.create_user(username="musteri@example.com", password="x")
        self.profil = Profil.objects.create(user=self.musteri_user, aks_no=aks_no_modul.uret())

        self.kurum_a = Kurum.objects.create(ad="A Bankası", kod="a-bankasi")
        self.kurum_b = Kurum.objects.create(ad="B Bankası", kod="b-bankasi")
        self.kurum_a_kullanici = User.objects.create_user(username="a-personel@example.com", password="x")
        KurumUyeligi.objects.create(user=self.kurum_a_kullanici, kurum=self.kurum_a)
        self.kurum_b_kullanici = User.objects.create_user(username="b-personel@example.com", password="x")
        KurumUyeligi.objects.create(user=self.kurum_b_kullanici, kurum=self.kurum_b)

        Assessment.objects.create(
            profil=self.profil, musteri_id="-1", aks_skor=700, risk_seviyesi="düşük risk",
            karar="onaylanabilir", kaynak="portal",
        )

    def _musteri_giris(self):
        self.client.force_login(self.musteri_user)

    def _kurum_a_giris(self):
        self.client.force_login(self.kurum_a_kullanici)

    def test_kurum_uyesi_olmayan_kullanici_kurum_ucuna_giremiyor(self):
        self._musteri_giris()  # musteri, hiçbir kuruma üye değil
        r = self.client.get("/api/kimlik/kurum/musteriler")
        self.assertEqual(r.status_code, 403)

    def test_riza_olmadan_musteri_detayi_403(self):
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 403)

    def test_riza_sonrasi_erisim_calisir_ve_baska_kurum_goremiyor(self):
        # Kurum A talep açar
        self._kurum_a_giris()
        r = self.client.post(
            "/api/kimlik/kurum/erisim-talebi",
            {"aks_no": self.profil.aks_no, "amac": "kredi başvurusu değerlendirmesi"},
        )
        self.assertEqual(r.status_code, 201)
        talep_id = r.json()["talep_id"]

        # Müşteri onaylar
        self.client.logout()
        self._musteri_giris()
        r = self.client.post(f"/api/kimlik/erisim-talebi/{talep_id}/onayla", {"gecerlilik_gun": 30})
        self.assertEqual(r.status_code, 200)

        # Kurum A artık görebiliyor
        self.client.logout()
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["aks_skor"], 700)

        # Kurum B (rızası yok) HALA giremiyor — çapraz kiracı sızıntısı yok
        self.client.logout()
        self.client.force_login(self.kurum_b_kullanici)
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 403)

    def test_musteri_rizayi_iptal_edince_erisim_kesilir(self):
        talep = ErisimTalebi.objects.create(
            kurum=self.kurum_a, profil=self.profil, amac="test",
            durum="onaylandi", gecerlilik_bitis=timezone.now() + timezone.timedelta(days=30),
        )
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 200, "Onaylı rıza ile erişim çalışmalı")

        self.client.logout()
        self._musteri_giris()
        r = self.client.post(f"/api/kimlik/erisim-talebi/{talep.id}/iptal")
        self.assertEqual(r.status_code, 200)

        self.client.logout()
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 403, "İptal edilen rıza ile erişim SÜRMEMELİ")

    def test_suresi_dolmus_riza_erisim_vermiyor(self):
        ErisimTalebi.objects.create(
            kurum=self.kurum_a, profil=self.profil, amac="test",
            durum="onaylandi", gecerlilik_bitis=timezone.now() - timezone.timedelta(days=1),
        )
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 403, "Süresi dolmuş rıza ile erişim VERİLMEMELİ")

    def test_musteri_detayi_risk_istahi_alanini_iceriyor(self):
        """§3b Phase 7/7.4: kurum tarafı, müşterinin 3 risk-iştahı profilinden
        hangilerinde onaylandığını görmeli (risk_istahi_raporu.json üretilmişse)."""
        from api import services
        if not services.risk_istahi_var():
            self.skipTest("risk_istahi_raporu.json henüz üretilmedi")

        talep = ErisimTalebi.objects.create(
            kurum=self.kurum_a, profil=self.profil, amac="test",
            durum="onaylandi", gecerlilik_bitis=timezone.now() + timezone.timedelta(days=30),
        )
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 200)
        veri = r.json()
        self.assertIn("risk_istahi", veri)
        self.assertEqual(set(veri["risk_istahi"]), {"ihtiyatli", "dengeli", "atak"})
        for profil_sonucu in veri["risk_istahi"].values():
            self.assertIn("onaylanir_mi", profil_sonucu)

    def test_reddedilen_talep_erisim_vermiyor(self):
        self._kurum_a_giris()
        r = self.client.post(
            "/api/kimlik/kurum/erisim-talebi", {"aks_no": self.profil.aks_no, "amac": "test"}
        )
        talep_id = r.json()["talep_id"]

        self.client.logout()
        self._musteri_giris()
        r = self.client.post(f"/api/kimlik/erisim-talebi/{talep_id}/reddet")
        self.assertEqual(r.status_code, 200)

        self.client.logout()
        self._kurum_a_giris()
        r = self.client.get(f"/api/kimlik/kurum/musteri/{self.profil.aks_no}")
        self.assertEqual(r.status_code, 403)


class RizaDefteriDegistirilemezlikTesti(TestCase):
    """RizaKaydi append-only olmalı — AuditLog'daki DenetimIziDegistirilemezlikTesti
    deseninin aynısı."""

    def setUp(self):
        musteri_user = User.objects.create_user(username="m@example.com", password="x")
        profil = Profil.objects.create(user=musteri_user, aks_no=aks_no_modul.uret())
        kurum = Kurum.objects.create(ad="Test Bankası", kod="test-bankasi")
        self.talep = ErisimTalebi.objects.create(kurum=kurum, profil=profil, amac="test")

    def _kayit(self):
        return RizaKaydi.objects.create(
            erisim_talebi=self.talep, olay="talep_olusturuldu",
            aks_no=self.talep.profil.aks_no, kurum_kod=self.talep.kurum.kod,
        )

    def test_riza_kaydi_guncellenemiyor(self):
        kayit = self._kayit()
        kayit.olay = "onaylandi"
        with self.assertRaises(RizaIhlali):
            kayit.save()

    def test_riza_kaydi_silinemiyor(self):
        kayit = self._kayit()
        with self.assertRaises(RizaIhlali):
            kayit.delete()


class ErisimTalebiUcNoktalariTesti(TestCase):
    def setUp(self):
        self.musteri_user = User.objects.create_user(username="m2@example.com", password="x")
        self.profil = Profil.objects.create(user=self.musteri_user, aks_no=aks_no_modul.uret())
        self.kurum = Kurum.objects.create(ad="Test Bankası", kod="test-bankasi-2")
        self.kurum_kullanici = User.objects.create_user(username="p2@example.com", password="x")
        KurumUyeligi.objects.create(user=self.kurum_kullanici, kurum=self.kurum)

    def test_gecersiz_aks_no_ile_talep_reddedilir(self):
        self.client.force_login(self.kurum_kullanici)
        r = self.client.post("/api/kimlik/kurum/erisim-talebi", {"aks_no": "AKS-XXXX-INVALID", "amac": "test"})
        self.assertEqual(r.status_code, 400)

    def test_var_olmayan_musteri_icin_talep_404(self):
        self.client.force_login(self.kurum_kullanici)
        # Geçerli checksum ama kayıtlı olmayan bir numara üret
        from kimlik.aks_no import uret
        baska_numara = uret()
        r = self.client.post("/api/kimlik/kurum/erisim-talebi", {"aks_no": baska_numara, "amac": "test"})
        self.assertEqual(r.status_code, 404)

    def test_musteri_kendi_talebini_gorebilir(self):
        ErisimTalebi.objects.create(kurum=self.kurum, profil=self.profil, amac="kredi değerlendirmesi")
        self.client.force_login(self.musteri_user)
        r = self.client.get("/api/kimlik/erisim-talepleri")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["talepler"]), 1)
        self.assertEqual(r.json()["talepler"][0]["durum"], "bekliyor")


class ProfilsizKullaniciTesti(TestCase):
    """Kurum personeli hesaplarının `Profil`'i yoktur. Müşteri-taraflı uçlar
    `request.user.profil`'i doğrudan okuduğu için bu hesaplar 500 alıyordu
    (kurum kullanıcısı portal sayfalarına girdiğinde tetiklenen gerçek bir
    hataydı). Artık `ProfilSahibi` izniyle 403 dönmeli."""

    UCLAR = [
        "/api/kimlik/profilim",
        "/api/kimlik/erisim-talepleri",
        "/api/kimlik/riza-defterim",
    ]

    def setUp(self):
        self.kurum = Kurum.objects.create(ad="Profilsiz Bankası", kod="profilsiz-bankasi")
        self.kurum_kullanici = User.objects.create_user(username="profilsiz@example.com", password="x")
        KurumUyeligi.objects.create(user=self.kurum_kullanici, kurum=self.kurum)

    def test_profilsiz_kullanici_403_alir_500_degil(self):
        self.client.force_login(self.kurum_kullanici)
        for uc in self.UCLAR:
            with self.subTest(uc=uc):
                self.assertEqual(self.client.get(uc).status_code, 403)

    def test_profilsiz_kullanici_telefon_dogrulama_baslatamaz(self):
        self.client.force_login(self.kurum_kullanici)
        r = self.client.post("/api/kimlik/telefon/gonder", {"telefon": "+905551112233"})
        self.assertEqual(r.status_code, 403)

    def test_profilli_kullanici_ayni_uclara_erisebilir(self):
        user = User.objects.create_user(username="profilli@example.com", password="x")
        Profil.objects.create(user=user, aks_no=aks_no_modul.uret())
        self.client.force_login(user)
        for uc in self.UCLAR:
            with self.subTest(uc=uc):
                self.assertEqual(self.client.get(uc).status_code, 200)
