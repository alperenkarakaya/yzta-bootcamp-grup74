# TECHSTACK — AKS (Alternatif Kapasite Skoru)
## Whole-project technology plan & target architecture

**Status:** Decided (this session). Supersedes the ad-hoc Sprint-2 stack. Drives the 5-section restructure and the FastAPI→Django migration.
**Owner project:** YZTA Bootcamp Grup 74 — see `product/frontend/README.md` (current) and `planning/ROADMAP.md` (workstreams BWS1–BWS5).

> **Hard boundary (product thesis = safety story):** AKS **complements, never replaces** the bank's classic score. The alternative score is an *additional* signal that rescues behaviorally-strong thin-file customers; it never overrides the bank's segment, never re-scores inside the bank's model, never auto-approves above policy. Every score is persisted as an immutable audit row. (Maps to `planning` source §4 and the ROADMAP boundary invariant.)

---

## 1. Decisions at a glance

| Layer | Decision | Rationale |
|---|---|---|
| **Frontend** | **React + Vite + TypeScript** (SPA) | Team choice; polished multi-view bank panel; Google Stitch design (HTML+Tailwind) integrated into React components |
| **Backend / API** | **Django + Django REST Framework** (replaces FastAPI) | Team choice; batteries-included ORM + migrations + **admin** (free audit-log browser) + **auth** — pairs naturally with Supabase Postgres and the audit-trail/auth requirements |
| **AI core** | **Keep** custom 3-agent orchestrator (`VeriAgent → SkorlamaAgent → DanismanAgent`) + `AsistanAgent` | Already meets the "agentic AI" jury criterion; framework-agnostic Python |
| **ML** | **Keep** XGBoost (AUC 0.829) + LightGBM + **SHAP** explainability + scikit-learn | Working and validated vs. classic-score baseline (0.729) |
| **LLM** | **Google Gemini** (via `GEMINI_API_KEY`), deterministic rule-based fallback | Already wired in `AsistanAgent`; fallback keeps demo working offline |
| **Database** | **Supabase (Postgres)** via Django ORM | Persist assessments, per-customer history (replaces in-memory `hafiza` dict), and the **audit trail**; optional Supabase Auth for the bank panel |
| **Cache / rate-limit** | **Upstash Redis** (`django-redis`, `rediss://` TLS) | Cache heavy `/portfoy` & `/adalet` aggregates (they re-score *all* customers per call); rate-limit the LLM assistant |
| **Packaging** | AI core as an installable package **`aks_core`** (`pip install -e`) | Both Django and the data/training scripts import one clean package; fixes the fragile `from src...` imports |
| **Deploy** | **Docker + Render** (Django serves built React bundle) · Supabase + Upstash hosted | One web service; keeps existing Render familiarity |
| **Preview ("simple tool")** | `python manage.py runserver` + `npm run dev` (Vite) locally; browser at `http://localhost:5173` (dev) / `:8000` (integrated) | The requested way to see UI changes live |

**Toolchain present:** Python 3.11.9, Node 18.14.0, npm 9.3.1. To add: Django, DRF, `dj-database-url`, `psycopg2-binary`, `django-redis`, `django-cors-headers`, `python-dotenv`; frontend via Vite.

---

## 2. Target architecture

```
┌────────────────────────────────────────────────────────────────┐
│  03-frontend  —  React + Vite + TS  (Google Stitch design)       │
│  Customer eval · Portfolio · Fairness · AKS Assistant            │
└───────────────┬────────────────────────────────────────────────┘
                │ REST (JSON) / CORS
                ▼
┌────────────────────────────────────────────────────────────────┐
│  04-backend  —  Django + DRF                                     │
│  /api/skorla /aciklama /simulasyon /portfoy /adalet              │
│  /csv-skorla /asistan /gecmis                                    │
│  ├─ auth (Supabase / Django)   ├─ audit middleware (immutable)   │
│  └─ cache layer (Upstash Redis: portfoy_agg, adalet_agg, RL)     │
└───────┬───────────────────────────────────┬────────────────────┘
        │ imports                            │ ORM
        ▼                                    ▼
┌───────────────────────────┐   ┌────────────────────────────────┐
│ 02-ai-agents / aks_core    │   │ Supabase (Postgres)             │
│ Orkestrator (memory)       │   │ customers · assessments ·       │
│  VeriAgent→Skorlama→Danisman│   │ audit_log (segment untouched,   │
│ model/ (XGBoost, SHAP,     │   │  base→aks, policy bound, agent, │
│  adalet, is_etkisi)        │   │  timestamp)                     │
│ artifacts/ aks_model.joblib│   └────────────────────────────────┘
└───────────┬───────────────┘
            │ reads
            ▼
┌───────────────────────────┐
│ 01-data                    │
│ generator (uretici.py) ·   │
│ datasets (CSV) · EDA ·     │
│ data dictionary/bias       │
└───────────────────────────┘

05-business — domain, personas, success metrics, regulatory-awareness note
              (pointers into /planning: BWS1, D1/D5/D7/D9)
```

