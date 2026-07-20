"""
Temerrüt (Default) Etiketleme
-----------------------------
Denetimli öğrenme için ground-truth üretir.

Kritik tasarım kararı: gizli (latent) temerrüt riski, kişinin PERSONA'sından
ya da GELİR HACMİNDEN değil, DAVRANIŞSAL DİSİPLİNDEN türetilir
(gider/gelir oranı, bakiye trendi, gelir düzenliliği, fatura ödeme düzeni).

Bu, projenin temel tezini kodlar: düşük gelirli görünen ama disiplinli bir
kişi GERÇEKTE düşük risklidir. Klasik skor bunu göremez (gelire bakar),
davranışsal model görebilir. Böylece iki yaklaşımın temerrüt tahmin gücü
adil şekilde karşılaştırılabilir.

Intercept (taban), verilen hedef temerrüt oranına otomatik kalibre edilir;
kişiye özel gürültü, gözlenemeyen faktörleri temsil eder.

Not (D2/E6 düzeltmesi): rastgelelik artık modül/global `random` durumunu
DEĞİŞTİRMEZ. Eskiden `random.seed(7)` hem import anında hem her çağrıda
global RNG'yi sıfırlıyordu — bu, aynı süreç içindeki başka hiçbir kodun
(ör. Django, testler) `random` modülünü güvenle kullanamayacağı, yan etkili
bir tasarımdı ve resampling/bootstrap belirsizliğini de gizliyordu. Şimdi
yerel bir `random.Random(seed)` örneği kullanılıyor; varsayılan seed=7,
demo tutarlılığını korur ama global durumu kirletmez ve gerektiğinde farklı
seed'lerle yeniden örnekleme (uncertainty) çalışmalarına izin verir.
"""
import math, random


def _sigmoid(x): return 1 / (1 + math.exp(-x))


def _kismi_logit(oz):
    """Intercept hariç, davranışsal risk katkısı (persona/hacim yok)."""
    z = 0.0
    z += 4.0 * (oz["gider_gelir_orani"] - 0.85)              # gider disiplini (ana etken)
    z += -0.7 * max(min(oz["bakiye_trendi"], 3), -3)         # bakiye trendi
    z += -1.2 * oz["gelir_duzenliligi"]                      # gelir düzenliliği
    z += -0.7 * oz["fatura_odeme_duzeni"]                    # fatura ödeme düzeni
    return z


def _intercept_kalibre(kismi_logitler, hedef_oran, tol=1e-4):
    """mean(sigmoid(b + z)) = hedef_oran olacak b'yi ikili aramayla bulur."""
    lo, hi = -12.0, 12.0
    for _ in range(60):
        b = (lo + hi) / 2
        ort = sum(_sigmoid(b + z) for z in kismi_logitler) / len(kismi_logitler)
        if abs(ort - hedef_oran) < tol:
            break
        if ort < hedef_oran:
            lo = b
        else:
            hi = b
    return b


def etiketle(musteri_ozellikleri, hedef_temerrut_orani=0.18, seed=7):
    """Yerel RNG (`random.Random(seed)`) kullanır — global `random` durumunu değiştirmez."""
    rng = random.Random(seed)
    z = [_kismi_logit(m) for m in musteri_ozellikleri]
    b = _intercept_kalibre(z, hedef_temerrut_orani)
    for m, zi in zip(musteri_ozellikleri, z):
        gurultu = rng.gauss(0, 0.9)  # kişiye özel gözlenemeyen faktörler
        p = _sigmoid(b + zi + gurultu)
        m["temerrut_olasiligi_gercek"] = round(p, 4)
        m["temerrut"] = 1 if rng.random() < p else 0
    return musteri_ozellikleri
