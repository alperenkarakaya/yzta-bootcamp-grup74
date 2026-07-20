"""
İş Etkisi Analizi
-----------------
Klasik skorun reddettiği ama GERÇEKTE temerrüde düşmeyen (kredibl) kişileri,
davranışsal modelin ne kadarını doğru şekilde 'onaylanabilir' olarak
yeniden kazandığını ölçer. Projenin bankaya değer önerisi buradan çıkar.

§3b/U6/D5: varsayılan veri kaynağı artık "dekuple" (özelliklerden bağımsız
etiket, architecture.md §5.1 düzeltmesi) — bu betiğin ürettiği "kurtarılan
kredibl kişi" sayısı önceden döngüsel veriyle hesaplanıyordu (D5: "973/1084
rescued... do not cite as validated"). Eski döngüsel veriyle karşılaştırma
için `veri_kaynagi="dongusel"` hâlâ seçilebilir.
"""
import numpy as np
from aks_core.model.egitim import klasik_risk_skoru, veri_hazirla, VERI_KAYNAKLARI
from aks_core.agents.skorlama_agent import olasilik_to_aks  # tek kaynak (U11 dedupe)


def analiz(islem_csv=None, klasik_esik=560, aks_esik=560, veri_kaynagi="dekuple"):
    from aks_core import paths
    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = islem_csv or paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"]) if kaynak["etiket"] else None
    from aks_core.model import kayit
    _model, _model_adi, _ozellikler = kayit.yukle()
    paket = {"model": _model, "model_adi": _model_adi, "ozellikler": _ozellikler}
    model, ozellikler = paket["model"], paket["ozellikler"]
    musteriler = veri_hazirla(islem_csv, veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)
    X = np.array([[m[o] for o in ozellikler] for m in musteriler], dtype=float)
    p = model.predict_proba(X)[:, 1]

    for m, pi in zip(musteriler, p):
        m["klasik_skor"] = klasik_risk_skoru(m)
        m["aks_skor"] = olasilik_to_aks(pi)

    # Klasik skorun reddettikleri
    reddedilenler = [m for m in musteriler if m["klasik_skor"] < klasik_esik]
    # Bunlardan gerçekte temerrüde düşmeyenler (haksız yere reddedilen kredibl kişiler)
    haksiz_red = [m for m in reddedilenler if m["temerrut"] == 0]
    # Modelimizin bu kredibl kişilerden onayladıkları
    kurtarilan = [m for m in haksiz_red if m["aks_skor"] >= aks_esik]
    # Modelin yanlışlıkla onayladığı gerçek temerrütler (risk kontrolü)
    red_temerrutler = [m for m in reddedilenler if m["temerrut"] == 1]
    yanlis_onay = [m for m in red_temerrutler if m["aks_skor"] >= aks_esik]

    print(f"Toplam müşteri: {len(musteriler)}")
    print(f"Klasik skorun reddettiği (skor<{klasik_esik}): {len(reddedilenler)}")
    print(f"  → bunlardan gerçekte KREDİBL olan (temerrüt yok): {len(haksiz_red)}")
    print(f"  → modelin doğru şekilde KURTARDIĞI kredibl kişi: {len(kurtarilan)} "
          f"(%{100*len(kurtarilan)/max(1,len(haksiz_red)):.0f})")
    print(f"  → reddedilenler içindeki gerçek temerrütler: {len(red_temerrutler)}")
    print(f"  → modelin yanlışlıkla onayladığı temerrüt: {len(yanlis_onay)} "
          f"(%{100*len(yanlis_onay)/max(1,len(red_temerrutler)):.0f}) [düşük olmalı]")

    # Persona kırılımı: kurtarılanlar kim?
    from collections import Counter
    kirilim = Counter(m["persona"] for m in kurtarilan)
    print("\nKurtarılan kredibl kişilerin persona dağılımı:")
    for persona, adet in kirilim.most_common():
        print(f"  {persona:<26}{adet}")

    # Basit getiri senaryosu (illüstratif varsayımlar)
    ort_kredi = 25000      # kurtarılan kişi başına ort. kredi hacmi (TL)
    getiri_orani = 0.12    # bankanın net getiri oranı
    ort_zarar_orani = 0.55 # temerrütte kredinin kaybedilen kısmı
    kazanc = len(kurtarilan) * ort_kredi * getiri_orani
    kayip = len(yanlis_onay) * ort_kredi * ort_zarar_orani
    print(f"\nİllüstratif getiri (bu örneklem, varsayımsal):")
    print(f"  Kurtarılan kredibl müşterilerden potansiyel net getiri: {kazanc:,.0f} TL")
    print(f"  Yanlış onaylardan beklenen zarar: {kayip:,.0f} TL")
    print(f"  Net: {kazanc - kayip:,.0f} TL")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--veri-kaynagi", default="dekuple", choices=list(VERI_KAYNAKLARI))
    a = p.parse_args()
    analiz(veri_kaynagi=a.veri_kaynagi)
