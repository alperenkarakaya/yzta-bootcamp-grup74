"""ek_onay.py (Backlog #13b) birim testleri — saf fonksiyonlar, model gerektirmez."""
import numpy as np
import pytest

from aks_core.model.ek_onay import (
    _onay_orani_sabit_riskte,
    _delta,
    _bootstrap_onay_ci,
)


def test_mukemmel_siralama_hedefe_kadar_onaylar():
    # 10 iyi (y=0) yüksek skorlu, 10 kötü (y=1) düşük skorlu -> mükemmel ayrışma.
    skor = np.concatenate([np.linspace(1, 0.6, 10), np.linspace(0.4, 0, 10)])
    y = np.array([0] * 10 + [1] * 10)
    onay, kotu, k = _onay_orani_sabit_riskte(skor, y, hedef_kotu_oran=0.0)
    # Kötü-oran 0 hedefinde tam 10 iyi müşteri onaylanmalı.
    assert k == 10
    assert onay == pytest.approx(0.5)
    assert kotu == pytest.approx(0.0)


def test_rastgele_skor_hedef_altinda_kalamaz():
    # Skor bilgi taşımıyorsa (sabit), her onay taban orana yakın kötü-oran verir.
    rng = np.random.default_rng(0)
    y = (rng.random(1000) < 0.3).astype(int)
    skor = np.zeros(1000)  # ayrıştırma yok
    onay, kotu, _ = _onay_orani_sabit_riskte(skor, y, hedef_kotu_oran=0.10)
    # 0.10 hedefi taban 0.30'un altında; bilgisiz skor bunu tutturamaz -> ~0 onay.
    assert onay < 0.05


def test_hedef_gevsedikce_onay_monoton_artar():
    rng = np.random.default_rng(1)
    y = (rng.random(500) < 0.2).astype(int)
    skor = -y + rng.normal(0, 0.5, 500)  # gerçek ama gürültülü sinyal
    o1, *_ = _onay_orani_sabit_riskte(skor, y, 0.05)
    o2, *_ = _onay_orani_sabit_riskte(skor, y, 0.15)
    assert o2 >= o1


def test_delta_pozitif_ayristirici_skor_lehine():
    rng = np.random.default_rng(2)
    n = 800
    y = (rng.random(n) < 0.18).astype(int)
    aks = -y + rng.normal(0, 0.4, n)          # temerrütü ayrıştırır
    klasik = rng.normal(600, 50, n)           # temerrütle ilgisiz (statü gürültüsü)
    d, r_yildiz, ref_onay, aks_onay, _ = _delta(klasik, aks, y, referans_esik=560)
    assert aks_onay >= ref_onay
    assert d >= 0


def test_bootstrap_ci_sirali():
    rng = np.random.default_rng(3)
    y = (rng.random(400) < 0.2).astype(int)
    skor = -y + rng.normal(0, 0.4, 400)
    ort, (lo, hi) = _bootstrap_onay_ci(skor, y, 0.10, n_boot=200)
    assert lo <= ort <= hi
    assert 0.0 <= lo and hi <= 1.0


def test_bos_girdi_sifir_doner():
    onay, kotu, k = _onay_orani_sabit_riskte(np.array([]), np.array([]), 0.1)
    assert (onay, kotu, k) == (0.0, 0.0, 0)
