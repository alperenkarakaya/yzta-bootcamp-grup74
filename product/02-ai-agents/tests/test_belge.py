"""
Belge işleme hattı testleri (`aks_core.belge`) — execution.md §3b Phase 7 / 7.1.

Çalıştırmak için:
    cd product/02-ai-agents
    pip install -e ".[test]"
    pytest tests/test_belge.py
"""
import io

import pytest

from aks_core.belge import BelgeHatasi, ayristir
from aks_core.belge import normalizer, parmak_izi

# --------------------------------------------------------------------------
# Fixture içerikleri — üç formatta AYNI 8 işlemi temsil eder (parmak izi testi)
# --------------------------------------------------------------------------
_ISLEMLER = [
    # tarih,      açıklama,              tutar (gider negatif)
    ("2026-01-05", "Maaş Ödemesi",        15000.00),
    ("2026-01-10", "Migros Market",        -450.50),
    ("2026-01-15", "Elektrik Faturası",    -320.00),
    ("2026-02-05", "Maaş Ödemesi",        15000.00),
    ("2026-02-12", "Kira Ödemesi",        -6000.00),
    ("2026-02-20", "Netflix Aboneliği",     -149.99),
    ("2026-03-05", "Maaş Ödemesi",        15000.00),
    ("2026-03-18", "Migros Market",        -510.25),
]


def _csv_baytlari():
    satirlar = ["tarih,islem_tipi,kategori,tutar,aciklama"]
    for tarih, aciklama, tutar in _ISLEMLER:
        tip = "gelir" if tutar > 0 else "gider"
        kategori = "maas" if "Maaş" in aciklama else ("market" if "Market" in aciklama else
                    "fatura" if "Fatura" in aciklama else "kira" if "Kira" in aciklama else "eglence")
        satirlar.append(f"{tarih},{tip},{kategori},{tutar},{aciklama}")
    return ("\n".join(satirlar)).encode("utf-8")


def _xlsx_baytlari():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(["İşlem Tarihi", "Açıklama", "Tutar"])
    for tarih, aciklama, tutar in _ISLEMLER:
        ws.append([tarih, aciklama, tutar])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _pdf_baytlari_tablolu():
    """pdfplumber'ın extract_tables() ile yakalayabileceği, gerçek çizgili bir tablo.

    reportlab'ın varsayılan Helvetica/WinAnsi fontu Türkçe'ye özgü noktasız 'ı'/'ş'/'ğ'
    glifllerini içermez (WinAnsi ⊃ Latin-1, ama bu üçü değil) — gerçek bir Unicode font
    kaydetmek yerine (platforma bağlı .ttf yolu gerektirir, taşınabilirliği bozar) bu
    fixture'da açıklamalar ASCII'ye çevrilir. Kategori anahtar-kelime listesi zaten
    ASCII varyantları da içeriyor (örn. "maas"), bu yüzden kategori tahmini etkilenmez —
    yalnızca font sınırlaması, üretim kodunun bir kısıtı değil."""
    pytest.importorskip("reportlab", reason="PDF fixture'ı için reportlab gerekir")
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    _ascii_aciklama = {
        "Maaş Ödemesi": "Maas Odemesi", "Elektrik Faturası": "Elektrik Faturasi",
        "Kira Ödemesi": "Kira Odemesi", "Netflix Aboneliği": "Netflix Aboneligi",
    }
    veri = [["Tarih", "Aciklama", "Tutar"]]
    for tarih, aciklama, tutar in _ISLEMLER:
        veri.append([tarih, _ascii_aciklama.get(aciklama, aciklama), f"{tutar:.2f}"])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    tablo = Table(veri)
    tablo.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([tablo])
    return buf.getvalue()


# --------------------------------------------------------------------------
# okuyucu.ayristir — format yönlendirme + uçtan uca
# --------------------------------------------------------------------------

def test_desteklenmeyen_uzanti_reddedilir():
    with pytest.raises(BelgeHatasi):
        ayristir("ekstre.docx", b"herhangi")


def test_csv_ayristirilir_ve_8_islem_doner():
    islemler, meta = ayristir("ekstre.csv", _csv_baytlari())
    assert len(islemler) == 8
    assert meta["kaynak_format"] == "csv"
    assert meta["kategori_guveni"] == 1.0  # CSV'de kategori doğrudan verildi


def test_xlsx_ayristirilir_kategori_tahmin_edilir():
    islemler, meta = ayristir("ekstre.xlsx", _xlsx_baytlari())
    assert len(islemler) == 8
    assert meta["kaynak_format"] == "xlsx"
    # Excel'de kategori kolonu yok -> anahtar-kelime tahmini, güven < 1.0
    assert 0.0 < meta["kategori_guveni"] < 1.0
    maas_islemleri = [i for i in islemler if i["kategori"] == "maas"]
    assert len(maas_islemleri) == 3