**Boundary enforcement in this architecture:** the classic (bank) score is read-only input; `SkorlamaAgent` only emits the *complementary* AKS score + a within-policy limit suggestion; the **audit middleware** writes an immutable row for every scoring (who/what/when, classic score unchanged); Django **admin** exposes the audit log for inspection. Nothing in the request path can mutate the bank's segment.

---

## 3. Repository layout (5 sections = 5 workstreams)

```
product/
├── README.md                     # how the 5 sections fit together
├── 01-data/            (BWS2)    # "data explore"
│   ├── generator/                #   uretici.py — synthetic transaction generator
│   ├── datasets/                 #   sentetik_islemler.csv, egitim_verisi.csv, skor_raporu.csv
│   ├── notebooks/                #   EDA (to add)
│   └── docs/                     #   data dictionary, quality/bias report (to add)
├── 02-ai-agents/       (BWS3)    # "ai & agents"
│   └── aks_core/                 #   installable package
│       ├── ozellik/              #     feature extraction (cikarim.py)
│       ├── model/                #     egitim, etiketleme, aciklama(SHAP), adalet, is_etkisi
│       ├── agents/               #     veri, skorlama, danisman, asistan, orkestrator
│       ├── artifacts/            #     aks_model.joblib, metrikler.json
│       └── pyproject.toml
├── 03-frontend/        (BWS4)    # React + Vite + TS  (Google Stitch UI)
├── 04-backend/         (BWS5)    # Django + DRF, Supabase, Redis, audit, tests, CI, deploy
│   ├── config/                   #   settings, urls, wsgi/asgi
│   ├── api/                      #   DRF views/serializers (ported endpoints)
│   ├── audit/                    #   models + middleware (audit trail)
│   ├── manage.py
│   └── requirements.txt
└── 05-business/        (BWS1)    # personas, metrics, regulatory-awareness (links to /planning)
```

**Import fix:** `from src.agents...` / `from src.model...` → `from aks_core.agents...` / `from aks_core.model...`. Model + dataset paths become package-relative (`importlib.resources`) or env-configurable (`AKS_VERI`, `AKS_MODEL`) so they work regardless of the process CWD (Django vs. scripts).

---

## 4. Environment & secrets contract (`.env` — never committed)

```
# LLM
GEMINI_API_KEY=...                     # optional; without it, assistant uses rule-based fallback

# Supabase (Postgres)
DATABASE_URL=postgresql://...supabase...:5432/postgres
SUPABASE_URL=https://<proj>.supabase.co
SUPABASE_ANON_KEY=...                  # frontend auth (if Supabase Auth used)
SUPABASE_SERVICE_ROLE_KEY=...          # backend only

# Upstash Redis
REDIS_URL=rediss://default:<token>@<host>.upstash.io:6379

# Django
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<render-domain>
CORS_ALLOWED_ORIGINS=http://localhost:5173,<frontend-domain>

# Data / model paths (optional overrides)
AKS_VERI=../01-data/datasets/sentetik_islemler.csv
AKS_MODEL=../02-ai-agents/aks_core/artifacts/aks_model.joblib
```
A committed `.env.example` documents these with placeholder values.

---

## 5. Local development & preview

```bash
# one-time
python -m venv .venv && .venv/Scripts/activate
pip install -e product/02-ai-agents            # aks_core
pip install -r product/04-backend/requirements.txt
cd product/03-frontend && npm install

# run (two terminals)
cd product/04-backend && python manage.py runserver      # API at :8000
cd product/03-frontend && npm run dev                     # UI at :5173 (proxies /api -> :8000)
```
For an integrated single-port preview (demo): `npm run build` in the frontend, Django serves the static bundle at `:8000`. This is the "simple tool to see the changes" — edit a component, Vite hot-reloads the browser.

---

## 6. Migration steps & status

| # | Step | Status |
|---|---|---|
| 0 | git init + baseline snapshot (restore point) | ✅ done |
| 1 | This TECHSTACK.md | ✅ done |
| 2 | Restructure `product/frontend/` → 5 sections; `src`→`aks_core`; fix imports; tests green | ⏳ next |
| 3 | Scaffold Django + DRF; port endpoints; keep behavior parity with FastAPI | ⏳ |
| 4 | Supabase ORM (customers/assessments/audit_log) + audit middleware | ⏳ |
| 5 | Upstash Redis cache (portfoy/adalet) + assistant rate-limit | ⏳ |
| 6 | React (Vite+TS) scaffold; integrate Google Stitch design when provided | ⏳ |
| 7 | Docker/Render update (Django serves React build); CI | ⏳ |

**Reversibility:** step 0 gives a clean baseline commit; each step lands as its own commit so any migration step can be rolled back independently.

---

## 7. Open decisions (routed to `planning/00-program/open-questions.md`)
- **OQ-33** — Supabase Auth vs. plain Django auth for the bank panel? (affects frontend login flow)
- **OQ-34** — Does Google Stitch export plain HTML+Tailwind or React/JSX? (affects integration effort in 03-frontend)
- Existing bootcamp unknowns still open: OQ-27 (duration), OQ-28 (team size), OQ-29 (mandated stack — now partly answered by this doc), OQ-30 (jury rubric), OQ-31 (demo format), OQ-32 (velocity).
