"""
Kapasite-Sürümlü Sentetik İşlem Üretici (DÖNGÜSELLİK-KIRAN)
==========================================================
Bu üretici, mevcut `uretici.py` + `etiketleme.py` ikilisindeki YAPISAL
DÖNGÜSELLİĞİ çözer (bkz. architecture.md §5.1, planning/data-architecture.md §3).

Mevcut sorun:
  persona  ─►  özellikler  ─►  etiket        (persona hem özellikleri hem
       └──────────────────────►  etiket        etiketi belirliyor → tautoloji)

Bu üreticinin çözümü — persona'dan BAĞIMSIZ gizli kapasite:
  gizli_kapasite (c) ~ N(0,1)   [persona'dan BAĞIMSIZ çekilir]
       ├──►  ETİKET  = f(c) + gürültü        (etiket YALNIZCA c'ye bağlı)
       └──►  ÖZELLİKLER = c'nin gürültülü, kısmi gözlemleri + persona sunumu

Sonuç: davranışsal özellikler c'yi gerçekten kurtarır (gerçek sinyal),
klasik/gelir kanalı c'yi zayıf/yanlı gözlemler (thin-file kör noktası) —
ama HİÇBİR özellik etiketin kendisi DEĞİLDİR. Bu, ürünün tezini
("davranış, geleneksel dosyanın göremediği kapasiteyi ortaya çıkarır")
DÜRÜST biçimde ölçülebilir kılar.

Araştırma girdisi (open banking cash-flow) burada ZENGİN ham alanlar olarak
üretilir: kanal, karşı-taraf tipi, brüt vs net gelir, zorunlu/ihtiyari gider.
Bunlar Tier-1 özelliklerinin (02-ai-agents) çıkarılmasını mümkün kılar.

NOT: Bu, canlı üreticiyi (`uretici.py`) DEĞİŞTİRMEZ. OQ-36/OQ-37 (gerçek veri
vs sentetik, ve sıralama) Product Owner kararıdır. Bu modül honest-fallback
prototipidir; `dekuple_kanit.py` döngüselliğin kırıldığını sayısal kanıtlar.
"""
import argparse
import csv
import math
import random
from datetime import datetime, timedelta

SEED = 20260710

PERSONA_DAGILIMI = {
    "ogrenci_yuksek_hacim": 0.30,
    "stajyer_degisken_gelir": 0.25,
    "klasik_maasli": 0.30,
    "dusuk_hacim_riskli": 0.15,
}

# Persona SUNUM parametreleri (yalnızca gözlemi/sunumu etkiler; c'yi ve etiketi ASLA etkilemez)
PERSONA_SUNUM = {
    "klasik_maasli":         {"aylik_gelir": 27000, "cv_baz": 0.06, "gio_baz": 0.74, "kaynaklar": ("maas",)},
    "ogrenci_yuksek_hacim":  {"aylik_gelir": 7500,  "cv_baz": 0.42, "gio_baz": 0.80, "kaynaklar": ("burs", "part_time", "aile", "freelance")},
    "stajyer_degisken_gelir":{"aylik_gelir": 11000, "cv_baz": 0.50, "gio_baz": 0.83, "kaynaklar": ("staj", "freelance")},
    "dusuk_hacim_riskli":    {"aylik_gelir": 4800,  "cv_baz": 0.38, "gio_baz": 0.97, "kaynaklar": ("duzensiz",)},
}

KAYNAK_KARSI_TARAF = {
    "maas": "isveren", "burs": "kurum", "part_time": "isveren", "aile": "birey",
    "freelance": "platform", "staj": "isveren", "duzensiz": "birey",
}
KAYNAK_KANAL = {
    "maas": "otomatik_odeme", "burs": "havale", "part_time": "havale", "aile": "havale",
    "freelance": "havale", "staj": "havale", "duzensiz": "nakit",
}
GIDER_ZORUNLU = {"kira", "fatura", "market", "ulasim", "saglik"}
GIDER_IHTIYARI = {"abonelik", "yeme_icme", "giyim", "eglence", "egitim"}


