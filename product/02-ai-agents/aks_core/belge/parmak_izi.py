"""Belge parmak izi — normalize edilmiş işlem listesinin içerik özeti.

Sahiplik-çakışma TESPİTİ için kullanılır (execution.md §3b Phase 7 / 7.3):
aynı ekstre içeriği farklı AKS numaraları altında yüklenirse iki kaydın da
parmak izi eşleşir ve kurum tarafına `coklu_sahiplik_supheli` bayrağı olarak
yansır. Bu bir İSPAT değil — yalnızca TESPİT (bkz. plan §"Dürüstlük notu":
minimum kişisel veriyle sahiplik teknik olarak ispatlanamaz).

Kanonikleştirme sıralı olduğu için (tarih, tip, kategori, tutar) satır SIRASI
önemsizdir — aynı içerik farklı sırada ayrıştırılsa bile (örn. CSV vs PDF
tablo sırası) aynı özeti üretir.
"""
import hashlib


def hesapla(islemler):
    kanonik = sorted(
        (i["tarih"], i["islem_tipi"], i["kategori"], f"{i['tutar']:.2f}")
        for i in islemler
    )
    metin = "|".join("~".join(satir) for satir in kanonik)
    return hashlib.sha256(metin.encode("utf-8")).hexdigest()
