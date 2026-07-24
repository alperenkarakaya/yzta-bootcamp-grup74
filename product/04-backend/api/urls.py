from django.urls import path

from . import auth_views, portal_views, views

urlpatterns = [
    path("bilgi", views.bilgi),
    path("metrikler", views.metrikler),
    path("politika", views.politika),
    path("segmentasyon", views.segmentasyon),
    path("genelleme-saglamlik", views.genelleme_saglamlik),
    path("demo-musteriler", views.demo_musteriler),
    path("skorla", views.skorla),
    path("skorla/<int:musteri_id>", views.skorla_demo),
    path("aciklama", views.aciklama),
    path("simulasyon", views.simulasyon),
    path("portfoy", views.portfoy),
    path("adalet", views.adalet),
    path("csv-skorla", views.csv_skorla),
    path("asistan", views.asistan),
    path("gecmis/<int:musteri_id>", views.gecmis),
    # Kullanıcı portalı — §3b Phase 6
    path("auth/ben", auth_views.ben),
    path("auth/kayit", auth_views.kayit),
    path("auth/giris", auth_views.giris),
    path("auth/cikis", auth_views.cikis),
    path("portal/yukle", portal_views.portal_yukle),
    path("portal/gecmis", portal_views.portal_gecmis),
]
