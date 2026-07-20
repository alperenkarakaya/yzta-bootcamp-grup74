"""
aks_core çekirdek testleri.

Çalıştırmak için:
    cd product/02-ai-agents
    pip install -e ".[test]"
    pytest
"""
import random

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
    assert ad in ("XGBoost", "LightGBM", "LogisticRegression")
    assert len(ozellikler) == 9
    assert hasattr(model, "predict_proba")


def test_model_pickle_degil_metin_formatinda():
    """XGBoost/LightGBM artifact'i okunabilir metin olmalı — pickle'lanmış C++ buffer değil.

    Pickle buffer'ı platforma bağlıdır; bu test formatın geri kaymasını engeller.
    LogisticRegression (U8) joblib/pickle ile kaydedilir — LR saf NumPy/sklearn
    durumu tutar, XGBoost/LightGBM'in platforma bağlı C++ buffer'ı yok, bu yüzden
    bu testin gerekçesi (cross-platform corruption) onun için geçerli değil.
    """
    from pathlib import Path
    from aks_core import paths

    meta = Path(paths.ARTIFACTS_DIR) / kayit.META_ADI
    assert meta.exists(), "aks_model_meta.json yok — model eski formatta kaydedilmiş olabilir"

    import json
    with open(meta, encoding="utf-8") as f:
        m = json.load(f)
    assert m["bicim"] in ("xgboost_json", "lightgbm_txt", "logistic_joblib")

    if m["bicim"] in ("xgboost_json", "lightgbm_txt"):
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


# --------------------------------------------------------------------------
# U5 — etiketleme.py global RNG durumunu artık kirletmiyor
# --------------------------------------------------------------------------

def test_etiketle_global_random_durumunu_degistirmiyor():
    from aks_core.model.etiketleme import etiketle

    ozellikler = [{"gider_gelir_orani": 0.9, "bakiye_trendi": 0.1,
                   "gelir_duzenliligi": 0.5, "fatura_odeme_duzeni": 0.5} for _ in range(5)]

    random.seed(123)
    once = random.random()
    random.seed(123)
    etiketle([dict(o) for o in ozellikler])  # global 'random' modülünü etkilememeli
    sonra = random.random()
    assert once == sonra, "etiketle() global random durumunu değiştirmemeli (D2/E6)"


def test_etiketle_ayni_seed_ayni_sonuc():
    from aks_core.model.etiketleme import etiketle

    ozellikler = [{"gider_gelir_orani": 0.9, "bakiye_trendi": 0.1,
                   "gelir_duzenliligi": 0.5, "fatura_odeme_duzeni": 0.5} for _ in range(20)]
    a = etiketle([dict(o) for o in ozellikler], seed=7)
    b = etiketle([dict(o) for o in ozellikler], seed=7)
    assert [m["temerrut"] for m in a] == [m["temerrut"] for m in b]


# --------------------------------------------------------------------------
# U11 — karar mekanizması politikası (tek kaynak, aynı davranış)
# --------------------------------------------------------------------------

def test_politika_bantlari_skorlama_agent_ile_ayni_davranisi_veriyor():
    from aks_core import politika

    for skor, beklenen_seviye in [(850, "düşük risk"), (720, "düşük risk"),
                                   (719, "orta-düşük risk"), (620, "orta-düşük risk"),
                                   (619, "orta risk"), (540, "orta risk"),
                                   (539, "yüksek risk"), (300, "yüksek risk")]:
        assert politika.bant_bul(skor)["seviye"] == beklenen_seviye


def test_is_etkisi_ve_skorlama_agent_ayni_olasilik_to_aks_fonksiyonunu_kullaniyor():
    from aks_core.model import is_etkisi
    from aks_core.agents import skorlama_agent
    assert is_etkisi.olasilik_to_aks is skorlama_agent.olasilik_to_aks


# --------------------------------------------------------------------------
# U9/U10 — kalibrasyon ve Formülasyon B yardımcıları
# --------------------------------------------------------------------------

def test_kalibrasyon_fit_apply_roundtrip_monotonik():
    from aks_core.model import kalibrasyon

    rng = np.random.default_rng(0)
    x = np.sort(rng.uniform(0, 1, 200))
    y = (x > 0.5).astype(float)
    tablo = kalibrasyon.fit_isotonic(x, y, increasing=True)
    dusuk = kalibrasyon.apply_isotonic(0.1, tablo)
    yuksek = kalibrasyon.apply_isotonic(0.9, tablo)
    assert dusuk <= yuksek, "Artan izotonik kalibrasyon monotonikliği korumalı"


def test_formulasyon_b_pd_fark_yonu():
    from aks_core.model import kalibrasyon, formulasyon_b

    # Sentetik bant tablosu: skor yükseldikçe temerrüt olasılığı düşer (azalan).
    tablo = kalibrasyon.fit_isotonic([300, 500, 700, 850], [0.5, 0.3, 0.1, 0.02], increasing=False)
    yuksek_skor = formulasyon_b.hesapla(800, pd_davranissal=0.05, tablo=tablo)
    assert yuksek_skor["pd_fark"] is not None
    assert yuksek_skor["kapasite_sinyali"] == 50 + round(yuksek_skor["pd_fark"] * 200)


def test_formulasyon_b_dosya_yoksa_yukle_none_doner(tmp_path):
    """`hesapla()`in None-alan fallback'i buna dayanır: henüz eğitilmemiş bir
    kurulumda (formulasyon_b.json yok) sessizce None döner, hata fırlatmaz."""
    from aks_core.model import formulasyon_b
    assert formulasyon_b.yukle(dosya_yolu=tmp_path / "yok.json") is None


# --------------------------------------------------------------------------
# U8 — LogisticRegression + StandardScaler taşınabilir kayıt/yükleme
# --------------------------------------------------------------------------

def test_lojistik_model_scaler_ile_birlikte_kaydedilip_yukleniyor(tmp_path):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    X = np.random.default_rng(0).normal(size=(50, 9))
    y = (X[:, 0] > 0).astype(int)
    sc = StandardScaler().fit(X)
    model = LogisticRegression().fit(sc.transform(X), y)

    d = tmp_path / "artifacts"
    d.mkdir()
    onceki = kayit.paths.ARTIFACTS_DIR
    kayit.paths.ARTIFACTS_DIR = d
    try:
        kayit.kaydet(model, "LogisticRegression", [f"o{i}" for i in range(9)], scaler=sc)
        yuklenen, ad, ozellikler = kayit.yukle()
        assert ad == "LogisticRegression"
        p = yuklenen.predict_proba(X)
        assert p.shape == (50, 2)
        np.testing.assert_allclose(p[:, 1], model.predict_proba(sc.transform(X))[:, 1])
    finally:
        kayit.paths.ARTIFACTS_DIR = onceki
