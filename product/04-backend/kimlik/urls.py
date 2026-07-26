from django.urls import path

from . import kurum_views, views

urlpatterns = [
    # Müşteri taraflı (portal oturumu)
    path("profilim", views.profilim),
    path("telefon/gonder", views.telefon_gonder),
    path("telefon/dogrula", views.telefon_dogrula),
    path("erisim-talepleri", views.erisim_talepleri),
    path("erisim-talebi/<int:talep_id>/onayla", views.erisim_talebi_onayla),
    path("erisim-talebi/<int:talep_id>/reddet", views.erisim_talebi_reddet),
    path("erisim-talebi/<int:talep_id>/iptal", views.erisim_talebi_iptal),
    path("riza-defterim", views.riza_defterim),
    # Kurum taraflı (banka oturumu)
    path("kurum/ben", kurum_views.ben),
    path("kurum/erisim-talebi", kurum_views.erisim_talebi_olustur),
    path("kurum/musteriler", kurum_views.musteriler),
    path("kurum/musteri/<str:aks_numarasi>", kurum_views.musteri_detay),
]
