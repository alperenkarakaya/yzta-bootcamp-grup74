# AKS — Teknik Referans (Product Tech README)

**Bu dosya sadece teknik içerik içerir: mimari, kurulum, API, veri modeli, testler, deploy.** Ürün anlatısı (problem/çözüm/tez), personalar, ekip, sprint geçmişi ve bootcamp bağlamı için bkz. **[`/planning/README.md`](../planning/README.md)** — repo'nun ana/kapsamlı dosyası.

> Kök teknoloji planı ve karar gerekçeleri: [`/TECHSTACK.md`](../TECHSTACK.md) · Görev/sprint yol haritası: [`/planning/ROADMAP.md`](../planning/ROADMAP.md)

---

## İçindekiler

1. [Sınır (Boundary) — Mimariyi Şekillendiren Kural](#1-sınır-boundary--mimariyi-şekillendiren-kural)
2. [Mimari](#2-mimari)
3. [Teknoloji Yığını](#3-teknoloji-yığını)
4. [Proje Yapısı (5 Bölüm)](#4-proje-yapısı-5-bölüm)
5. [Kurulum ve Çalıştırma](#5-kurulum-ve-çalıştırma)
6. [Ortam Değişkenleri](#6-ortam-değişkenleri)
7. [API Referansı](#7-api-referansı)
8. [Veri Modeli ve Denetim İzi (Audit Trail)](#8-veri-modeli-ve-denetim-izi-audit-trail)
9. [Model ve Metrikler](#9-model-ve-metrikler)
10. [Adalet / Önyargı Analizi](#10-adalet--önyargı-analizi)
11. [Testler — Mevcut Durum](#11-testler--mevcut-durum)
12. [Deploy](#12-deploy)

---

## 1. Sınır (Boundary) — Mimariyi Şekillendiren Kural

> **AKS, bankanın klasik skorunu/segmentini asla ezmez veya değiştirmez — yalnızca tamamlar.**

Bu, kâğıt üzerinde bir taahhüt değil, koddaki bir gerçektir: her skorlama, bankanın klasik skorunu **değiştirilmeden** kaydeden değiştirilemez bir denetim satırı (`AuditLog`) üretir (bkz. [§8](#8-veri-modeli-ve-denetim-izi-audit-trail)). `SkorlamaAgent` yalnızca **tamamlayıcı** AKS skorunu üretir; klasik skor hiçbir agent tarafından okunup değiştirilmez. Ürün tezi ve bu kararın iş gerekçesi için bkz. `/planning/README.md`.

## 2. Mimari

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
│  api/   — 11 uç nokta (bkz. §7), servis katmanı aks_core'u sarar  │
│  audit/ — Customer · Assessment · AuditLog (değiştirilemez)       │
│  cache  — Upstash Redis (portföy/adalet agregatları, TTL)          │
└──────────┬──────────────────────────────────┬─────────────────────┘
           │ import (aks_core)                 │ ORM
           ▼                                    ▼
┌───────────────────────────────┐   ┌─────────────────────────────┐
│ 02-ai-agents/aks_core          │   │ Supabase (Postgres)           │
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
```

### Uçtan uca veri akışı (bir skorlama isteğinde)

```
Ham işlemler (CSV / demo / kullanıcı yüklemesi)
    │
    ▼  VeriAgent
Davranışsal özellikler (9 adet — bkz. §9)
    │
    ▼  SkorlamaAgent (XGBoost, aks_model.joblib)
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

Django admin panelinde (`/admin/`) `AuditLog` **salt-okunur**dur (`has_change_permission` / `has_delete_permission` = `False`).

## 3. Teknoloji Yığını

Tam gerekçelendirme ve ortam değişkeni sözleşmesi için bkz. [`/TECHSTACK.md`](../TECHSTACK.md). Özet:

| Katman | Teknoloji | Not |
|---|---|---|
| Frontend | **React 18 + Vite 5 + TypeScript** | `03-frontend/`; Google Stitch tasarımı entegre edilecek |
| Backend / API | **Django 5.2 + Django REST Framework 3.17** | `04-backend/`; eski FastAPI'nin yerini aldı |
| AI çekirdeği | Özel **3-agent orkestrasyon** (`aks_core.agents`) | Framework-agnostik, `pip install -e` ile kurulan paket |
| ML | **XGBoost** (birincil) + LightGBM (karşılaştırma) + scikit-learn | `aks_core/model/egitim.py` |
| Açıklanabilirlik | **SHAP** | `aks_core/model/aciklama.py` |
| LLM | **Google Gemini** (`GEMINI_API_KEY`), tanımlı değilse deterministik kural-tabanlı yedek | `aks_core/agents/asistan.py` — demo her koşulda çalışır |
| Veritabanı | **Supabase (Postgres)** üzerinden Django ORM; env yoksa yerel **SQLite**'a düşer | `04-backend/audit/models.py`, `config/settings.py` |
| Cache | **Upstash Redis** (`django-redis`); env yoksa yerel bellek cache | portföy/adalet agregatlarını önbellekler |
| Paketleme | `aks_core` — `pyproject.toml` ile editable-install | Hem Django hem CLI scriptleri aynı paketi kullanır |
| Deploy (hedef) | Docker + Render; Supabase + Upstash hosted | Eski Docker/render.yaml `04-backend/_legacy_fastapi/`'de referans olarak duruyor |

**Doğrulanmış araç zinciri:** Python 3.11.9 · Node 18.14.0 · npm 9.3.1 · Django 5.2.16 · DRF 3.17.1 · Vite 5.4.21. **Not:** `numpy<2` sabitlenmiştir — model artefaktları (XGBoost/SHAP) NumPy 1.x ile derlendi.

## 4. Proje Yapısı (5 Bölüm)

Proje, [`ROADMAP.md`](../planning/ROADMAP.md)'deki 5 iş akışını (BWS1–5) yansıtan 5 bölüme ayrılmıştır:

```
product/
├── PRODUCT_TECH_README.md          # bu dosya
├── 01-data/                         (BWS2 — Veri & Simülasyon)
│   ├── generator/
│   │   ├── veri/uretici.py          #   güncel sentetik işlem verisi üretici
│   │   ├── legacy_sentetik_veri_uretici.py   # Sprint 1 üretici (referans)
│   │   └── legacy_skor_hesaplama.py          # Sprint 1 kural-tabanlı skor (referans)
│   └── datasets/
│       ├── sentetik_islemler.csv    #   ~2000 müşteri, 180 gün işlem (~7.6 MB)
│       ├── egitim_verisi.csv        #   özellik çıkarımı sonrası eğitim seti
│       └── skor_raporu.csv          #   Sprint 1 skor çıktısı (referans)
│
├── 02-ai-agents/                    (BWS3 — AI Çekirdek ★ en yüksek jüri ağırlığı)
│   ├── pyproject.toml               #   aks-core paketi (editable install)
│   ├── requirements-core.txt        #   scikit-learn, xgboost, lightgbm, shap, joblib, numpy<2
│   └── aks_core/
│       ├── paths.py                 #   paket-göreli, CWD-bağımsız yol çözümü (AKS_DATA_DIR, AKS_MODEL)
│       ├── ozellik/cikarim.py       #   ham işlemlerden 9 davranışsal özellik
│       ├── model/
│       │   ├── egitim.py            #     XGBoost/LightGBM eğitimi + klasik skor karşılaştırması
│       │   ├── etiketleme.py        #     davranışsal disiplinden temerrüt etiketi türetimi
│       │   ├── aciklama.py          #     SHAP açıklayıcı
│       │   ├── adalet.py            #     equal-opportunity adalet raporu
│       │   └── is_etkisi.py         #     iş etkisi analizi (kurtarılan kredibl segment)
│       ├── agents/
│       │   ├── veri_agent.py        #     VeriAgent — özellik çıkarımı
│       │   ├── skorlama_agent.py    #     SkorlamaAgent — AKS skoru + karar
│       │   ├── danisman_agent.py    #     DanismanAgent — SHAP'tan öneri üretimi
│       │   ├── asistan.py           #     AsistanAgent — Gemini / kural-tabanlı soru-cevap
│       │   └── orkestrator.py       #     Orkestrator — 3 agent'ı sırayla çalıştırır + hafıza
│       └── artifacts/
│           ├── aks_model.joblib     #   eğitilmiş XGBoost modeli (paket içi)
│           └── metrikler.json       #   AUC/AP metrikleri (bkz. §9)
│
├── 03-frontend/                     (BWS4 — Ürün, UX & Açıklanabilirlik)
│   ├── src/
│   │   ├── api.ts                   #   tipli API istemcisi (Bilgi, SkorSonuc, Portfoy arayüzleri)
│   │   ├── App.tsx                  #   "döngüyü kanıtlayan" yer tutucu görünüm
│   │   ├── main.tsx, index.css, vite-env.d.ts
│   ├── vite.config.ts               #   dev proxy: /api -> http://localhost:8000
│   ├── package.json, tsconfig.json
│
├── 04-backend/                      (BWS5 — Mühendislik, Entegrasyon & Kalite)
│   ├── manage.py
│   ├── config/                      #   settings.py (env-driven, SQLite+LocMem fallback), urls.py, wsgi.py, asgi.py
│   ├── api/
│   │   ├── services.py              #   aks_core'u sarar: tekil Orkestrator/Asistan, denetim yazımı, cache
│   │   ├── views.py                 #   11 DRF view (bkz. §7)
│   │   └── urls.py
│   ├── audit/
│   │   ├── models.py                #   Customer, Assessment, AuditLog
│   │   ├── admin.py                 #   salt-okunur denetim izi paneli
│   │   └── migrations/
│   ├── requirements.txt
│   ├── .env.example                 #   tüm ortam değişkenlerinin şablonu (bkz. §6)
│   └── _legacy_fastapi/             #   ESKİ FastAPI + tek-dosya dashboard — PORTLAMA REFERANSI, CANLI DEĞİL
│       ├── api/main.py              #     eski uç noktalar (Django'ya taşındı)
│       ├── web/index.html           #     eski vanilla-JS bankacılık paneli
│       ├── tests/test_pipeline.py   #     eski testler (from src.* — artık geçersiz, bkz. §11)
│       ├── Dockerfile, render.yaml
│
└── 05-business/                     (BWS1 — İş & Alan; ürün anlatısı için bkz. /planning/README.md)
    └── docs/sprints/
        ├── sprint1/                 #   Daily Scrum notları, Slack ekran görüntüleri, board
        └── sprint2/                 #   model sonuçları görseli
```

## 5. Kurulum ve Çalıştırma

### 5.1 Ön koşullar
- Python **3.11+**
- Node.js **18+** / npm **9+**
- (Opsiyonel) Supabase projesi, Upstash Redis, Gemini API anahtarı — hiçbiri zorunlu değil, bkz. §6

### 5.2 Yerel geliştirme (iki terminal)

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

Tarayıcıda `http://localhost:5173` açın: "Skorla" butonu klasik vs AKS skorunu, riski, kararı ve önerilen limiti canlı olarak gösterir; portföy özeti otomatik yüklenir. Vite hot-reload ile her `App.tsx`/CSS değişikliği anında tarayıcıda görünür.

### 5.3 Tek-port entegre önizleme (demo günü tarzı)

```bash
cd product/03-frontend && npm run build     # dist/ üretir
# (Django'ya statik servis eklenmesi bu adımdan sonraki iş; şu an ayrı :5173/:8000 kullanın)
```

### 5.4 Modeli yeniden eğitmek / sentetik veri üretmek

```bash
# Sentetik işlem verisi üret (2000 müşteri, 180 gün)
python -m aks_core.model.egitim --girdi product/01-data/datasets/sentetik_islemler.csv

# ya da güncel üretici ile yeni veri üret:
python product/01-data/generator/veri/uretici.py --musteri-sayisi 2000 --gun 180 \
    --cikti product/01-data/datasets/sentetik_islemler.csv

# İş etkisi analizi
python -c "from aks_core.model.is_etkisi import analiz; print(analiz())"
```

### 5.5 Django admin (denetim izini görüntüleme)

```bash
cd product/04-backend
python manage.py createsuperuser
python manage.py runserver
# -> http://127.0.0.1:8000/admin/  (Denetim İzi bölümü salt-okunur)
```

## 6. Ortam Değişkenleri

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

## 7. API Referansı

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

## 8. Veri Modeli ve Denetim İzi (Audit Trail)

`product/04-backend/audit/models.py` — "AKS bankayı asla ezmez" tezinin **operasyonel kanıtıdır**.

| Model | Amaç | Kritik alanlar |
|---|---|---|
| `Customer` | Demo müşteri kimliği + persona | `external_id`, `persona` |
| `Assessment` | Her skorlamanın tam kaydı (geçmiş / `/gecmis` uç noktası) | `klasik_skor`, `aks_skor`, `risk_seviyesi`, `karar`, `onerilen_limit`, `ozellikler` (JSON), `kaynak` |
| `AuditLog` | **Değiştirilemez** denetim satırı — Django admin'de salt-okunur | `klasik_skor` ("**DEĞİŞTİRİLMEDİ**" notuyla), `aks_skor`, `politika_notu` (varsayılan: *"AKS tamamlayıcıdır; banka segmenti/skoru değiştirilmedi."*), `ajanlar` (kullanılan agent listesi), `kaynak`, `created_at` |

`api/services.py::_denetim_yaz()` her skorlamadan sonra **best-effort** olarak hem `Assessment` hem `AuditLog` yazar; yazım başarısız olsa bile (ör. DB yoksa) skorlama yanıtı etkilenmez — demo hiçbir koşulda kesintiye uğramaz.

## 9. Model ve Metrikler

**9 davranışsal özellik** (`aks_core/ozellik/cikarim.py`, `OZELLIK_ADLARI`): `toplam_gelir_hacmi`, `toplam_gider_hacmi`, `gelir_islem_sayisi`, `gelir_kaynagi_sayisi`, `gelir_duzenliligi`, `gider_gelir_orani`, `bakiye_trendi`, `fatura_odeme_duzeni`, `hesap_hareket_yogunlugu`.

**Etiketleme:** temerrüt (default) etiketi kişinin davranışsal disiplininden türetilir (persona veya gelir hacminden değil) — bkz. `aks_core/model/etiketleme.py`.

**Model karşılaştırması** (`aks_core/artifacts/metrikler.json`):

| Model | ROC-AUC | PR-AUC (AP) |
|---|---|---|
| **XGBoost** (seçilen, `n_estimators=300, max_depth=4`) | **0.8294** | 0.6871 |
| LightGBM | 0.8233 | 0.6837 |
| Klasik skor (baseline) | 0.7288 | 0.5687 |

**İş etkisi** (`aks_core/model/is_etkisi.py`, doğrulanmış canlı sonuç): klasik skorun "prime" eşiğinin altında bıraktığı kredibl kişilerden **%90'ı (973/1084) model tarafından doğru şekilde kurtarılıyor**. Görsel: `05-business/docs/sprints/sprint2/model_sonuclari.png`. İş sonuçlarının tam yorumu için bkz. `/planning/README.md`.

> ⚠️ **Metodolojik uyarı (bkz. `/planning/RESEARCH_STRATEGY.md`):** yukarıdaki AUC karşılaştırması ve iş etkisi rakamı, etiketin (`temerrut`) sentetik üretim mekanizmasıyla döngüsel (circular) bir ilişkisi olduğu tespit edilene kadar doğrulanmış sayılmamalıdır — ablasyon testi, XGBoost'un lojistik regresyondan farkının istatistiksel olarak anlamsız olduğunu (0.0004 AUC) ve etiketin gerçek nedensel yapısının sentetik üreticinin persona-koşullu tasarımına gömülü olduğunu gösteriyor. Rakamlar boru hattının uçtan uca çalıştığını kanıtlar, iş tezini henüz kanıtlamaz. Detay ve düzeltme planı: `/planning/RESEARCH_STRATEGY.md` §2.1, §4.

## 10. Adalet / Önyargı Analizi

`aks_core/model/adalet.py` — equal-opportunity metriği: kredibl kişilerin onaylanma oranı gruplar arası karşılaştırılır (`/api/adalet` uç noktası). Sonuç: klasik skorda kredibl bir öğrencinin onaylanma oranı **%0.4** iken AKS'de **%97.8**; adalet boşluğu **1.00'den 0.39'a** iner. Model, ayrımcı sinyalleri (yaş, cinsiyet vb.) doğrudan kullanmaz — yalnızca davranışsal/finansal özelliklere dayanır.

## 11. Testler — Mevcut Durum

⚠️ **Bilinen boşluk:** Sprint 2'deki 22 birim/entegrasyon testi (`product/04-backend/_legacy_fastapi/tests/test_pipeline.py`) hâlâ eski `from src.*` içe aktarmalarını ve `from src.api.main import app` (FastAPI `TestClient`) kullanır — **Django'ya geçiş sonrası bu haliyle çalışmaz**. Testler henüz `aks_core` + Django DRF'e taşınmadı.

Bunun yerine bu oturumda **manuel uçtan uca doğrulama** yapıldı: `aks_core` paketinin model yükleyip skorladığı, Django `manage.py check` + migrasyonların temiz geçtiği ve gerçek `runserver` üzerinden `curl` ile `/api/bilgi` ve `/api/skorla/{id}`'nin doğru sonuç döndürdüğü (`portfoy` sonucunun Sprint 2 ile birebir eşleştiği: 973/1084) doğrulandı.

**Yapılacak (ROADMAP `BWS5-T9` / `BWS5-T8`):** `pytest` testlerini `aks_core` + Django `APIClient` ile yeniden yazmak; boundary testleri eklemek (klasik skorun hiçbir agent tarafından değiştirilemediğini doğrulayan testler).

## 12. Deploy

Eski `Dockerfile` + `render.yaml` (`product/04-backend/_legacy_fastapi/`) **tek-servis FastAPI + statik dashboard** için yazılmıştı ve artık güncel değil (referans olarak tutuluyor). Yeni hedef mimaride (React + Django) deploy konfigürasyonu **Google Stitch tasarımı entegre edildikten sonra** güncellenecek — bkz. `/TECHSTACK.md` §6 Migration Steps ve `OQ-34`. Supabase + Upstash hesapları oluşturulduğunda (`OQ-35`) `.env` doldurularak canlı kalıcılık/cache devreye girer; kod zaten hazırdır (bkz. §6).

---

*Ürün anlatısı, personalar, ekip, sprint geçmişi, iş etkisi yorumu ve bootcamp bağlamı için: [`/planning/README.md`](../planning/README.md).*
