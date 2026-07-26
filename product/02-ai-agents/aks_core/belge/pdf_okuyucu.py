"""PDF hesap ekstresi okuma — pdfplumber.

Çok-stratejili, kendini denetleyen bir akış (bkz. `agents/belge_agent.py`'nin
sardığı agentic çerçeve — execution.md §3b Phase 7 / 7.5):

    1) `extract_tables()`: PDF gerçek bir tablo yapısı içeriyorsa (çoğu banka
       ekstresi PDF'i böyledir) en güvenilir yol.
    2) Yetersizse `extract_text()` + satır regex: tablo tanınamayan PDF'lerde
       her satırda tarih + tutar geçen serbest metin satırlarını ayıklar.
    3) İkisi de en az 5 satır vermezse `BelgeHatasi` — hangi adımın kaç satır
       ürettiğini söyler (kullanıcıya gösterilebilir, sessiz başarısızlık yok).

Çıktısı `tablo_okuyucu.py` ile AYNI ham satır şeması (`normalizer.normalize()`
girdisi) — iki okuyucu da tek bir dönüştürme/doğrulama mantığından geçer.
"""
import io
import re

import pdfplumber

from aks_core.belge.hatalar import BelgeHatasi

# "12.03.2026  Market Alışverişi Migros          -450,00"
_SATIR_DESENI = re.compile(
    r"(?P<tarih>\d{2}[./]\d{2}[./]\d{4})\s+(?P<aciklama>.+?)\s+"
    r"(?P<tutar>\(?-?\d{1,3}(?:\.\d{3})*,\d{2}\)?)\s*$"
)

_MIN_SATIR = 5


def _hucre_esle(satir_sozluk, adaylar):
    for baslik, deger in satir_sozluk.items():
        if any(aday in str(baslik or "").strip().lower() for aday in adaylar):
            return deger
    return None


def _tablolardan_oku(pdf):
    ham = []
    for sayfa in pdf.pages:
        for tablo in (sayfa.extract_tables() or []):
            if not tablo or len(tablo) < 2:
                continue
            baslik = [str(h or "").strip() for h in tablo[0]]
            for satir in tablo[1:]:
                if not any(satir):
                    continue
                kayit = dict(zip(baslik, satir))
                tarih = _hucre_esle(kayit, ["tarih", "işlem tarihi", "date"])
                if not tarih:
                    continue
                ham.append({
                    "tarih_ham": tarih,
                    "aciklama": _hucre_esle(kayit, ["açıklama", "aciklama", "description"]),
                    "tutar_ham": _hucre_esle(kayit, ["tutar", "amount"]),
                    "borc_ham": _hucre_esle(kayit, ["borç", "borc", "debit"]),
                    "alacak_ham": _hucre_esle(kayit, ["alacak", "credit"]),
                })
    return ham


def _metinden_oku(pdf):
    ham = []
    for sayfa in pdf.pages:
        metin = sayfa.extract_text() or ""
        for satir in metin.splitlines():
            eslesme = _SATIR_DESENI.match(satir.strip())
            if eslesme:
                ham.append({
                    "tarih_ham": eslesme.group("tarih"),
                    "aciklama": eslesme.group("aciklama").strip(),
                    "tutar_ham": eslesme.group("tutar"),
                })
    return ham


def pdf_oku(veri_baytlari, iz=None):
    """`iz`: opsiyonel, insan-okur trace listesi — verilirse her strateji
    denemesi buraya eklenir (`agents/belge_agent.py`'nin kullandığı kanca).
    `None` ise (varsayılan, `okuyucu.py`'nin çağırdığı yol) davranış TAMAMEN
    aynı kalır — yan etkisiz, geriye dönük uyumlu."""
    def _kaydet(mesaj):
        if iz is not None:
            iz.append(mesaj)

    try:
        kaynak = pdfplumber.open(io.BytesIO(veri_baytlari))
    except Exception as e:
        _kaydet(f"PDF açılamadı: {e}")
        raise BelgeHatasi(f"PDF açılamadı — dosya bozuk olabilir: {e}")

    with kaynak as pdf:
        _kaydet("Strateji 1: extract_tables() ile tablo çıkarımı deneniyor")
        ham_tablo = _tablolardan_oku(pdf)
        if len(ham_tablo) >= _MIN_SATIR:
            _kaydet(f"Strateji 1 başarılı: {len(ham_tablo)} satır")
            return ham_tablo
        _kaydet(f"Strateji 1 yetersiz: {len(ham_tablo)} satır (< {_MIN_SATIR})")

        _kaydet("Strateji 2: extract_text() + satır deseni deneniyor")
        ham_metin = _metinden_oku(pdf)
        if len(ham_metin) >= _MIN_SATIR:
            _kaydet(f"Strateji 2 başarılı: {len(ham_metin)} satır")
            return ham_metin
        _kaydet(f"Strateji 2 yetersiz: {len(ham_metin)} satır (< {_MIN_SATIR})")

        en_iyi = max(len(ham_tablo), len(ham_metin))
        if en_iyi > 0:
            raise BelgeHatasi(
                f"PDF'ten yalnızca {en_iyi} işlem satırı okunabildi (en az {_MIN_SATIR} gerekli). "
                "Ekstre formatı tam tanınamadı; CSV veya Excel olarak yüklemeyi deneyin."
            )
        raise BelgeHatasi(
            "PDF'ten işlem tablosu bulunamadı — ne tablo yapısı ne satır-bazlı tarih/tutar "
            "deseni tanındı. PDF taranmış bir görüntü (OCR gerektiren) olabilir; "
            "bu durumda CSV veya Excel formatını kullanın."
        )