def _sigmoid(x):
    return 1 / (1 + math.exp(-x))


def _intercept_kalibre(kismi_logitler, hedef_oran, tol=1e-4):
    """mean(sigmoid(b + z)) = hedef_oran olacak b'yi ikili aramayla bulur."""
    lo, hi = -12.0, 12.0
    b = 0.0
    for _ in range(80):
        b = (lo + hi) / 2
        ort = sum(_sigmoid(b + z) for z in kismi_logitler) / len(kismi_logitler)
        if abs(ort - hedef_oran) < tol:
            break
        if ort < hedef_oran:
            lo = b
        else:
            hi = b
    return b


def _persona_sec(rng):
    r = rng.random()
    k = 0.0
    for persona, oran in PERSONA_DAGILIMI.items():
        k += oran
        if r <= k:
            return persona
    return "klasik_maasli"


def _gelir_uret(rng, persona, c, gun_sayisi, baslangic):
    """
    Gelir işlemleri. Gelir DÜZENLİLİĞİ ve TUTAR İSTİKRARI c ile artar
    (yüksek c = disiplinli), persona akış YAPISINI belirler (sunum).
    Toplam gelir seviyesi persona-baz + ZAYIF c etkisi (klasik/gelir kanalı
    kapasiteyi ancak zayıf ve yanlı gözlemler — thin-file kör noktası).
    """
    s = PERSONA_SUNUM[persona]
    aylik = s["aylik_gelir"]
    # Gelir düzenliliği: yüksek c -> düşük değişkenlik katsayısı (daha düzenli aralık)
    cv = max(0.02, min(0.9, s["cv_baz"] - 0.10 * c + rng.gauss(0, 0.03)))
    # Toplam gelir: persona baz * lognormal gürültü * (1 + zayıf c)  -> gelir c'yi ZAYIF taşır
    hacim_carpani = math.exp(rng.gauss(0, 0.18)) * (1 + 0.05 * c)

    islemler = []
    kaynaklar = s["kaynaklar"]
    for kaynak in kaynaklar:
        pay = 1.0 / len(kaynaklar)
        if kaynak == "maas":
            aralik = 30
        elif kaynak in ("burs", "aile", "staj"):
            aralik = 30
        elif kaynak == "part_time":
            aralik = 15
        else:  # freelance / duzensiz
            aralik = rng.randint(20, 45)
        gun = rng.randint(1, max(2, aralik))
        while gun < gun_sayisi:
            taban = aylik * pay * (aralik / 30.0) * hacim_carpani
            # Tutar istikrarı: yüksek c -> düşük tutar oynaklığı
            tutar_net = max(200, taban * (1 + rng.gauss(0, max(0.03, 0.35 - 0.12 * c))))
            # Brüt vs net (araştırma: upstream payroll) — kesinti kaynak tipine göre
            kesinti = 0.18 if kaynak in ("maas", "staj") else (0.05 if kaynak == "freelance" else 0.0)
            brut = tutar_net / (1 - kesinti)
            islemler.append({
                "tarih": baslangic + timedelta(days=int(gun)),
                "tutar": round(tutar_net, 2), "brut_tutar": round(brut, 2),
                "kategori": kaynak, "kanal": KAYNAK_KANAL[kaynak],
                "karsi_taraf_tipi": KAYNAK_KARSI_TARAF[kaynak], "zorunlu_mu": "",
            })
            # Sonraki olay: aralık + c'ye bağlı jitter (yüksek c -> düşük jitter -> düzenli)
            gun += max(3, aralik * (1 + rng.gauss(0, cv)))
    return islemler, sum(i["tutar"] for i in islemler)


