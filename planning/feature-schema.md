# AKS — Feature & Column Schema

Concrete column-by-column schema for the data structure in [`data-architecture.md`](data-architecture.md). Every column lists: **type · tier · hypothesis (why it exists) · KVKK class · gaming risk · status**. Status legend: `NOW` (build/keep today) · `NEXT` (real-data path, OQ-36) · `GUARDED` (governance gate first) · `REJECTED` (documented, not collected).

Column names are Turkish to match the existing `aks_core` codebase. Existing columns are marked **(mevcut)**.

---

## 1. Raw transaction schema (`islemler`)

The ingest-level record. One row per transaction. Source of every T0 feature.

| Column | Type | Tier | Hypothesis / why | KVKK | Status |
|---|---|---|---|---|---|
| `musteri_id` | int/uuid | T0 | Entity key | financial | NOW **(mevcut)** |
| `tarih` | date | T0 | Temporal ordering; point-in-time correctness | financial | NOW **(mevcut)** |
| `islem_tipi` | enum(`gelir`,`gider`) | T0 | Income vs expense split | financial | NOW **(mevcut)** |
| `kategori` | string | T0 | Category → essential/discretionary + income-source diversity | financial | NOW **(mevcut)** |
| `tutar` | decimal | T0 | Magnitude of every cash-flow feature | financial | NOW **(mevcut)** |
| `aciklama` | string | T0 | Category enrichment (NLP-light) | financial | NOW **(mevcut)** |
| `kanal` | enum(`havale`,`otomatik_odeme`,`karti`,`nakit`,…) | T0 | Distinguishes recurring/automated from ad-hoc → discipline signal | financial | NEXT |
| `karsi_taraf_tipi` | enum(`isveren`,`platform`,`birey`,`kurum`,`mikrokredi`) | T1 | Detects gig-platform income and undisclosed micro-lender repayments | financial | NEXT |
| `para_birimi` | enum | T0 | Multi-currency normalization | none | NEXT |
| `kvkk_sinifi` / `yasal_dayanak` / `riza_id` / `kaynak` / `alindigi_zaman` | governance | all | See data-architecture.md §4 | — | NOW |

## 2. Engineered feature schema (`feature_store`)

One versioned row per `(musteri_id, feature_version)`. **All features are point-in-time (computed strictly before the outcome window).** No feature here may be derived from the outcome — this is the anti-circularity firewall.

### 2.1 T0 — current 9 features (keep; already extracted by `aks_core/ozellik/cikarim.py`)

| Column | Type | Hypothesis | Gaming risk | Status |
|---|---|---|---|---|
| `toplam_gelir_hacmi` | float | Capacity: total income throughput | med (structuring) | NOW **(mevcut)** |
| `toplam_gider_hacmi` | float | Spending scale vs income | low | NOW **(mevcut)** |
| `gelir_islem_sayisi` | int | Income frequency/regularity proxy | med | NOW **(mevcut)** |
| `gelir_kaynagi_sayisi` | int | Income diversification (resilience) | med | NOW **(mevcut)** |
| `gelir_duzenliligi` | float 0–1 | Character: predictable income = discipline | **high** (RQ-3) | NOW **(mevcut)** |
| `gider_gelir_orani` | float | Affordability headroom | med | NOW **(mevcut)** |
| `bakiye_trendi` | float | Savings tendency / trajectory | med | NOW **(mevcut)** |
| `fatura_odeme_duzeni` | float 0–1 | Character: on-time bill payment | **high** (RQ-3) | NOW **(mevcut)** |
| `hesap_hareket_yogunlugu` | float | Account liveness | med | NOW **(mevcut)** |

> **Note:** the four features `gider_gelir_orani, bakiye_trendi, gelir_duzenliligi, fatura_odeme_duzeni` are the ones the *synthetic* label was leaking from (architecture.md §5.1). They are legitimate features — the fix is at the **label** side (§3), not deleting them. Their `high` gaming risk is separately flagged for the RQ-3 adversarial review.

### 2.2 T1 — open-banking cash-flow additions (the research brief's strongest layer)

| Column | Type | Hypothesis | KVKK | Gaming risk | Status |
|---|---|---|---|---|---|
| `brut_net_gelir_orani` | float | Gross vs net income (upstream payroll) reveals true capacity vs downstream lag | financial | low | NEXT |
| `gelir_oynakligi` | float | Income volatility/CoV — underwrites non-linear gig income | financial | med | NEXT |
| `gelir_trend_egimi` | float | Income trajectory (rising/falling) over the window | financial | med | NEXT |
| `zorunlu_harcama_orani` | float 0–1 | Essential (rent/utilities) share of outflow | financial | low | NEXT |
| `ihtiyari_harcama_orani` | float 0–1 | Discretionary share — affordability under inflation | financial | low | NEXT |
| `overdraft_sikligi` | int | Overdraft events / window — distress signal | financial | low | NEXT |
| `overdraft_suresi_gun` | float | Days in overdraft — severity | financial | low | NEXT |
| `gizli_kredi_odemeleri` | float | Payments routed to 3rd-party/micro-lenders (undisclosed liabilities) | financial | low | NEXT |
| `nakit_akis_tamponu_gun` | float | Days of buffer at current burn — resilience | financial | low | NEXT |

