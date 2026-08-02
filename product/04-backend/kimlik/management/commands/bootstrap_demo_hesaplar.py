"""
Test/jüri için üç demo hesabı tek komutta hazırlar — her biri FARKLI bir
yüzeye düşer, böylece "kim neyi görebiliyor" sınırı canlı denenebilir:

    ornek@aks.com  -> /portal            (yalnızca kendi yüklemeleri)
    admin@aks.com  -> /                  (banka içi araştırma; is_staff)
    kurum@demo.aks -> /kurum/musteriler  (yalnızca aktif rızalı müşteriler)

Kurum hesabı ayrı bir komutta (`bootstrap_kurum`) — bu komut onu da çağırır,
mantık kopyalanmaz.

Şifreler `--*-sifre` ile geçilebilir; geçilmezse giriş sayfasında gösterilen
demo değerleri kullanılır (GirisPage.tsx ile AYNI olmalı — değiştirirsen
ikisini birlikte değiştir).

Çalıştırma:
    python manage.py bootstrap_demo_hesaplar
"""
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from kimlik.aks_no import uret
from kimlik.models import Profil


class Command(BaseCommand):
    help = "Demo kullanıcı + yönetici + kurum hesaplarını oluşturur (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--kullanici-email", default="ornek@aks.com")
        parser.add_argument("--kullanici-sifre", default="OrnekSifre123")
        parser.add_argument("--admin-email", default="admin@aks.com")
        parser.add_argument("--admin-sifre", default="AdminSifre123")

    def _hesap(self, email, sifre, *, yonetici):
        """Idempotent: hesap varsa şifresini/rolünü demo değerine geri çeker —
        test edenler her koşulda giriş sayfasında yazan bilgilerle girebilsin.

        GERÇEKTEN idempotent olmak zorunda (§7.19). Önceki hali her çağrıda
        koşulsuz `set_password()` + `save()` yapıyordu. Aynı şifreyle bile
        `set_password()` YENİ bir hash üretir (farklı salt); Django ise oturumda
        parola hash'inin türevini (`_auth_user_hash`) saklar ve her istekte
        karşılaştırır. Sonuç: hash değiştiği an o hesabın TÜM açık oturumları
        sessizce geçersiz oluyordu.

        Bu komut `deploy/baslat.sh` içinde HER konteyner açılışında koştuğu için
        pratik etkisi şuydu: her dağıtım ve ücretsiz katmanda her uykudan uyanış
        (15 dk hareketsizlik) giriş yapmış herkesi çıkış yaptırıyordu. Kullanıcı
        bunu "belge yükleyince hata veriyor" olarak yaşadı — arayüz oturumu
        yalnızca sayfa açılışında kontrol ettiği için girişli görünüyor ama her
        istek reddediliyordu.

        Çözüm: yalnızca GEREKTİĞİNDE yaz. `check_password()` mevcut hash'i
        doğrular, eşleşiyorsa dokunulmaz — böylece hem "şifre her zaman
        giriş sayfasındakiyle aynı" garantisi korunur hem de oturumlar yaşar.
        """
        with transaction.atomic():
            user, yeni = User.objects.get_or_create(username=email, defaults={"email": email})
            degisti = yeni
            if user.email != email:
                user.email = email
                degisti = True
            if user.is_staff != yonetici:
                user.is_staff = yonetici
                degisti = True
            # Sadece şifre GERÇEKTEN farklıysa yaz (bkz. docstring).
            if not user.check_password(sifre):
                user.set_password(sifre)
                degisti = True
            if degisti:
                user.save()
            # Yönetici hesabı banka içi araştırma yüzeyini kullanır, kendi
            # ekstresini yüklemez — ama Profil'i olması zarar vermez ve portal
            # uçlarını da denemesine izin verir.
            if not Profil.objects.filter(user=user).exists():
                Profil.objects.create(user=user, aks_no=uret())
        return user, yeni

    def handle(self, *args, **o):
        _, yeni = self._hesap(o["kullanici_email"], o["kullanici_sifre"], yonetici=False)
        self.stdout.write(self.style.SUCCESS(
            f"Kullanıcı {'oluşturuldu' if yeni else 'güncellendi'}: {o['kullanici_email']} / {o['kullanici_sifre']}"
        ))

        _, yeni = self._hesap(o["admin_email"], o["admin_sifre"], yonetici=True)
        self.stdout.write(self.style.SUCCESS(
            f"Yönetici {'oluşturuldu' if yeni else 'güncellendi'}: {o['admin_email']} / {o['admin_sifre']} (is_staff)"
        ))

        call_command("bootstrap_kurum")
