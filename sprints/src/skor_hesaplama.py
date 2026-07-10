"""
Özellik Mühendisliği & Alternatif Skor Hesaplama
--------------------------------------------------
Bu modül, ham banka işlem (transaction) verisinden kişi bazlı davranışsal
özellikler çıkarır ve resmi gelir beyanına dayanmayan, hesap hareketi
temelli bir "Alternatif Kapasite Skoru (AKS)" üretir.

Fikir: Resmi/beyan edilen gelir düşük olsa bile (örn. öğrenci, stajyer),
hesap hareketleri yüksek hacimli, düzenli ve disiplinliyse, gerçek ödeme
kapasitesi klasik skorlamanın öngördüğünden daha yüksektir.

Çıkarılan özellikler (kişi başına):
    toplam_gelir_hacmi      : Dönem içindeki toplam gelir tutarı
    gelir_islem_sayisi      : Kaç ayrı gelir işlemi olduğu (kaynak çeşitliliği +sıklık)
    gelir_kaynagi_sayisi    : Farklı gelir kategorisi sayısı (burs, part-time, aile, vs.)
    gelir_duzenliligi       : Gelir işlemleri arası gün farkının tutarlılığı (düşük varyans = düzenli)
    gider_gelir_orani       : Toplam gider / toplam gelir (1'e yakın ya da üstü riskli)
    ortalama_bakiye_trendi  : Kümülatif bakiyenin dönem içindeki eğimi (pozitif = tasarruf eğiliminde)
    fatura_odeme_duzeni     : "fatura" kategorisindeki işlemlerin düzenliliği (gecikme/aksama olmadan ödeme sinyali)
    hesap_hareket_yogunlugu : Dönem içi toplam işlem sayısı / gün sayısı

Skor: 300-850 aralığında (klasik kredi skoru formatına benzer, karşılaştırma
kolaylığı için), iki bileşenden oluşur:
    - klasik_skor   : Sadece beyan edilen/sabit gelir varsayımıyla (referans/baseline)
    - alternatif_skor (AKS) : Yukarıdaki davranışsal özelliklerle ağırlıklandırılmış skor

Not: Bu, üretim ortamında kullanılacak nihai bir kredi risk modeli DEĞİLDİR;
bootcamp kapsamında kavramı kanıtlamak (proof of concept) için tasarlanmış,
yorumlanabilir (explainable) basit bir kural+ağırlık tabanlı modeldir.
İleriki sprintlerde scikit-learn/XGBoost ile denetimli öğrenme modeline
genişletilecektir.
"""

import csv
import statistics
from collections import defaultdict
from datetime import datetime


def _tarih_oku(s):
    return datetime.strptime(s, "%Y-%m-%d")


def csv_oku(dosya_yolu):
    musteri_islemleri = defaultdict(list)
    persona_map = {}
    with open(dosya_yolu, encoding="utf-8") as f:
        okuyucu = csv.DictReader(f)
        for satir in okuyucu:
            mid = int(satir["musteri_id"])
            satir["tutar"] = float(satir["tutar"])
            satir["tarih_obj"] = _tarih_oku(satir["tarih"])
            musteri_islemleri[mid].append(satir)
            persona_map[mid] = satir["persona"]
    return musteri_islemleri, persona_map


def ozellik_cikar(islemler):
    gelirler = [i for i in islemler if i["islem_tipi"] == "gelir"]
    giderler = [i for i in islemler if i["islem_tipi"] == "gider"]

    toplam_gelir = sum(i["tutar"] for i in gelirler)
    toplam_gider = abs(sum(i["tutar"] for i in giderler))

    gelir_islem_sayisi = len(gelirler)
    gelir_kaynagi_sayisi = len(set(i["kategori"] for i in gelirler))

    # Gelir düzenliliği: ardışık gelir tarihleri arası gün farkının
    # standart sapması ne kadar düşükse o kadar düzenli demektir.
    gelir_duzenliligi = 0.0
    if len(gelirler) >= 3:
        tarihler = sorted(i["tarih_obj"] for i in gelirler)
        farklar = [(tarihler[i + 1] - tarihler[i]).days for i in range(len(tarihler) - 1)]
        if len(farklar) >= 2 and statistics.mean(farklar) > 0:
            varyasyon_katsayisi = statistics.pstdev(farklar) / statistics.mean(farklar)
            gelir_duzenliligi = max(0.0, 1 - min(varyasyon_katsayisi, 1.0))

    gider_gelir_orani = (toplam_gider / toplam_gelir) if toplam_gelir > 0 else 1.5

    # Basit bakiye trendi: tarih sırasına göre kümülatif bakiyenin eğimi
    tum_islemler = sorted(islemler, key=lambda i: i["tarih_obj"])
    kumulatif = 0.0
    seri = []
    for i in tum_islemler:
        kumulatif += i["tutar"]
        seri.append(kumulatif)
    bakiye_trendi = 0.0
    if len(seri) >= 2:
        bakiye_trendi = (seri[-1] - seri[0]) / (abs(seri[0]) + 1)

    fatura_islemleri = [i for i in giderler if i["kategori"] == "fatura"]
    fatura_odeme_duzeni = min(len(fatura_islemleri) / 6.0, 1.0)  # 6+ düzenli fatura ödemesi = tam puan

    if tum_islemler:
        gun_araligi = (tum_islemler[-1]["tarih_obj"] - tum_islemler[0]["tarih_obj"]).days + 1
    else:
        gun_araligi = 1
    hesap_hareket_yogunlugu = len(islemler) / max(gun_araligi, 1)

    return {
        "toplam_gelir_hacmi": round(toplam_gelir, 2),
        "toplam_gider_hacmi": round(toplam_gider, 2),
        "gelir_islem_sayisi": gelir_islem_sayisi,
        "gelir_kaynagi_sayisi": gelir_kaynagi_sayisi,
        "gelir_duzenliligi": round(gelir_duzenliligi, 3),
        "gider_gelir_orani": round(gider_gelir_orani, 3),
        "bakiye_trendi": round(bakiye_trendi, 3),
        "fatura_odeme_duzeni": round(fatura_odeme_duzeni, 3),
        "hesap_hareket_yogunlugu": round(hesap_hareket_yogunlugu, 3),
    }


