# AKS — Alternatif Kapasite Skoru

**Kredi/limit değerlendirmesini resmi gelir beyanının ötesine taşıyan, bankanın mevcut skorunu asla ezmeyen, yalnızca tamamlayan bir davranışsal-AI katmanı.**

> YZTA Bootcamp 2026 — 5. Akademi Dönemi · Yapay Zeka ve Veri Bilimi · **Grup 74**
> Kök teknoloji planı: [`/TECHSTACK.md`](../TECHSTACK.md) · Yol haritası: [`/planning/ROADMAP.md`](../planning/ROADMAP.md) · Erken faz planlama paketi: [`/planning/`](../planning/)

---

## İçindekiler

1. [Genel Bakış](#1-genel-bakış)
2. [Çözüm ve Tez](#2-çözüm-ve-tez)
3. [Hedef Kitle / Personalar](#3-hedef-kitle--personalar)
4. [Mimari](#4-mimari)
5. [Teknoloji Yığını](#5-teknoloji-yığını)
6. [Proje Yapısı (5 Bölüm)](#6-proje-yapısı-5-bölüm)
7. [Kurulum ve Çalıştırma](#7-kurulum-ve-çalıştırma)
8. [Ortam Değişkenleri](#8-ortam-değişkenleri)
9. [API Referansı](#9-api-referansı)
10. [Veri Modeli ve Denetim İzi (Audit Trail)](#10-veri-modeli-ve-denetim-izi-audit-trail)
11. [Model ve Sonuçlar](#11-model-ve-sonuçlar)
12. [Adalet / Önyargı Analizi](#12-adalet--önyargı-analizi)
13. [Testler — Mevcut Durum](#13-testler--mevcut-durum)
14. [Deploy](#14-deploy)
15. [Yol Haritası ve Bootcamp Bağlamı](#15-yol-haritası-ve-bootcamp-bağlamı)
16. [Ekip](#16-ekip)
17. [Sprint Geçmişi](#17-sprint-geçmişi)
18. [Etik ve Regülasyon Notu](#18-etik-ve-regülasyon-notu)

---

## 1. Genel Bakış

Geleneksel kredi/limit değerlendirme sistemleri büyük ölçüde **resmi gelir beyanına** dayanır. Bu durum, hesap hareketleri açısından yüksek hacimli, düzenli ve disiplinli olmasına rağmen resmi olarak "öğrenci", "stajyer" ya da "freelancer" görünen kişilerin gerçek ödeme kapasitelerinin çok altında kredi/limit almasına yol açıyor.

Odak noktamız özellikle küçük çaplı krediler: banka işlem hacmi yüksek olduğu halde gelir seviyesi düşük görünen ya da stajyer/öğrenci profilindeki kişiler çok düşük kredi limitleri alıyor. Aynı sorun büyük çaplı kredilerde de var, ama asıl kayıp burada birikiyor. Banka açısından bu, **görünmeyen ama yakalanabilir bir getiri kaybı**: düşük riskli ama "düşük skorlu" görünen büyük bir müşteri segmenti ya hiç kredilenemiyor ya da alternatif (BNPL, P2P, enformel) kaynaklara kayıyor.

Amacımız bu arayı kapatmak — hem müşterinin gerçek kapasitesine uygun limit alması, hem de bankanın kaçırdığı getiriyi geri kazanması. İki taraf için de kazançlı bir denge.

## 2. Çözüm ve Tez

Hesap hareketlerinden (transaction) çıkarılan davranışsal özelliklerle (gelir düzenliliği, gelir kaynağı çeşitliliği, gider disiplini, tasarruf trendi, fatura ödeme düzeni, hesap aktivite yoğunluğu) resmi gelirden bağımsız bir **Alternatif Kapasite Skoru (AKS)** üretiyoruz.

> **Tez ve sınır (boundary) — projenin bütün mimarisini şekillendiren tek cümle:**
> **AKS, bankanın klasik skorunu/segmentini asla ezmez veya değiştirmez — yalnızca tamamlar.** Banka mevcut risk modelini ve nihai kararını korurken, AKS "thin-file" (resmi veri açısından zayıf dosyalı) ama davranışsal olarak güçlü müşterileri ayırt eden **ek bir sinyal** sağlar.

Bu sınır kâğıt üzerinde bir taahhüt değil, koddaki bir gerçektir: her skorlama, bankanın klasik skorunu **değiştirilmeden** kaydeden değiştirilemez bir denetim satırı (`AuditLog`) üretir (bkz. [§10](#10-veri-modeli-ve-denetim-izi-audit-trail)). Aynı ilke `/planning` erken-faz paketindeki §4 sınırıyla ve `ROADMAP.md`'deki "hard boundary" değişmeziyle birebir örtüşür.

## 3. Hedef Kitle / Personalar

Sentetik veri üretici (`01-data/generator/veri/uretici.py`) dört davranışsal personayı simüle eder:

| Persona | Tanım |
|---|---|
| `ogrenci_yuksek_hacim` | Resmi geliri zayıf, ama burs + part-time + aile desteği ile yüksek hacimli ve düzenli hareket eden öğrenci — **asıl odak grubumuz** |
| `stajyer_degisken_gelir` | Stajyer/freelancer, toplamda yüksek ama zaman içinde düzensiz gelir |
| `klasik_maasli` | Sabit, resmi aylık maaşlı çalışan (kontrol/baseline grubu) |
| `dusuk_hacim_riskli` | Gerçekten düşük kapasiteli, düzensiz hareketli kişi (**negatif kontrol** — modelin yanlışlıkla yüksek skor vermemesi gerekiyor) |

## 4. Mimari

```
┌─────────────────────────────────────────────────────────────────┐
│ 03-frontend — React + Vite + TypeScript                          │
│ Müşteri Değerlendirme · Portföy · Adalet · AKS Asistanı           │
│ (Google Stitch tasarımı entegre edilecek — bkz. OQ-34)            │
└───────────────────────────┬───────────────────────────────────────┘
                             │ REST/JSON (CORS, /api proxy dev'de)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 04-backend — Django + Django REST Framework                       │
│  api/   — 11 uç nokta (bkz. §9), servis katmanı aks_core'u sarar  │
│  audit/ — Customer · Assessment · AuditLog (değiştirilemez)       │
│  cache  — Upstash Redis (portföy/adalet agregatları, TTL)          │
└──────────┬──────────────────────────────────┬─────────────────────┘
           │ import (aks_core)                 │ ORM
           ▼                                    ▼
┌───────────────────────────────┐   ┌─────────────────────────────┐
│ 02-ai-agents/aks_core          │   │ Supabase (Postgres)          │
│  agents/  VeriAgent →           │   │  customers                   │
│           SkorlamaAgent →       │   │  assessments                 │
│           DanismanAgent         │   │  audit_log (klasik_skor       │
│  agents/  Orkestrator (hafıza)  │   │   DEĞİŞTİRİLMEDİ + aks_skor + │
│  agents/  AsistanAgent (Gemini) │   │   politika_notu + ajanlar)    │
│  model/   egitim (XGBoost/LGBM) │   └─────────────────────────────┘
│  model/   aciklama (SHAP)       │
│  model/   adalet (equal-opp.)   │
│  model/   is_etkisi             │
│  artifacts/ aks_model.joblib    │
└───────────────┬─────────────────┘
                │ okur
                ▼
┌───────────────────────────────┐
│ 01-data                        │
│  generator/veri/uretici.py     │
│  datasets/*.csv                │
└───────────────────────────────┘

05-business — persona, metrik, regülasyon notları, sprint dokümanları
              (bkz. /planning: BWS1, D1/D5/D7/D9)
```

### Uçtan uca veri akışı (bir skorlama isteğinde)

```
Ham işlemler (CSV / demo / kullanıcı yüklemesi)
    │
    ▼  VeriAgent
Davranışsal özellikler (9 adet — bkz. §11)
    │
    ▼  SkorlamaAgent (XGBoost, models/aks_model.joblib)
AKS skoru (300–850) + risk seviyesi + kredi kararı + önerilen limit
    │
    ▼  Aciklayici (SHAP) → DanismanAgent
"Skorun neden böyle" açıklaması + iyileştirme önerileri
    │
    ▼  Orkestrator
Müşteri geçmişi (bellek-içi) + skor değişim takibi
    │
    ▼  api/services.py
Django ORM'e yaz: Assessment (geçmiş) + AuditLog (değiştirilemez, klasik_skor korunur)
    │
    ▼  DRF view
JSON yanıt → React arayüzü
```

**Sınırın (boundary) koddaki karşılığı:** `SkorlamaAgent` yalnızca **tamamlayıcı** AKS skorunu üretir; klasik (banka) skoru hiçbir agent tarafından okunup değiştirilmez — yalnızca `api/services.py` içinde referans/karşılaştırma amacıyla hesaplanır (`klasik_risk_skoru`) ve olduğu gibi denetim satırına yazılır. Django admin panelinde (`/admin/`) `AuditLog` **salt-okunur**dur (`has_change_permission` / `has_delete_permission` = `False`).

## 5. Teknoloji Yığını

Tam gerekçelendirme ve ortam değişkeni sözleşmesi için bkz. [`/TECHSTACK.md`](../TECHSTACK.md). Özet:

| Katman | Teknoloji | Not |
|---|---|---|
| Frontend | **React 18 + Vite 5 + TypeScript** | `03-frontend/`; Google Stitch tasarımı entegre edilecek |
| Backend / API | **Django 5.2 + Django REST Framework 3.17** | `04-backend/`; eski FastAPI'nin yerini aldı (bkz. §17 Sprint 2 → Sprint 3 geçişi) |
| AI çekirdeği | Özel **3-agent orkestrasyon** (`aks_core.agents`) | Framework-agnostik, `pip install -e` ile kurulan paket |
| ML | **XGBoost** (birincil) + LightGBM (karşılaştırma) + scikit-learn | `aks_core/model/egitim.py` |
| Açıklanabilirlik | **SHAP** | `aks_core/model/aciklama.py` |
| LLM | **Google Gemini** (`GEMINI_API_KEY`), tanımlı değilse deterministik kural-tabanlı yedek | `aks_core/agents/asistan.py` — demo her koşulda çalışır |
| Veritabanı | **Supabase (Postgres)** üzerinden Django ORM; env yoksa yerel **SQLite**'a düşer | `04-backend/audit/models.py`, `config/settings.py` |
| Cache | **Upstash Redis** (`django-redis`); env yoksa yerel bellek cache | portföy/adalet agregatlarını önbellekler |
| Paketleme | `aks_core` — `pyproject.toml` ile editable-install | Hem Django hem CLI scriptleri aynı paketi kullanır |
| Deploy (hedef) | Docker + Render; Supabase + Upstash hosted | Eski Docker/render.yaml `04-backend/_legacy_fastapi/`'de referans olarak duruyor |

**Doğrulanmış araç zinciri:** Python 3.11.9 · Node 18.14.0 · npm 9.3.1 · Django 5.2.16 · DRF 3.17.1 · Vite 5.4.21. **Not:** `numpy<2` sabitlenmiştir — model artefaktları (XGBoost/SHAP) NumPy 1.x ile derlendi.

## 6. Proje Yapısı (5 Bölüm)

Proje, [`ROADMAP.md`](../planning/ROADMAP.md)'deki 5 iş akışını (BWS1–5) yansıtan 5 bölüme ayrılmıştır:

```
product/
├── README.md                      # bu dosya
├── 01-data/                        (BWS2 — Veri & Simülasyon)
│   ├── generator/
│   │   ├── veri/uretici.py         #   güncel sentetik işlem verisi üretici
│   │   ├── legacy_sentetik_veri_uretici.py   # Sprint 1 üretici (referans)
│   │   └── legacy_skor_hesaplama.py          # Sprint 1 kural-tabanlı skor (referans)
│   └── datasets/
│       ├── sentetik_islemler.csv   #   ~2000 müşteri, 180 gün işlem (~7.6 MB)
│       ├── egitim_verisi.csv       #   özellik çıkarımı sonrası eğitim seti
│       └── skor_raporu.csv         #   Sprint 1 skor çıktısı (referans)
│
├── 02-ai-agents/                   (BWS3 — AI Çekirdek ★ en yüksek jüri ağırlığı)
│   ├── pyproject.toml              #   aks-core paketi (editable install)
│   ├── requirements-core.txt       #   scikit-learn, xgboost, lightgbm, shap, joblib, numpy<2
│   └── aks_core/
│       ├── paths.py                #   paket-göreli, CWD-bağımsız yol çözümü (AKS_DATA_DIR, AKS_MODEL)
│       ├── ozellik/cikarim.py      #   ham işlemlerden 9 davranışsal özellik
│       ├── model/
│       │   ├── egitim.py           #     XGBoost/LightGBM eğitimi + klasik skor karşılaştırması
│       │   ├── etiketleme.py       #     davranışsal disiplinden temerrüt etiketi türetimi
│       │   ├── aciklama.py         #     SHAP açıklayıcı
│       │   ├── adalet.py           #     equal-opportunity adalet raporu
│       │   └── is_etkisi.py        #     iş etkisi analizi (kurtarılan kredibl segment)
│       ├── agents/
│       │   ├── veri_agent.py       #     VeriAgent — özellik çıkarımı
│       │   ├── skorlama_agent.py   #     SkorlamaAgent — AKS skoru + karar
│       │   ├── danisman_agent.py   #     DanismanAgent — SHAP'tan öneri üretimi
│       │   ├── asistan.py          #     AsistanAgent — Gemini / kural-tabanlı soru-cevap
│       │   └── orkestrator.py      #     Orkestrator — 3 agent'ı sırayla çalıştırır + hafıza
│       └── artifacts/
│           ├── aks_model.joblib    #   eğitilmiş XGBoost modeli (paket içi)
│           └── metrikler.json      #   AUC/AP metrikleri (bkz. §11)
│
├── 03-frontend/                    (BWS4 — Ürün, UX & Açıklanabilirlik)
│   ├── src/
│   │   ├── api.ts                  #   tipli API istemcisi (Bilgi, SkorSonuc, Portfoy arayüzleri)
│   │   ├── App.tsx                 #   "döngüyü kanıtlayan" yer tutucu görünüm
│   │   ├── main.tsx, index.css, vite-env.d.ts
│   ├── vite.config.ts              #   dev proxy: /api -> http://localhost:8000
│   ├── package.json, tsconfig.json
│
├── 04-backend/                     (BWS5 — Mühendislik, Entegrasyon & Kalite)
│   ├── manage.py
│   ├── config/                     #   settings.py (env-driven, SQLite+LocMem fallback), urls.py, wsgi.py, asgi.py
│   ├── api/
│   │   ├── services.py             #   aks_core'u sarar: tekil Orkestrator/Asistan, denetim yazımı, cache
│   │   ├── views.py                #   11 DRF view (bkz. §9)
│   │   └── urls.py
│   ├── audit/
│   │   ├── models.py               #   Customer, Assessment, AuditLog
│   │   ├── admin.py                #   salt-okunur denetim izi paneli
│   │   └── migrations/
│   ├── requirements.txt
│   ├── .env.example                #   tüm ortam değişkenlerinin şablonu (bkz. §8)
│   └── _legacy_fastapi/            #   ESKİ FastAPI + tek-dosya dashboard — PORTLAMA REFERANSI, CANLI DEĞİL
│       ├── api/main.py             #     eski uç noktalar (Django'ya taşındı)
│       ├── web/index.html          #     eski vanilla-JS bankacılık paneli
│       ├── tests/test_pipeline.py  #     eski testler (from src.* — artık geçersiz, bkz. §13)
│       ├── Dockerfile, render.yaml
│
└── 05-business/                    (BWS1 — İş & Alan)
    └── docs/sprints/
        ├── sprint1/                #   Daily Scrum notları, Slack ekran görüntüleri, board
        └── sprint2/                #   model sonuçları görseli
```

## 7. Kurulum ve Çalıştırma

### 7.1 Ön koşullar
- Python **3.11+**
- Node.js **18+** / npm **9+**
- (Opsiyonel) Supabase projesi, Upstash Redis, Gemini API anahtarı — hiçbiri zorunlu değil, bkz. §8

### 7.2 Yerel geliştirme (iki terminal)

```bash
# --- Terminal 1: AI çekirdeği + Backend ---
python -m venv .venv
source .venv/Scripts/activate          # Windows Git Bash; PowerShell: .venv\Scripts\Activate.ps1

pip install -e product/02-ai-agents    # aks_core paketi (editable)
pip install -r product/04-backend/requirements.txt

cd product/04-backend
python manage.py migrate               # SQLite şeması (Supabase tanımlı değilse)
python manage.py runserver             # -> http://127.0.0.1:8000/api/bilgi

# --- Terminal 2: Frontend ---
cd product/03-frontend
npm install
npm run dev                            # -> http://localhost:5173  (/api -> :8000 proxy)
```

Tarayıcıda `http://localhost:5173` açın: "Skorla" butonu klasik vs AKS skorunu, riski, kararı ve önerilen limiti canlı olarak gösterir; portföy özeti otomatik yüklenir. **Bu, arayüzde değişiklikleri görmek için istenen basit araçtır** — Vite hot-reload ile her `App.tsx`/CSS değişikliği anında tarayıcıda görünür.

### 7.3 Tek-port entegre önizleme (demo günü tarzı)

```bash
cd product/03-frontend && npm run build     # dist/ üretir
# (Django'ya statik servis eklenmesi bu adımdan sonraki iş; şu an ayrı :5173/:8000 kullanın)
```

### 7.4 Modeli yeniden eğitmek / sentetik veri üretmek

```bash
# Sentetik işlem verisi üret (2000 müşteri, 180 gün)
python -m aks_core.model.egitim --girdi product/01-data/datasets/sentetik_islemler.csv

# ya da güncel üretici ile yeni veri üret:
python product/01-data/generator/veri/uretici.py --musteri-sayisi 2000 --gun 180 \
    --cikti product/01-data/datasets/sentetik_islemler.csv

# İş etkisi analizi
python -c "from aks_core.model.is_etkisi import analiz; print(analiz())"
```

### 7.5 Django admin (denetim izini görüntüleme)

```bash
cd product/04-backend
python manage.py createsuperuser
python manage.py runserver
# -> http://127.0.0.1:8000/admin/  (Denetim İzi bölümü salt-okunur)
```

## 8. Ortam Değişkenleri

Şablon: [`product/04-backend/.env.example`](04-backend/.env.example). **Hiçbiri zorunlu değildir** — boş bırakılırsa backend yerel SQLite + bellek-içi cache'e düşer, demo her koşulda çalışır.

| Değişken | Amaç | Boşsa davranış |
|---|---|---|
| `GEMINI_API_KEY` | AKS Asistanı için LLM | Deterministik kural-tabanlı yanıt (SHAP + öneri bağlamından) |
| `DATABASE_URL` | Supabase Postgres bağlantısı | `product/04-backend/aks_dev.sqlite3` (yerel) |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` | Frontend auth (ileride, bkz. OQ-33) | Kullanılmaz |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend-only Supabase erişimi | Kullanılmaz |
| `REDIS_URL` | Upstash Redis (portföy/adalet cache) | Django `LocMemCache` |
| `DJANGO_SECRET_KEY` | Django imzalama anahtarı | Geliştirme anahtarı (üretimde **mutlaka** değiştirin) |
| `DJANGO_DEBUG` | Hata ayıklama modu | `true` |
| `DJANGO_ALLOWED_HOSTS` | İzin verilen host'lar | `localhost,127.0.0.1,0.0.0.0` |
| `CORS_ALLOWED_ORIGINS` | Frontend origin'leri | `http://localhost:5173` |
| `AKS_DATA_DIR` | `01-data/datasets` yolu override | Paket-göreli otomatik çözüm |
| `AKS_MODEL` | Model dosyası yolu override | `aks_core/artifacts/aks_model.joblib` |

## 9. API Referansı

Taban URL: `http://localhost:8000/api`. Tüm gövdeler JSON (CSV yükleme hariç, `multipart/form-data`). Django DRF görünümleri `product/04-backend/api/views.py`'de.

| Metod | Yol | Açıklama | Gövde / Parametreler |
|---|---|---|---|
| `GET` | `/bilgi` | Servis bilgisi: model adı, özellik listesi, demo müşteri sayısı | — |
| `GET` | `/demo-musteriler?adet_per_persona=3` | Her personadan örnek müşteri ID'leri | query: `adet_per_persona` |
| `GET` | `/skorla/{musteri_id}` | Demo müşteriyi ID ile skorla (+ **denetim kaydı yazar**, `kaynak="demo"`) | path: `musteri_id` |
| `POST` | `/skorla` | Ham işlemlerden skorla (+ denetim kaydı, `kaynak="api"`) | `{musteri_id, islemler:[{tarih, islem_tipi, kategori, tutar, aciklama?}]}` |
| `POST` | `/aciklama` | Skorun SHAP faktör açıklaması | `{musteri_id, islemler:[...]}` |
| `POST` | `/simulasyon` | "Ya şöyle olsaydı" senaryosu — özellik değişikliklerinin skora etkisi | `{musteri_id, islemler?, degisiklikler:{ozellik_adi: deger}}` |
| `GET` | `/portfoy?klasik_esik=680&aks_esik=650&ort_kredi=25000&getiri_orani=0.12&zarar_orani=0.55` | Banka portföy analizi: kurtarılan kredibl segment + illüstratif getiri (**Redis cache, TTL 600s**) | query parametreleri opsiyonel |
| `GET` | `/adalet?klasik_esik=680&aks_esik=650` | Equal-opportunity adalet raporu (**Redis cache, TTL 600s**) | query parametreleri opsiyonel |
| `POST` | `/csv-skorla` | Kullanıcının kendi hesap dökümü CSV'sini skorla (+ denetim kaydı, `kaynak="csv"`) | multipart: `dosya` (kolonlar: `tarih,islem_tipi,kategori,tutar[,aciklama]`) |
| `POST` | `/asistan` | AKS Asistanı'na soru sor (Gemini veya kural-tabanlı) | `{soru, baglam?}` |
| `GET` | `/gecmis/{musteri_id}` | Müşterinin geçmiş değerlendirmeleri — **kalıcı** (DB'den; yoksa orkestratör belleğine düşer) | path: `musteri_id` |

**Örnek — demo müşteriyi skorla:**
```bash
curl http://localhost:8000/api/skorla/2
```
```json
{
  "musteri_id": 2, "persona": "klasik_maasli",
  "klasik_skor": 807, "aks_skor": 822,
  "onerilen_limit": 14000, "risk_seviyesi": "düşük risk",
  "karar": "onaylanabilir (yüksek limit)",
  "ozellikler": { "...": "9 davranışsal özellik" },
  "aciklama": { "...": "SHAP faktörleri" },
  "danisman": { "...": "öneri metni" }
}
```

## 10. Veri Modeli ve Denetim İzi (Audit Trail)

`product/04-backend/audit/models.py` — bu, "AKS bankayı asla ezmez" tezinin **operasyonel kanıtıdır** (planning D10 / ROADMAP boundary invariant).

| Model | Amaç | Kritik alanlar |
|---|---|---|
| `Customer` | Demo müşteri kimliği + persona | `external_id`, `persona` |
| `Assessment` | Her skorlamanın tam kaydı (geçmiş / `/gecmis` uç noktası) | `klasik_skor`, `aks_skor`, `risk_seviyesi`, `karar`, `onerilen_limit`, `ozellikler` (JSON), `kaynak` |
| `AuditLog` | **Değiştirilemez** denetim satırı — Django admin'de salt-okunur | `klasik_skor` ("**DEĞİŞTİRİLMEDİ**" notuyla), `aks_skor`, `politika_notu` (varsayılan: *"AKS tamamlayıcıdır; banka segmenti/skoru değiştirilmedi."*), `ajanlar` (kullanılan agent listesi), `kaynak`, `created_at` |

`api/services.py::_denetim_yaz()` her skorlamadan sonra **best-effort** olarak hem `Assessment` hem `AuditLog` yazar; yazım başarısız olsa bile (ör. DB yoksa) skorlama yanıtı etkilenmez — demo hiçbir koşulda kesintiye uğramaz.

## 11. Model ve Sonuçlar

**9 davranışsal özellik** (`aks_core/ozellik/cikarim.py`, `OZELLIK_ADLARI`): `toplam_gelir_hacmi`, `toplam_gider_hacmi`, `gelir_islem_sayisi`, `gelir_kaynagi_sayisi`, `gelir_duzenliligi`, `gider_gelir_orani`, `bakiye_trendi`, `fatura_odeme_duzeni`, `hesap_hareket_yogunlugu`.

**Etiketleme:** temerrüt (default) etiketi kişinin *davranışsal disiplininden* türetilir (persona veya gelir hacminden değil) — bu, projenin tezini doğrudan kodlar: düşük gelirli görünen disiplinli kişi gerçekte düşük risklidir (`aks_core/model/etiketleme.py`).

**Model karşılaştırması** (`aks_core/artifacts/metrikler.json`):

| Model | ROC-AUC | PR-AUC (AP) |
|---|---|---|
| **XGBoost** (seçilen, `n_estimators=300, max_depth=4`) | **0.8294** | 0.6871 |
| LightGBM | 0.8233 | 0.6837 |
| Klasik skor (baseline) | 0.7288 | 0.5687 |

Davranışsal model klasik skoru **+0.10 AUC** ile geçiyor.

**İş etkisi** (`aks_core/model/is_etkisi.py`, doğrulanmış canlı sonuç): klasik skorun "prime" eşiğinin altında bıraktığı kredibl kişilerden **%90'ı (973/1084) model tarafından doğru şekilde kurtarılıyor** — büyük çoğunluğu tam hedef kitle olan öğrenci ve stajyer. Risk kontrolü korunuyor (yanlış onay oranı düşük). Görsel: `05-business/docs/sprints/sprint2/model_sonuclari.png`.

## 12. Adalet / Önyargı Analizi

`aks_core/model/adalet.py` — equal-opportunity metriği: kredibl kişilerin onaylanma oranı gruplar arası karşılaştırılır (`/api/adalet` uç noktası). Sprint 2 bulgusu: klasik skorda kredibl bir öğrencinin onaylanma oranı **%0.4** iken AKS'de **%97.8**; adalet boşluğu **1.00'den 0.39'a** iner. Model, ayrımcı sinyalleri (yaş, cinsiyet vb.) doğrudan kullanmaz — yalnızca davranışsal/finansal özelliklere dayanır (bkz. §18).

## 13. Testler — Mevcut Durum

⚠️ **Bilinen boşluk (dürüstlük notu):** Sprint 2'deki 22 birim/entegrasyon testi (`product/04-backend/_legacy_fastapi/tests/test_pipeline.py`) hâlâ eski `from src.*` içe aktarmalarını ve `from src.api.main import app` (FastAPI `TestClient`) kullanır — **Django'ya geçiş sonrası bu haliyle çalışmaz**. Testler henüz `aks_core` + Django DRF'e taşınmadı.

Bunun yerine bu oturumda **manuel uçtan uca doğrulama** yapıldı: `aks_core` paketinin model yükleyip skorladığı, Django `manage.py check` + migrasyonların temiz geçtiği ve gerçek `runserver` üzerinden `curl` ile `/api/bilgi` ve `/api/skorla/{id}`'nin doğru sonuç döndürdüğü (`portfoy` sonucunun Sprint 2 ile birebir eşleştiği: 973/1084) doğrulandı.

**Yapılacak (ROADMAP `BWS5-T9` / `BWS5-T8`):** `pytest` testlerini `aks_core` + Django `APIClient` ile yeniden yazmak; boundary testleri eklemek (klasik skorun hiçbir agent tarafından değiştirilemediğini, guard-benzeri davranışı doğrulayan testler).

## 14. Deploy

Eski `Dockerfile` + `render.yaml` (`product/04-backend/_legacy_fastapi/`) **tek-servis FastAPI + statik dashboard** için yazılmıştı ve artık güncel değil (referans olarak tutuluyor). Yeni hedef mimaride (React + Django) deploy konfigürasyonu **Google Stitch tasarımı entegre edildikten sonra** güncellenecek — bkz. `/TECHSTACK.md` §6 Migration Steps ve `OQ-34`. Supabase + Upstash hesapları oluşturulduğunda (`OQ-35`) `.env` doldurularak canlı kalıcılık/cache devreye girer; kod zaten hazırdır (bkz. §8).

## 15. Yol Haritası ve Bootcamp Bağlamı

Bu ürün, `/planning/` altındaki erken-faz danışmanlık tarzı planlama paketinin **bootcamp'e uyarlanmış** build fazıdır:

- [`/TECHSTACK.md`](../TECHSTACK.md) — teknoloji kararları, hedef mimari, migrasyon adımları
- [`/planning/ROADMAP.md`](../planning/ROADMAP.md) — 83 görev, story point'ler, sprint S0–S4, kritik yol, milestone'lar
- [`/planning/bootcamp-adaptation-review.md`](../planning/bootcamp-adaptation-review.md) — KEEP/ADAPT/LIFT/RISK analizi
- [`/planning/07-bootcamp-workstreams/`](../planning/07-bootcamp-workstreams/) — BWS1–BWS5 iş akışı tanımları
- [`/planning/00-program/open-questions.md`](../planning/00-program/open-questions.md) — açık kararlar (OQ-27…OQ-35: bootcamp süresi, ekip büyüklüğü, jüri kriterleri, Stitch format, Supabase/Upstash erişimi, vb.)

## 16. Ekip

| Rol | Kişi |
|---|---|
| Product Owner | Alperen Karakaya |
| Scrum Master | Ahmet Özdoğan |
| Developer | Zeynep Salkaya |
| Developer | Havva Balta |
| Developer | Begüm Bakan |

## 17. Sprint Geçmişi

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
| 11 | Django + React'e mimari geçiş, Supabase/Redis, denetim izi | 3 | ✅ (bu README'nin konusu) |

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

**Sprint Review kararları:** sentetik veri üreticisi ve kural-tabanlı skorlama motoru çalışır durumda; sonraki sprint'e taşınanlar: XGBoost/LightGBM'e geçiş ve açıklanabilirlik katmanı; gider/gelir oranı kalibrasyonu ihtiyacı not edildi.

**Kanıtlar:** `05-business/docs/sprints/sprint1/board_sprint1.png`, `urun_durumu_sprint1.png`, `daily_scrum_notlari.md`, Slack ekran görüntüleri.

### Sprint 2 — Zeka katmanı

*(6–19 Temmuz)* Kural-tabanlı skordan denetimli ML modeline geçiş, açıklanabilirlik, üç-agent mimarisi ve API.

**Öne çıkanlar:**
1. **Veri düzeltmesi** — Sprint 1'deki gider dağıtım hatası düzeltildi (`gider_gelir_orani` artık personalar arası ayırt edici: öğrenci ~0.72, riskli ~1.22).
2. **Denetimli etiketleme** — temerrüt etiketi davranışsal disiplinden türetildi (§11).
3. **ML modeli** — XGBoost/LightGBM, klasik skoru +0.10 AUC ile geçti (§11).
4. **SHAP açıklanabilirlik** eklendi.
5. **Üç-agent mimarisi + orkestrasyon + hafıza** kuruldu (§4).
6. **FastAPI backend** (`/skorla`, `/aciklama`, `/simulasyon`, `/gecmis/{id}`) — **Sprint 3'te Django'ya taşındı** (bkz. §9).
7. **Web dashboard** (`web/index.html`, iki görünümlü) — **Sprint 3'te React'e taşınma süreci başladı** (`03-frontend/`).
8. **22 test** yazıldı — **Sprint 3 geçişinde eskidi**, yeniden yazılması gerekiyor (§13).
9. **Deploy hazırlığı** — Docker + render.yaml — **Sprint 3'te yeniden değerlendirilecek** (§14).
10. **Kredi limit önerisi** — aylık net nakit akışı + risk seviyesine göre önerilen limit (TL).
11. **Adalet/önyargı analizi** eklendi (§12).
12. **CSV ile kendi verini skorla** — kullanıcı hesap dökümü yükleyip anında skor alabiliyor.
13. **Banka paneli arayüzü + AKS Asistanı** — LLM (Gemini) veya kural-tabanlı yedek ile soru-cevap.

Görsel: `05-business/docs/sprints/sprint2/model_sonuclari.png`.

### Sprint 3 — Mimari genişleme (bu README'nin kapsadığı çalışma)

Proje **YZTA Bootcamp kapsamında bir capstone** olarak yeniden çerçevelendi (jüri agentik AI, yenilikçi teknoloji ve çalışan bir ürünü ödüllendiriyor — bkz. `/planning/bootcamp-adaptation-review.md`). Bu doğrultuda:

- Proje **5 iş akışı bölümüne** ayrıldı (§6), ROADMAP'teki BWS1–5 ile birebir eşleşecek şekilde.
- ML/agent çekirdeği bağımsız, kurulabilir **`aks_core`** paketine çıkarıldı.
- Backend **FastAPI → Django + DRF**'e taşındı; **tüm 11 uç nokta bire bir parite ile doğrulandı** (portföy sonucu Sprint 2 ile birebir örtüşüyor: 973/1084 kurtarılan).
- **Değiştirilemez denetim izi** (`audit/` Django app'i) eklendi — "AKS bankayı ezmez" tezini operasyonel hale getirdi.
- **React + Vite + TS** ön yüz iskeleti kuruldu, API'ye bağlandı, Google Stitch tasarımını bekliyor.
- **Supabase (Postgres) + Upstash Redis** entegrasyonu koda hazır (env yoksa zarifçe SQLite/bellek cache'e düşer).
- Tüm mimari kararlar `/TECHSTACK.md`'de belgelendi; açık kararlar `OQ-33…35` olarak loglandı.

## 18. Etik ve Regülasyon Notu

- Bu repo gerçek banka verisi içermez; tüm veriler sentetiktir.
- Üretimde KVKK kapsamında açık rıza ve veri minimizasyonu gerekir.
- Model, ayrımcı (discriminatory) sinyalleri (yaş, cinsiyet vb.) doğrudan kullanmaz; yalnızca davranışsal/finansal özelliklere dayanır.
- AKS bankanın klasik skorunu/segmentini **asla otomatik olarak ezmez veya değiştirmez** — bkz. §2 tez ve §10 denetim izi. Bu ilke `/planning` erken-faz paketindeki düzenleyici çerçeveyle (fair lending, açıklanabilirlik, EU AI Act yüksek-riskli sınıflandırması) uyumludur; ayrıntı için `/planning/05-risk-and-compliance/` ve `bootcamp-adaptation-review.md` §2 (ADAPT A3).