def test_pdf_tablolu_ayristirilir():
    islemler, meta = ayristir("ekstre.pdf", _pdf_baytlari_tablolu())
    assert len(islemler) == 8
    assert meta["kaynak_format"] == "pdf"


def test_ayni_icerik_uc_formatta_ayni_parmak_izini_verir():
    _, meta_csv = ayristir("a.csv", _csv_baytlari())
    _, meta_xlsx = ayristir("a.xlsx", _xlsx_baytlari())
    _, meta_pdf = ayristir("a.pdf", _pdf_baytlari_tablolu())
    assert meta_csv["parmak_izi"] == meta_xlsx["parmak_izi"] == meta_pdf["parmak_izi"]


def test_bozuk_pdf_anlamli_hata_verir():
    with pytest.raises(BelgeHatasi):
        ayristir("bozuk.pdf", b"%PDF-1.4 bu gecerli bir pdf degil")


def test_eksik_kolonlu_csv_anlamli_hata_verir():
    with pytest.raises(BelgeHatasi):
        ayristir("eksik.csv", b"a,b,c\n1,2,3\n")


def test_az_islemli_dosya_reddedilir():
    icerik = b"tarih,islem_tipi,kategori,tutar,aciklama\n2026-01-01,gelir,maas,1000,x\n"
    with pytest.raises(BelgeHatasi):
        ayristir("az.csv", icerik)


# --------------------------------------------------------------------------
# normalizer — tarih/tutar ayrıştırma birim testleri
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ham,beklenen", [
    ("2026-03-05", "2026-03-05"),
    ("05.03.2026", "2026-03-05"),
    ("05/03/2026", "2026-03-05"),
])
def test_tarih_bicimleri_taniniyor(ham, beklenen):
    assert normalizer._tarih_ayikla(ham) == beklenen


@pytest.mark.parametrize("ham,beklenen", [
    ("1234.56", 1234.56),
    ("1.234,56", 1234.56),
    ("-450,50", -450.50),
    ("(450,50)", -450.50),
])
def test_tutar_bicimleri_taniniyor(ham, beklenen):
    assert normalizer._tutar_ayikla(ham) == pytest.approx(beklenen)


def test_gider_isareti_kanonik_negatife_zorlanir():
    """Kaynakta işaret tutarsız olsa bile (ör. borç kolonu pozitif) kanonik
    kural (gider < 0) her zaman uygulanır — bakiye_trendi'nin anlamlı kalması
    için (bkz. modül docstring'i)."""
    ham = [{"tarih_ham": "2026-01-01", "tutar_ham": "100", "islem_tipi": "gider"}]
    islemler, _, _ = normalizer.normalize(ham)
    assert islemler[0]["tutar"] == -100.0


def test_tarihsiz_satir_atlanir_hata_vermez():
    ham = [{"tarih_ham": "", "tutar_ham": "100"}, {"tarih_ham": "2026-01-01", "tutar_ham": "100"}]
    islemler, _, toplam = normalizer.normalize(ham)
    assert len(islemler) == 1
    assert toplam == 2


# --------------------------------------------------------------------------
# parmak_izi — sıra bağımsızlığı
# --------------------------------------------------------------------------

def test_parmak_izi_satir_sirasindan_bagimsiz():
    a = [{"tarih": "2026-01-01", "islem_tipi": "gelir", "kategori": "maas", "tutar": 100.0},
         {"tarih": "2026-01-02", "islem_tipi": "gider", "kategori": "market", "tutar": -50.0}]
    b = list(reversed(a))
    assert parmak_izi.hesapla(a) == parmak_izi.hesapla(b)


def test_parmak_izi_farkli_icerik_farkli_ozet():
    a = [{"tarih": "2026-01-01", "islem_tipi": "gelir", "kategori": "maas", "tutar": 100.0}]
    b = [{"tarih": "2026-01-01", "islem_tipi": "gelir", "kategori": "maas", "tutar": 200.0}]
    assert parmak_izi.hesapla(a) != parmak_izi.hesapla(b)


# --------------------------------------------------------------------------
# kategori çıkarım doğruluğu (kritik bulgu — plan §7.1)
# --------------------------------------------------------------------------

def test_kategori_tahmin_dogrulugu_bilinen_ekstrede():
    """Bilinen kategorili bir ekstrede (Excel, kategori kolonu yok) tahmin
    doğruluğunu ölçer — sessizce güvenilir varsayılmaz, raporlanır."""
    islemler, meta = ayristir("ekstre.xlsx", _xlsx_baytlari())
    beklenen_kategori = {
        "Maaş Ödemesi": "maas", "Migros Market": "market",
        "Elektrik Faturası": "fatura", "Kira Ödemesi": "kira", "Netflix Aboneliği": "eglence",
    }
    dogru = sum(1 for i in islemler if beklenen_kategori.get(i["aciklama"]) == i["kategori"])
    dogruluk = dogru / len(islemler)
    assert dogruluk >= 0.75, f"Kategori tahmin doğruluğu düşük: {dogruluk:.2f}"
