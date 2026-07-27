"""
Denetim izi modelleri — sınır (boundary) hikâyesini operasyonelleştirir.

Her skorlama, DEĞİŞTİRİLEMEZ bir AuditLog satırı yazar: klasik (banka) skoru
OLDUĞU GİBİ kaydedilir, yanına AKS'nin ürettiği tamamlayıcı skor + karar +
politika notu konur. Böylece "AKS bankanın segmentini asla ezmez, yalnızca
tamamlar" ilkesi kayıt altında kanıtlanır (bkz. overview.md §7 / architecture.md §9).
"""
from django.conf import settings
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
    kaynak = models.CharField(max_length=16, default="api")  # demo / csv / api / portal
    # Kullanıcı portalı (§3b Phase 6): giriş yapmış bir son kullanıcının kendi
    # yüklediği ekstre — "Geçmişim" listesini besler. Banka/demo skorlamalarında
    # (kaynak != "portal") her zaman null — bu alan yalnızca portal kullanıcısını
    # KENDİ geçmişine bağlar, bankanın gördüğü hiçbir veriyi etkilemez.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="degerlendirmeler"
    )
    # §3b Phase 7/7.2 — kurumun (banka) rıza-tabanlı erişimle görebildiği kayıt
    # bu FK üzerinden bulunur (`kimlik.kurum_views.musteri_detay`). String
    # referans kullanılıyor ('kimlik.Profil') — audit app'i kimlik'i DOĞRUDAN
    # import ETMEZ, yalnızca migration bağımlılığı kurulur (uygulama sırası
    # gevşek kalır). `user` alanından ayrı: `user` portal oturumunu, `profil`
    # kimlik/rıza katmanını temsil eder — ikisi normalde aynı kullanıcıya
    # işaret eder ama kavramsal olarak farklı katmanlardır.
    profil = models.ForeignKey(
        "kimlik.Profil", on_delete=models.SET_NULL, null=True, blank=True, related_name="degerlendirmeler"
    )
    # §3b Phase 7/7.3 (sahiplik savunması) — bu turda ŞEMA eklenir, doldurma
    # mantığı 7.3'te gelir. `sahiplik_bayraklari` örn. ["coklu_sahiplik_supheli"].
    belge_parmak_izi = models.CharField(max_length=64, blank=True, default="")
    sahiplik_beyani = models.BooleanField(default=False, help_text="Yükleyen 'bu ekstre bana ait' onayı verdi mi")
    # Planın ilk taslağı bu olayı RizaKaydi'na yazmayı öngörmüştü; RizaKaydi
    # zorunlu bir ErisimTalebi FK'sine bağlı (KURUM erişim rızası içindir) —
    # kendi-yükleme beyanı kavramsal olarak farklı bir olay, o modele
    # zorlanmadı. Zaman zaten `created_at`'te var; IP burada tutulur.
    yukleme_ip = models.GenericIPAddressField(null=True, blank=True)
    sahiplik_bayraklari = models.JSONField(default=list, blank=True)
    kaynak_format = models.CharField(max_length=16, blank=True, default="", help_text="csv/xlsx/pdf")
    # PO kararı: müşteri tarafından yüklenen ham işlemler (normalize edilmiş
    # {tarih, islem_tipi, kategori, tutar, aciklama} listesi) müşteri bazlı
    # saklanmalı — yalnızca türetilmiş `ozellikler` yeterli değil. Yalnızca
    # `profil` doluyken (yani kimliği doğrulanmış bir müşterinin kendi portal
    # yüklemesinde) doldurulur; bankanın demo/anonim skorlamalarında (kaynak
    # in {"demo","api"}, `profil` yok) boş kalır — o veri zaten kaynak CSV'de
    # duruyor, ikinci kez saklamanın kişisel veri ayak izini büyütmekten başka
    # faydası yok. `aciklama` serbest metin alanı da dahildir; bu nedenle bu
    # alan yalnızca `ProfilSahibi` sahibine (`portal_gecmis_detay`) ve rızalı
    # erişimi olan kuruma DEĞİL, YALNIZCA müşterinin kendisine açılır.
    ham_islemler = models.JSONField(default=list, blank=True)
    # Formülasyon B (architecture.md §5.3, §3b U10/U18) — yalnızca klasik skor
    # biliniyorsa (persona verildiyse) hesaplanır; aksi halde null.
    pd_fark = models.FloatField(null=True, blank=True, help_text="pd_geleneksel_bant − pd_davranissal")
    kapasite_sinyali = models.IntegerField(null=True, blank=True, help_text="0-100, 50=nötr")
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
    # Formülasyon B (architecture.md §5.3, §3b U10/U18) — klasik_skor gibi salt-okunur
    # bir türetilmiş alan; audit satırının append-only doğasını değiştirmez.
    pd_fark = models.FloatField(null=True, blank=True, help_text="pd_geleneksel_bant − pd_davranissal")
    kapasite_sinyali = models.IntegerField(null=True, blank=True, help_text="0-100, 50=nötr")
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
