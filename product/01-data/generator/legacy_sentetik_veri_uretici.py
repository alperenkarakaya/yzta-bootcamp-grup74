"""
Sentetik Banka İşlem Verisi Üretici
------------------------------------
Amaç: Gerçek banka verisi kullanmadan, resmi gelir beyanı düşük/zayıf
görünen ama hesap hareketleri (transaction) açısından yüksek hacimli ve
düzenli davranış sergileyen kişileri (öğrenci, stajyer, freelancer) ve
karşılaştırma grubu olarak "klasik" maaşlı çalışanları simüle eden
işlem (transaction) kayıtları üretir.

Çıktı: data/sentetik_islemler.csv
Sütunlar:
    musteri_id, persona, tarih, islem_tipi, kategori, tutar, aciklama

Persona tipleri:
    - ogrenci_yuksek_hacim   : Düşük/yok resmi gelir, ama burs+part-time+
                                aile desteği ile düzenli ve yüksek hacimli
                                hareket. Asıl odak grubumuz.
    - stajyer_degisken_gelir : Stajyer/freelancer, değişken ama toplamda
                                yüksek gelir, düzensiz zamanlama.
    - klasik_maasli          : Resmi, sabit aylık maaşlı çalışan. Kontrol
                                (baseline) grubu.
    - dusuk_hacim_riskli     : Gerçekten düşük kapasiteli, düzensiz ve
                                az hareketli kişi. Modelin bunu da doğru
                                ayırt edebilmesi gerekiyor (negatif kontrol).

Kullanım:
    python sentetik_veri_uretici.py --musteri-sayisi 500 --gun 180
"""

import argparse
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

PERSONA_DAGILIMI = {
    "ogrenci_yuksek_hacim": 0.30,
    "stajyer_degisken_gelir": 0.25,
    "klasik_maasli": 0.30,
    "dusuk_hacim_riskli": 0.15,
}

KATEGORILER_GIDER = [
    "market", "kira", "fatura", "ulasim", "abonelik",
    "yeme_icme", "giyim", "eglence", "saglik", "egitim",
]

GELIR_ACIKLAMALARI = {
    "ogrenci_yuksek_hacim": ["burs_odemesi", "part_time_maas", "aile_destegi", "freelance_proje"],
    "stajyer_degisken_gelir": ["staj_ucreti", "freelance_proje", "ek_is_geliri"],
    "klasik_maasli": ["maas_odemesi"],
    "dusuk_hacim_riskli": ["duzensiz_gelir", "nakit_yatirma"],
}


def _persona_sec():
    r = random.random()
    kumulatif = 0.0
    for persona, oran in PERSONA_DAGILIMI.items():
        kumulatif += oran
        if r <= kumulatif:
            return persona
    return "klasik_maasli"


def _gelir_paterni(persona, gun_sayisi, baslangic):
    """Persona'ya göre gelir işlemleri üretir (tarih, tutar, açıklama)."""
    islemler = []

    if persona == "klasik_maasli":
        # Her ayın ilk iş günü sabit maaş
        maas = random.randint(18000, 35000)
        gun = 1
        while gun < gun_sayisi:
            tarih = baslangic + timedelta(days=gun)
            islemler.append((tarih, maas + random.randint(-200, 200), "maas_odemesi"))
            gun += 30

    elif persona == "ogrenci_yuksek_hacim":
        # Burs + part-time + ailesinden düzenli destek -> sıklık yüksek,
        # tek tek tutarlar küçük görünse de TOPLAM hacim yüksek.
        burs = random.randint(2000, 4000)
        part_time = random.randint(4000, 9000)
        aile = random.randint(1500, 4000)
        gun = random.randint(1, 5)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), burs, "burs_odemesi"))
            gun += 30
        gun = random.randint(1, 15)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), part_time + random.randint(-500, 500), "part_time_maas"))
            gun += 15
        gun = random.randint(1, 30)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), aile, "aile_destegi"))
            gun += 30
        # Ek olarak arada freelance/proje geliri (hacmi yukarı çeken kısım)
        for _ in range(random.randint(2, 6)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(1500, 6000), "freelance_proje"))

    elif persona == "stajyer_degisken_gelir":
        gun = random.randint(1, 10)
        while gun < gun_sayisi:
            tutar = random.randint(6000, 16000)
            islemler.append((baslangic + timedelta(days=gun), tutar, "staj_ucreti"))
            gun += random.randint(20, 40)  # düzensiz periyot
        for _ in range(random.randint(3, 8)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(1000, 7000), "freelance_proje"))

    else:  # dusuk_hacim_riskli
        for _ in range(random.randint(1, 4)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(500, 3000), "duzensiz_gelir"))

    return islemler


