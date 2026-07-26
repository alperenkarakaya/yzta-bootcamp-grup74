"""
Risk iştahı testleri (`aks_core.model.risk_istahi`) — execution.md §3b Phase 7 / 7.4.

Çalıştırmak için:
    cd product/02-ai-agents
    pytest tests/test_risk_istahi.py
"""
import pytest

from aks_core.model import risk_istahi


@pytest.fixture(scope="module")
def rapor():
    return risk_istahi.hesapla(veri_kaynagi="dekuple", seed=42)


def test_uc_profil_de_uretiliyor(rapor):
    assert set(rapor["profiller"]) == {"ihtiyatli", "dengeli", "atak"}


def test_her_profil_hedefi_karsiliyor_ya_da_durustce_uyariyor(rapor):
    for anahtar, veri in rapor["profiller"].items():
        if veri["uyari"] is None:
            assert veri["gerceklesen_kotu_oran"] <= veri["hedef_kotu_oran"] + 1e-9, (
                f"{anahtar}: gerçekleşen kötü oran hedefi aşıyor ama uyarı yok"
            )


def test_esikler_artan_risk_istahina_gore_azaliyor(rapor):
    """Daha atak bir profil, daha düşük (daha kolay geçilen) bir eşik seçmeli."""
    ihtiyatli = rapor["profiller"]["ihtiyatli"]["secilen_esik"]
    dengeli = rapor["profiller"]["dengeli"]["secilen_esik"]
    atak = rapor["profiller"]["atak"]["secilen_esik"]
    assert ihtiyatli >= dengeli >= atak


def test_onay_oranlari_artan_riskle_birlikte_artiyor(rapor):
    ihtiyatli = rapor["profiller"]["ihtiyatli"]["onay_orani"]
    dengeli = rapor["profiller"]["dengeli"]["onay_orani"]
    atak = rapor["profiller"]["atak"]["onay_orani"]
    assert ihtiyatli <= dengeli <= atak


def test_ci95_araligi_ortalamayi_iceriyor(rapor):
    for veri in rapor["profiller"].values():
        if veri["onay_orani_ci95"] is not None:
            lo, hi = veri["onay_orani_ci95"]
            assert lo <= veri["onay_orani"] <= hi


def test_dongusel_veri_kaynagi_reddedilir():
    with pytest.raises(ValueError):
        risk_istahi.hesapla(veri_kaynagi="dongusel")


def test_musteri_risk_istahi_esik_kararlari_tutarli(rapor):
    esikler = {k: v["secilen_esik"] for k, v in rapor["profiller"].items()}
    en_yuksek = max(esikler.values())
    en_dusuk = min(esikler.values())

    # En yüksek eşiğin üstünde bir skor -> üç profilde de onay
    sonuc_yuksek = risk_istahi.musteri_risk_istahi(en_yuksek + 1, rapor=rapor)
    assert all(v["onaylanir_mi"] for v in sonuc_yuksek.values())

    # En düşük eşiğin altında bir skor -> hiçbir profilde onay yok
    sonuc_dusuk = risk_istahi.musteri_risk_istahi(max(300, en_dusuk - 1), rapor=rapor)
    assert not any(v["onaylanir_mi"] for v in sonuc_dusuk.values())


def test_kaydet_ve_raporu_yukle_round_trip(rapor, tmp_path):
    yol = tmp_path / "risk_istahi_test.json"
    risk_istahi.kaydet(rapor, dosya_yolu=str(yol))
    yuklenen = risk_istahi.raporu_yukle(dosya_yolu=str(yol))
    assert yuklenen["profiller"].keys() == rapor["profiller"].keys()
