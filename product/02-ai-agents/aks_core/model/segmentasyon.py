"""
Segmentasyon — Denetimsiz Persona Keşfi
-----------------------------------------
K-Means ile davranışsal özellikler üzerinde denetimsiz kümeleme: ürünün 4
hardcoded personasının (`klasik_maasli` vb., sentetik üreticiden gelen bir
ETİKET) gerçek davranışsal kümelenmeyle ne kadar örtüştüğünü, ya da farklı/
daha ince bir segmentasyonun mümkün olup olmadığını KEŞFETMEK için.

Bu bir karar bileşeni DEĞİLDİR: sonucu hiçbir skorlama/karar yoluna
beslenmez — yalnızca offline, salt-okunur bir keşif raporudur
(is_etkisi.py/degerlendirme.py ile aynı "araştırma betiği" kategorisi).
Beş-soru testi: deterministik istatistiksel araç, agent değil.

Neden K-Means + silhouette taraması (k=2..6): basit, yorumlanabilir, az
varsayım. Silhouette skoru veriye en uygun küme sayısını seçmek için
kullanılıyor — k sabit/varsayılmıyor.
"""
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from aks_core import paths
from aks_core.ozellik.cikarim import OZELLIK_ADLARI

RAPOR_ADI = "segmentasyon_raporu.json"


def kumele(X, k_araligi=range(2, 7), seed=42):
    """k=2..6 arası dener, en yüksek silhouette skoruna sahip olanı seçer.
    Döner: (model, silhouette_skoru, k)."""
    sc = StandardScaler().fit(X)
    Xs = sc.transform(X)
    en_iyi = None
    for k in k_araligi:
        km = KMeans(n_clusters=k, random_state=seed, n_init=10).fit(Xs)
        sil = silhouette_score(Xs, km.labels_)
        if en_iyi is None or sil > en_iyi[1]:
            en_iyi = (km, sil, k)
    return en_iyi


def profil_cikar(musteriler, etiketler):
    """Küme başına: boyut, bilinen-persona dağılımı, ampirik temerrüt oranı,
    özellik ortalamaları."""
    kumeler = {}
    for m, k in zip(musteriler, etiketler):
        kumeler.setdefault(int(k), []).append(m)
    profil = {}
    for k, uyeler in kumeler.items():
        persona_dagilimi = Counter(u["persona"] for u in uyeler)
        temerrut_orani = sum(u["temerrut"] for u in uyeler) / len(uyeler)
        ozellik_ortalamalari = {o: round(float(np.mean([u[o] for u in uyeler])), 3) for o in OZELLIK_ADLARI}
        profil[str(k)] = {
            "n": len(uyeler),
            "persona_dagilimi": dict(persona_dagilimi),
            "temerrut_orani": round(temerrut_orani, 4),
            "ozellik_ortalamalari": ozellik_ortalamalari,
        }
    return profil


def rapor_uret(veri_kaynagi="dekuple", seed=42, dosya_yolu=None):
    from aks_core.model.egitim import VERI_KAYNAKLARI, veri_hazirla

    kaynak = VERI_KAYNAKLARI[veri_kaynagi]
    islem_csv = paths.data(kaynak["islem"])
    etiket_csv = paths.data(kaynak["etiket"]) if kaynak["etiket"] else None
    musteriler = veri_hazirla(islem_csv, veri_kaynagi=veri_kaynagi, etiket_csv=etiket_csv)
    X = np.array([[m[o] for o in OZELLIK_ADLARI] for m in musteriler], dtype=float)

    model, silhouette, k = kumele(X, seed=seed)
    profil = profil_cikar(musteriler, model.labels_)

    rapor = {
        "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "veri_kaynagi": veri_kaynagi,
        "n_musteri": len(musteriler),
        "k": k,
        "silhouette_skoru": round(float(silhouette), 4),
        "bilinen_personalar": sorted(set(m["persona"] for m in musteriler)),
        "kume_profilleri": profil,
        "not": (
            "Denetimsiz keşif raporu — hiçbir skorlama/karar yoluna beslenmez. "
            "Silhouette skoru 1'e yakınsa kümeler iyi ayrışmış, 0'a yakınsa örtüşüyor demektir. "
            "Bu sentetik veri üzerinde 4 persona ETİKETİ zaten üretici tarafından gömülü olduğundan, "
            "kümelerin bunu 'yeniden keşfetmesi' beklenir; gerçek veride bu doğrulanmadı."
        ),
    }
    yol = Path(dosya_yolu) if dosya_yolu else paths.ARTIFACTS_DIR / RAPOR_ADI
    yol.parent.mkdir(parents=True, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    return rapor


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--veri-kaynagi", default="dekuple", choices=["dongusel", "dekuple"])
    a = p.parse_args()
    r = rapor_uret(veri_kaynagi=a.veri_kaynagi)
    print(f"k={r['k']}  silhouette={r['silhouette_skoru']}  n={r['n_musteri']}")
    for kume, prof in sorted(r["kume_profilleri"].items(), key=lambda kv: -kv[1]["n"]):
        print(f"  Küme {kume}: n={prof['n']:<5} temerrüt={prof['temerrut_orani']:.3f}  personalar={prof['persona_dagilimi']}")
