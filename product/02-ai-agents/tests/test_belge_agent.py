"""
BelgeAgent testleri — execution.md §3b Phase 7 / 7.5.

`test_belge.py`'nin fixture'larını (CSV/XLSX/PDF üretimi) yeniden kullanır;
burada odak agent'ın İZ bıraktığı ve çok-stratejili davrandığı.
"""
import pytest

from aks_core.agents.belge_agent import BelgeAgent
from aks_core.belge.hatalar import BelgeHatasi
from tests.test_belge import _csv_baytlari, _pdf_baytlari_tablolu, _xlsx_baytlari


def test_basarili_calistirma_iz_birakir():
    islemler, meta = BelgeAgent().calistir("ekstre.csv", _csv_baytlari())
    assert len(islemler) == 8
    assert "iz" in meta
    assert len(meta["iz"]) >= 3
    assert any("Format tespiti" in adim for adim in meta["iz"])


def test_pdf_izinde_strateji_1_basarili_gorunuyor():
    """PDF fixture'ı gerçek bir tablo içeriyor — Strateji 1 (extract_tables)
    başarılı olmalı, Strateji 2'ye düşülmemeli."""
    _, meta = BelgeAgent().calistir("ekstre.pdf", _pdf_baytlari_tablolu())
    iz_metni = " | ".join(meta["iz"])
    assert "Strateji 1 başarılı" in iz_metni
    assert "Strateji 2" not in iz_metni


def test_desteklenmeyen_format_hata_izi_tasir():
    with pytest.raises(BelgeHatasi) as exc_info:
        BelgeAgent().calistir("ekstre.docx", b"icerik")
    assert hasattr(exc_info.value, "iz")
    assert len(exc_info.value.iz) >= 1


def test_yetersiz_islem_hata_izi_tasir():
    icerik = b"tarih,islem_tipi,kategori,tutar,aciklama\n2026-01-01,gelir,maas,1000,x\n"
    with pytest.raises(BelgeHatasi) as exc_info:
        BelgeAgent().calistir("az.csv", icerik)
    assert "yetersiz" in " ".join(exc_info.value.iz).lower() or "reddedildi" in " ".join(exc_info.value.iz).lower()


def test_xlsx_de_calisir_ve_kategori_tahmini_izde_gorunur():
    _, meta = BelgeAgent().calistir("ekstre.xlsx", _xlsx_baytlari())
    iz_metni = " | ".join(meta["iz"])
    assert "kategori güveni" in iz_metni.lower()
