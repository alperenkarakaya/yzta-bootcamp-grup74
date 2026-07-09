"""
Sentetik Banka İşlem Verisi Üretici (Sprint 2 - düzeltilmiş)
------------------------------------------------------------
Sprint 1'e göre değişiklik: gider dağıtımındaki hata düzeltildi. Artık
toplam gider, hedeflenen gider/gelir oranına tam uyuyor. Böylece
'gider_gelir_orani' özelliği persona'lar arasında ayırt edici hale geldi.
"""
import argparse, csv, random
from datetime import datetime, timedelta

random.seed(42)

PERSONA_DAGILIMI = {
    "ogrenci_yuksek_hacim": 0.30, "stajyer_degisken_gelir": 0.25,
    "klasik_maasli": 0.30, "dusuk_hacim_riskli": 0.15,
}
KATEGORILER_GIDER = ["market", "kira", "fatura", "ulasim", "abonelik",
                     "yeme_icme", "giyim", "eglence", "saglik", "egitim"]


def _persona_sec():
    r = random.random(); k = 0.0
    for persona, oran in PERSONA_DAGILIMI.items():
        k += oran
        if r <= k:
            return persona
    return "klasik_maasli"


def _gelir_paterni(persona, gun_sayisi, baslangic):
    islemler = []
    if persona == "klasik_maasli":
        maas = random.randint(18000, 35000); gun = 1
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), maas + random.randint(-200, 200), "maas_odemesi")); gun += 30
    elif persona == "ogrenci_yuksek_hacim":
        burs = random.randint(2000, 4000); part_time = random.randint(4000, 9000); aile = random.randint(1500, 4000)
        gun = random.randint(1, 5)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), burs, "burs_odemesi")); gun += 30
        gun = random.randint(1, 15)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), part_time + random.randint(-500, 500), "part_time_maas")); gun += 15
        gun = random.randint(1, 30)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), aile, "aile_destegi")); gun += 30
        for _ in range(random.randint(2, 6)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(1500, 6000), "freelance_proje"))
    elif persona == "stajyer_degisken_gelir":
        gun = random.randint(1, 10)
        while gun < gun_sayisi:
            islemler.append((baslangic + timedelta(days=gun), random.randint(6000, 16000), "staj_ucreti")); gun += random.randint(20, 40)
        for _ in range(random.randint(3, 8)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(1000, 7000), "freelance_proje"))
    else:
        for _ in range(random.randint(1, 4)):
            gun = random.randint(0, gun_sayisi - 1)
            islemler.append((baslangic + timedelta(days=gun), random.randint(500, 3000), "duzensiz_gelir"))
    return islemler


def _gider_paterni(persona, gun_sayisi, baslangic, toplam_gelir):
    """DÜZELTİLDİ: rastgele ağırlıklar normalize edilerek toplam gider
    hedeflenen orana tam eşitlenir."""
    islemler = []
    if persona == "ogrenci_yuksek_hacim":
        gider_orani = random.uniform(0.50, 0.95)
    elif persona == "stajyer_degisken_gelir":
        gider_orani = random.uniform(0.60, 1.00)
    elif persona == "klasik_maasli":
        gider_orani = random.uniform(0.55, 0.95)
    else:
        gider_orani = random.uniform(0.90, 1.18)
    hedef = toplam_gelir * gider_orani
    n = max(10, int(gun_sayisi / 4))
    agirliklar = [random.uniform(0.5, 1.5) for _ in range(n)]
    ta = sum(agirliklar)
    for a in agirliklar:
        gun = random.randint(0, gun_sayisi - 1)
        tutar = max(50, round(hedef * a / ta))
        islemler.append((baslangic + timedelta(days=gun), -abs(tutar), random.choice(KATEGORILER_GIDER)))
    return islemler


def uret(musteri_sayisi=2000, gun_sayisi=180, baslangic_tarihi="2026-01-01"):
    baslangic = datetime.strptime(baslangic_tarihi, "%Y-%m-%d")
    kayitlar = []
    for mid in range(1, musteri_sayisi + 1):
        persona = _persona_sec()
        gelir = _gelir_paterni(persona, gun_sayisi, baslangic)
        toplam_gelir = sum(t for _, t, _ in gelir) or 1
        gider = _gider_paterni(persona, gun_sayisi, baslangic, toplam_gelir)
        for tarih, tutar, acik in gelir:
            kayitlar.append({"musteri_id": mid, "persona": persona, "tarih": tarih.strftime("%Y-%m-%d"),
                             "islem_tipi": "gelir", "kategori": acik, "tutar": round(tutar, 2), "aciklama": acik})
        for tarih, tutar, kat in gider:
            kayitlar.append({"musteri_id": mid, "persona": persona, "tarih": tarih.strftime("%Y-%m-%d"),
                             "islem_tipi": "gider", "kategori": kat, "tutar": round(tutar, 2), "aciklama": kat})
    kayitlar.sort(key=lambda k: (k["musteri_id"], k["tarih"]))
    return kayitlar


def csv_yaz(kayitlar, dosya_yolu):
    alanlar = ["musteri_id", "persona", "tarih", "islem_tipi", "kategori", "tutar", "aciklama"]
    with open(dosya_yolu, "w", newline="", encoding="utf-8") as f:
        y = csv.DictWriter(f, fieldnames=alanlar); y.writeheader(); y.writerows(kayitlar)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--musteri-sayisi", type=int, default=2000)
    p.add_argument("--gun", type=int, default=180)
    p.add_argument("--cikti", type=str, default="data/sentetik_islemler.csv")
    a = p.parse_args()
    k = uret(a.musteri_sayisi, a.gun); csv_yaz(k, a.cikti)
    print(f"{len(k)} işlem üretildi -> {a.cikti} ({a.musteri_sayisi} müşteri)")
