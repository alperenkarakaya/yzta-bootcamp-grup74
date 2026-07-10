"""
Veri Doğrulama + PII Sınıflandırma — 01-data (pipeline Adım 2)
=============================================================
`uretici_kapasite.py` çıktısını doğrular: şema, tip, bütünlük ve UCUZ bir
döngüsellik-kapısı (persona bazında temerrüt yayılımı). Ağır AUC kanıtı ayrı
(`dekuple_kanit.py`).

Ayrıca her kolonu KVKK/PII sınıfına göre etiketler (planning/data-architecture.md §4).

Çalıştırma:  python product/01-data/generator/dogrulama.py
Çıkış kodu 0 = geçti, 1 = kaldı (CI'de kapı olarak kullanılabilir).
"""
import csv
import os
import sys
from collections import defaultdict

BURADA = os.path.dirname(__file__)
DATASETS = os.path.join(BURADA, "..", "datasets")
ISLEM_CSV = os.path.join(DATASETS, "kapasite_islemler.csv")
ETIKET_CSV = os.path.join(DATASETS, "kapasite_etiketleri.csv")

ISLEM_ZORUNLU = ["musteri_id", "persona", "tarih", "islem_tipi", "kategori", "tutar"]
ETIKET_ZORUNLU = ["musteri_id", "persona", "gizli_kapasite", "temerrut_olasiligi_gercek", "temerrut"]

# KVKK / PII sınıflandırması (planning/data-architecture.md §4)
PII_SINIF = {
    "musteri_id": "financial", "persona": "financial", "tarih": "financial",
    "islem_tipi": "financial", "kategori": "financial", "tutar": "financial",
    "aciklama": "financial", "kanal": "financial", "karsi_taraf_tipi": "financial",
    "brut_tutar": "financial", "zorunlu_mu": "none",
    # etiket tarafı — gizli_kapasite ve olasılık MODEL GİRDİSİ DEĞİLDİR (leakage firewall)
    "gizli_kapasite": "none (yalnız üretim; ASLA özellik değil)",
    "temerrut_olasiligi_gercek": "none (oracle; ASLA özellik değil)",
    "temerrut": "financial (hedef etiket)",
}
YASAL_DAYANAK = {"financial": "sozlesme (contractual necessity)", "none": "-"}

MAX_PERSONA_TEMERRUT_YAYILIMI = 0.06  # döngüsellik kapısı: bunun üstü = persona etiketi belirliyor


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dogrula():
    hatalar, uyarilar = [], []

    if not (os.path.exists(ISLEM_CSV) and os.path.exists(ETIKET_CSV)):
        print("HATA: veri yok. Önce: python product/01-data/generator/veri/uretici_kapasite.py")
        return 1

    islem = _oku(ISLEM_CSV)
    etiket = _oku(ETIKET_CSV)

    # 1) Şema
    for ad, kolonlar in [("islemler", ISLEM_ZORUNLU), ("etiketler", ETIKET_ZORUNLU)]:
        veri = islem if ad == "islemler" else etiket
        eksik = [k for k in kolonlar if veri and k not in veri[0]]
        if eksik:
            hatalar.append(f"{ad}: eksik kolon(lar): {eksik}")

    # 2) Tipler + boş değer
    for i, r in enumerate(islem):
        try:
            float(r["tutar"]); int(r["musteri_id"])
        except (ValueError, KeyError):
            hatalar.append(f"islemler satır {i+2}: tutar/musteri_id sayısal değil")
            break
        if r["islem_tipi"] not in ("gelir", "gider"):
            hatalar.append(f"islemler satır {i+2}: geçersiz islem_tipi={r['islem_tipi']}")
            break

    # 3) İşaret tutarlılığı: gelir>0, gider<0
    ts = [(float(r["tutar"]), r["islem_tipi"]) for r in islem]
    if any(t > 0 and tip == "gider" for t, tip in ts) or any(t < 0 and tip == "gelir" for t, tip in ts):
        hatalar.append("islemler: tutar işareti islem_tipi ile uyumsuz (gelir>0, gider<0 olmalı)")

    # 4) zorunlu_mu bayrağı yalnız giderlerde 0/1
    for i, r in enumerate(islem):
        if r["islem_tipi"] == "gider" and r.get("zorunlu_mu") not in ("0", "1", ""):
            uyarilar.append(f"islemler satır {i+2}: zorunlu_mu beklenmeyen değer '{r.get('zorunlu_mu')}'")
            break

    # 5) Referans bütünlüğü: her etiketin işlemi var mı
    islem_musteri = {int(r["musteri_id"]) for r in islem}
    etiket_musteri = {int(r["musteri_id"]) for r in etiket}
    yetim = etiket_musteri - islem_musteri
    if yetim:
        hatalar.append(f"{len(yetim)} etiket müşterisinin işlemi yok (ör. {sorted(yetim)[:5]})")

    # 6) DÖNGÜSELLİK KAPISI (ucuz): persona bazında temerrüt yayılımı
    per_n = defaultdict(int); per_t = defaultdict(int)
    for r in etiket:
        per_n[r["persona"]] += 1
        per_t[r["persona"]] += int(r["temerrut"])
    oranlar = {p: per_t[p] / per_n[p] for p in per_n}
    yayilim = (max(oranlar.values()) - min(oranlar.values())) if oranlar else 0.0

    # --- Rapor ---
    print("=" * 66)
    print("VERİ DOĞRULAMA — 01-data (kapasite_islemler / kapasite_etiketleri)")
    print("=" * 66)
    print(f"İşlem: {len(islem)}   Müşteri: {len(etiket)}")
    print("\nPII / KVKK sınıflandırması:")
    for kol, sinif in PII_SINIF.items():
        temel = sinif.split()[0]
        print(f"  {kol:<28}{sinif:<40}{YASAL_DAYANAK.get(temel, '-')}")

    print(f"\nDöngüsellik kapısı — persona temerrüt yayılımı: {yayilim:.3f} "
          f"(eşik ≤ {MAX_PERSONA_TEMERRUT_YAYILIMI})")
    for p, o in sorted(oranlar.items()):
        print(f"    {p:<24} {o:.3f}")
    if yayilim > MAX_PERSONA_TEMERRUT_YAYILIMI:
        hatalar.append(f"döngüsellik kapısı: persona yayılımı {yayilim:.3f} > {MAX_PERSONA_TEMERRUT_YAYILIMI} "
                       "(etiket persona'ya bağlı görünüyor)")

    print("\n" + "-" * 66)
    if uyarilar:
        print("UYARILAR:")
        for u in uyarilar:
            print(f"  ! {u}")
    if hatalar:
        print("HATALAR:")
        for h in hatalar:
            print(f"  x {h}")
        print("SONUÇ: KALDI")
        return 1
    print("SONUÇ: GEÇTİ — şema, bütünlük ve döngüsellik kapısı tamam.")
    return 0


if __name__ == "__main__":
    sys.exit(dogrula())
