# AKS — Ürün (5 Bölümlü Yapı)

> YZTA Bootcamp 2026 — Grup 74. Kök teknoloji planı: [`/TECHSTACK.md`](../TECHSTACK.md) · Yol haritası: [`/planning/ROADMAP.md`](../planning/ROADMAP.md)

Proje, ROADMAP'teki 5 iş akışını (BWS1–5) yansıtan 5 bölüme ayrılmıştır:

| Bölüm | İçerik | Workstream |
|---|---|---|
| **`01-data/`** | Sentetik veri üretici (`generator/`), veri setleri (`datasets/`), EDA, veri sözlüğü | BWS2 Veri & Simülasyon |
| **`02-ai-agents/`** | `aks_core` paketi: özellik çıkarımı, ML modeli (XGBoost/SHAP), adalet, üç-agent orkestratör | BWS3 AI Çekirdek ★ |
| **`03-frontend/`** | React + Vite + TS arayüz (Google Stitch tasarımı entegre edilecek) | BWS4 Ürün/UX |
| **`04-backend/`** | Django + DRF API, Supabase kalıcılık, Redis cache, **denetim izi** (audit), testler, deploy | BWS5 Mühendislik |
| **`05-business/`** | Persona, metrik, regülasyon notları, sprint dokümanları (`docs/`) | BWS1 İş & Alan |

### Hızlı başlangıç (yerel geliştirme)

```bash
# 1) AI çekirdeğini kur
pip install -e product/02-ai-agents
# 2) Backend
cd product/04-backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver            # API -> http://127.0.0.1:8000/api/bilgi
# 3) Frontend (ayrı terminal)
cd product/03-frontend
npm install
npm run dev                           # UI -> http://localhost:5173  (/api proxy -> :8000)
```

`.env` gerekmez: Supabase/Redis tanımlı değilse backend yerel SQLite + bellek-içi cache'e düşer; demo her koşulda çalışır. Üretim değişkenleri için `product/04-backend/.env.example`.

> **Sınır (boundary):** AKS, bankanın klasik skorunu/segmentini **asla ezmez**, yalnızca tamamlar. Her skorlama, klasik skoru olduğu gibi koruyan **değiştirilemez bir denetim kaydı** yazar (`04-backend/audit/`). Bu, hem alan bütünlüğü hem de jüri için en güçlü hikâyemiz.

> **Not:** `04-backend/_legacy_fastapi/` eski FastAPI + tek-dosya dashboard'u içerir — Django'ya taşınırken referans olarak tutuluyor, canlı değil.

Aşağıdaki bölüm, ürünün detaylı anlatımı ve sprint geçmişidir (yapı yeniden düzenlenmeden önceki §5 klasör şeması tarihseldir).

---

# Gerçek Kapasite Skoru (GKS) — Alternatif Kredi Değerlendirme Sistemi

> YZTA Bootcamp 2026 — 5. Akademi Dönemi · Yapay Zeka ve Veri Bilimi · Grup 74

## Takım

| Rol | Kişi |
|---|---|
| Product Owner | Alperen Karakaya |
| Scrum Master | Ahmet Özdoğan |
| Developer | Zeynep Salkaya |
| Developer | Havva Balta |
| Developer | Begüm Bakan |

## 1. Problem

Geleneksel kredi/limit değerlendirme sistemleri büyük ölçüde **resmi gelir
beyanına** dayanır. Bu durum, hesap hareketleri açısından yüksek hacimli,
düzenli ve disiplinli olmasına rağmen resmi olarak "öğrenci", "stajyer" ya da
"freelancer" görünen kişilerin gerçek ödeme kapasitelerinin çok altında
kredi/limit almasına yol açıyor.

