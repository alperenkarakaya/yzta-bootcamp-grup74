"""
Demo kurum (banka) + kurum personeli hesabı oluşturur — kurum girişini
canlı denemek için Django admin'e gitmeye gerek kalmadan.

§3b Phase 7/7.2: kurum üyeliği ÖZ-KAYIT (self-serve) değil, kasıtlı olarak
provizyonlanır — bir kurumun kendi kendine "kurum" olarak kaydolabilmesi,
rıza sisteminin dayandığı "kurum kimliği doğrulanmıştır" varsayımını
zayıflatır (execution.md §3b Phase 7, yeni OQ: gerçek kurum onboarding'i
nasıl olmalı — sözleşme + manuel doğrulama mı, otomatik bir süreç mi).

Çalıştırma:
    python manage.py bootstrap_kurum
    python manage.py bootstrap_kurum --email banka@ornek.com --sifre GucluSifre123
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from kimlik.models import Kurum, KurumUyeligi


class Command(BaseCommand):
    help = "Demo kurum + kurum personeli hesabı oluşturur (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--kurum-adi", default="Demo Bankası")
        parser.add_argument("--kurum-kod", default="demo-bankasi")
        parser.add_argument("--email", default="kurum@demo.aks")
        parser.add_argument("--sifre", default="DemoKurum123!")

    def handle(self, *args, **o):
        kurum, olusturuldu = Kurum.objects.get_or_create(kod=o["kurum_kod"], defaults={"ad": o["kurum_adi"]})
        self.stdout.write(
            self.style.SUCCESS(f"Kurum {'oluşturuldu' if olusturuldu else 'zaten vardı'}: {kurum.ad} ({kurum.kod})")
        )

        user, kullanici_olusturuldu = User.objects.get_or_create(
            username=o["email"], defaults={"email": o["email"]}
        )
        if kullanici_olusturuldu:
            user.set_password(o["sifre"])
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Kurum personeli oluşturuldu: {o['email']} / {o['sifre']}"))
        else:
            self.stdout.write(self.style.WARNING(f"Kullanıcı zaten vardı: {o['email']} (şifre değiştirilmedi)"))

        _, uyelik_olusturuldu = KurumUyeligi.objects.get_or_create(
            user=user, kurum=kurum, defaults={"rol": "yonetici"}
        )
        if uyelik_olusturuldu:
            self.stdout.write(self.style.SUCCESS(f"{user.username} -> {kurum.ad} üyeliği eklendi (yönetici)."))
        else:
            self.stdout.write(self.style.WARNING(f"{user.username} zaten {kurum.ad} üyesiydi."))
