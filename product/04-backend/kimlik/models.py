"""
Kimlik, telefon doğrulama, kurum üyeliği ve rıza defteri — execution.md §3b
Phase 7 / 7.2.

Tasarım ilkesi: MİNİMUM kişisel veri (PO kararı). İsim/soyisim/TCKN hiç
istenmez. Kullanıcının kimlik-katmanı karşılığı tamamen rastgele üretilen bir
"AKS numarası"dır (`aks_no.py`) — hiçbir kişisel veriden türetilmez. Telefon
yalnızca Sybil-direnci için istenir ve yalnızca HMAC-SHA256 özeti saklanır.

"Başkasının verisini yüklemeyi engelleme" iddiası kasıtlı olarak yapılmıyor
(bkz. execution.md §3b Phase 7 "Dürüstlük notu") — bunun yerine TESPİT +
İZLENEBİLİRLİK + HESAP VEREBİLİRLİK kurulur: `RizaKaydi`, `audit.AuditLog`
ile AYNI append-only deseni tekrarlar (KVKK savunmasının temeli).
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class Profil(models.Model):
    """Bir Django `User`'ın kimlik-katmanı karşılığı — 1:1.

    `aks_no`, kurumların müşteriden isteyeceği, kimlik numarası gibi davranan
    ama hiçbir resmi kimlikten türetilmemiş bir tanımlayıcıdır (plan §7.2).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profil")
    aks_no = models.CharField(max_length=20, unique=True, db_index=True)
    telefon_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    telefon_dogrulandi_mi = models.BooleanField(default=False)
    telefon_dogrulandi_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profiller"

    def __str__(self):
        return self.aks_no


class TelefonDogrulama(models.Model):
    """OTP akışı — kod hash'li saklanır, süreli, deneme sayısı sınırlı
    (bkz. `telefon.py`: gerçek kod/numara hiçbir yerde açık yazılmaz)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telefon_dogrulamalari"
    )
    telefon_hash = models.CharField(max_length=64)
    kod_hash = models.CharField(max_length=64)
    son_gecerlilik = models.DateTimeField()
    deneme_sayisi = models.IntegerField(default=0)
    kullanildi_mi = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    MAKS_DENEME = 5

    class Meta:
        verbose_name = "Telefon Doğrulama"
        ordering = ["-created_at"]

    def gecerli_mi(self) -> bool:
        return (
            not self.kullanildi_mi
            and self.deneme_sayisi < self.MAKS_DENEME
            and timezone.now() < self.son_gecerlilik
        )


class Kurum(models.Model):
    """Banka/finans kuruluşu — çok kiracılılığın kiracı (tenant) birimi."""
    ad = models.CharField(max_length=128)
    kod = models.SlugField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kurum"

    def __str__(self):
        return f"{self.ad} ({self.kod})"


class KurumUyeligi(models.Model):
    """Bir Django `User`'ın hangi kurum(lar) adına hareket edebileceği —
    kiracılık zorlamasının (`izinler.py`) dayandığı tablo."""
    ROL_SECENEKLERI = [("uye", "Üye"), ("yonetici", "Yönetici")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="kurum_uyelikleri")
    kurum = models.ForeignKey(Kurum, on_delete=models.CASCADE, related_name="uyeler")
    rol = models.CharField(max_length=16, choices=ROL_SECENEKLERI, default="uye")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Kurum Üyeliği"
        unique_together = [("user", "kurum")]


class ErisimTalebi(models.Model):
    """Kurumun bir müşterinin (`Profil`) verisine erişim TALEBİ.

    Müşteri onayı zorunlu (PO kararı: "müşteri onayı ile erişim") — `durum`
    yalnızca müşterinin kendi aksiyonuyla `onaylandi`/`reddedildi` olur; kurum
    tarafı yalnızca `bekliyor` durumunda talep açabilir/iptal edebilir.
    """
    DURUM_SECENEKLERI = [
        ("bekliyor", "Bekliyor"), ("onaylandi", "Onaylandı"),
        ("reddedildi", "Reddedildi"), ("iptal_edildi", "İptal Edildi"),
    ]
    kurum = models.ForeignKey(Kurum, on_delete=models.CASCADE, related_name="erisim_talepleri")
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="erisim_talepleri")
    talep_eden = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    amac = models.CharField(max_length=200)
    durum = models.CharField(max_length=16, choices=DURUM_SECENEKLERI, default="bekliyor")
    gecerlilik_bitis = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    karar_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Erişim Talebi"
        ordering = ["-created_at"]

    def aktif_mi(self) -> bool:
        return (
            self.durum == "onaylandi"
            and self.gecerlilik_bitis is not None
            and self.gecerlilik_bitis > timezone.now()
        )

    def __str__(self):
        return f"{self.kurum.kod} -> {self.profil.aks_no} ({self.durum})"


class RizaIhlali(Exception):
    """Rıza defterine yazıldıktan sonra dokunulmaya çalışıldı."""


class RizaKaydi(models.Model):
    """Değiştirilemez rıza/erişim defteri — `audit.models.AuditLog` ile AYNI
    append-only deseni tekrarlar (`save()`/`delete()` kısıtı). Her onay/ret/
    iptal/erişim olayı buraya yazılır; KVKK savunmasının kanıtı budur — bir
    müşteri "kim, ne zaman, ne için verime eriştiğini" burada tam olarak görür.
    """
    OLAY_SECENEKLERI = [
        ("talep_olusturuldu", "Talep Oluşturuldu"), ("onaylandi", "Onaylandı"),
        ("reddedildi", "Reddedildi"), ("iptal_edildi", "İptal Edildi"),
        ("erisim_kullanildi", "Erişim Kullanıldı"),
    ]
    erisim_talebi = models.ForeignKey(ErisimTalebi, on_delete=models.CASCADE, related_name="riza_kayitlari")
    olay = models.CharField(max_length=24, choices=OLAY_SECENEKLERI)
    aks_no = models.CharField(max_length=20, db_index=True)
    kurum_kod = models.CharField(max_length=32, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Rıza Kaydı"
        verbose_name_plural = "Rıza Defteri"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise RizaIhlali(
                "Rıza kaydı değiştirilemez (append-only). Düzeltme için yeni bir kayıt ekleyin."
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RizaIhlali("Rıza kaydı silinemez (append-only).")

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] {self.aks_no} <- {self.kurum_kod} ({self.olay})"
