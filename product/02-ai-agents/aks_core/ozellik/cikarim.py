"""
Özellik Mühendisliği
--------------------
Ham işlem (transaction) kayıtlarından kişi bazlı davranışsal özellikler çıkarır.
Hem model eğitiminde hem de canlı skorlamada (API) aynı fonksiyon kullanılır;
böylece eğitim/servis arasında tutarlılık garanti edilir.
"""
import csv, statistics
from collections import defaultdict
from datetime import datetime

OZELLIK_ADLARI = [
    "toplam_gelir_hacmi", "toplam_gider_hacmi", "gelir_islem_sayisi",
    "gelir_kaynagi_sayisi", "gelir_duzenliligi", "gider_gelir_orani",
    "bakiye_trendi", "fatura_odeme_duzeni", "hesap_hareket_yogunlugu",
]


def _tarih(s): return datetime.strptime(s, "%Y-%m-%d")


def csv_oku(dosya_yolu):
    musteri = defaultdict(list); persona = {}
    with open(dosya_yolu, encoding="utf-8") as f:
        for satir in csv.DictReader(f):
            mid = int(satir["musteri_id"])
            satir["tutar"] = float(satir["tutar"])
            satir["tarih_obj"] = _tarih(satir["tarih"])
            musteri[mid].append(satir); persona[mid] = satir["persona"]
    return musteri, persona


def ozellik_cikar(islemler):
    gelirler = [i for i in islemler if i["islem_tipi"] == "gelir"]
    giderler = [i for i in islemler if i["islem_tipi"] == "gider"]
    toplam_gelir = sum(i["tutar"] for i in gelirler)
    toplam_gider = abs(sum(i["tutar"] for i in giderler))

    gelir_duzenliligi = 0.0
    if len(gelirler) >= 3:
        t = sorted(i["tarih_obj"] for i in gelirler)
        farklar = [(t[i + 1] - t[i]).days for i in range(len(t) - 1)]
        if len(farklar) >= 2 and statistics.mean(farklar) > 0:
            vk = statistics.pstdev(farklar) / statistics.mean(farklar)
            gelir_duzenliligi = max(0.0, 1 - min(vk, 1.0))

    gider_gelir_orani = (toplam_gider / toplam_gelir) if toplam_gelir > 0 else 1.5

    tum = sorted(islemler, key=lambda i: i["tarih_obj"])
    kum = 0.0; seri = []
    for i in tum:
        kum += i["tutar"]; seri.append(kum)
    bakiye_trendi = (seri[-1] - seri[0]) / (abs(seri[0]) + 1) if len(seri) >= 2 else 0.0

    fatura = [i for i in giderler if i["kategori"] == "fatura"]
    fatura_odeme_duzeni = min(len(fatura) / 6.0, 1.0)

    gun = (tum[-1]["tarih_obj"] - tum[0]["tarih_obj"]).days + 1 if tum else 1
    return {
        "toplam_gelir_hacmi": round(toplam_gelir, 2),
        "toplam_gider_hacmi": round(toplam_gider, 2),
        "gelir_islem_sayisi": len(gelirler),
        "gelir_kaynagi_sayisi": len(set(i["kategori"] for i in gelirler)),
        "gelir_duzenliligi": round(gelir_duzenliligi, 3),
        "gider_gelir_orani": round(gider_gelir_orani, 3),
        "bakiye_trendi": round(bakiye_trendi, 3),
        "fatura_odeme_duzeni": round(fatura_odeme_duzeni, 3),
        "hesap_hareket_yogunlugu": round(len(islemler) / max(gun, 1), 3),
    }


def tum_musteriler(dosya_yolu):
    musteri, persona = csv_oku(dosya_yolu)
    sonuc = []
    for mid, islemler in musteri.items():
        oz = ozellik_cikar(islemler)
        sonuc.append({"musteri_id": mid, "persona": persona[mid], **oz})
    return sonuc
