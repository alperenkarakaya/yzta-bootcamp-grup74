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
        test edenler her koşulda giriş sayfasında yazan bilgilerle girebilsin."""
        with transaction.atomic():
            user, yeni = User.objects.get_or_create(username=email, defaults={"email": email})
            user.email = email
            user.is_staff = yonetici
            user.set_password(sifre)
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
