"""
Bağlantı doğrulama — Supabase (Postgres) ve Upstash (Redis) canlı mı, yoksa
yerel yedeğe (SQLite / LocMemCache) mi düşülmüş, açıkça raporlar.

Çalıştırma:  python manage.py check_connections
"""
import os

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Supabase (DB) ve Upstash (Redis) bağlantılarını doğrular; yerel yedeğe düşüldüyse açıkça belirtir."

    def handle(self, *args, **options):
        self._veritabani()
        self._cache()

    def _veritabani(self) -> None:
        vendor = connection.vendor
        db_url_set = bool(os.environ.get("DATABASE_URL"))
        self.stdout.write(f"\n== Veritabanı ==")
        self.stdout.write(f"  DATABASE_URL tanımlı mı: {'evet' if db_url_set else 'hayır (yerel SQLite kullanılıyor)'}")
        try:
            with connection.cursor() as c:
                c.execute("SELECT 1")
                c.fetchone()
            durum = self.style.SUCCESS("BAŞARILI")
        except Exception as e:
            durum = self.style.ERROR(f"HATA: {e}")
        self.stdout.write(f"  Motor: {vendor} — bağlantı: {durum}")
        if vendor == "postgresql":
            self.stdout.write(self.style.SUCCESS("  -> Supabase (Postgres) CANLI ve bağlı."))
        else:
            self.stdout.write(self.style.WARNING(
                "  -> Supabase henüz bağlı DEĞİL; SQLite yerel dosyaya yazılıyor "
                "(product/04-backend/aks_dev.sqlite3). DATABASE_URL'i .env'e ekleyip tekrar çalıştırın."))

    def _cache(self) -> None:
        redis_url_set = bool(os.environ.get("REDIS_URL"))
        backend = cache.__class__.__module__ + "." + cache.__class__.__name__
        self.stdout.write(f"\n== Cache ==")
        self.stdout.write(f"  REDIS_URL tanımlı mı: {'evet' if redis_url_set else 'hayır (yerel bellek cache kullanılıyor)'}")
        try:
            cache.set("aks_baglanti_testi", "ok", timeout=10)
            deger = cache.get("aks_baglanti_testi")
            durum = self.style.SUCCESS("BAŞARILI") if deger == "ok" else self.style.ERROR("YAZMA/OKUMA UYUŞMUYOR")
        except Exception as e:
            durum = self.style.ERROR(f"HATA: {e}")
        self.stdout.write(f"  Backend: {backend} — okuma/yazma: {durum}")
        if "redis" in backend.lower():
            self.stdout.write(self.style.SUCCESS("  -> Upstash Redis CANLI ve bağlı."))
        else:
            self.stdout.write(self.style.WARNING(
                "  -> Upstash henüz bağlı DEĞİL; Django LocMemCache (process-içi bellek) kullanılıyor. "
                "REDIS_URL'i .env'e ekleyip tekrar çalıştırın."))
        self.stdout.write("")