Odak noktamız özellikle küçük çaplı krediler: banka işlem hacmi yüksek olduğu
halde gelir seviyesi düşük görünen ya da stajyer/öğrenci profilindeki kişiler
çok düşük kredi limitleri alıyor. Aynı sorun büyük çaplı kredilerde de var, ama
asıl kayıp burada birikiyor. Banka açısından bu, **görünmeyen ama yakalanabilir
bir getiri kaybı**: düşük riskli ama "düşük skorlu" görünen büyük bir müşteri
segmenti ya hiç kredilenemiyor ya da alternatif (BNPL, P2P, enformel) kaynaklara
kayıyor.

Amacımız bu arayı kapatmak — hem müşterinin gerçek kapasitesine uygun limit
alması, hem de bankanın kaçırdığı getiriyi geri kazanması. İki taraf için de
kazançlı bir denge.

## 2. Çözüm

Hesap hareketlerinden (transaction) çıkarılan davranışsal özelliklerle
(gelir düzenliliği, gelir kaynağı çeşitliliği, gider disiplini, tasarruf
trendi, fatura ödeme düzeni, hesap aktivite yoğunluğu) resmi gelirden
bağımsız bir **Alternatif Kapasite Skoru (AKS)** üretiyoruz. Bu skor,
klasik skorlamayı **değiştirmek değil tamamlamak** için tasarlandı: banka
mevcut risk modelini korurken, "thin-file" (resmi veri açısından zayıf
dosyalı) ama davranışsal olarak güçlü müşterileri ayırt edebiliyor.

## 3. Hedef Kitle / Persona'lar

| Persona | Tanım |
|---|---|
| `ogrenci_yuksek_hacim` | Resmi geliri zayıf, ama burs + part-time + aile desteği ile yüksek hacimli ve düzenli hareket eden öğrenci — asıl odak grubumuz |
| `stajyer_degisken_gelir` | Stajyer/freelancer, toplamda yüksek ama zaman içinde düzensiz gelir |
| `klasik_maasli` | Sabit, resmi aylık maaşlı çalışan (kontrol/baseline grubu) |
| `dusuk_hacim_riskli` | Gerçekten düşük kapasiteli, düzensiz hareketli kişi (negatif kontrol — modelin yanlışlıkla yüksek skor vermemesi gerekiyor) |

## 4. Mimari (Plan)

```
[Sentetik/Gerçek İşlem Verisi]
        │
        ▼
[Özellik Mühendisliği]  ── gelir düzenliliği, gider/gelir oranı, ...
        │
        ▼
[Skorlama Motoru]  ── klasik_skor (baseline) + alternatif_skor (AKS)
        │
        ▼
[Açıklanabilirlik Katmanı]  ── "neden bu skor?" (SHAP / kural bazlı / LLM)
        │
        ▼
[API (FastAPI)]  ── /score  /explain  /simulate
        │
        ▼
[Dashboard]  ── kullanıcı görünümü + banka portföy görünümü
```

