"""Belge işleme hattının giriş noktası — format yönlendirici.

`04-backend` (hem anonim `/api/csv-skorla` hem giriş yapmış `/api/portal/yukle`)
ve `pytest` testleri BUNU çağırır; hiçbiri `tablo_okuyucu`/`pdf_okuyucu`'yu
doğrudan bilmez (execution.md §3b Phase 7 / 7.1).
"""
import os

from aks_core.belge import kalite, normalizer, parmak_izi, pdf_okuyucu, tablo_okuyucu
from aks_core.belge.hatalar import BelgeHatasi

DESTEKLENEN_UZANTILAR = {".csv", ".xlsx", ".xls", ".pdf"}
MIN_ISLEM_SAYISI = 5


def ayristir(dosya_adi, veri_baytlari):
    """Bir dosyanın (ad + ham baytlar) kanonik işlem listesine + meta rapora çevrilmesi.

    Döner: (islemler: list[dict], meta: dict). `meta` şunları içerir:
    `kaynak_format`, `parmak_izi`, `kategori_guveni`, ve `kalite.degerlendir()`'in
    ürettiği tüm alanlar (`islem_sayisi`, `pencere_uyumlu`, `bayraklar`, ...).

    `BelgeHatasi` fırlatır (mesajı doğrudan kullanıcıya gösterilebilir).
    """
    ext = os.path.splitext(dosya_adi or "")[1].lower()
    if ext not in DESTEKLENEN_UZANTILAR:
        raise BelgeHatasi(
            f"Desteklenmeyen dosya türü: '{ext or '(uzantısız)'}'. "
            "Kabul edilen formatlar: CSV, XLSX, PDF."
        )

    if ext == ".csv":
        ham, format_adi = tablo_okuyucu.csv_oku(veri_baytlari), "csv"
    elif ext in (".xlsx", ".xls"):
        ham, format_adi = tablo_okuyucu.excel_oku(veri_baytlari), "xlsx"
    else:
        ham, format_adi = pdf_okuyucu.pdf_oku(veri_baytlari), "pdf"

    islemler, kategori_guveni, toplam_ham = normalizer.normalize(ham)
    if len(islemler) < MIN_ISLEM_SAYISI:
        raise BelgeHatasi(
            f"Anlamlı bir skor için en az {MIN_ISLEM_SAYISI} işlem gerekli "
            f"(ayrıştırılabilen: {len(islemler)})."
        )

    rapor = kalite.degerlendir(islemler, kategori_guveni, toplam_ham)
    meta = {
        "kaynak_format": format_adi,
        "kategori_guveni": kategori_guveni,
        "parmak_izi": parmak_izi.hesapla(islemler),
        **rapor,
    }
    return islemler, meta
