# 01-data — Veri Sözlüğü (Data Dictionary)

`product/01-data`'nın ürettiği veri kümelerinin kolon-bazlı tanımı. Tasarım gerekçesi ve tier modeli: [`../../../planning/data-architecture.md`](../../../planning/data-architecture.md) ve [`feature-schema.md`](../../../planning/feature-schema.md). Her kolon: **tip · tier · hipotez (neden var) · KVKK sınıfı · manipülasyon riski · durum**.

> **Veri minimizasyonu (mandat):** hipotezi olmayan hiçbir kolon toplanmaz. Bu sözlük, hipotez kaydının somut halidir (05-business #23 ile hizalı).

---

## 1. Üreticiler

| Betik | Ne üretir | Not |
|---|---|---|
| `generator/veri/uretici.py` | **Canlı (Sprint 2)** üretici — `sentetik_islemler.csv` | DÖNGÜSEL (bkz. architecture.md §5.1). Değiştirilmedi; OQ-37 sıralaması PO kararı. |
| `generator/veri/uretici_kapasite.py` | **Döngüsellik-kıran** üretici — `kapasite_islemler.csv` + `kapasite_etiketleri.csv` | Honest-fallback. Gizli kapasite persona'dan bağımsız; etiket yalnız kapasiteden. |
| `generator/dekuple_kanit.py` | Döngüselliğin kırıldığının sayısal kanıtı (rapor) | Gerçek `aks_core.ozellik.cikarim` ile özellik çıkarır. |
| `generator/dogrulama.py` | Şema + bütünlük + PII + döngüsellik-kapısı doğrulaması | CI kapısı (çıkış kodu 0/1). |

## 2. `kapasite_islemler.csv` — ham işlemler (Tier-0 + Tier-1 zenginleştirme)

Her satır bir işlem. `aks_core.ozellik.cikarim` ile geriye dönük uyumlu (ek kolonlar yok sayılır).

| Kolon | Tip | Tier | Hipotez / neden | KVKK | Manip. risk | Durum |
|---|---|---|---|---|---|---|
| `musteri_id` | int | T0 | Varlık anahtarı | financial | — | NOW |
| `persona` | enum(4) | T0 | Segment/sunum; **etiketi belirlemez** | financial | düşük | NOW |
| `tarih` | date | T0 | Zamansal sıralama; point-in-time | financial | düşük | NOW |
| `islem_tipi` | enum(`gelir`,`gider`) | T0 | Gelir/gider ayrımı | financial | düşük | NOW |
| `kategori` | string | T0 | Gelir kaynağı çeşitliliği + zorunlu/ihtiyari | financial | orta | NOW |
| `tutar` | decimal | T0 | Tüm nakit-akış özelliklerinin büyüklüğü (net) | financial | orta | NOW |
| `aciklama` | string | T0 | Kategori zenginleştirme | financial | düşük | NOW |
| `kanal` | enum(`havale`,`otomatik_odeme`,`kart`,`nakit`) | T0/T1 | Otomatik/tekrarlı ödeme = disiplin sinyali (araştırma: recurring detection) | financial | orta | NEXT |
| `karsi_taraf_tipi` | enum(`isveren`,`platform`,`birey`,`kurum`,`mikrokredi`) | T1 | Gig-platform geliri + gizli mikro-kredi tespiti (araştırma: undisclosed liabilities) | financial | düşük | NEXT |
| `brut_tutar` | decimal/"" | T1 | Brüt vs net (araştırma: upstream payroll) — gerçek kapasite | financial | düşük | NEXT |
| `zorunlu_mu` | enum(`0`,`1`,"") | T1 | Zorunlu vs ihtiyari harcama (araştırma: essential vs discretionary) | none | orta | NEXT |

## 3. `kapasite_etiketleri.csv` — hedef (özelliklerden AYRI)

**Anti-döngüsellik güvenlik duvarı.** Bu kolonlar hiçbir zaman model girdisi olamaz.

| Kolon | Tip | Tanım | Model girdisi? |
|---|---|---|---|
| `musteri_id` | int | Join anahtarı | — |
| `persona` | enum | Segment (analiz için) | evet (yalnız segment analizi) |
| `gizli_kapasite` | float | **Latent kapasite `c` ~ N(0,1)**, persona'dan bağımsız. Etiketi üreten tek büyüklük. | **ASLA** |
| `temerrut_olasiligi_gercek` | float | `sigmoid(b − 2.4·c + gürültü)` — oracle/Bayes-optimal olasılık | **ASLA** |
| `temerrut` | bool | `Bernoulli(temerrut_olasiligi_gercek)` — hedef etiket | evet (hedef `y`) |

## 4. Doğrulanmış kanıt (dekuple_kanit.py, 2000 müşteri)

| Ölçüm | Sonuç | Yorum |
|---|---|---|
| Persona temerrüt yayılımı | **0.015** | Etiket persona'dan ayrıştı (eski: persona etiketi belirliyordu) |
| Oracle (Bayes tavanı) | 0.909 | Gürültü nedeniyle < 1.0 (gerçekçi) |
| XGBoost (9 özellik) | 0.845 | Oracle'a yaklaşıyor, aşmıyor = gerçek kurtarım |
| LojistikRegresyon (9) | 0.863 | LR ≈ XGB → ensemble gereksiz (mandat: basit modeli seç) |
| En iyi tek özellik | 0.826 | Çoklu modelden 0.037 düşük → hiçbir özellik etiket DEĞİL |
| **Geleneksel/gelir kanalı** | **0.500** | Thin-file kör noktası (gelir kapasiteyi göremiyor) |
| **Davranışsal disiplin** | **0.844** | Gerçek sinyal — kaldıraç **+0.344 AUC** |

## 5. Dürüstlük notları (mandat: fazla iddia etme)

Bu üretici bir **prototip/honest-fallback**tir, üretim gerçeği değil. Bilinen kalibrasyon boşlukları:

1. **Gelir kanalı ~şans (0.50).** Gelir yükü kasıtlı zayıf (`0.05·c`) tutuldu; gerçekte geleneksel kanal *zayıf ama sıfır değil* olmalı. Gelir yükünü artırmak kaldıracı daha gerçekçi (ama daha küçük) yapar — bir kalibrasyon düğmesi.
2. **`gider_gelir_orani` tek başına güçlü (0.826).** `c` yükü yüksek (`0.13·c`, düşük gürültü). Gerçekte hiçbir tek davranışsal özellik bu kadar baskın olmamalı; çoklu-özellik kurtarımı tercih edilir. Gürültüyü artırmak bunu yumuşatır.
3. **Sentetik ≠ gerçek.** OQ-36 gerçek veri (Home Credit) sağlarsa bu üretici birim-test fikstürüne iner (planning/data-architecture.md §2, execution.md M4).

Bu boşluklar çekirdek sonucu (döngüsellik kırıldı) DEĞİŞTİRMEZ; yalnızca gerçekçilik ayarıdır.

## 6. Çalıştırma

```bash
pip install -e product/02-ai-agents            # aks_core (bir kez)
python product/01-data/generator/veri/uretici_kapasite.py   # veri üret
python product/01-data/generator/dogrulama.py               # doğrula (CI kapısı)
python product/01-data/generator/dekuple_kanit.py           # döngüsellik kanıtı
```
