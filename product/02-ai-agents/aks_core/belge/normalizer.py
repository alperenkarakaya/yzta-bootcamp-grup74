"""Ham (format-bağımsız) satırları kanonik işlem şemasına çevirir.

Kanonik şema: {tarih: "YYYY-MM-DD", islem_tipi: "gelir"|"gider", kategori: str,
tutar: float, aciklama: str} — `aks_core.ozellik.cikarim.ozellik_cikar()`'ın
beklediği ile birebir aynı (o fonksiyon DEĞİŞTİRİLMEDİ, bkz. execution.md
§3b Phase 7 / 7.1: eğitim/servis tutarlılığı P1 önceliği).

Tutar işareti kanonik: gelir > 0, gider < 0. Bu, sentetik veri üreticisinin
(`01-data/generator/veri/uretici_kapasite.py`) de uyduğu kural — bakiye
trendi (`bakiye_trendi`) işaretli tutarların kümülatif toplamına dayanıyor,
işaret tutarlılığı bozulursa o özellik anlamsızlaşır.

`tarih_ham`/`tutar_ham`/`borc_ham`/`alacak_ham` gibi ham anahtarlar
`tablo_okuyucu.py` ve `pdf_okuyucu.py`'nin ürettiği ortak ara şemadır; ikisi
de aynı `normalize()` fonksiyonundan geçer (tek doğrulama/dönüştürme mantığı).
"""
import re
from datetime import datetime