def klasik_skor_hesapla(ozellikler, persona):
    """Sadece düzenli/resmi gelir varsa yüksek skor veren basit baseline.
    Öğrenci/stajyer gibi resmi geliri zayıf görünenleri cezalandırır -
    bu, projenin 'çözmeye çalıştığı' mevcut durumu simüle eder."""
    taban = 500
    if persona == "klasik_maasli":
        taban += 200
    elif persona == "stajyer_degisken_gelir":
        taban += 40
    elif persona == "ogrenci_yuksek_hacim":
        taban += 10  # mevcut sistemde neredeyse hiç avantaj yok
    else:
        taban += 0

    skor = taban + ozellikler["toplam_gelir_hacmi"] * 0.001
    return int(max(300, min(850, skor)))


def alternatif_skor_hesapla(ozellikler):
    """Davranışsal özelliklere dayalı, persona'dan bağımsız skor (AKS).
    Ağırlıklar yorumlanabilir olacak şekilde basit tutulmuştur."""
    puan = 300

    # Gelir hacmi (logaritmik etkiye yakın, üst sınırla)
    puan += min(ozellikler["toplam_gelir_hacmi"] / 1000, 150)

    # Gelir düzenliliği ve kaynak çeşitliliği -> öngörülebilirlik
    puan += ozellikler["gelir_duzenliligi"] * 100
    puan += min(ozellikler["gelir_kaynagi_sayisi"] * 15, 60)

    # Gider disiplini: oran ne kadar düşükse o kadar iyi
    gider_orani = ozellikler["gider_gelir_orani"]
    if gider_orani <= 1:
        puan += (1 - gider_orani) * 120
    else:
        puan -= (gider_orani - 1) * 150

    # Bakiye trendi (tasarruf eğilimi)
    puan += max(min(ozellikler["bakiye_trendi"], 1), -1) * 60

    # Düzenli fatura ödemesi -> güvenilirlik sinyali
    puan += ozellikler["fatura_odeme_duzeni"] * 50

    # Hesap hareket yoğunluğu -> aktif/canlı hesap sinyali
    puan += min(ozellikler["hesap_hareket_yogunlugu"] * 30, 30)

    return int(max(300, min(850, puan)))


def musteri_raporu_olustur(dosya_yolu):
    musteri_islemleri, persona_map = csv_oku(dosya_yolu)
    rapor = []
    for mid, islemler in musteri_islemleri.items():
        ozellikler = ozellik_cikar(islemler)
        persona = persona_map[mid]
        klasik = klasik_skor_hesapla(ozellikler, persona)
        alternatif = alternatif_skor_hesapla(ozellikler)
        rapor.append({
            "musteri_id": mid,
            "persona": persona,
            "klasik_skor": klasik,
            "alternatif_skor": alternatif,
            "skor_farki": alternatif - klasik,
            **ozellikler,
        })
    return rapor


def ozet_yazdir(rapor):
    persona_gruplari = defaultdict(list)
    for r in rapor:
        persona_gruplari[r["persona"]].append(r)

    print(f"{'Persona':<28}{'N':<6}{'Ort.Klasik':<12}{'Ort.Alternatif':<16}{'Ort.Fark':<10}")
    print("-" * 72)
    for persona, kayitlar in persona_gruplari.items():
        n = len(kayitlar)
        ort_klasik = statistics.mean(k["klasik_skor"] for k in kayitlar)
        ort_alt = statistics.mean(k["alternatif_skor"] for k in kayitlar)
        ort_fark = ort_alt - ort_klasik
        print(f"{persona:<28}{n:<6}{ort_klasik:<12.1f}{ort_alt:<16.1f}{ort_fark:<10.1f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sentetik veriden alternatif kredi skoru üretir")
    parser.add_argument("--girdi", type=str, default="../data/sentetik_islemler.csv")
    parser.add_argument("--cikti", type=str, default="../data/skor_raporu.csv")
    args = parser.parse_args()

    rapor = musteri_raporu_olustur(args.girdi)

    alanlar = list(rapor[0].keys()) if rapor else []
    with open(args.cikti, "w", newline="", encoding="utf-8") as f:
        yazici = csv.DictWriter(f, fieldnames=alanlar)
        yazici.writeheader()
        yazici.writerows(rapor)

    print(f"{len(rapor)} müşteri için skor hesaplandı -> {args.cikti}\n")
    ozet_yazdir(rapor)
