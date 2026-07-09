from django.urls import path

from . import views

urlpatterns = [
    path("bilgi", views.bilgi),
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
]
