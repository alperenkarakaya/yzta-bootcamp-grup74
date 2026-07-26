"""
Gerçek örnek belge testleri (`01-data/datasets/example_datas/`) —
execution.md §3b Phase 7 / 7.1 doğrulama turu.

Bu klasör PO tarafından sağlanan, GERÇEKÇİ (sentetik ama gerçek banka
ekstresi formatına yakın) PDF/CSV örnekleri içerir — 3 gelir seviyesinde
öğrenci persona'sı, her biri için hem "dekont" (tek işlemlik makbuz) hem
"hesap dökümü" (çok sayfalı gerçek tablo) PDF'i + iki CSV varyantı.

`test_belge.py`'nin `reportlab` ile üretilen SENTETİK fixture'larından farkı:
bu dosyalar gerçek bir PDF üretim aracının (muhtemelen farklı bir kütüphane/
şablon) çıktısı — gerçek Türkçe karakterler, çok sayfalı tablo, tekrarlanan
başlık satırları, "İşlem Tutarı" vs "Brüt Tutar" gibi birden fazla tutar
kolonu içeriyor. Bu, sentetik fixture'ların YAKALAYAMADIĞI bir bulguyu ortaya
çıkardı: PDF'in "Açıklama" kolonu doğrudan kategori adının kendisini taşıyor
("eglence", "ulasim" gibi) — marka/anahtar-kelime bazlı kategori tahmini
(`normalizer.py::_KATEGORI_ANAHTAR`) bunu tanımıyordu, kategori güveni ~%50'ye
düşüyordu. Anahtar kelime listesi bu turda genişletildi (fix + bu test).

`01-data/` yalnızca OKUNUR (execution.md §3b sınırı) — bu dosya hiçbir zaman
o klasöre yazmaz. Klasör yoksa (örn. bu örnek veriler henüz eklenmemiş bir
clone'da) testler `skip` ile geçilir, başarısız olmaz.

Çalıştırmak için:
    cd product/02-ai-agents
    pytest tests/test_ornek_belgeler.py
"""
from pathlib import Path

import pytest

from aks_core.agents.belge_agent import BelgeAgent
from aks_core.belge.hatalar import BelgeHatasi

_ORNEK_KOK = Path(__file__).resolve().parents[2] / "01-data" / "datasets" / "example_datas"

KATEGORI_GUVEN_ESIGI = 0.85  # gerçek veriyle ölçülen ~0.9'un altında bir taban


def _klasorler():
    if not _ORNEK_KOK.is_dir():
        return []
    return sorted(p for p in _ORNEK_KOK.iterdir() if p.is_dir())


pytestmark = pytest.mark.skipif(
    not _klasorler(), reason=f"Örnek belge klasörü yok: {_ORNEK_KOK}"
)


def _oku(yol: Path) -> bytes:
    return yol.read_bytes()


@pytest.mark.parametrize("klasor", _klasorler(), ids=lambda p: p.name)
def test_hesap_dokumu_pdf_basariyla_ayristirilir(klasor):
    pdfler = list(klasor.glob("*_hesap_dokumu.pdf"))
    assert len(pdfler) == 1, f"{klasor.name}: tam olarak 1 hesap dökümü PDF'i bekleniyor"
    islemler, meta = BelgeAgent().calistir(pdfler[0].name, _oku(pdfler[0]))

    assert len(islemler) >= 80, "Çok sayfalı PDF'in tüm sayfaları okunmalı (tek sayfa değil)"
    assert meta["kaynak_format"] == "pdf"
    assert meta["kategori_guveni"] >= KATEGORI_GUVEN_ESIGI, (
        f"Kategori güveni düşük ({meta['kategori_guveni']}) — normalizer.py'nin "
        "anahtar-kelime listesi bu gerçek veri formatını tanımıyor olabilir"
    )
    assert "dusuk_kategori_guveni" not in meta["bayraklar"]


