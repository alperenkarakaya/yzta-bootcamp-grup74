"""
Belge Agent — çok stratejili, kendini denetleyen belge işleme sarmalayıcısı
(execution.md §3b Phase 7 / 7.5).

Neden "gerçek" bir agent (OQ-38'in kapanışı): `veri_agent`/`skorlama_agent`
sabit bir pipeline adımını sarmalayan deterministik fonksiyonlardır — hedefi
yok, strateji seçmez. Bu agent farklı: bir HEDEFİ var (bir dosyayı BAŞARILI
şekilde skorlanabilir işlem listesine çevirmek), bu hedefe ulaşmak için
BİRDEN FAZLA strateji dener (format-özel okuyucu, PDF için tablo→metin
sırasıyla), KENDİ ÇIKTISINI denetler (kalite bayrakları, min. işlem sayısı)
ve her adımı bir İZ (trace) olarak bırakır — beş-soru testini (overview.md §6)
gerçekten geçer.

`aks_core.belge.okuyucu.ayristir()` (7.1) ile AYNI alt modülleri kullanır —
mantık kopyalanmaz, yalnızca trace toplama katmanı eklenir. `04-backend`
tercihen bu agent'ı çağırır (`services.belge_ayristir`); `okuyucu.ayristir()`
izsiz, düşük-seviye API olarak (ör. testler) hâlâ durur.
"""
import os

from aks_core.belge import kalite, normalizer, parmak_izi, pdf_okuyucu, tablo_okuyucu
from aks_core.belge.hatalar import BelgeHatasi
from aks_core.belge.okuyucu import DESTEKLENEN_UZANTILAR, MIN_ISLEM_SAYISI


class BelgeAgent:
    ad = "belge_agent"

    def calistir(self, dosya_adi, veri_baytlari):
        """Döner: (islemler, meta) — `meta["iz"]` agent'ın attığı her adımı
        insan-okur cümlelerle taşır. Başarısızlıkta `BelgeHatasi` fırlatır;
        o ana kadarki iz, `hata.iz` özniteliğine eklenir (çağıran taraf
        isterse hata yanıtına ekleyebilir — şeffaflık, sessiz başarısızlık yok).
        """
        iz = []
        ext = os.path.splitext(dosya_adi or "")[1].lower()
        iz.append(f"Format tespiti: '{dosya_adi}' -> {ext or '(uzantısız)'}")

        if ext not in DESTEKLENEN_UZANTILAR:
            iz.append("Karar: desteklenmeyen format, reddedildi")
            hata = BelgeHatasi(
                f"Desteklenmeyen dosya türü: '{ext or '(uzantısız)'}'. Kabul edilen formatlar: CSV, XLSX, PDF."
            )
            hata.iz = iz
            raise hata

        try:
            if ext == ".csv":
                iz.append("Strateji seçimi: CSV tablo okuyucu")
                ham, format_adi = tablo_okuyucu.csv_oku(veri_baytlari), "csv"
            elif ext in (".xlsx", ".xls"):
                iz.append("Strateji seçimi: Excel tablo okuyucu")
                ham, format_adi = tablo_okuyucu.excel_oku(veri_baytlari), "xlsx"
            else:
                ham, format_adi = pdf_okuyucu.pdf_oku(veri_baytlari, iz=iz), "pdf"
        except BelgeHatasi as e:
            iz.append(f"Ayrıştırma başarısız: {e}")
            e.iz = iz
            raise

        iz.append(f"{len(ham)} ham satır çıkarıldı — normalize ediliyor")
        islemler, kategori_guveni, toplam_ham = normalizer.normalize(ham)
        iz.append(f"Kendi kendini denetleme: {len(islemler)}/{toplam_ham} satır normalize edildi "
                   f"(ortalama kategori güveni: {kategori_guveni})")

        if len(islemler) < MIN_ISLEM_SAYISI:
            iz.append(f"Karar: yetersiz işlem sayısı (< {MIN_ISLEM_SAYISI}), reddedildi")
            hata = BelgeHatasi(
                f"Anlamlı bir skor için en az {MIN_ISLEM_SAYISI} işlem gerekli "
                f"(ayrıştırılabilen: {len(islemler)})."
            )
            hata.iz = iz
            raise hata

        rapor = kalite.degerlendir(islemler, kategori_guveni, toplam_ham)
        if rapor["bayraklar"]:
            iz.append(f"Kalite kontrolü: bayrak(lar) bulundu — {rapor['bayraklar']}")
        else:
            iz.append("Kalite kontrolü: sorun bulunamadı")

        meta = {
            "kaynak_format": format_adi, "kategori_guveni": kategori_guveni,
            "parmak_izi": parmak_izi.hesapla(islemler), "iz": iz, **rapor,
        }
        return islemler, meta
