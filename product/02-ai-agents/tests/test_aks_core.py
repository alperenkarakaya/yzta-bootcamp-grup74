"""
aks_core çekirdek testleri.

Çalıştırmak için:
    cd product/02-ai-agents
    pip install -e ".[test]"
    pytest
"""
import numpy as np
import pytest

from aks_core.agents.orkestrator import Orkestrator
from aks_core.agents.skorlama_agent import limit_oner, olasilik_to_aks
from aks_core.agents.veri_agent import VeriAgent
from aks_core.model import kayit


# --------------------------------------------------------------------------
# Model kaydı — platform taşınabilirliği
# --------------------------------------------------------------------------
# Bu testler bir regresyona karşı duruyor: model önceden joblib/pickle ile
# kaydediliyordu ve Linux'ta eğitilen model Windows'ta açılmıyordu
# ("XGBoostError: input stream corrupted"). Artık kütüphanenin kendi
# serileştirme formatı kullanılıyor.

def test_model_diskten_yuklenebiliyor():
    model, ad, ozellikler = kayit.yukle()
    assert ad in ("XGBoost", "LightGBM")
    assert len(ozellikler) == 9
    assert hasattr(model, "predict_proba")


def test_model_pickle_degil_metin_formatinda():
    """Kaydedilen artifact okunabilir metin olmalı — pickle'lanmış C++ buffer değil.

    Pickle buffer'ı platforma bağlıdır; bu test formatın geri kaymasını engeller.
    """
    from pathlib import Path
    from aks_core import paths

    meta = Path(paths.ARTIFACTS_DIR) / kayit.META_ADI
    assert meta.exists(), "aks_model_meta.json yok — model eski formatta kaydedilmiş olabilir"

    import json
    with open(meta, encoding="utf-8") as f:
        m = json.load(f)
    assert m["bicim"] in ("xgboost_json", "lightgbm_txt")

    model_dosyasi = Path(paths.ARTIFACTS_DIR) / m["dosya"]
    ham = model_dosyasi.read_bytes()[:16]
    assert not ham.startswith(b"\x80"), "Dosya pickle ile başlıyor — taşınabilir değil"


def test_yuklenen_model_tahmin_uretiyor():
    model, _, ozellikler = kayit.yukle()
    X = np.zeros((1, len(ozellikler)))
    p = model.predict_proba(X)
    assert p.shape == (1, 2)
    assert 0.0 <= float(p[0, 1]) <= 1.0


# --------------------------------------------------------------------------
# Skor dönüşümü ve limit mantığı
# --------------------------------------------------------------------------

def test_aks_skoru_300_850_araliginda():
    for p in (0.0, 0.25, 0.5, 0.75, 1.0):
        assert 300 <= olasilik_to_aks(p) <= 850


def test_temerrut_olasiligi_arttikca_skor_dusuyor():
    skorlar = [olasilik_to_aks(p) for p in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    assert skorlar == sorted(skorlar, reverse=True), "Skor, riskle birlikte azalmalı"


def test_yuksek_riskli_musteriye_limit_verilmiyor():
    ozellikler = {"toplam_gelir_hacmi": 60000, "toplam_gider_hacmi": 30000}
    assert limit_oner(400, ozellikler) == 0, "539 altı skorda limit 0 olmalı"


def test_limit_net_nakit_akisiyla_olceklenir():
    az = {"toplam_gelir_hacmi": 60000, "toplam_gider_hacmi": 54000}
    cok = {"toplam_gelir_hacmi": 120000, "toplam_gider_hacmi": 54000}
    assert limit_oner(800, cok) > limit_oner(800, az)


def test_gideri_gelirini_asan_musteriye_limit_yok():
    """Negatif nakit akışı limite dönüşmemeli."""
    batik = {"toplam_gelir_hacmi": 30000, "toplam_gider_hacmi": 90000}
    assert limit_oner(800, batik) == 0


# --------------------------------------------------------------------------
# Orkestratör — boru hattı ve hafıza
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def orkestrator():
    return Orkestrator()


@pytest.fixture
def islemler():
    """6 aylık düzenli maaş + kira + fatura; deterministik ve gerçek CSV şemasında."""
    kayitlar = []
    for ay in range(1, 7):
        kayitlar.append({"tarih": f"2026-0{ay}-01", "islem_tipi": "gelir",
                         "kategori": "maas_odemesi", "tutar": 25000.0})
        kayitlar.append({"tarih": f"2026-0{ay}-05", "islem_tipi": "gider",
                         "kategori": "kira", "tutar": -9000.0})
        kayitlar.append({"tarih": f"2026-0{ay}-12", "islem_tipi": "gider",
                         "kategori": "fatura", "tutar": -1500.0})
    return kayitlar


def test_boru_hatti_ucunu_de_calistiriyor(orkestrator, islemler):
    k = orkestrator.degerlendir(9001, islemler)
    assert k["kullanilan_agentlar"] == ["veri_agent", "skorlama_agent", "danisman_agent"]
    assert 300 <= k["aks_skor"] <= 850
    assert k["aciklama"]["riski_azaltan"] or k["aciklama"]["riski_artiran"]
    assert k["danisman"]["ozet"]


def test_hafiza_gecmis_tutuyor(orkestrator, islemler):
    orkestrator.degerlendir(9002, islemler)
    orkestrator.degerlendir(9002, islemler)
    gecmis = orkestrator.gecmis(9002)
    assert len(gecmis) == 2, "Her değerlendirme hafızaya yazılmalı"


def test_hafiza_skor_degisimini_hesapliyor(orkestrator, islemler):
    orkestrator.degerlendir(9003, islemler)
    ikinci = orkestrator.degerlendir(9003, islemler)
    assert "onceki_skor" in ikinci
    assert ikinci["skor_degisimi"] == ikinci["aks_skor"] - ikinci["onceki_skor"]


def test_ilk_degerlendirmede_onceki_skor_yok(orkestrator, islemler):
    ilk = orkestrator.degerlendir(9004, islemler)
    assert "onceki_skor" not in ilk


def test_musterilerin_hafizasi_birbirine_karismiyor(orkestrator, islemler):
    orkestrator.degerlendir(9005, islemler)
    assert orkestrator.gecmis(9006) == []


def test_ayni_girdi_ayni_skoru_uretiyor(orkestrator, islemler):
    """Skorlama deterministik olmalı — aynı hesap dökümü, aynı skor."""
    a = orkestrator.degerlendir(9007, islemler)
    b = orkestrator.degerlendir(9007, islemler)
    assert a["aks_skor"] == b["aks_skor"]


def test_ozellik_sirasi_modelle_ayni(orkestrator):
    """Özellik sırası kayarsa model sessizce yanlış tahmin üretir — sessiz felaket."""
    from aks_core.ozellik.cikarim import OZELLIK_ADLARI
    assert list(orkestrator.skorlama_agent.ozellikler) == list(OZELLIK_ADLARI)


def test_bos_islem_listesi_sessizce_skor_uretmiyor(orkestrator):
    """Boş hesap dökümünden skor üretmek tehlikeli: sıfır özellik = sahte 'temiz' profil.

    Şu an çekirdek bunu engellemiyor (API katmanında yakalanıyor). Bu test o
    davranışı belgeliyor; çekirdeğe doğrulama eklendiğinde raises'a çevrilecek.
    """
    k = orkestrator.degerlendir(9008, [])
    assert k["ozellikler"]["toplam_gelir_hacmi"] == 0, "Boş dökümde gelir sıfır olmalı"
    assert k.get("onerilen_limit", 0) == 0, "Boş dökümden limit önerilmemeli"
