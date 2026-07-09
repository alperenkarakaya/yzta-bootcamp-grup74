from django.contrib import admin

from .models import AuditLog, Assessment, Customer


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "musteri_id", "klasik_skor", "aks_skor", "karar", "kaynak")
    list_filter = ("kaynak", "created_at")
    search_fields = ("musteri_id",)
    readonly_fields = [f.name for f in AuditLog._meta.fields]  # görüntüle, değiştirme

    def has_change_permission(self, request, obj=None):
        return False  # denetim izi değiştirilemez

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("created_at", "musteri_id", "klasik_skor", "aks_skor", "risk_seviyesi", "karar")
    list_filter = ("risk_seviyesi", "kaynak", "created_at")
    search_fields = ("musteri_id",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("external_id", "persona", "created_at")
    search_fields = ("external_id",)
