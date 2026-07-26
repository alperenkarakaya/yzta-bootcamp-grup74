"""
Belge işleme hattı — kullanıcının yüklediği PDF/Excel/CSV hesap ekstresini
`ozellik/cikarim.py`'nin beklediği kanonik işlem şemasına ({tarih, islem_tipi,
kategori, tutar, aciklama}) çevirir (execution.md §3b Phase 7 / U-belge).

Modüller:
    okuyucu      — format yönlendirici (uzantıya göre pdf/tablo okuyucuya devreder)
    pdf_okuyucu  — pdfplumber ile tablo, olmazsa metin+regex çıkarımı
    tablo_okuyucu— pandas/openpyxl ile CSV/XLSX, bulanık kolon eşleme
    normalizer   — kanonik şemaya çevirme + kategori güven skoru
    parmak_izi   — belge içeriğinin SHA-256'sı (sahiplik-çakışma tespiti için)
    kalite       — işlem sayısı/tarih aralığı/pencere uygunluğu raporu

Django'dan bağımsızdır (aks_core deseni) — `pip install -e .` ile pytest'le
test edilir; 04-backend yalnızca `okuyucu.ayristir()`'i çağırır.
"""
from aks_core.belge.okuyucu import BelgeHatasi, ayristir

__all__ = ["ayristir", "BelgeHatasi"]