Sprint 2'de skorlama motoru XGBoost/LightGBM tabanlı denetimli modele, açıklama
katmanı da üç-agent yapısına (veri/özellik agent'ı → skorlama agent'ı →
danışman agent'ı) genişletilecek.

## 5. Klasör Yapısı

```
yzta-bootcamp-grup74/
├── data/
│   ├── sentetik_islemler.csv      # Üretilen ham sentetik işlem verisi
│   └── skor_raporu.csv            # Müşteri bazlı skor çıktısı
├── src/
│   ├── sentetik_veri_uretici.py   # Sentetik banka işlem verisi üretici
│   └── skor_hesaplama.py          # Özellik mühendisliği + skorlama
├── docs/
│   └── sprint1/                   # Daily Scrum notları, board görüntüleri
├── requirements.txt
└── README.md
```

## 6. Çalıştırma

```bash
cd src
python3 sentetik_veri_uretici.py --musteri-sayisi 500 --gun 180
python3 skor_hesaplama.py
```

`random.seed(42)` sabit olduğu için üretilen veri ve skorlar tekrarlanabilir.

## 7. Erken Bulgu (Sprint 1)

500 sentetik müşteri üzerinde:

| Persona | Ort. Klasik Skor | Ort. Alternatif Skor |
|---|---|---|
| klasik_maasli | 840.8 | 462.3 |
| ogrenci_yuksek_hacim | 636.1 | 440.6 |
| stajyer_degisken_gelir | 631.9 | 345.5 |
| dusuk_hacim_riskli | 504.2 | 300.0 |

**Yorum:** Klasik skorlamada `klasik_maasli` ile `ogrenci_yuksek_hacim`
arasındaki fark **~205 puan**. Alternatif skorlamada bu fark **~22 puana**
düşüyor — yani davranışsal model, resmi gelir farkının yarattığı
dengesizliğin büyük kısmını kapatıyor. `dusuk_hacim_riskli` grubu ise
beklendiği gibi alternatif modelde de düşük kalıyor (negatif kontrol başarılı).
*(Mutlak skor seviyeleri Sprint 2'de gerçek/açık datasetlerle kalibre
edilecek; buradaki amaç göreceli farkı göstermek.)*

## 8. Product Backlog

Backlog bu repo içinde tutulmaktadır: aşağıdaki tablo story bazında,
`docs/sprint1/board_sprint1.png` ise sprint panosu (Backlog / To Do / In
Progress / Done) olarak takip edilmektedir.

| # | User Story | Sprint | Durum |
|---|---|---|---|
| 1 | Sentetik işlem verisi üretici | 1 | ✅ |
| 2 | Özellik mühendisliği + baseline skor | 1 | ✅ |
| 3 | Persona bazlı doğrulama / kalibrasyon | 2 | ⏳ |
| 4 | XGBoost/LightGBM ile denetimli model | 2 | ⏳ |
| 5 | Üç-agent mimarisi (veri / skor / danışman) | 2 | ⏳ |
| 6 | Açıklanabilirlik katmanı (SHAP veya LLM) | 2 | ⏳ |
| 7 | FastAPI `/score` `/explain` `/simulate` | 2 | ⏳ |
| 8 | Kullanıcı dashboard'u | 3 | ⏳ |
| 9 | Banka portföy/getiri simülasyon görünümü | 3 | ⏳ |
| 10 | Deploy + demo video | 3 | ⏳ |

---

# Sprint 1

**Sprint Notu:** Bu sprintte hedef, projenin veri temelini ve kavram kanıtını
(proof of concept) kurmaktı: sentetik banka işlem verisi üretmek, davranışsal
özellikleri çıkarmak ve resmi gelirden bağımsız bir baseline alternatif skor
üretip persona'lar üzerinde doğrulamak.

**Sprint içi kapsam ve tahmin:** Backlog story'leri göreli olarak boyutlandırıldı.
Sprint 1 kapsamı iki ana story'den oluştu — sentetik veri üreticisi ve özellik
mühendisliği + baseline skor — ve bunların alt task'lerinden. Story başına tahmin,
sprint toplamının yarısını geçmeyecek şekilde tutuldu.

**Puan tamamlama mantığı:** Backlog, ilk yapılacak story'lere göre düzenlendi.
Story başına tahmin puanı, sprint toplamının yarısından az tutuldu. Miro
Board'da kırmızı item'lar yapılacak işleri (task), mavi item'lar story'leri
temsil ediyor.

**Daily Scrum:** Daily Scrum toplantıları zaman kısıtı nedeniyle Slack üzerinden
(grup DM + huddle) yürütüldü. Toplantı notları
`docs/sprint1/daily_scrum_notlari.md` altında; ilgili Slack ekran görüntüleri de
aynı klasörde (`slack_01_fikir_tartismasi.png`, `slack_02_fikir_form_gorev.png`,
`slack_03_huddle_roadmap.png`, `slack_04_koordinasyon.png`).

**Sprint Board Update:**

![Sprint 1 Board](docs/sprint1/board_sprint1.png)

**Ürün Durumu:**

![Skor raporu özeti](docs/sprint1/urun_durumu_sprint1.png)

**Sprint Review — alınan kararlar:**

- Sentetik veri üreticisi ve kural-tabanlı skorlama motoru çalışır durumda;
  testlerde bir problem görülmedi.
- Baseline model, hedeflenen etkiyi gösterdi: klasik skorda maaşlı ile öğrenci
  arasındaki ~205 puanlık uçurum, alternatif skorda ~22 puana iniyor. Negatif
  kontrol grubu (`dusuk_hacim_riskli`) beklendiği gibi düşük kaldı.
- Bir sonraki sprint'e taşınan işler: kural-tabanlı skorun XGBoost/LightGBM ile
  denetimli modele dönüştürülmesi ve açıklanabilirlik katmanı.
- Sentetik veri üreticisinde gider/gelir oranının olması gerekenden yüksek
  çıktığı fark edildi; kalibrasyon Sprint 2'ye alındı.
- Sprint Review katılımcıları: Alperen Karakaya, Ahmet Özdoğan, Zeynep Salkaya, Havva Balta, Begüm Bakan

**Sprint Retrospective:**

- Takım içi görev dağılımı gözden geçirilip netleştirilecek.
- Tahmin puanları yeniden değerlendirilecek; sprint planlamada developer
  geri bildirimlerinin alındığından emin olunacak.
- Unit test'ler için ayrılan efor/saat arttırılmalı.

---

# Sprint 2

*(6 – 19 Temmuz) — Zeka katmanı: kural-tabanlı skordan denetimli ML modeline geçiş, açıklanabilirlik, üç-agent mimarisi ve API.*

## Yapılanlar

**1. Veri düzeltmesi.** Sprint 1'deki gider dağıtım hatası düzeltildi (giderler
hedeflenen orandan ~2 kat yüksek çıkıyordu). Artık `gider_gelir_orani`
persona'lar arasında ayırt edici ve gerçekçi (öğrenci ~0.72, riskli ~1.22).

