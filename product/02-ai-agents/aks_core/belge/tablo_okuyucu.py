"""CSV/Excel okuma — pandas ile, kolon başlığı bulanık eşleme.

Yüklenen dosya, ürünün kendi basit CSV şablonunu (tarih, islem_tipi, kategori,
tutar, aciklama — bkz. `CsvUploadPage.tsx`'in örnek indirmesi) izleyebilir ya
da gerçek bir banka ekstresi formatında olabilir ("İşlem Tarihi", "Açıklama",
"Borç", "Alacak" vb.). İkisi de aynı ham satır şemasına indirgenir; kesin
sınıflandırma (işaret, kategori) `normalizer.py`'nin işi — burada yalnızca
HANGİ kolonun hangi kanonik alana karşılık geldiği çözülür.
"""
import io

import pandas as pd

from aks_core.belge.hatalar import BelgeHatasi

KOLON_ESLEME = {
    "tarih": ["tarih", "işlem tarihi", "islem tarihi", "date", "valör", "valor"],
    "aciklama": ["açıklama", "aciklama", "description", "işlem açıklaması", "islem aciklamasi"],
    "tutar": ["tutar", "amount", "işlem tutarı", "islem tutari"],
    "borc": ["borç", "borc", "debit", "çıkan", "cikan"],
    "alacak": ["alacak", "credit", "giren"],
    "kategori": ["kategori", "category"],
    "islem_tipi": ["islem_tipi", "işlem tipi", "islem tipi", "type"],
}


def _eslesiyor(baslik, adaylar):
    b = str(baslik).strip().lower()
    return any(aday in b for aday in adaylar)


def _kolonlari_esle(sutunlar):
    esleme = {}
    for anahtar, adaylar in KOLON_ESLEME.items():
        esleme[anahtar] = next((s for s in sutunlar if _eslesiyor(s, adaylar)), None)
    return esleme


def _df_to_ham(df):
    if df.empty:
        raise BelgeHatasi("Dosyada okunabilir satır bulunamadı.")
    esleme = _kolonlari_esle(df.columns)
    if esleme["tarih"] is None:
        raise BelgeHatasi(
            "Tarih kolonu bulunamadı. Kolon başlıklarından biri 'tarih' ya da "
            "'işlem tarihi' benzeri bir ad taşımalı."
        )
    if esleme["tutar"] is None and esleme["borc"] is None and esleme["alacak"] is None:
        raise BelgeHatasi(
            "Tutar (veya borç/alacak) kolonu bulunamadı. Kolon başlıklarından biri "
            "'tutar' ya da 'borç'/'alacak' benzeri bir ad taşımalı."
        )

    ham = []
    for _, satir in df.iterrows():
        kayit = {"tarih_ham": satir.get(esleme["tarih"])}
        for anahtar, hedef in (("aciklama", "aciklama"), ("tutar", "tutar_ham"),
                                ("borc", "borc_ham"), ("alacak", "alacak_ham"),
                                ("kategori", "kategori"), ("islem_tipi", "islem_tipi")):
            if esleme[anahtar] is not None:
                kayit[hedef] = satir.get(esleme[anahtar])
        ham.append(kayit)
    return ham


def csv_oku(veri_baytlari):
    try:
        metin = veri_baytlari.decode("utf-8-sig")
    except UnicodeDecodeError:
        metin = veri_baytlari.decode("latin-1")
    try:
        df = pd.read_csv(io.StringIO(metin), dtype=str, keep_default_na=False)
    except Exception as e:
        raise BelgeHatasi(f"CSV ayrıştırılamadı: {e}")
    return _df_to_ham(df)


def excel_oku(veri_baytlari):
    try:
        df = pd.read_excel(io.BytesIO(veri_baytlari), dtype=str)
    except Exception as e:
        raise BelgeHatasi(f"Excel dosyası ayrıştırılamadı: {e}")
    return _df_to_ham(df.fillna(""))
