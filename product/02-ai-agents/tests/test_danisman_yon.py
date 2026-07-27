"""
Danışman önerilerinin yönü ile modelin öğrendiği yön uyumlu mu?

Bu testin varlık sebebi gerçek bir hatadır: `ONERI_HARITASI` her faktör için
sabit bir tavsiye cümlesi tutuyordu ve cümleler "bu özelliği ARTIR" varsayımıyla
yazılmıştı. Oysa dekuple veriyle eğitilen LogisticRegression iki özellikte
bunun TERSİNİ öğrenmişti (`gelir_kaynagi_sayisi`, `gelir_duzenliligi`) ve ürün,
kullanıcıya kendi modeline göre riskini ARTIRACAK adımı tavsiye ediyordu —
üstelik `gelir_kaynagi_sayisi` gerçek bir örnek belgede 1 numaralı risk
sürücüsüydü. Ayrıca en güçlü ikinci katsayı olan `toplam_gider_hacmi` için
hiç tavsiye üretilmiyordu.

Model yeniden eğitildiğinde bir katsayının işareti değişirse bu test kırılır;
ürün sessizce yanlış tavsiye vermeye başlamaz.
"""
import numpy as np
import pytest

from aks_core.agents.danisman_agent import ONERI_HARITASI
from aks_core.model.kayit import yukle


def _katsayilar():
    model, _, ozellikler = yukle()
    taban = getattr(model, "taban_model", model)
    ic = getattr(taban, "model", taban)
    if not hasattr(ic, "coef_"):
        pytest.skip("Doğrusal olmayan model — global katsayı yönü tanımsız")
    return dict(zip(ozellikler, np.asarray(ic.coef_).ravel()))


def test_her_ozellik_icin_bir_yon_kaydi_var():
    _, _, ozellikler = yukle()
    eksik = set(ozellikler) - set(ONERI_HARITASI)
    assert not eksik, f"ONERI_HARITASI'nda yön kaydı olmayan özellik(ler): {sorted(eksik)}"


def test_oneri_yonu_modelin_katsayi_isaretiyle_uyumlu():
    katsayi = _katsayilar()
    tutarsiz = []
    for kod, (yon, _metin) in ONERI_HARITASI.items():
        c = katsayi.get(kod)
        if c is None:
            continue
        beklenen = "azalt" if c > 0 else "artir"
        if yon != beklenen:
            tutarsiz.append(f"{kod}: katsayı {c:+.4f} -> '{beklenen}' beklenirdi, haritada '{yon}'")
    assert not tutarsiz, "Tavsiye yönü modelle çelişiyor:\n" + "\n".join(tutarsiz)


def test_sezgiye_aykiri_yonde_eylem_tavsiyesi_verilmez():
    """Model "azalt" diyorsa ama azaltmak savunulabilir bir davranış tavsiyesi
    değilse (`metin is None`), kullanıcıya hiçbir şey söylenmemeli — ters yönde
    tavsiye üretmek yerine susmak doğru davranış."""
    from aks_core.agents.danisman_agent import DanismanAgent

    aciklama = {
        "riski_azaltan": [],
        "riski_artiran": [{"faktor": "gelir düzenliliği", "kod": "gelir_duzenliligi", "etki": 0.5}],
    }
    sonuc = DanismanAgent().calistir({"aks_skor": 700, "risk_seviyesi": "orta risk"}, aciklama)
    assert all("düzenli ve öngörülebilir" not in o for o in sonuc["oneriler"])