### 2.3 T2 — behavioral / engagement (GUARDED, mostly monitoring-only)

| Column | Type | Intended use | KVKK | Gaming risk | Status |
|---|---|---|---|---|---|
| `zorluk_sayfasi_erisimi` | bool/int | **Pre-delinquency early-warning (monitoring only, NOT an origination feature)** | sensitive | high | GUARDED |
| `uygulama_etkilesim_skoru` | float | Engagement proxy | sensitive | high | GUARDED (DPIA) |
| `basvuru_tereddut_sinyali` | float | Clickstream hesitation → fraud triage | sensitive | high | GUARDED (DPIA) |

### 2.4 T3 — alternative proxies (GUARDED, fairness-gated)

| Column | Type | Intended use | KVKK | Status |
|---|---|---|---|---|
| `egitim_kurumu_getiri_proxy` | float | Institution value-added → future capacity (student segment) | sensitive-adjacent | GUARDED (fair-lending sign-off) |
| `akademik_performans_ayarli` | float | Difficulty-adjusted GPA proxy | sensitive-adjacent | GUARDED (fair-lending sign-off) |
| `sinir_otesi_kredi_pasaportu` | struct | Immigrant home-country history (Nova-Credit style) | financial | FUTURE |

### 2.5 REJECTED (documented, not collected — data minimization)

| Column family | Why rejected |
|---|---|
| `psikometrik_*` (gamified character scores, risk-appetite, integrity markers) | Weak evidence, gameable, KVKK *sensitive* character profiling, fair-lending exposure |
| `cihaz_parmak_izi_*` (dense smartphone metadata) | Unvalidated vendor uplift, consent-heavy, leakage/gaming magnet |

## 3. Target / label schema (`etiketler`) — separated from features by construction

The anti-circularity firewall. **These columns are never fed back as model inputs.**

| Column | Type | Definition | Status |
|---|---|---|---|
| `temerrut_gerceklesen` | bool | **Realized** default from a real outcome window (OQ-36) OR a decoupled-latent-capacity generator. Never a function of §2 features. | NEXT (blocks modeling — M4) |
| `outcome_penceresi` | date range | The forward window the label is observed over (out-of-time discipline) | NEXT |
| `pd_davranissal` | float 0–1 | Calibrated behavioral PD from AKS | NEXT |
| `pd_geleneksel_bant` | float 0–1 | Traditional-band-implied PD from the bank's classic score | NEXT |
| `pd_fark` | float | **PD-gap** = `pd_geleneksel_bant − pd_davranissal` (the core product signal; >0 = hidden capacity) | NEXT |
| `kapasite_sinyali` | float | Supplementary capacity signal surfaced to the bank | NEXT |
| `calibration_ece_segment` | float | Per-segment ECE at scoring time (calibration guarantee) | NEXT |
| `calibration_version` | string | Which calibration map produced these PDs | NEXT |

## 4. Persistence / audit schema (extends current Django models)

Current models (`product/04-backend/audit/models.py`) extended; the classic score stays **read-only**.

| Model | Current fields | Added fields |
|---|---|---|
| `Customer` | `external_id`, `persona` **(mevcut)** | `riza_durumu` (consent state), `veri_kaynaklari` (permitted sources) |
| `Assessment` | `klasik_skor`, `aks_skor`, `risk_seviyesi`, `karar`, `onerilen_limit`, `ozellikler`, `kaynak` **(mevcut)** | `pd_davranissal`, `pd_geleneksel_bant`, `pd_fark`, `kapasite_sinyali`, `feature_version`, `calibration_version` |
| `AuditLog` | `klasik_skor` (UNCHANGED), `aks_skor`, `politika_notu`, `ajanlar`, `kaynak`, `created_at` **(mevcut)** | `karar_kaynagi` (`otomatik`/`insan`), `itiraz_durumu`, `yasal_dayanak`, `riza_id` |
| **`FeatureStore`** *(new)* | — | `musteri_id`, `feature_version`, all §2 columns, `hesaplandigi_zaman` |
| **`Consent`** *(new)* | — | `riza_id`, `musteri_id`, `kapsam` (scope), `verilis_zamani`, `geri_cekilme_zamani`, `yasal_dayanak` |
| **`DataProvenance`** *(new)* | — | per-column source, ingest time, retention deadline (KVKK erasure) |

## 5. Schema invariants (enforced in the pipeline, see `data-pipeline-steps.md`)

1. `klasik_skor` is written **only** by ingest from the bank input — no agent/service writes it.
2. No `feature_store` column is a function of any `etiketler` column (deny-list check).
3. Every populated `acik_riza` column has a non-null `riza_id` with active consent.
4. Every feature row's `hesaplandigi_zaman` precedes its label's `outcome_penceresi` start (point-in-time).
5. Model may not be selected/tuned until `temerrut_gerceklesen` is non-circular (M4 gate).