def _gider_uret(rng, persona, c, gun_sayisi, baslangic, toplam_gelir):
    """
    Gider işlemleri. Gider/gelir oranı ve fatura ödeme düzeni c ile İYİLEŞİR;
    zorunlu/ihtiyari ayrımı üretilir (araştırma: essential vs discretionary).
    """
    s = PERSONA_SUNUM[persona]
    # gider/gelir oranı: yüksek c -> düşük oran (disiplin). persona baz + c.
    gio = max(0.30, min(1.35, s["gio_baz"] - 0.13 * c + rng.gauss(0, 0.05)))
    hedef_gider = toplam_gelir * gio
    # İhtiyari harcama payı: yüksek c -> düşük ihtiyari pay
    ihtiyari_pay = max(0.05, min(0.7, 0.42 - 0.10 * c + rng.gauss(0, 0.05)))

    islemler = []
    # Fatura ödeme düzeni: 6 ayın kaçında fatura ödendi — yüksek c -> daha çok ay
    fatura_olasilik = max(0.1, min(1.0, 0.55 + 0.18 * c + rng.gauss(0, 0.08)))
    for ay in range(6):
        if rng.random() < fatura_olasilik:
            gun = ay * 30 + rng.randint(1, 28)
            if gun < gun_sayisi:
                islemler.append({"tarih": baslangic + timedelta(days=gun),
                                 "tutar": -round(hedef_gider * 0.12 / 6, 2),
                                 "brut_tutar": "", "kategori": "fatura", "kanal": "otomatik_odeme",
                                 "karsi_taraf_tipi": "kurum", "zorunlu_mu": "1"})

    kalan = hedef_gider - sum(abs(i["tutar"]) for i in islemler)
    n = max(8, int(gun_sayisi / 5))
    agirliklar = [rng.uniform(0.5, 1.5) for _ in range(n)]
    ta = sum(agirliklar)
    for a in agirliklar:
        gun = rng.randint(0, gun_sayisi - 1)
        ihtiyari = rng.random() < ihtiyari_pay
        kat = rng.choice(list(GIDER_IHTIYARI)) if ihtiyari else rng.choice(list(GIDER_ZORUNLU - {"fatura"}))
        tutar = max(30, round(kalan * a / ta, 2))
        islemler.append({"tarih": baslangic + timedelta(days=gun), "tutar": -abs(tutar),
                         "brut_tutar": "", "kategori": kat,
                         "kanal": rng.choice(("kart", "havale", "nakit")),
                         "karsi_taraf_tipi": "kurum", "zorunlu_mu": "0" if ihtiyari else "1"})
    return islemler


def uret(musteri_sayisi=2000, gun_sayisi=180, baslangic_tarihi="2026-01-01",
         hedef_temerrut_orani=0.18, seed=SEED):
    """
    Döngüsellik-kıran sentetik üretim.
    Dönüş: (islem_kayitlari, etiket_kayitlari)
      - islem_kayitlari: zengin ham işlemler (Tier-0 + Tier-1 alanları)
      - etiket_kayitlari: musteri_id -> gizli_kapasite, temerrut (YALNIZCA c'den)
    """
    rng = random.Random(seed)
    baslangic = datetime.strptime(baslangic_tarihi, "%Y-%m-%d")

    # 1. PASS — persona ve gizli kapasite (c persona'dan BAĞIMSIZ)
    musteriler = []
    for mid in range(1, musteri_sayisi + 1):
        persona = _persona_sec(rng)
        c = rng.gauss(0, 1)          # <<< THE FIX: c ⊥ persona
        musteriler.append({"musteri_id": mid, "persona": persona, "c": c})

    # 2. PASS — etiket YALNIZCA c'den (özelliklerden DEĞİL). Intercept hedef orana kalibre.
    ETKI_C = 2.4
    kismi = [-ETKI_C * m["c"] for m in musteriler]
    b = _intercept_kalibre(kismi, hedef_temerrut_orani)
    etiketler = []
    for m in musteriler:
        gurultu = rng.gauss(0, 0.55)   # gözlenemeyen faktörler (irreducible)
        p = _sigmoid(b - ETKI_C * m["c"] + gurultu)
        m["temerrut"] = 1 if rng.random() < p else 0
        m["p_gercek"] = round(p, 4)
        etiketler.append({"musteri_id": m["musteri_id"], "persona": m["persona"],
                          "gizli_kapasite": round(m["c"], 4),
                          "temerrut_olasiligi_gercek": m["p_gercek"], "temerrut": m["temerrut"]})

    # 3. PASS — işlemleri üret (özellikler c'nin gürültülü gözlemleri)
    kayitlar = []
    for m in musteriler:
        persona, c, mid = m["persona"], m["c"], m["musteri_id"]
        gelir, toplam_gelir = _gelir_uret(rng, persona, c, gun_sayisi, baslangic)
        if toplam_gelir <= 0:
            toplam_gelir = 1
        gider = _gider_uret(rng, persona, c, gun_sayisi, baslangic, toplam_gelir)
        for i in gelir + gider:
            tip = "gelir" if i["tutar"] > 0 else "gider"
            kayitlar.append({
                "musteri_id": mid, "persona": persona,
                "tarih": i["tarih"].strftime("%Y-%m-%d"), "islem_tipi": tip,
                "kategori": i["kategori"], "tutar": round(i["tutar"], 2),
                "aciklama": i["kategori"], "kanal": i["kanal"],
                "karsi_taraf_tipi": i["karsi_taraf_tipi"],
                "brut_tutar": i["brut_tutar"], "zorunlu_mu": i["zorunlu_mu"],
            })
    kayitlar.sort(key=lambda k: (k["musteri_id"], k["tarih"]))
    return kayitlar, etiketler