**2. Denetimli etiketleme.** Temerrüt (default) etiketi, kişinin *davranışsal
disiplininden* türetildi (persona/gelir hacminden değil). Bu, projenin tezini
kodlar: düşük gelirli görünen disiplinli kişi gerçekte düşük risklidir.

**3. ML modeli (XGBoost & LightGBM).** Davranışsal özelliklerle temerrüt tahmini.
Mevcut sistemi temsil eden klasik skorla karşılaştırıldı:

| Model | ROC-AUC |
|---|---|
| **XGBoost** | **0.829** |
| LightGBM | 0.823 |
| Klasik skor (baseline) | 0.729 |

Davranışsal model klasik skoru **+0.10 AUC** ile geçiyor.

**4. Açıklanabilirlik (SHAP).** Her skor için riski artıran/azaltan faktörler
faktör bazında çıkarılıyor.

**5. Üç-agent mimarisi + orkestrasyon + hafıza.**
- `VeriAgent` → ham işlemlerden özellik çıkarır
- `SkorlamaAgent` → ML modeliyle 300-850 AKS skoru + kredi kararı üretir
- `DanismanAgent` → SHAP açıklamasından skoru anlatır ve iyileştirme önerir
- `Orkestrator` → üçünü sırayla çalıştırır ve müşteri bazında hafıza tutar

**6. FastAPI backend.** `/skorla`, `/aciklama`, `/simulasyon`, `/gecmis/{id}`.

**7. Web dashboard.** İki görünümlü arayüz (`web/index.html`, API kökünden servis edilir):
*Müşteri görünümü* — klasik vs AKS skor karşılaştırması, SHAP faktörleri, danışman
önerileri ve interaktif "ne olurdu?" simülasyonu. *Banka görünümü* — klasik sistemin
kaçırdığı kredibl segment, kurtarma oranı ve illüstratif getiri.

**8. Testler.** 22 birim/entegrasyon testi (`tests/`): özellik çıkarımı, etiket
kalibrasyonu, skorlama sınırları, orkestratör hafızası, API uç noktaları ve hata
durumları. Çalıştırma: `python -m pytest tests/ -v`

