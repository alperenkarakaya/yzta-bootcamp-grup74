# AKS / Early Phase Working Package — Master Index
**This is the master file for the entire repository. Read it first in any future session.** It covers the product itself (problem, solution, team, results, sprint history) *and* the consulting-style Early Phase planning package built on top of it. Technical/engineering detail lives in [`/product/PRODUCT_TECH_README.md`](../product/PRODUCT_TECH_README.md); this file is the narrative and program-management home.

> **Read [`RESEARCH_STRATEGY.md`](RESEARCH_STRATEGY.md) immediately after this file, before trusting any AUC/business/fairness number cited below.** The project now operates under a statistical-rigor-first mandate (venture-fundable product, not bootcamp demo); a code-grounded audit found the current headline model results are measured circularly. §6 below carries the caveat inline, but the full finding, the ablation evidence, and three open decisions (OQ-36…38) live there.

**Note on language:** the planning package (source doc, artifacts, IDs) is English throughout. The product narrative, team, and sprint history below are kept in the team's original **Turkish**, as authored by YZTA Bootcamp Grup 74 — this is preserved for authenticity rather than translated.

---

## Table of contents

- [Part A — The Product (AKS)](#part-a--the-product-aks)
  1. [Repository Map](#1-repository-map)
  2. [Ürün Özeti (Problem & Çözüm)](#2-ürün-özeti-problem--çözüm)
  3. [Hedef Kitle / Personalar](#3-hedef-kitle--personalar)
  4. [Ekip](#4-ekip)
  5. [Mimari ve Teknoloji Özeti](#5-mimari-ve-teknoloji-özeti)
  6. [Model, İş Etkisi ve Adalet Sonuçları](#6-model-i̇ş-etkisi-ve-adalet-sonuçları)
  7. [Sprint Geçmişi](#7-sprint-geçmişi)
  8. [Etik ve Regülasyon Notu](#8-etik-ve-regülasyon-notu)
- [Part B — The Early Phase Planning Package](#part-b--the-early-phase-planning-package)
  9. [What This Package Is](#9-what-this-package-is)
  10. [Hard Constraints](#10-hard-constraints)
  11. [Package Structure (50 Files)](#11-package-structure-50-files)
  12. [Execution Plan at a Glance](#12-execution-plan-at-a-glance)
  13. [Bootcamp Adaptation Layer](#13-bootcamp-adaptation-layer)
  14. [Current Status](#14-current-status)
  15. [Self-Review Record](#15-self-review-record)
  16. [Rules for Future Sessions](#16-rules-for-future-sessions)

---

# Part A — The Product (AKS)

## 1. Repository Map

The repo root has no single README; orientation starts here. Three top-level things:

| Location | What it is | Read this for |
|---|---|---|
| **`/planning/README.md`** (this file) | Master index: product narrative + planning package | Everything — start here |
| **`/planning/RESEARCH_STRATEGY.md`** | **Operating mandate + critical statistical assessment of the current system.** Supersedes "bootcamp demo" framing wherever they conflict. | The quality bar every model/AI/eng decision is now held to; the circularity finding; open decisions OQ-36…38 |
| **`/planning/`** | Early Phase consulting-style package (Part B below) + bootcamp adaptation + `ROADMAP.md` | Problem framing, hypotheses, governance, sprint/task roadmap |
| **`/TECHSTACK.md`** | Whole-project technology decisions & target architecture | Why React/Django/Supabase/Redis were chosen |
| **`/product/`** | The actual AKS build, split into 5 workstream sections (`01-data` … `05-business`) | The code |
| **`/product/PRODUCT_TECH_README.md`** | Pure technical reference: architecture, setup, API, data model, tests, deploy | Running/building the product |
| **`/planning/early-phase-plan-credit-offer-optimization.md`** | Source of truth for the planning package — never edited | Original consulting brief this package was built from |

**One-sentence orientation:** `/planning` tells you *why and in what order* to build; `/product` *is* the build; `TECHSTACK.md` tells you *what technology* it's built with; this file connects all three.

## 2. Ürün Özeti (Problem & Çözüm)

Geleneksel kredi/limit değerlendirme sistemleri büyük ölçüde **resmi gelir beyanına** dayanır. Bu durum, hesap hareketleri açısından yüksek hacimli, düzenli ve disiplinli olmasına rağmen resmi olarak "öğrenci", "stajyer" ya da "freelancer" görünen kişilerin gerçek ödeme kapasitelerinin çok altında kredi/limit almasına yol açıyor.

Odak noktamız özellikle küçük çaplı krediler: banka işlem hacmi yüksek olduğu halde gelir seviyesi düşük görünen ya da stajyer/öğrenci profilindeki kişiler çok düşük kredi limitleri alıyor. Aynı sorun büyük çaplı kredilerde de var, ama asıl kayıp burada birikiyor. Banka açısından bu, **görünmeyen ama yakalanabilir bir getiri kaybı**: düşük riskli ama "düşük skorlu" görünen büyük bir müşteri segmenti ya hiç kredilenemiyor ya da alternatif (BNPL, P2P, enformel) kaynaklara kayıyor.

Amacımız bu arayı kapatmak — hem müşterinin gerçek kapasitesine uygun limit alması, hem de bankanın kaçırdığı getiriyi geri kazanması. İki taraf için de kazançlı bir denge.

**Çözüm.** Hesap hareketlerinden (transaction) çıkarılan davranışsal özelliklerle (gelir düzenliliği, gelir kaynağı çeşitliliği, gider disiplini, tasarruf trendi, fatura ödeme düzeni, hesap aktivite yoğunluğu) resmi gelirden bağımsız bir **Alternatif Kapasite Skoru (AKS)** üretiyoruz.

> **Tez ve sınır (boundary) — projenin bütün mimarisini şekillendiren tek cümle:**
> **AKS, bankanın klasik skorunu/segmentini asla ezmez veya değiştirmez — yalnızca tamamlar.** Banka mevcut risk modelini ve nihai kararını korurken, AKS "thin-file" (resmi veri açısından zayıf dosyalı) ama davranışsal olarak güçlü müşterileri ayırt eden **ek bir sinyal** sağlar.

Bu sınır kâğıt üzerinde bir taahhüt değil, koddaki bir gerçektir: her skorlama, bankanın klasik skorunu **değiştirilmeden** kaydeden değiştirilemez bir denetim satırı (`AuditLog`) üretir. Bu ilke, Part B'deki (aşağıda) erken-faz planlama paketinin §4 sınırıyla ve `ROADMAP.md`'deki "hard boundary" değişmeziyle birebir örtüşür — proje, gerçek bir danışmanlık brief'inin disipliniyle başlayıp bootcamp'e uyarlandı (bkz. [§13](#13-bootcamp-adaptation-layer)).

## 3. Hedef Kitle / Personalar

Sentetik veri üretici (`product/01-data/generator/veri/uretici.py`) dört davranışsal personayı simüle eder:

| Persona | Tanım |
|---|---|
| `ogrenci_yuksek_hacim` | Resmi geliri zayıf, ama burs + part-time + aile desteği ile yüksek hacimli ve düzenli hareket eden öğrenci — **asıl odak grubumuz** |
| `stajyer_degisken_gelir` | Stajyer/freelancer, toplamda yüksek ama zaman içinde düzensiz gelir |
| `klasik_maasli` | Sabit, resmi aylık maaşlı çalışan (kontrol/baseline grubu) |
| `dusuk_hacim_riskli` | Gerçekten düşük kapasiteli, düzensiz hareketli kişi (**negatif kontrol** — modelin yanlışlıkla yüksek skor vermemesi gerekiyor) |

Bu dört persona hem sentetik veri üretiminde hem de aşağıdaki §6 sonuçlarının yorumlanmasında (ör. "kurtarılan" segmentin %92'si öğrenci/stajyer) referans noktasıdır.

## 4. Ekip

| Rol | Kişi |
|---|---|
| Product Owner | Alperen Karakaya |
| Scrum Master | Ahmet Özdoğan |
| Developer | Zeynep Salkaya |
| Developer | Havva Balta |
| Developer | Begüm Bakan |

## 5. Mimari ve Teknoloji Özeti

Tam mimari diyagram, veri akışı, API referansı ve kurulum adımları için: **[`/product/PRODUCT_TECH_README.md`](../product/PRODUCT_TECH_README.md)**. Teknoloji kararlarının gerekçesi için: **[`/TECHSTACK.md`](../TECHSTACK.md)**.

Kısa özet:

```
React (Vite+TS)  →  Django + DRF API  →  aks_core (3-agent orkestrasyon, XGBoost, SHAP)  →  Supabase (Postgres, denetim izi) + Upstash Redis (cache)
```

Ürün, `ROADMAP.md`'deki 5 iş akışını (BWS1–5) yansıtan 5 bölüme ayrılmıştır (`product/01-data` … `product/05-business`). Backend Sprint 2'de FastAPI iken Sprint 3'te **Django + DRF**'e, ön yüz vanilla-JS dashboard'dan **React + TypeScript**'e taşındı; tüm uç noktalar bire bir parite ile doğrulandı (bkz. §7 Sprint 3).

## 6. Model, İş Etkisi ve Adalet Sonuçları

**9 davranışsal özellik:** gelir hacmi, gider hacmi, gelir işlem sayısı, gelir kaynağı çeşitliliği, gelir düzenliliği, gider/gelir oranı, bakiye trendi, fatura ödeme düzeni, hesap hareket yoğunluğu. Temerrüt (default) etiketi kişinin *davranışsal disiplininden* türetilir (persona veya gelir hacminden değil) — bu, projenin tezini doğrudan kodlar: düşük gelirli görünen disiplinli kişi gerçekte düşük risklidir.

**Model karşılaştırması:**

| Model | ROC-AUC | PR-AUC (AP) |
|---|---|---|
| **XGBoost** (seçilen) | **0.8294** | 0.6871 |
| LightGBM | 0.8233 | 0.6837 |
| Klasik skor (baseline) | 0.7288 | 0.5687 |

Davranışsal model klasik skoru **+0.10 AUC** ile geçiyor.

**İş etkisi (bankaya değer).** Klasik skorun "prime" eşiğinin altında bıraktığı kredibl kişilerden **%90'ı (973 kişi) model tarafından doğru şekilde kurtarılıyor** — %92'si tam hedef kitle olan öğrenci ve stajyer. Risk kontrolü korunuyor (yanlış onay oranı düşük). Bu sonuç, Django'ya geçiş sonrası (Sprint 3) yeniden çalıştırılıp **birebir doğrulandı**: `/api/portfoy` uç noktası aynı 973/1084 rakamını döndürüyor — mimari değişikliğin iş sonucunu bozmadığının kanıtı.

**Adalet/önyargı analizi (sorumlu YZ).** Equal-opportunity metriği: kredibl kişilerin onaylanma oranı gruplar arası karşılaştırılır. Sonuç çarpıcı — klasik skorda kredibl bir öğrencinin onaylanma oranı **%0.4** iken AKS'de **%97.8**; adalet boşluğu **1.00'den 0.39'a** iner.

Görsel: `product/05-business/docs/sprints/sprint2/model_sonuclari.png`. Teknik detay ve metrik dosyası: `PRODUCT_TECH_README.md` §9–10.

> ⚠️ **Metodolojik uyarı — bu bölümdeki tüm sayılar (AUC, %90 kurtarma, adalet boşluğu) aynı döngüsel ölçüm sorununu paylaşır.** `RESEARCH_STRATEGY.md`'de kod-temelli tespit + ablasyon testiyle doğrulandı: etiket, modelin gördüğü özelliklerden üretiliyor (XGBoost ile lojistik regresyon farkı 0.0004 AUC — anlamsız), ve döngüsellik yalnızca 4 "nedensel" özellikle sınırlı değil, sentetik üreticinin persona-koşullu tasarımına yapısal olarak gömülü (5 "nedensel olmayan" özellik bile tek başına 0.82 AUC veriyor). **Bu rakamlar boru hattının uçtan uca çalıştığını doğrular; "davranışsal veri gizli ödeme kapasitesini ortaya çıkarır" tezini henüz doğrulamaz.** Düzeltme planı, gerçek veri seti ihtiyacı (OQ-36) ve karar noktaları (OQ-37, OQ-38) için: [`RESEARCH_STRATEGY.md`](RESEARCH_STRATEGY.md).

## 7. Sprint Geçmişi

### Product Backlog

| # | User Story | Sprint | Durum |
|---|---|---|---|
| 1 | Sentetik işlem verisi üretici | 1 | ✅ |
| 2 | Özellik mühendisliği + baseline skor | 1 | ✅ |
| 3 | Persona bazlı doğrulama / kalibrasyon | 2 | ✅ |
| 4 | XGBoost/LightGBM ile denetimli model | 2 | ✅ |
| 5 | Üç-agent mimarisi (veri / skor / danışman) | 2 | ✅ |
| 6 | Açıklanabilirlik katmanı (SHAP) | 2 | ✅ |
| 7 | API `/skorla` `/aciklama` `/simulasyon` | 2 | ✅ |
| 8 | Kullanıcı dashboard'u | 2–3 | ✅ (React'e taşınıyor) |
| 9 | Banka portföy/getiri simülasyon görünümü | 2 | ✅ |
| 10 | Deploy + demo video | 3 | ⏳ |
| 11 | Django + React'e mimari geçiş, Supabase/Redis, denetim izi | 3 | ✅ |

### Sprint 1 — Veri temeli ve kavram kanıtı

**Sprint Notu:** Hedef, projenin veri temelini ve kavram kanıtını (proof of concept) kurmaktı: sentetik banka işlem verisi üretmek, davranışsal özellikleri çıkarmak ve resmi gelirden bağımsız bir baseline alternatif skor üretip persona'lar üzerinde doğrulamak.

**Erken bulgu** — 500 sentetik müşteri üzerinde:

| Persona | Ort. Klasik Skor | Ort. Alternatif Skor |
|---|---|---|
| klasik_maasli | 840.8 | 462.3 |
| ogrenci_yuksek_hacim | 636.1 | 440.6 |
| stajyer_degisken_gelir | 631.9 | 345.5 |
| dusuk_hacim_riskli | 504.2 | 300.0 |

Klasik skorlamada `klasik_maasli` ile `ogrenci_yuksek_hacim` arasındaki fark **~205 puan**. Alternatif skorlamada bu fark **~22 puana** düşüyor — davranışsal model, resmi gelir farkının yarattığı dengesizliğin büyük kısmını kapatıyor. `dusuk_hacim_riskli` grubu beklendiği gibi düşük kaldı (negatif kontrol başarılı).

**Sprint Review kararları:** sentetik veri üreticisi ve kural-tabanlı skorlama motoru çalışır durumda; sonraki sprint'e taşınanlar: XGBoost/LightGBM'e geçiş ve açıklanabilirlik katmanı; gider/gelir oranı kalibrasyonu ihtiyacı not edildi. Katılımcılar: Alperen Karakaya, Ahmet Özdoğan, Zeynep Salkaya, Havva Balta, Begüm Bakan.

**Sprint Retrospective:** takım içi görev dağılımı gözden geçirilecek; tahmin puanları yeniden değerlendirilecek; unit test efor/saati artırılmalı.

**Kanıtlar:** `product/05-business/docs/sprints/sprint1/board_sprint1.png`, `urun_durumu_sprint1.png`, `daily_scrum_notlari.md`, Slack ekran görüntüleri (`slack_01…04`).

### Sprint 2 — Zeka katmanı

*(6–19 Temmuz)* Kural-tabanlı skordan denetimli ML modeline geçiş, açıklanabilirlik, üç-agent mimarisi ve API.

**Öne çıkanlar:**
1. **Veri düzeltmesi** — Sprint 1'deki gider dağıtım hatası düzeltildi (`gider_gelir_orani` artık personalar arası ayırt edici: öğrenci ~0.72, riskli ~1.22).
2. **Denetimli etiketleme** — temerrüt etiketi davranışsal disiplinden türetildi.
3. **ML modeli** — XGBoost/LightGBM, klasik skoru +0.10 AUC ile geçti (§6).
4. **SHAP açıklanabilirlik** eklendi.
5. **Üç-agent mimarisi + orkestrasyon + hafıza** kuruldu: `VeriAgent` → `SkorlamaAgent` → `DanismanAgent`, `Orkestrator` tarafından koordine edilir.
6. **FastAPI backend** (`/skorla`, `/aciklama`, `/simulasyon`, `/gecmis/{id}`).
7. **Web dashboard** — iki görünümlü arayüz: müşteri görünümü (klasik vs AKS karşılaştırması, SHAP faktörleri, danışman önerileri, "ne olurdu?" simülasyonu) ve banka görünümü (kurtarılan segment, kurtarma oranı, illüstratif getiri).
8. **22 birim/entegrasyon testi** yazıldı.
9. **Deploy hazırlığı** — Docker + render.yaml.
10. **Kredi limit önerisi** — aylık net nakit akışı + risk seviyesine göre önerilen limit (TL).
11. **Adalet/önyargı analizi** eklendi (§6).
12. **CSV ile kendi verini skorla** — kullanıcı hesap dökümü yükleyip anında skor alabiliyor.
13. **Banka paneli arayüzü + AKS Asistanı** — LLM (Gemini) veya kural-tabanlı yedek ile soru-cevap; `GEMINI_API_KEY` tanımlı değilse demo yine çalışır.

Görsel: `product/05-business/docs/sprints/sprint2/model_sonuclari.png`.

### Sprint 3 — Mimari genişleme ve bootcamp uyarlaması

Proje, YZTA Bootcamp kapsamında bir **capstone** olarak yeniden çerçevelendi — jüri agentik AI, yenilikçi teknoloji ve çalışan bir ürünü ödüllendiriyor (bkz. [§13](#13-bootcamp-adaptation-layer)). Bu doğrultuda paralel iki iş yapıldı:

**(a) Planlama:** gerçek bir bankayla değil bootcamp'te çalışıldığı netleştirildi; `bootcamp-adaptation-review.md` (KEEP/ADAPT/LIFT/RISK), 5 iş akışı tanımı (`07-bootcamp-workstreams/`), ve tüm görevleri story point'lerle sprint'lere yerleştiren `ROADMAP.md` üretildi (bkz. Part B).

**(b) Build:**
- Proje **5 iş akışı bölümüne** ayrıldı (`product/01-data` … `05-business`), ROADMAP'teki BWS1–5 ile birebir eşleşecek şekilde.
- ML/agent çekirdeği bağımsız, kurulabilir **`aks_core`** paketine çıkarıldı (`from src.*` → `from aks_core.*`).
- Backend **FastAPI → Django + DRF**'e taşındı; **tüm 11 uç nokta bire bir parite ile doğrulandı** — portföy sonucu Sprint 2 ile birebir örtüşüyor (973/1084 kurtarılan, §6).
- **Değiştirilemez denetim izi** (`audit/` Django app'i: `Customer`, `Assessment`, `AuditLog`) eklendi — "AKS bankayı ezmez" tezini operasyonel hale getirdi; Django admin'de salt-okunur.
- **React + Vite + TS** ön yüz iskeleti kuruldu, API'ye bağlandı, Google Stitch tasarımını bekliyor (`OQ-34`).
- **Supabase (Postgres) + Upstash Redis** entegrasyonu koda hazır — env tanımlı değilse SQLite/bellek cache'e zarifçe düşer, demo her koşulda çalışır.
- Tüm mimari kararlar `/TECHSTACK.md`'de belgelendi.
- **Bilinen boşluk:** eski 22 testlik pytest paketi hâlâ `from src.*`/FastAPI'ye bağımlı, Django'ya taşınmadı — `PRODUCT_TECH_README.md` §11'de açıkça işaretlendi, ROADMAP `BWS5-T8/T9`'a bağlandı.

## 8. Etik ve Regülasyon Notu

- Bu repo gerçek banka verisi içermez; tüm veriler sentetiktir.
- Üretimde KVKK kapsamında açık rıza ve veri minimizasyonu gerekir (bkz. Part B §10 data minimization rule — aynı disiplin bootcamp'e de taşındı).
- Model, ayrımcı (discriminatory) sinyalleri (yaş, cinsiyet vb.) doğrudan kullanmaz; yalnızca davranışsal/finansal özelliklere dayanır.
- AKS bankanın klasik skorunu/segmentini **asla otomatik olarak ezmez veya değiştirmez** — bkz. §2 tez. Bu ilke, aşağıdaki Part B'deki düzenleyici çerçeveyle (fair lending, açıklanabilirlik, EU AI Act yüksek-riskli sınıflandırması) uyumludur; ayrıntı için `05-risk-and-compliance/` ve `bootcamp-adaptation-review.md` §2 (ADAPT A3 — regulatory-awareness note, gerçek hukuki görüş değildir).

---

# Part B — The Early Phase Planning Package

*(Original consulting-style planning package, built before the bootcamp context was confirmed. Still the methodology backbone: problem decomposition, hypotheses, governance discipline, and now the sprint/task roadmap for the actual build. See [§13](#13-bootcamp-adaptation-layer) for how it was adapted.)*

## 9. What This Package Is

An execution-ready **Phase 1 (Early Phase) working package** for the "Intelligent Offer Optimization Bridge Layer for Credit Segmentation" consulting engagement, built entirely from the source of truth:

> **`early-phase-plan-credit-offer-optimization.md`** (this folder)

Every artifact traces to that document's IDs: sub-problems **P1–P3**, assumptions **A1–A10**, hypotheses **H1–H14**, opportunities **O1–O8**, deliverables **D1–D11**, exit criteria **E1–E10**, §6 risks, §7 data inventory, §8 KPIs, Appendices A/B. The source document wins any conflict; ambiguities go to the open-questions log (`00-program/open-questions.md`), never resolved by guessing.

The problem the *source document* frames abstractly ("customers get lower credit segments than they deserve") is, concretely, the AKS thesis in Part A: officially thin-file customers (students, interns) are under-classified by a system that only reads formal income. The planning package's P1/P2/P3 decomposition, hypotheses, and governance discipline are the methodology AKS was built to satisfy.

## 10. Hard Constraints

Binding on all future work in the *planning package itself* (not the product build, which lifted several of these — see §13):

1. **No solution design, no algorithms, no ML model recommendations, no product code, no architecture.** Phase 1 is planning, discovery, templates, validation protocols, and project-management artifacts only (source scope-discipline line, quoted in `00-program/charter.md` §2).
2. **The bridge-layer boundaries are bright lines** (source §4, verbatim): the layer shall never re-score customers, override segments automatically, adjust the engine's inputs, or auto-approve above-policy limits. *(This is the exact rule AKS's audit trail operationalizes — Part A §2.)*
3. **"No-go is a valid outcome"** (source §10) is preserved in every decision-related artifact: charter, workplan, D5, D11, E10 checklist, steering pack.
4. **Data minimization** (source §7 rule): no data item is collected without a stated hypothesis.
5. **Do not rename source IDs.** New IDs exist only where the source assigned none, declared conventions: data items **M1–M9 / U1–U8 / OPT1–OPT5**; risks **R-BUS-xx / R-AI-xx / R-REG-xx / R-OPS-xx / R-DAT-xx**; open questions **OQ-01…OQ-35** (OQ-01–10 = Appendix B verbatim); milestones **MS1–MS6**; workstreams **WS1–WS6** (source) / **BWS1–BWS5** (bootcamp, §13).

## 11. Package Structure (50 Files)

```
credit-calc/
├── early-phase-plan-credit-offer-optimization.md   ← SOURCE OF TRUTH (do not edit)
├── TECHSTACK.md                 ← whole-project technology plan (Part A §5)
├── product/                     ← the actual build (Part A) — see PRODUCT_TECH_README.md
├── planning/
│   ├── README.md                ← this file: master index (product + package)
│   ├── CLAUDE.md                ← session pointer for Claude Code
│   ├── TRACEABILITY.md          ← A/H/O/D/E/data → artifact matrix + orphan/defect log + BWS map
│   ├── ROADMAP.md               ← master delivery plan: 83 tasks, story points, sprints S0–S4
│   ├── bootcamp-adaptation-review.md   ← KEEP/ADAPT/LIFT/RISK (§13)
│   ├── 00-program/
│   │   ├── charter.md               ← objectives, scope, quoted boundaries, governance, decision rights
│   │   ├── workplan.md              ← weeks 1–10 (Appendix A expanded), critical path → E1–E10
│   │   ├── raci.md                  ← D1–D11 × all §3 stakeholders (+Finance/IT/CRO flags)
│   │   └── open-questions.md        ← OQ-01…OQ-35 (Appendix B + found ambiguities + bootcamp + tech)
│   ├── 01-hypothesis-validation/
│   │   ├── h01.md … h14.md          ← per hypothesis: statement, verbatim falsification, data (M/U/OPT),
│   │   │                               protocol (business terms), sign-offs, effort, exit criteria fed
│   │   └── validation-plan.md       ← dependency groups, waves, H→data→D→E table, A1–A10 coverage,
│   │                                   "≥10 tested" deferral priority (OQ-26)
│   ├── 02-stakeholders/             ← one interview guide per §3 group (8–12 questions each,
│   │   │                               evidence lists, tensions incl. Risk-vs-Business shared metric, D3 feeds)
│   │   ├── guide-credit-risk.md          guide-business-commercial.md
│   │   ├── guide-model-risk-validation.md guide-compliance-legal.md
│   │   ├── guide-data-science.md         guide-product-team.md
│   │   ├── guide-executives.md           guide-front-line.md
│   │   ├── guide-internal-audit.md       guide-customer.md   (customer research guide)
│   │   └── guide-regulator-dialogue.md   (contingent brief — via Compliance only, per H13)
│   ├── 03-data/
│   │   ├── data-inventory-tracker.md ← all 22 §7 categories (M/U/OPT), status cells TODO, E5 gate rules
│   │   └── data-request-pack.md      ← formal Data Office request; every item cites its hypothesis;
│   │                                    OPT1/OPT4 excluded (minimization); OPT5 legal-gated placeholder
│   ├── 04-deliverables/              ← skeleton templates D1–D11, sign-off blocks per source §9
│   │   ├── d01-problem-definition-diagnosis.md        d02-current-state-decision-flow-map.md
│   │   ├── d03-stakeholder-analysis-engagement-log.md d04-assumption-hypothesis-validation-report.md
│   │   ├── d05-opportunity-assessment-prioritization.md d06-risk-register.md
│   │   ├── d07-regulatory-legal-position-paper.md     d08-data-inventory-access-disposition.md
│   │   ├── d09-success-metrics-baseline-book.md       d10-governance-accountability-proposal.md
│   │   └── d11-mid-phase-charter-draft.md
│   ├── 05-risk-and-compliance/
│   │   ├── risk-register.md          ← all 26 §6 risks with IDs, owners, mitigations, trigger indicators
│   │   └── regulatory-workplan.md    ← D7 production: H13 opinion, jurisdiction scan, H14 protocol
│   │                                    (process level), legal-basis mapping
│   ├── 06-gates/
│   │   ├── exit-criteria-checklist.md          ← E1–E10 gates (verbatim tests/consequences) + minuted
│   │   │                                          E10 Go/No-Go decision template
│   │   └── steering-committee-pack-outline.md  ← week-10 pack; proceed/pivot/stop argued equally
│   └── 07-bootcamp-workstreams/
│       ├── workstreams.md           ← BWS1–5 dependency graph, sprint sequencing, jury-scoring table
│       └── ws1.md … ws5.md          ← per-workstream task breakdown (83 tasks total)
```

## 12. Execution Plan at a Glance

*(Source Appendix-A plan, detail: `00-program/workplan.md`. For the bootcamp/build sequencing, see `ROADMAP.md` and §13 below — the two plans coexist: this one describes the original 8–10 week consulting-discovery cadence, `ROADMAP.md` describes the bootcamp sprints S0–S4.)*

- **Weeks 1–2 (WS1 Mobilize & map):** charter signed, Appendix B questions issued, data request pack sent, interviews begin, D2 walkthrough, ground-truth workshop #1, H13 legal ToR.
- **Weeks 2–4 (WS2 Legal & governance, parallel):** jurisdiction scan, legal-basis mapping, governance pre-alignment, mock-review setup.
- **Weeks 3–6 (WS3 Evidence):** H1–H8 backtests/cohorts, H9–H11 customer analyses. **E2 (ground truth signed) targeted week 4 — critical path.**
- **Weeks 5–7 (WS4 Sizing & synthesis):** P1/P2/P3 quantification (D1), risk-adjusted O1–O8 sizing (D5), H14 fairness audit after week-5 legal gate.
- **Weeks 7–8 (WS5 Alignment):** D9 KPI negotiation (E7), D10 governance acceptance (E8), D6/D7/D8 closure.
- **Weeks 8–10 (WS6 Close):** steering pack, D11 draft, **E10 minuted Go/No-Go (proceed / pivot / stop)**.
- **Critical path:** data request (wk1) → M-data delivery (wk3) → E2 (wk4) → H1–H4 (wk4–6) → D1 (wk7) → D5 (wk7–8) → E7 (wk8) → E10 (wk10). Single points of failure: Mandatory data delivery and ground-truth signature.

## 13. Bootcamp Adaptation Layer

The engagement is confirmed to be an **AI & Technology bootcamp capstone** (YZTA Bootcamp Grup 74, Part A), not a real bank client. A delta layer re-interprets the package for that reality **without editing the source of truth**:

- **[`bootcamp-adaptation-review.md`](bootcamp-adaptation-review.md)** — KEEP / ADAPT / LIFT / RISK review. Lifts the "no solution/model/architecture" constraint (now in scope and high-scoring — this is exactly what Part A's build did), swaps real bank data→synthetic simulation, real stakeholders→personas, legal opinion→regulatory-awareness note, and maps the 10-week plan to bootcamp sprints. **The hard boundary (never override the bank's segment) is preserved and hardened into architecture** — literally: Part A §2's audit trail.
- **[`07-bootcamp-workstreams/`](07-bootcamp-workstreams/)** — `workstreams.md` (dependency graph, sprint sequencing S0–S4, cross-cutting rituals, jury-scoring alignment) + `ws1.md`–`ws5.md` (BWS1 Business, BWS2 Data/Simulation, BWS3 AI Core & Agentic ★, BWS4 Product/UX, BWS5 Engineering/Integration). Build lands under `/product/` (Part A).
- **`TRACEABILITY.md` §8** — source ID → bootcamp workstream (BWS1–BWS5) map + bootcamp orphan/deferral log; §8.2 also maps BWS task IDs into `ROADMAP.md`.
- **[`ROADMAP.md`](ROADMAP.md)** — the single master delivery plan the team works from: all 83 ws tasks consolidated (84 rows after 1 documented split) with Fibonacci story points, sprint S0–S4 placement, dependencies, critical path, and 6 milestones. **Operational source for task status**; ws files stay the definition source.
- Open questions **OQ-27…OQ-35** (bootcamp duration, team, tech rules, jury rubric, demo format, team velocity, auth choice, Stitch export format, Supabase/Upstash credentials) — logged, not guessed.

**How Part A relates to this layer:** every "Build" item in Sprint 3 (§7) is traceable to a BWS workstream task in `ROADMAP.md` — e.g. the Django migration is `BWS5` engineering work, the audit trail is `BWS5-T5`/`D10`, the React scaffold is `BWS4-T3/T4`. `TRACEABILITY.md` §8 is the authoritative cross-reference.

## 14. Current Status

All 50 original planning artifacts are **built and internally consistent**; all bank-dependent content is explicitly marked **TODO** (tracker statuses, risk L/I scores, names in sign-off blocks, OQ answers) — this reflects that Part B was written under real-consulting assumptions before the bootcamp context was confirmed, and is retained as methodology scaffolding rather than executed against a real bank.

**The actual build (Part A) is live and ahead of the original package's assumptions**: synthetic data, a working model, and a full Django+React application exist — see Part A §5–7 and `PRODUCT_TECH_README.md`. Remaining open items are tracked as OQ-27…OQ-35 and in `ROADMAP.md`'s task statuses.

## 15. Self-Review Record

**(a) Coverage** — automated ID scan across all 48 original package files (excluding source): every one of **P1–P3, A1–A10, H1–H14, O1–O8, D1–D11, E1–E10, M1–M9, U1–U8, OPT1–OPT5, and all 26 risk IDs** appears in ≥1 artifact — **0 missing**. All OQ references map to defined log entries. §8.1 KPIs appear in charter §7 / D9 §4; all eight §8.2 KPIs templated with baseline requirements in D9 §2; §1.2 root causes → D1 §6 + guides; §2.1 steps → D2 §2; §2.3 pain points → guides/D2 §7.

**(b) Scope discipline** — keyword scan for solution/model/architecture design language in the *original 50 files*: all hits are verbatim source quotes or explicit "no design" disclaimers. H5/H8 protocols carry the source's own scope guards ("signal existence only — no model building"; cadence replay of the bank's existing model). *(Scope discipline was deliberately lifted for the bootcamp build — §13, `bootcamp-adaptation-review.md` §3 LIFT — this does not apply to Part A.)*

**(c) Cross-references** — automated checks: no out-of-range IDs (no A11+, H15+, O9+, D12+, E11+, M10+, U9+, OPT6+, R-\*-06+/R-REG-07+); no broken `.md` file references.

**Items that could not be traced to a downstream analytical artifact (by design, logged as defects and resolved):** OPT1 and OPT4 carry no Phase-1 hypothesis in the source — per the source's own §7 minimization rule they are dispositioned **DO-NOT-COLLECT** (tracker) and routed to OQ-22; U7's opportunity-not-hypothesis purpose is flagged as OQ-21. Full log: `TRACEABILITY.md` §7.

**Bootcamp roadmap self-review (run at `ROADMAP.md` build time):**
- **Task count reconciliation** — ws files 83 tasks → `ROADMAP.md` 84 rows; delta = +1, the single documented split `BWS3-T13`→`T13a`/`T13b` (§7.3 there). Every original T-number appears exactly once (or as its two halves); none dropped or duplicated. Detail: `TRACEABILITY.md` §8.2.
- **Story points** — BWS1 68 · BWS2 87 · BWS3 102 · BWS4 89 · BWS5 88 = **434 SP**. Mapping S→2/M→5/L→8; one adjustment (BWS1-T15 S→1, admin); one split (BWS3-T13, >8).
- **Critical-path integrity** — all 15 🔴 tasks have every dependency scheduled in an earlier or same sprint (verified in `ROADMAP.md` §5.1). Two SPOFs: ground-truth definition (BWS1-T4) and seam+guard contract (BWS5-T3/BWS3-T3).
- **Sprint load** — avg 86.8 SP; S1 (128) and S2 (125) flagged REBALANCE-CANDIDATE (>40% over), with suggest-only moves; not silently rebalanced (`ROADMAP.md` §4.2).
- **[INFERRED] placements** — 9, all listed with reasoning in `ROADMAP.md` §7.4.
- **Undecidable → OQ** — team velocity vs. sprint load logged as **OQ-32** (not guessed); frontend export format, auth choice, and Supabase/Upstash credentials logged as **OQ-33…OQ-35**.

**Build-vs-plan reconciliation (Part A ↔ Part B, added this revision):** Sprint 3's Django migration, `aks_core` extraction, and audit-trail implementation are real, verified work (manual end-to-end curl tests against a live `runserver`, `portfoy` result matching Sprint 2's 973/1084 exactly) but are **not yet reflected as DONE statuses in `ROADMAP.md`** — the roadmap's task-status column is the operational source per §16 rule 4 below and should be updated in the next session to mark the relevant `BWS5`/`BWS3`/`BWS4` tasks in progress/done. Flagged here rather than silently left stale.

## 16. Rules for Future Sessions

1. Read the source document (`early-phase-plan-credit-offer-optimization.md`) before changing anything in Part B; never contradict it or rename its IDs.
2. New scope, new data categories, or new risks require an open-questions entry and the declared ID conventions.
3. Keep "no-go is a valid outcome" language intact in charter, D5, D11, E10 checklist, and steering pack.
4. After any edit to the planning package, re-run the traceability checks (ID coverage, no invalid IDs, no broken refs) and update `TRACEABILITY.md` and this file's status sections (§14, §15).
5. **Product changes** (Part A: code, architecture, results) are made in `/product/`; document them in `PRODUCT_TECH_README.md` (technical detail) and summarize narrative-relevant changes here in Part A §7 (Sprint history) and §6 (results) — this file stays the one place a new session can read to understand the whole picture without opening every file.
6. When Part A and Part B drift (e.g. a build milestone not yet reflected in `ROADMAP.md` task status), flag it explicitly in §15 rather than silently resolving it — mirrors the package's own "never guess" discipline.