@pytest.mark.parametrize("klasor", _klasorler(), ids=lambda p: p.name)
def test_tek_islemlik_dekont_zarifce_reddedilir(klasor):
    """Bir "dekont" (tek işlem makbuzu) < 5 işlem içerir — model için anlamlı
    bir skor üretilemez. BelgeHatasi bekleniyor, sessiz/yanlış sonuç değil."""
    dekontlar = list(klasor.glob("*_dekont.pdf"))
    assert len(dekontlar) == 1
    with pytest.raises(BelgeHatasi):
        BelgeAgent().calistir(dekontlar[0].name, _oku(dekontlar[0]))


@pytest.mark.parametrize("klasor", _klasorler(), ids=lambda p: p.name)
def test_pdf_ve_iki_csv_varyanti_ayni_parmak_izini_verir(klasor):
    """Aynı müşterinin PDF hesap dökümü + iki CSV varyantı (kapasite_islemler
    ve sentetik_islemler şemaları) — üçü de AYNI parmak izini vermeli. Gerçek
    veriyle, sentetik test_belge.py fixture'larının ötesinde bir doğrulama."""
    pdf = next(klasor.glob("*_hesap_dokumu.pdf"))
    kapasite_csv = next(klasor.glob("*_kapasite_islemler.csv"))
    sentetik_csv = next(klasor.glob("*_sentetik_islemler.csv"))

    _, meta_pdf = BelgeAgent().calistir(pdf.name, _oku(pdf))
    _, meta_kapasite = BelgeAgent().calistir(kapasite_csv.name, _oku(kapasite_csv))
    _, meta_sentetik = BelgeAgent().calistir(sentetik_csv.name, _oku(sentetik_csv))

    assert meta_pdf["parmak_izi"] == meta_kapasite["parmak_izi"] == meta_sentetik["parmak_izi"]


@pytest.mark.parametrize("klasor", _klasorler(), ids=lambda p: p.name)
def test_csv_varyanti_tam_kategori_guveniyle_ayristirilir(klasor):
    """CSV'lerde kategori kolonu doğrudan verili — güven her zaman 1.0 olmalı."""
    for glob_deseni in ("*_kapasite_islemler.csv", "*_sentetik_islemler.csv"):
        dosya = next(klasor.glob(glob_deseni))
        _, meta = BelgeAgent().calistir(dosya.name, _oku(dosya))
        assert meta["kategori_guveni"] == 1.0, dosya.name


def test_uc_gelir_seviyesi_arasinda_onerilen_limit_artan_sirada():
    """Düşük → Orta → Yüksek gelirli öğrenci persona'ları arasında önerilen
    kredi limiti (net nakit akışına dayalı) tutarlı biçimde artmalı — belge
    hattının uçtan uca iş mantığı doğrulaması (yalnızca ayrıştırma değil)."""
    klasorler = _klasorler()
    if len(klasorler) < 3:
        pytest.skip("3 gelir seviyesi klasörü bulunamadı")

    from aks_core.agents.orkestrator import Orkestrator
    orkestrator = Orkestrator()

    limitler = {}
    for klasor in klasorler:
        pdf = next(klasor.glob("*_hesap_dokumu.pdf"))
        islemler, _ = BelgeAgent().calistir(pdf.name, _oku(pdf))
        sonuc = orkestrator.degerlendir(klasor.name, islemler)
        limitler[klasor.name] = sonuc.get("onerilen_limit") or 0

    # Klasör adları alfabetik sırayla gelir sırasını vermez — açıkça eşle.
    dusuk = next(v for k, v in limitler.items() if "üşük" in k.lower() or "dusuk" in k.lower())
    orta = next(v for k, v in limitler.items() if "orta" in k.lower())
    yuksek = next(v for k, v in limitler.items() if "üksek" in k.lower() or "yuksek" in k.lower())
    assert dusuk <= orta <= yuksek, limitler