ISLEM_ALANLARI = ["musteri_id", "persona", "tarih", "islem_tipi", "kategori",
                  "tutar", "aciklama", "kanal", "karsi_taraf_tipi", "brut_tutar", "zorunlu_mu"]
ETIKET_ALANLARI = ["musteri_id", "persona", "gizli_kapasite",
                   "temerrut_olasiligi_gercek", "temerrut"]


def csv_yaz(kayitlar, alanlar, dosya_yolu):
    with open(dosya_yolu, "w", newline="", encoding="utf-8") as f:
        y = csv.DictWriter(f, fieldnames=alanlar)
        y.writeheader()
        y.writerows(kayitlar)


if __name__ == "__main__":
    import os
    p = argparse.ArgumentParser(description="Döngüsellik-kıran kapasite üreticisi")
    p.add_argument("--musteri-sayisi", type=int, default=2000)
    p.add_argument("--gun", type=int, default=180)
    p.add_argument("--hedef-temerrut", type=float, default=0.18)
    varsayilan_dizin = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")
    p.add_argument("--islem-cikti", type=str,
                   default=os.path.join(varsayilan_dizin, "kapasite_islemler.csv"))
    p.add_argument("--etiket-cikti", type=str,
                   default=os.path.join(varsayilan_dizin, "kapasite_etiketleri.csv"))
    a = p.parse_args()

    islemler, etiketler = uret(a.musteri_sayisi, a.gun, hedef_temerrut_orani=a.hedef_temerrut)
    csv_yaz(islemler, ISLEM_ALANLARI, a.islem_cikti)
    csv_yaz(etiketler, ETIKET_ALANLARI, a.etiket_cikti)

    from collections import Counter
    per = Counter(e["persona"] for e in etiketler)
    tem = Counter(e["persona"] for e in etiketler if e["temerrut"] == 1)
    print(f"{len(islemler)} işlem, {len(etiketler)} müşteri üretildi.")
    print(f"  -> {a.islem_cikti}")
    print(f"  -> {a.etiket_cikti}")
    genel = sum(e["temerrut"] for e in etiketler) / len(etiketler)
    print(f"\nGenel temerrüt oranı: {genel:.3f} (hedef {a.hedef_temerrut})")
    print("Persona bazında temerrüt oranı (DÜŞÜK yayılım = etiket persona'dan bağımsız):")
    for persona in PERSONA_DAGILIMI:
        n = per[persona]
        oran = tem[persona] / n if n else 0
        print(f"  {persona:<24} n={n:<5} temerrüt={oran:.3f}")