_TARIH_BICIMLERI = ["%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
_TARIH_ICI_DESEN = re.compile(r"(\d{2})[./](\d{2})[./](\d{4})")

# Kategori tahmini — düşük güvenli, kaba anahtar-kelime kuralı. Kategori,
# `ozellik_cikar()`'da `gelir_kaynagi_sayisi` (gelir kategorilerinin tekilliği)
# ve `fatura_odeme_duzeni` (kategori == "fatura" sayımı) için doğrudan girdi —
# bu yüzden düşük güvenli tahminler `kategori_guveni` ile açıkça işaretlenir,
# sessizce üretilmez (bkz. plan §7.1 "kritik bulgu").
_KATEGORI_ANAHTAR = {
    "fatura": ["fatura", "elektrik", "doğalgaz", "dogalgaz", "internet", "telefon fatura", "aidat", "su sayaç"],
    "market": ["market", "migros", "carrefour", "bim ", "a101", "şok ", "sok market"],
    "kira": ["kira"],
    "maas": ["maaş", "maas", "ücret öde", "salary", "bordro"],
    "kredi_odeme": ["kredi taksit", "kredi ödeme", "kredi odeme", "loan"],
    "eglence": ["sinema", "netflix", "spotify", "restoran", "kafe", "eglence", "eğlence"],
    "saglik": ["eczane", "hastane", "sağlık", "saglik"],
    "ulasim": ["akbil", "otobüs", "otobus", "metro", "yakıt", "yakit", "benzin", "ulasim", "ulaşım"],
    # Gerçek örnek verilerle (execution.md §3b Phase 7, PO-sağlanan PDF/CSV
    # örnekleri) test edilirken eklendi: bazı bankalar "açıklama" alanına
    # doğrudan kategori adının kendisini yazıyor (örn. "eglence", "ulasim" —
    # yukarıdaki marka/anahtar-kelime listeleri bunu yakalamıyordu, kategori
    # güveni ~%50'ye düşüyordu). Aşağıdaki girişler bu boşluğu kapatır.
    "abonelik": ["abonelik", "subscription"],
    "egitim": ["egitim", "eğitim", "okul", "kurs", "harç", "harc"],
    "giyim": ["giyim", "kıyafet", "kiyafet", "tekstil"],
    "yeme_icme": ["yeme_icme", "yeme-icme", "yemek", "içme"],
    "aile": ["aile", "family"],
    "burs": ["burs", "scholarship"],
    "freelance": ["freelance"],
    "part_time": ["part_time", "part-time", "part time"],
}


def _tarih_ayikla(deger):
    s = str(deger or "").strip()
    if not s:
        return None
    for bicim in _TARIH_BICIMLERI:
        try:
            return datetime.strptime(s[:10], bicim).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # PDF metin satırlarında tarih genelde başka içerikle aynı hücrede/satırda
    # gelir ("12.03.2026 Market Alışverişi") — içinden tarihi ara.
    m = _TARIH_ICI_DESEN.search(s)
    if m:
        gun, ay, yil = (int(x) for x in m.groups())
        try:
            return datetime(yil, ay, gun).strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None


def _tutar_ayikla(deger):
    """TR ("1.234,56") ve EN ("1234.56") ondalık biçimlerini kabul eder.

    Parantez ("(150,00)") veya baştaki '-' negatif kabul edilir — banka
    ekstrelerinde borç/çıkış genelde böyle gösterilir.
    """
    if deger is None:
        return None
    s = str(deger).strip()
    if not s:
        return None
    s = s.replace("TL", "").replace("₺", "").strip()
    negatif = s.startswith("-") or (s.startswith("(") and s.endswith(")"))
    s = s.lstrip("-").strip("()").strip()
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")  # TR: binlik nokta, ondalık virgül
    elif "," in s:
        s = s.replace(",", ".")
    try:
        tutar = float(s)
    except ValueError:
        return None
    return -tutar if negatif else tutar


def _kategori_tahmin(aciklama, islem_tipi):
    a = (aciklama or "").lower()
    for kategori, anahtarlar in _KATEGORI_ANAHTAR.items():
        if any(k in a for k in anahtarlar):
            return kategori, 0.9
    return ("diger_gider" if islem_tipi == "gider" else "diger_gelir"), 0.3


def normalize(ham_kayitlar):
    """(islemler, ortalama_kategori_guveni, toplam_ham_sayisi) döner.

    Tarih/tutar ayrıştırılamayan satırlar atlanır (PDF'te başlık/toplam/sayfa
    numarası gibi gürültü satırları olağan) — sessizce değil: `toplam_ham_sayisi`
    ile birlikte döner, `kalite.py` atlanan oranını raporlar.
    """
    islemler = []
    guvenler = []
    for ham in ham_kayitlar:
        tarih = _tarih_ayikla(ham.get("tarih_ham"))
        if tarih is None:
            continue

        tutar = None
        if ham.get("tutar_ham") not in (None, ""):
            tutar = _tutar_ayikla(ham["tutar_ham"])
        else:
            borc = _tutar_ayikla(ham.get("borc_ham")) or 0.0
            alacak = _tutar_ayikla(ham.get("alacak_ham")) or 0.0
            if borc or alacak:
                tutar = alacak - abs(borc)
        if tutar is None or tutar == 0.0:
            continue

        islem_tipi = str(ham.get("islem_tipi") or "").strip().lower()
        if islem_tipi not in ("gelir", "gider"):
            islem_tipi = "gelir" if tutar > 0 else "gider"
        tutar = abs(tutar) if islem_tipi == "gelir" else -abs(tutar)  # kanonik işaret zorlanır

        aciklama = str(ham.get("aciklama") or "").strip()
        kategori_ham = str(ham.get("kategori") or "").strip().lower()
        if kategori_ham:
            kategori, guven = kategori_ham, 1.0
        else:
            kategori, guven = _kategori_tahmin(aciklama, islem_tipi)
        guvenler.append(guven)

        islemler.append({
            "tarih": tarih, "islem_tipi": islem_tipi, "kategori": kategori,
            "tutar": round(tutar, 2), "aciklama": aciklama,
        })

    ortalama_guven = round(sum(guvenler) / len(guvenler), 3) if guvenler else 0.0
    return islemler, ortalama_guven, len(ham_kayitlar)