**9. Deploy hazırlığı.** `Dockerfile` + `render.yaml` ile tek komutla canlıya
alınabilir:

```bash
docker build -t aks-grup74 .
docker run -p 8000:8000 aks-grup74
# -> http://localhost:8000 (dashboard) ve /docs (API)
```

**10. Kredi limit önerisi.** Skor sadece bir sayı değil: aylık net nakit akışı ve
risk seviyesine göre önerilen kredi limiti (TL) üretilir — bankaya değeri somutlaştırır.

**11. Adalet/önyargı analizi (sorumlu YZ).** Equal-opportunity metriği: kredibl
kişilerin onaylanma oranı gruplar arası karşılaştırılır. Sonuç çarpıcı — klasik
skorda kredibl bir öğrencinin onaylanma oranı %0.4 iken AKS'de %97.8; adalet
boşluğu 1.00'den 0.39'a iner. (`src/model/adalet.py`, dashboard banka görünümü)

**12. CSV ile kendi verini skorla.** Dashboard'dan hesap dökümü CSV'si yüklenip
anında skor + limit + faktör açıklaması alınabilir (`/api/csv-skorla`).

**13. Banka paneli arayüzü + AKS Asistanı.** Ön yüz, gerçek bir bankacılık paneli
gibi yeniden tasarlandı: sol menü navigasyonu (Genel Bakış / Müşteri Değerlendirme /
Portföy / Adalet), koyu profesyonel tema ve imza öğe olarak canlı skor yayı (gauge).
Sağ altta **AKS Asistanı**: skorlama, limit, faktör ve adalet sorularını yanıtlar.
Asistan LLM'e bağlanabilir (`GEMINI_API_KEY` env değişkeni tanımlıysa Gemini kullanır),
tanımlı değilse SHAP + öneri bağlamından deterministik kural-tabanlı yanıt verir —
demo her koşulda çalışır.

## İş etkisi (bankaya değer)

Klasik skorun "prime" eşiğinin altında bıraktığı kredibl kişilerden **%90'ı
(973 kişi) model tarafından doğru şekilde kurtarılıyor** — %92'si tam hedef
kitle olan öğrenci ve stajyer. Risk kontrolü korunuyor (yanlış onay %8).

![Sprint 2 model sonuçları](docs/sprint2/model_sonuclari.png)

## Çalıştırma

```bash
pip install -r requirements.txt

# 1) Sentetik veri üret
python -m src.veri.uretici --musteri-sayisi 2000 --gun 180 --cikti data/sentetik_islemler.csv

# 2) Modeli eğit (XGBoost/LightGBM vs klasik skor karşılaştırması)
python -m src.model.egitim

# 3) İş etkisi analizi
python -m src.model.is_etkisi

# 4) API'yi başlat
uvicorn src.api.main:app --reload
# LLM asistan için (opsiyonel): setx GEMINI_API_KEY "anahtarınız"
# -> http://127.0.0.1:8000/docs (interaktif test arayüzü)
```

## Mimari

```
Ham işlemler
    │
    ▼  VeriAgent
Davranışsal özellikler (9 adet)
    │
    ▼  SkorlamaAgent (XGBoost)
AKS skoru (300-850) + risk seviyesi + kredi kararı
    │
    ▼  Aciklayici (SHAP) → DanismanAgent
"Skorun neden böyle" + iyileştirme önerileri
    │
    ▼  Orkestrator (hafıza)
Müşteri geçmişi + skor değişim takibi
```

---

# Sprint 3

---

## Etik & Regülasyon Notu

- Bu repo gerçek banka verisi içermez; tüm veriler sentetiktir.
- Üretimde KVKK kapsamında açık rıza ve veri minimizasyonu gerekir.
- Model, ayrımcı (discriminatory) sinyalleri (yaş, cinsiyet vb.) doğrudan
  kullanmaz; yalnızca davranışsal/finansal özelliklere dayanır.
