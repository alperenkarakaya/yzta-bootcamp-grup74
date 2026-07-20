"""
Formülasyon B — kalibre edilmiş kapasite + PD-gap (architecture.md §5.3, U10)
-------------------------------------------------------------------------------
Ürünün asıl çıktısı agregat AUC değil, davranışsal PD'nin klasik skor
bandının ima ettiği PD'den NE KADAR ve HANGİ YÖNDE farklı olduğudur.
Pozitif `pd_fark` = davranışsal kanıt, ince dosyanın ima ettiğinden DAHA
FAZLA kapasite gösteriyor demektir (bankanın skorunu değiştirmez — yalnızca
tamamlayıcı bir sinyal, overview.md §7).

`pd_geleneksel_bant`, klasik skor -> o banttaki AMPİRİK temerrüt oranı
eşlemesidir: sabit bir formül değil, eğitim popülasyonundan izotonik
regresyonla fit edilip `formulasyon_b.json`'a kaydedilir (`egitim.py` bunu
her eğitimde günceller).

`kapasite_sinyali` (0-100, 50=nötr) basit, doğrusal bir v1 ölçeklemesidir —
architecture.md §12'deki "fazla iddia etme" ilkesi gereği kalibre edilmiş bir
olasılık gibi değil, yalnızca yön/büyüklük göstergesi olarak sunulmalıdır.
"""
import json
from pathlib import Path

from aks_core import paths
from aks_core.model import kalibrasyon

DOSYA_ADI = "formulasyon_b.json"


def bant_tablosu_fit_et(klasik_skorlar, temerrut_etiketleri):
    """Klasik skor -> ampirik temerrüt oranı (azalan monotonik izotonik regresyon)."""
    return kalibrasyon.fit_isotonic(klasik_skorlar, temerrut_etiketleri, increasing=False)


def kaydet(tablo, dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else Path(paths.ARTIFACTS_DIR) / DOSYA_ADI
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(tablo, f, ensure_ascii=False, indent=2)
    return str(yol)


def yukle(dosya_yolu=None):
    yol = Path(dosya_yolu) if dosya_yolu else Path(paths.ARTIFACTS_DIR) / DOSYA_ADI
    if not yol.exists():
        return None
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def hesapla(klasik_skor, pd_davranissal, tablo=None):
    """architecture.md §5.3 alanlarını döner.

    Bant tablosu henüz eğitilmemiş/kaydedilmemişse (ör. eski bir model
    artifact'i) None alanlarla sessizce döner — hata fırlatmaz, çağıran
    (backend) bunu 'henüz mevcut değil' olarak taşıyabilir.
    """
    tablo = tablo if tablo is not None else yukle()
    if tablo is None:
        return {"pd_geleneksel_bant": None, "pd_fark": None, "kapasite_sinyali": None}
    pd_geleneksel = kalibrasyon.apply_isotonic(klasik_skor, tablo)
    pd_fark = pd_geleneksel - pd_davranissal
    kapasite_sinyali = int(round(max(0, min(100, 50 + pd_fark * 200))))
    return {
        "pd_geleneksel_bant": round(pd_geleneksel, 4),
        "pd_fark": round(pd_fark, 4),
        "kapasite_sinyali": kapasite_sinyali,
    }
