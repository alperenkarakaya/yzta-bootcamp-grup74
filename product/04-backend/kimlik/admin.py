from django.contrib import admin

from .models import ErisimTalebi, Kurum, KurumUyeligi, Profil, RizaKaydi, TelefonDogrulama


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ("aks_no", "user", "telefon_dogrulandi_mi", "created_at")
    search_fields = ("aks_no",)


@admin.register(TelefonDogrulama)
class TelefonDogrulamaAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "kullanildi_mi", "deneme_sayisi", "son_gecerlilik")
    readonly_fields = ("kod_hash", "telefon_hash")


@admin.register(Kurum)
class KurumAdmin(admin.ModelAdmin):
    list_display = ("ad", "kod", "created_at")


@admin.register(KurumUyeligi)
class KurumUyeligiAdmin(admin.ModelAdmin):
    list_display = ("user", "kurum", "rol", "created_at")


@admin.register(ErisimTalebi)
class ErisimTalebiAdmin(admin.ModelAdmin):
    list_display = ("kurum", "profil", "durum", "gecerlilik_bitis", "created_at")
    list_filter = ("durum", "kurum")


@admin.register(RizaKaydi)
class RizaKaydiAdmin(admin.ModelAdmin):
    list_display = ("created_at", "aks_no", "kurum_kod", "olay")
    list_filter = ("olay", "kurum_kod")
    readonly_fields = [f.name for f in RizaKaydi._meta.fields]

    def has_change_permission(self, request, obj=None):
        return False  # rıza defteri değiştirilemez

    def has_delete_permission(self, request, obj=None):
        return False
