"""Belge kalite/uygunluk raporu.

Model 180 günlük pencerede eğitildi ve `ozellik_cikar()`'ın iki alanı
(`gelir_kaynagi_sayisi`, `fatura_odeme_duzeni`) kategori çıkarımına bağımlı
(bkz. plan §7.1 "kritik bulgular"). `ozellik_cikar()`'ın kendisi bu varsayımlar
için DEĞİŞTİRİLMEDİ (eğitim/servis tutarlılığı, P1) — bunun yerine bu modül
sapmaları BAYRAKLA bildirir; skor bu uyarılarla birlikte sunulur, sessizce
düzeltilmez ya da gizlenmez.
"""
from datetime import datetime

BEKLENEN_PENCERE_GUN = 180
PENCERE_TOLERANSI = 0.35  # ±%35 sapma kabul edilebilir kabul edilir
DUSUK_KATEGORI_GUVEN_ESIGI = 0.6
YUKSEK_ATLANAN_ORANI_ESIGI = 0.2  # ham satırların >%20'si ayrıştırılamadıysa uyar


def degerlendir(islemler, kategori_guveni=None, toplam_ham_sayisi=None):
    if not islemler:
        return {
            "islem_sayisi": 0, "pencere_gun": 0, "pencere_uyumlu": False,
            "bayraklar": ["bos_belge"],
        }

    tarihler = sorted(datetime.strptime(i["tarih"], "%Y-%m-%d") for i in islemler)
    pencere_gun = (tarihler[-1] - tarihler[0]).days + 1
    sapma = abs(pencere_gun - BEKLENEN_PENCERE_GUN) / BEKLENEN_PENCERE_GUN
    pencere_uyumlu = sapma <= PENCERE_TOLERANSI

    bayraklar = []
    if not pencere_uyumlu:
        bayraklar.append("pencere_uyumsuz")
    if kategori_guveni is not None and kategori_guveni < DUSUK_KATEGORI_GUVEN_ESIGI:
        bayraklar.append("dusuk_kategori_guveni")

    atlanan_orani = None
    if toplam_ham_sayisi:
        atlanan_orani = round(1 - (len(islemler) / toplam_ham_sayisi), 3)
        if atlanan_orani > YUKSEK_ATLANAN_ORANI_ESIGI:
            bayraklar.append("yuksek_atlanan_satir_orani")

    return {
        "islem_sayisi": len(islemler),
        "tarih_araligi": {
            "baslangic": tarihler[0].strftime("%Y-%m-%d"),
            "bitis": tarihler[-1].strftime("%Y-%m-%d"),
        },
        "pencere_gun": pencere_gun,
        "beklenen_pencere_gun": BEKLENEN_PENCERE_GUN,
        "pencere_uyumlu": pencere_uyumlu,
        "atlanan_satir_orani": atlanan_orani,
        "bayraklar": bayraklar,
    }
