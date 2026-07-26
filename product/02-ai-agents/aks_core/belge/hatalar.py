"""Belge hattının tek istisna türü — ayrı dosyada, dairesel import'u önlemek için
(`okuyucu.py`, `pdf_okuyucu.py`, `tablo_okuyucu.py` hepsi bunu import eder;
`okuyucu.py`'nin kendisi diğer ikisini import ettiği için BelgeHatasi orada
tanımlanamaz).
"""


class BelgeHatasi(Exception):
    """Kullanıcıya DOĞRUDAN gösterilebilir, Türkçe belge işleme hatası.

    Mesajları teknik değil, kullanıcının ne yapması gerektiğini söyleyen
    cümleler olmalı (bkz. çağıran yerler) — `services.csv_ayristir`'in eski
    `ValueError` deseninin devamı.
    """