def _gider_paterni(persona, gun_sayisi, baslangic, toplam_gelir):
    """Toplam gelire bağlı, persona'ya göre gider/tasarruf davranışı üretir."""
    islemler = []

    if persona == "ogrenci_yuksek_hacim":
        gider_orani = random.uniform(0.55, 0.75)  # disiplinli, tasarruflu
    elif persona == "stajyer_degisken_gelir":
        gider_orani = random.uniform(0.65, 0.85)
    elif persona == "klasik_maasli":
        gider_orani = random.uniform(0.60, 0.80)
    else:
        gider_orani = random.uniform(0.85, 1.05)  # riskli: gelirine yakın/fazla harcıyor

    hedef_toplam_gider = toplam_gelir * gider_orani
    islem_sayisi = max(10, int(gun_sayisi / 4))
    kalan = hedef_toplam_gider

    for i in range(islem_sayisi):
        gun = random.randint(0, gun_sayisi - 1)
        kategori = random.choice(KATEGORILER_GIDER)
        if i == islem_sayisi - 1:
            tutar = max(50, kalan)
        else:
            tutar = max(50, round(random.uniform(0.02, 0.08) * hedef_toplam_gider))
        kalan -= tutar
        islemler.append((baslangic + timedelta(days=gun), -abs(round(tutar)), kategori))

    return islemler


def uret(musteri_sayisi=500, gun_sayisi=180, baslangic_tarihi="2026-01-01"):
    baslangic = datetime.strptime(baslangic_tarihi, "%Y-%m-%d")
    kayitlar = []

    for musteri_id in range(1, musteri_sayisi + 1):
        persona = _persona_sec()
        gelir_islemleri = _gelir_paterni(persona, gun_sayisi, baslangic)
        toplam_gelir = sum(t for _, t, _ in gelir_islemleri) or 1
        gider_islemleri = _gider_paterni(persona, gun_sayisi, baslangic, toplam_gelir)

        for tarih, tutar, aciklama in gelir_islemleri:
            kayitlar.append({
                "musteri_id": musteri_id,
                "persona": persona,
                "tarih": tarih.strftime("%Y-%m-%d"),
                "islem_tipi": "gelir",
                "kategori": aciklama,
                "tutar": round(tutar, 2),
                "aciklama": aciklama,
            })
        for tarih, tutar, kategori in gider_islemleri:
            kayitlar.append({
                "musteri_id": musteri_id,
                "persona": persona,
                "tarih": tarih.strftime("%Y-%m-%d"),
                "islem_tipi": "gider",
                "kategori": kategori,
                "tutar": round(tutar, 2),
                "aciklama": kategori,
            })

    kayitlar.sort(key=lambda k: (k["musteri_id"], k["tarih"]))
    return kayitlar


def csv_yaz(kayitlar, dosya_yolu):
    alanlar = ["musteri_id", "persona", "tarih", "islem_tipi", "kategori", "tutar", "aciklama"]
    with open(dosya_yolu, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=alanlar)
        yazici.writeheader()
        yazici.writerows(kayitlar)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sentetik banka işlem verisi üretici")
    parser.add_argument("--musteri-sayisi", type=int, default=500)
    parser.add_argument("--gun", type=int, default=180)
    parser.add_argument("--baslangic", type=str, default="2026-01-01")
    parser.add_argument("--cikti", type=str, default="../data/sentetik_islemler.csv")
    args = parser.parse_args()

    kayitlar = uret(args.musteri_sayisi, args.gun, args.baslangic)
    csv_yaz(kayitlar, args.cikti)
    print(f"{len(kayitlar)} işlem kaydı üretildi -> {args.cikti}")
    print(f"Müşteri sayısı: {args.musteri_sayisi}, gün aralığı: {args.gun}")
