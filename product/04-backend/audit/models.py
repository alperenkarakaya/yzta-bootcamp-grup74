"""
Denetim izi modelleri — sınır (boundary) hikâyesini operasyonelleştirir.

Her skorlama, DEĞİŞTİRİLEMEZ bir AuditLog satırı yazar: klasik (banka) skoru
OLDUĞU GİBİ kaydedilir, yanına AKS'nin ürettiği tamamlayıcı skor + karar +
politika notu konur. Böylece "AKS bankanın segmentini asla ezmez, yalnızca
tamamlar" ilkesi kayıt altında kanıtlanır (bkz. overview.md §7 / architecture.md §9).
"""
from django.db import models


class Customer(models.Model):
    external_id = models.CharField(max_length=64, db_index=True)
    persona = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Müşteri"

    def __str__(self):
        return f"{self.external_id} ({self.persona or 'bilinmiyor'})"


class Assessment(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments"
    )
    musteri_id = models.CharField(max_length=64, db_index=True)
    klasik_skor = models.IntegerField(null=True, blank=True)
    aks_skor = models.IntegerField()
    risk_seviyesi = models.CharField(max_length=32)
    karar = models.CharField(max_length=128)
    onerilen_limit = models.IntegerField(null=True, blank=True)
    ozellikler = models.JSONField(default=dict)
    kaynak = models.CharField(max_length=16, default="api")  # demo / csv / api
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Değerlendirme"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.musteri_id} AKS={self.aks_skor} ({self.created_at:%Y-%m-%d %H:%M})"


class DenetimIziIhlali(Exception):
    """Denetim izine yazıldıktan sonra dokunulmaya çalışıldı."""


class AuditLog(models.Model):
    """Değiştirilemez denetim kaydı — sadece INSERT.

    Ürünün ana vaadi, bankanın klasik skorunun asla ezilmediği ve her kararın
    denetlenebilir bir iz bıraktığıdır. Bu iz sonradan düzenlenebiliyorsa vaat
    boştur: yanlış bir karar kayıttan silinebilir, klasik skor geriye dönük
    değiştirilebilir.

    Bu yüzden update ve delete kod düzeyinde engellenmiştir. Düzeltme gerekiyorsa
    yöntem kaydı değiştirmek değil, yeni bir kayıt eklemektir (append-only).
    `api/tests.py` içindeki sınır testleri bu kısıtı doğrular.
    """
    musteri_id = models.CharField(max_length=64, db_index=True)
    klasik_skor = models.IntegerField(null=True, blank=True, help_text="Banka skoru — DEĞİŞTİRİLMEDİ")
    aks_skor = models.IntegerField(help_text="AKS tamamlayıcı skor")
    karar = models.CharField(max_length=128)
    onerilen_limit = models.IntegerField(null=True, blank=True)
    politika_notu = models.CharField(
        max_length=200,
        default="AKS tamamlayıcıdır; banka segmenti/skoru değiştirilmedi.",
    )
    ajanlar = models.JSONField(default=list)  # kullanılan agent'lar
    kaynak = models.CharField(max_length=16, default="api")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Denetim Kaydı"
        verbose_name_plural = "Denetim İzi"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise DenetimIziIhlali(
                "Denetim kaydı değiştirilemez (append-only). "
                "Düzeltme için yeni bir kayıt ekleyin."
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise DenetimIziIhlali("Denetim kaydı silinemez (append-only).")

    def __str__(self):
        return f"[{self.created_at:%Y-%m-%d %H:%M}] #{self.musteri_id} AKS={self.aks_skor}"
