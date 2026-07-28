# AKS — Frontend Yeniden Yazımı için Teknik Devir Belgesi

> **Bu belge bir 4. "source of truth" değildir.** Gerçek kaynak hâlâ
> `overview.md` / `architecture.md` / `execution.md` üçlüsüdür (CLAUDE.md).
> Bu dosya, `product/03-frontend`'i sıfırdan yeniden yazacak birinin (insan
> veya ajan) backend'e dokunmadan çalışabilmesi için gereken **her şeyi tek
> yerde** toplayan, kod parçalarıyla desteklenmiş bir **anlık görüntü**dür.
> Tarih: 2026-07-27, commit `a0652d8` sonrası. Backend/aks_core değişirse bu
> belge eskir — güncel doğruluk için üç kök belge + kod esastır.
>
> Amaç: yeni frontend, burada anlatılan API sözleşmesine göre yazılacak.
> Backend'te (Django/aks_core) hiçbir değişiklik gerekmiyor; bu tamamen bir
> **istemci** yeniden yazımı.

---

## 1. Ürün nedir (30 saniyede)

AKS (Alternatif Kapasite Skoru), bankaların klasik kredi skoruna **ek**
(asla onun yerine geçmeyen) bir "ödeme kapasitesi" skoru üretir — banka
ekstresi/işlem geçmişinden davranışsal özellikler çıkarıp bir ML modeliyle
300–850 arası bir skor, risk seviyesi, karar ve önerilen limit üretir.

**Bağlayıcı sınır ilkesi:** AKS bankanın klasik skorunu **asla ezmez**,
yalnızca tamamlar. Bu her API yanıtında ve her ekranda görünür olmalı
(`klasik_skor` alanı asla gizlenmez/değiştirilmez).

**Üç ayrı kullanıcı yüzeyi var — üçü de farklı oturum/nav'a sahip:**

1. **Banka içi araştırma/demo arayüzü** (`/`, `/portfolio`, `/audit`,
   `/customers`, `/upload`) — **YALNIZCA YÖNETİCİ** (`is_staff`) hesaplara
   açık; jüriye/analiste model kanıtı gösterir. Gerçek müşteri verisi YOK,
   sentetik demo popülasyonu var — ama tüm demo popülasyonunu ve toplu
   istatistikleri gösterdiği için "herkesi gören" tek yüzeydir, bu yüzden
   yetkilendirilmiştir (execution.md §3b Phase 7/7.11).
2. **Müşteri portalı** (`/portal/*`) — e-posta/şifre ile giriş yapan gerçek
   son kullanıcı kendi ekstresini yükler, kendi geçmişini görür, kurumların
   erişim taleplerini onaylar/reddeder.
3. **Kurum (banka personeli) arayüzü** (`/kurum/*`) — banka çalışanı giriş
   yapar, yalnızca **aktif rızası olan** müşterileri AKS numarasıyla görür.

Bu üç yüzey **tamamen ayrı navigasyon/layout** kullanır ve birbirine
karışmamalı (aşağıda §6'da üç ayrı `Layout` bileşeni var).

---

## 2. Teknoloji yığını ve çalıştırma

| Katman | Teknoloji | Konum |
|---|---|---|
| Backend | Django 5.2 + DRF, SQLite (dev) / Postgres (Supabase, prod) | `product/04-backend/` |
| AI çekirdeği | Saf Python paketi (`aks_core`), Django'dan bağımsız, `pip install -e` ile editable kurulur | `product/02-ai-agents/` |
| Frontend (mevcut, DEĞİŞECEK) | React 18 + Vite 5 + TypeScript + Tailwind 3 | `product/03-frontend/` |
| Cache | Redis (Upstash) yoksa in-memory (LocMemCache) | — |

**Yerel çalıştırma (backend değişmiyor, referans için):**

```bash
# Backend
cd product/04-backend
pip install -r requirements.txt
pip install -e ../02-ai-agents
python manage.py migrate
python manage.py runserver          # http://127.0.0.1:8000

# Frontend (Vite dev proxy /api -> 127.0.0.1:8000, bkz. vite.config.ts)
cd product/03-frontend
npm install
npm run dev                          # http://localhost:5173
```

`npm run build` → `tsc --noEmit && vite build`. Yeni frontend de bu iki
komuta cevap vermeli (CI/deploy bunlara bakıyor olabilir).

---

## 3. Kimlik doğrulama ve oturum modeli (kritik — yanlış yapılırsa hiçbir şey çalışmaz)

Backend **tek bir** Django session tabanlı oturum sistemi kullanıyor (aynı
`django.contrib.auth.User`, `sessionid` çerezi) — ama bu oturum **üç farklı
"kim bu kullanıcı" anlamına** gelebilir. Login endpoint'i HER ZAMAN aynı,
`POST /api/auth/giris`; ayrım kullanıcının hangi yan-tablolara sahip
olduğunda:

- **Sıradan müşteri (portal) oturumu**: her yeni kayıtta (`POST /api/auth/kayit`)
  otomatik bir `kimlik.Profil` (rastgele AKS numarası) oluşturulur. Bu
  hesabın `is_staff=False` ve `KurumUyeligi` yoktur.
- **Kurum oturumu**: kullanıcı bir `kimlik.KurumUyeligi` satırına sahip
  olmalı (nasıl oluşturulduğu: `python manage.py bootstrap_kurum` —
  management command, `kimlik/management/`).
- **Yönetici (banka içi araştırma) oturumu** — execution.md §3b Phase 7/7.11
  ile eklendi: `User.is_staff=True`. Bu, `api/views.py` altındaki TÜM demo/
  araştırma uçlarını (`/api/demo-musteriler`, `/api/portfoy`, `/api/gecmis/…`,
  …) açan tek bayrak; `python manage.py bootstrap_demo_hesaplar` ile kurulan
  demo hesabı `admin@aks.com` bu tiptedir. `is_staff` kasıtlı seçildi — ayrı
  bir rol tablosu yerine Django'nun kendi yönetici bayrağı kullanıldı, çünkü
  bu yüzey admin paneliyle aynı güven seviyesini gerektiriyor.

**`GET /api/auth/ben` yanıtına eklenen `yonetici`/`kurum_uyesi` bayrakları**
(bkz. §4.2) frontend'in bu üç oturumu ayırt etmesinin kanonik yoludur —
`aks_no` alanının varlığına bakmak yerine bu ikisi kullanılmalı. **Bunlar
yalnızca YÖNLENDİRME ipucudur**, gerçek yetki her API ucunda sunucuda
zorlanır (`YoneticiKullanici` / `KurumUyesi` / `ProfilSahibi`) — tarayıcıda
bu bayrağı taklit etmek hiçbir veriye erişim sağlamaz, yalnızca 403 alınır.

**CSRF akışı (frontend'in doğru yapması gereken en kırılgan kısım):**

DRF'nin `SessionAuthentication`'ı, session-authenticated her `POST/PUT/DELETE`
isteğinde CSRF token zorunlu kılar. Django'nun normal `CsrfViewMiddleware`'i
DRF view'larında devre dışı; bunun yerine:

1. Sayfa açılışında **mutlaka** `GET /api/auth/ben` çağrılır — bu endpoint
   `@ensure_csrf_cookie` ile işaretli, yanıt ne olursa olsun (200 ya da 401)
   tarayıcıya `csrftoken` çerezini set eder.
2. Her sonraki `POST` isteğinde bu çerez okunup `X-CSRFToken` header'ına
   konur.
3. Tüm istekler `credentials: "same-origin"` ile atılır (Vite dev proxy
   `/api`'yi aynı origin'den Django'ya yönlendirdiği için `same-origin`
   yeterli — cross-origin bir kuruluma geçilirse `credentials: "include"` +
   `CORS_ALLOW_CREDENTIALS=True` + `CORS_ALLOWED_ORIGINS`/`CSRF_TRUSTED_ORIGINS`
   güncellemesi gerekir, bkz. `config/settings.py`).

Mevcut `api.ts`'teki referans implementasyon (yeni frontend bunu birebir
tekrar etmeli, yeni bir HTTP katmanı icat etmemeli):

```ts
function csrfTokenAl(): string | null {
  const eslesme = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return eslesme ? decodeURIComponent(eslesme[1]) : null;
}

async function post<T>(yol: string, govde: unknown): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(csrfTokenAl() ? { "X-CSRFToken": csrfTokenAl()! } : {}),
    },
    body: JSON.stringify(govde),
  });
  const yanit = await r.json().catch(() => null);
  if (!r.ok) throw new Error(_hataMesaji(yanit, r));
  return yanit as T;
}
```

Dosya yükleme (multipart) için `Content-Type` **elle set edilmez** —
tarayıcı boundary'yi kendisi ekler; elle yazmak isteği backend'de
parse edilemez hale getirir (bu, geçmişte gerçek bir hata kaynağıydı).

**Oturum tipi ayrımı frontend'de nasıl anlaşılır:**
- `GET /api/auth/ben` → 401 ise: giriş yok → `/giris`'e (`Layout`) veya
  ilgili yüzeyin kendi giriş sayfasına (`PortalLayout` → `/portal/giris`,
  `KurumLayout` → `/kurum/giris`) yönlendirilir.
- 200 dönerse gövdedeki `yonetici`/`kurum_uyesi` bayraklarına bakılır
  (yukarıdaki üçlü ayrım). `aks_no` alanı hâlâ vardır ama artık AYRIM için
  KULLANILMAMALI — bir yönetici hesabının da `Profil`'i (dolayısıyla
  `aks_no`'su) olabilir, tersi de mümkündür; bayraklar bunun için var.
- `GET /api/kimlik/kurum/ben` → 403 ise: bu kullanıcı hiçbir kuruma üye
  değil (kurum-taraflı sayfalarda ikinci bir doğrulama katmanı).

Dört `Layout`'un (`Layout`, `PortalLayout`, `KurumLayout` — `AnaSayfaPage`/
`GirisPage` layout kullanmaz) her biri kendi kapı mantığını uyguluyor (§6'da
tam kod var) — yeni frontend aynı deseni tekrar etmeli. `Layout` en katı
olanı: giriş yoksa `/giris`'e, giriş var ama `yonetici` değilse kendi
yüzeyine (`kurum_uyesi` ? kurum panel : portal) geri gönderir.

---

## 4. Tam API referansı

Taban yol: `/api` (kimlik uçları: `/api/kimlik`). Tüm yanıtlar JSON.
Hata yanıtı her zaman `{"hata": "..."}` şeklinde, HTTP status kodu ile
birlikte (400/401/403/404/409).

Aşağıdaki TypeScript tipleri **gerçek** backend yanıt şekilleridir (mevcut
`src/api.ts`'ten, ekstra alan yok, uydurma yok) — yeni frontend bu tipleri
aynen (ya da eşdeğerini) kullanmalı.

### 4.1 Banka içi demo/araştırma uçları (**yönetici — `is_staff` zorunlu**)

`/api/bilgi` dışındaki TÜM uçlar `YoneticiKullanici` izniyle korunur: giriş
yoksa 403, giriş var ama `is_staff` değilse yine 403. Yeniden yazılan
frontend bu sayfaları yalnızca `GET /api/auth/ben` yanıtında
`yonetici: true` görürse göstermeli; aksi halde kullanıcıyı kendi yüzeyine
(`kurum_uyesi` ise `/kurum/musteriler`, değilse `/portal`) yönlendirmeli.

| Method | Yol | Açıklama |
|---|---|---|
| GET | `/api/bilgi` | Servis bilgisi, model adı, özellik listesi — **tek girişsiz uç** |
| GET | `/api/metrikler` | CV+CI+kalibrasyon raporu (offline, `degerlendirme_raporu.json`) |
| GET | `/api/politika` | Karar bantları (300-850 → risk/karar/limit çarpanı) |
| GET | `/api/segmentasyon` | K-Means kümeleme raporu (denetimsiz, yalnızca araştırma) |
| GET | `/api/genelleme-saglamlik` | Persona-dışı genelleme + stres testi raporu |
| GET | `/api/risk-istahi` | 3 risk profili raporu (ihtiyatlı/dengeli/atak) |
| GET | `/api/demo-musteriler?adet_per_persona=8` | Persona → demo müşteri ID listesi |
| GET | `/api/skorla/<musteri_id>` | Demo müşteriyi skorla (tam `SkorSonuc`) |
| POST | `/api/aciklama` | SHAP açıklaması |
| POST | `/api/simulasyon` | What-if senaryo simülatörü |
| GET | `/api/portfoy` | Toplu portföy istatistikleri (⚠ döngüsel veri, `uyari` alanına bak) |
| GET | `/api/adalet` | Alt-grup adalet metrikleri (⚠ döngüsel veri) |
| POST | `/api/csv-skorla` | Belge yükleme (CSV/XLSX/PDF) — **artık yönetici gerektirir**; son kullanıcının karşılığı `/api/portal/yukle` |
| POST | `/api/asistan` | LLM/kural tabanlı danışman yanıtı |
| GET | `/api/gecmis/<musteri_id>` | **Demo** müşterinin skor geçmişi — portal (gerçek müşteri) kayıtlarını asla döndürmez |

**`SkorSonuc` (`GET /api/skorla/<id>`):**
```ts
interface SkorSonuc {
  musteri_id: number;
  persona: string;
  klasik_skor: number | null;      // banka skoru — DEĞİŞTİRİLMEZ, her zaman göster
  aks_skor: number;                // 300-850
  onerilen_limit: number | null;
  risk_seviyesi: string;
  karar: string;
  ozellikler: Record<string, number>;   // 9 davranışsal özellik, bkz. §5
  aciklama: { riski_artiran: FaktorEtki[]; riski_azaltan: FaktorEtki[] };
  danisman: { ozet: string; oneriler: string[]; dogal_dil?: string; dogal_dil_hatasi?: string };
  pd_geleneksel_bant: number | null;   // Formülasyon B — klasik_skor yoksa null
  pd_fark: number | null;
  kapasite_sinyali: number | null;     // 0-100, 50=nötr
  anomali_bayrak: boolean | null;      // yalnızca şeffaflık sinyali, KARARI ETKİLEMEZ
  anomali_skoru: number | null;
}
```

**`POST /api/csv-skorla`** (multipart, alan adı `dosya`) → `CsvSkorSonuc`:
```ts
interface BelgeMeta {
  kaynak_format: "csv" | "xlsx" | "pdf";
  kategori_guveni: number;         // 0-1; < 0.6 ise arayüzde açıkça uyar
  islem_sayisi: number;
  tarih_araligi?: { baslangic: string; bitis: string };
  pencere_gun?: number;
  beklenen_pencere_gun?: number;
  pencere_uyumlu?: boolean;        // model 180 günlük pencerede eğitildi
  atlanan_satir_orani?: number | null;
  bayraklar: string[];
  parmak_izi?: string;
  iz?: string[];                   // BelgeAgent'ın karar izi — "Agent İzi" panelinde göster
}
interface CsvSkorSonuc {
  islem_sayisi: number;
  aks_skor: number;
  risk_seviyesi: string;
  karar: string;
  onerilen_limit: number | null;
  aciklama: Aciklama;
  danisman: Danisman;
  anomali_bayrak: boolean | null;
  anomali_skoru: number | null;
  sahiplik_bayraklari?: string[];  // yalnızca portal yüklemesinde dolu, csv-skorla'da hep []
  belge_meta?: BelgeMeta;
}
```
Format hatasında (desteklenmeyen uzantı, min. işlem sayısının altı, bozuk
PDF) `400 {"hata": "..."}` döner — mesaj doğrudan kullanıcıya gösterilebilir
(backend zaten insan-okur üretiyor, frontend'in yeniden yorumlamasına
gerek yok).

**`Danisman` alanı ve `mod` üzerine not:** `POST /api/asistan` yanıtı
`{"yanit": str, "mod": "llm-arac" | "kural", "anlati_reddedildi": bool,
"arac_cagrilari": [...]}` şeklindedir (`danisman_llm.yanitla()`'nın
gerçek dönüş sözleşmesi). **Mevcut `api.ts`'teki `AsistanYanit.mod` tipi
yalnızca `"llm" | "kural"` içeriyor — `"llm-arac"` eksik, bu bir tip
tutarsızlığı** (bugün `ANTHROPIC_API_KEY` boş olduğu için hiç tetiklenmiyor,
ama anahtar eklenince — OQ-48 — canlı yanıtlar `mod: "llm-arac"` dönecek).
Yeni frontend `mod` alanını `string` olarak ele almalı ya da üç değeri de
kapsamalı: `"kural" | "llm" | "llm-arac"`.

### 4.2 Kullanıcı portalı — auth (girişsiz uçlar)

`KullaniciBilgisi` yanıtı `yonetici` ve `kurum_uyesi` bayraklarını da içerir;
giriş/kayıt sonrası yönlendirme bunlara göre yapılır (yönetici → `/`,
kurum üyesi → `/kurum/musteriler`, diğer → `/portal`). Bu bayraklar yalnızca
yönlendirme içindir — yetki her uçta sunucuda zorlanır.

| Method | Yol | Gövde | Yanıt |
|---|---|---|---|
| GET | `/api/auth/ben` | — | 200 `KullaniciBilgisi` / 401 `{giris_yapmamis:true}` — **her sayfa yüklemesinde çağrılmalı** (CSRF çerezini set eder) |
| POST | `/api/auth/kayit` | `{email, sifre}` | 201 `KullaniciBilgisi`, otomatik `Profil` oluşur |
| POST | `/api/auth/giris` | `{email, sifre}` | 200 `KullaniciBilgisi` / 401 |
| POST | `/api/auth/cikis` | — | `{cikis_yapildi:true}` |

```ts
interface KullaniciBilgisi {
  id: number; email: string; ad: string; aks_no?: string;
  yonetici?: boolean;     // is_staff — banka içi araştırma yüzeyine erişebilir
  kurum_uyesi?: boolean;  // KurumUyeligi var — kurum paneline erişebilir
}
```
`sifre` doğrulaması Django `MinimumLengthValidator` (min 8 karakter) +
standart Django parola kuralları (çok yaygın/tamamen sayısal parolalar
reddedilir) — hata mesajı `{"hata": "..."}` içinde Türkçe döner, frontend
doğrudan gösterebilir.

### 4.3 Kullanıcı portalı — belge yükleme + geçmiş (`ProfilSahibi`)

| Method | Yol | Gövde | Not |
|---|---|---|---|
| POST | `/api/portal/yukle` | multipart `dosya` + `beyan` ("true"/"false") | `beyan` ZORUNLU — yoksa 400 |
| GET | `/api/portal/gecmis` | — | Son 50 kayıt, özet liste |
| GET | `/api/portal/gecmis/<kayit_id>` | — | Tek kaydın TAM detayı, ham işlemler dahil |

```ts
interface PortalGecmisKayit {
  id: number; zaman: string; aks_skor: number; risk_seviyesi: string;
  karar: string; onerilen_limit: number | null; islem_sayisi: number;
}
interface PortalIslem {
  tarih: string; islem_tipi: string; kategori: string; tutar: number; aciklama: string;
}
interface PortalGecmisDetay {
  id: number; zaman: string; aks_skor: number; risk_seviyesi: string; karar: string;
  onerilen_limit: number | null; kaynak_format: string; sahiplik_bayraklari: string[];
  islemler: PortalIslem[];   // §3b Phase 7/7.9'da eklendi — PO kararı: ham veri saklanır
}
```
`portalYukle` çağrısı `CsvSkorSonuc` ile aynı şekli döner (§4.1). Ayırt edici
fark: `sahiplik_bayraklari` burada gerçekten dolabilir
(`coklu_sahiplik_supheli` / `profil_tutarsiz`) — **bu bayraklar kararı asla
değiştirmez**, yalnızca şeffaflık sinyalidir; UI'da bir "uyarı rozeti"
olarak gösterilmeli, kararı gizleyen/engelleyen bir şey OLMAMALI.

### 4.4 Kimlik / rıza — müşteri tarafı (`ProfilSahibi` = giriş yapmış + kendi `Profil`'i)

Taban: `/api/kimlik`

| Method | Yol | Gövde | Not |
|---|---|---|---|
| GET | `/profilim` | — | `{aks_no, telefon_dogrulandi_mi}` |
| POST | `/telefon/gonder` | `{telefon}` (E.164, ör. `+905551112233`) | Throttle: 5/dk. `DJANGO_DEBUG=true` VEYA `AKS_OTP_DEMO_KOD=true` iken yanıtta `demo_kod` döner (gerçek SMS sağlayıcısı yok — OQ; `debug_kod` eski ad, geriye dönük uyumluluk için hâlâ da döner) |
| POST | `/telefon/dogrula` | `{dogrulama_id, kod}` | 5 deneme hakkı, 5 dk geçerlilik |
| GET | `/erisim-talepleri` | — | Bu müşteriye gelen TÜM talepler (durum: bekliyor/onaylandi/reddedildi/iptal_edildi) |
| POST | `/erisim-talebi/<id>/onayla` | `{gecerlilik_gun?: number}` (varsayılan 30, 1-365 arası) | |
| POST | `/erisim-talebi/<id>/reddet` | — | |
| POST | `/erisim-talebi/<id>/iptal` | — | Yalnızca `onaylandi` durumundaki bir talep iptal edilebilir |
| GET | `/riza-defterim` | — | Append-only rıza defteri — kim, ne zaman, ne için eriştiğinin tam kaydı |

```ts
interface ErisimTalebiKaydi {
  id: number; kurum: string; kurum_kod: string; amac: string;
  durum: "bekliyor" | "onaylandi" | "reddedildi" | "iptal_edildi";
  gecerlilik_bitis: string | null; created_at: string; aktif_mi: boolean;
}
interface RizaDefteriKaydi { id: number; olay: string; kurum: string; amac: string; created_at: string; }
```

### 4.5 Kimlik / rıza — kurum tarafı (`KurumUyesi`)

| Method | Yol | Gövde | Not |
|---|---|---|---|
| GET | `/kurum/ben` | — | `{kurum, kurum_kod}` |
| POST | `/kurum/erisim-talebi` | `{aks_no, amac}` | Throttle: 20/saat. Geçersiz AKS no formatı → 400; müşteri yok → 404; zaten bekleyen talep var → 409 |
| GET | `/kurum/musteriler` | — | **Yalnızca şu an aktif rızası olan** müşteriler |
| GET | `/kurum/musteri/<aks_no>` | — | Rıza yoksa/süresi dolmuşsa/iptal edilmişse **403** |

```ts
interface KurumMusteriOzet { aks_no: string; amac: string; gecerlilik_bitis: string; }
interface MusteriRiskIstahiSonucu { ad: string; onaylanir_mi: boolean; esik: number; }
interface KurumMusteriDetay {
  aks_no: string; degerlendirme_var: boolean;
  aks_skor?: number; risk_seviyesi?: string; karar?: string; onerilen_limit?: number | null;
  kaynak_format?: string; sahiplik_bayraklari?: string[]; created_at?: string;
  risk_istahi?: Record<"ihtiyatli"|"dengeli"|"atak", MusteriRiskIstahiSonucu> | null;
  aciklama?: Aciklama | null;
  not?: string;   // degerlendirme_var=false ise: "Bu müşteri henüz bir belge yüklememiş."
}
```
AKS numarası formatı (frontend'de format-doğrulama için): `AKS-XXXX-XXXX-XX`
(Crockford Base32 + checksum, `kimlik/aks_no.py::gecerli_mi`).

---

## 5. Skorlama modeli — frontend'in bilmesi gereken kadarı

9 davranışsal özellik (`OZELLIK_ADLARI`, `aks_core/ozellik/cikarim.py`) —
her `ozellikler` sözlüğünde bu anahtarlar bulunur, açıklama/what-if
ekranları bunları isimlendirirken kullanır:

```
toplam_gelir_hacmi, toplam_gider_hacmi, gelir_islem_sayisi,
gelir_kaynagi_sayisi, gelir_duzenliligi, gider_gelir_orani,
bakiye_trendi, fatura_odeme_duzeni, hesap_hareket_yogunlugu
```

**Karar bantları** (`GET /api/politika`'dan canlı çekilmeli, frontend'de
hardcode EDİLMEMELİ — mevcut kod bunu `U21` kararıyla zaten tek kaynağa
taşımış durumda):

| AKS eşik | Risk seviyesi | Karar | Limit çarpanı |
|---|---|---|---|
| ≥720 | düşük risk | onaylanabilir (yüksek limit) | 8× aylık net nakit akışı |
| ≥620 | orta-düşük risk | onaylanabilir (standart limit) | 5× |
| ≥540 | orta risk | koşullu / düşük limitle onaylanabilir | 2× |
| ≥300 | yüksek risk | ek teminat/gözden geçirme önerilir | 0× |

**4 bilinen persona** (demo verisinde/segmentasyonda geçer, uydurma
segment adı YOK):
```ts
const PERSONA_ETIKET: Record<string, string> = {
  ogrenci_yuksek_hacim: "Öğrenci (Yüksek Hacim)",
  stajyer_degisken_gelir: "Stajyer / Değişken Gelir",
  klasik_maasli: "Klasik Maaşlı",
  dusuk_hacim_riskli: "Düşük Hacim (Riskli)",
};
```

**Döngüsellik uyarısı — kritik, frontend her yerde saygı göstermeli:**
`/api/portfoy` ve `/api/adalet` yanıtlarının `veri_kaynagi: "dongusel"` ve
`uyari: "..."` alanları var. Bu iki uç, hâlâ döngüsel-etiketli sentetik veri
üzerinden hesaplanıyor (tekil skorlama gibi dekuple/gerçek model değil).
**Bu `uyari` metni her zaman görünür şekilde render edilmeli** — CLAUDE.md'nin
bağlayıcı kuralı: döngüsel/doğrulanmamış sayılar asla "doğrulanmış" gibi
sunulamaz. Aynı desen `risk_istahi` (`RiskIstahiRaporu.uyari`) ve
`genelleme_saglamlik`/`segmentasyon` raporlarında da var — her birinin kendi
`uyari`/`not`/`gerekce` alanı okunup gösterilmeli, sessizce atlanmamalı.

---

## 6. Mevcut frontend envanteri (referans — yeniden yazımın kapsamı)

### Rota haritası (`App.tsx`)

```
/                          AnaSayfaPage                   (herkese açık ana sayfa — veri yok, yalnızca tanıtım + CTA)
/giris                     GirisPage                      (site geneli landing: Kullanıcı / Kurum kutucukları,
                                                           her birinin altında kendi giriş alanları + demo bilgileri)
/panel                     Layout → IntelligencePage      (banka içi, demo/araştırma — YALNIZCA yönetici)
/portfolio                 Layout → PortfolioPage
/audit                     Layout → AuditPage
/customers                 Layout → CustomersPage
/customers/:id             Layout → CustomerDetailPage
/upload                    Layout → CsvUploadPage         (yönetici, /api/csv-skorla)

/portal/giris               PortalLoginPage                (giriş/kayıt formu, iki sekme)
/portal                    PortalLayout → PortalPage       (belge yükle + Geçmişim, açılır-kapanır işlem tablosu)
/portal/profilim           PortalLayout → PortalProfilPage (AKS no, telefon doğrulama)
/portal/erisim-talepleri   PortalLayout → PortalTaleplerPage
/portal/riza-defterim      PortalLayout → PortalRizaPage

/kurum/giris                KurumLoginPage
/kurum/musteriler          KurumLayout → KurumMusterilerPage
/kurum/musteri/:aksNo      KurumLayout → KurumMusteriDetayPage

*                          BulunamadiPage (404)
```

### Üç `Layout` bileşeninin kapı mantığı

- **`Layout.tsx`** (banka içi): `api.ben()` çağırır. Giriş yoksa `/giris`'e,
  giriş var ama `yonetici` değilse kullanıcının kendi yüzeyine
  (`kurum_uyesi` ? `/kurum/musteriler` : `/portal`) `<Navigate replace>`
  eder. Yalnızca yönetici içeri girer. Üstte nav'da e-posta + "Çıkış" ve
  çapraz-yüzey linkleri ("Kullanıcı Portalı", "Kurum Girişi") var.
- **`PortalLayout.tsx`**: `api.ben()` çağırır; `kullanici?.aks_no` yoksa
  (giriş yok VEYA giriş var ama bu bir kurum kullanıcısı) `/portal/giris`'e
  `<Navigate replace>` eder. `<Outlet context={kullanici}>` ile alt
  sayfalara kullanıcı bilgisini geçirir (`useOutletContext<KullaniciBilgisi>()`
  deseni).
- **`KurumLayout.tsx`**: `api.kurumBen()` çağırır; hata (401/403) alırsa
  `/kurum/giris`'e yönlendirir. Aynı `Outlet context` deseni.

### Tasarım sistemi (Tailwind — yeniden yazımda korunması istenirse)

`tailwind.config.js`, Google Stitch "AKS Intelligence" tasarımından 1:1
taşınmış token'lar içeriyor: koyu tema (`background: #020617`), `primary:
#c3c0ff`, Material Design 3 renk rolleri (`surface-container-*`,
`on-*-container` vb.), `Geist` (body/display) + `JetBrains Mono` (label/kod)
font çifti, `material-symbols-outlined` ikon fontu (bkz. `Icon.tsx`).
Bu paletin yeni frontend'de korunup korunmayacağı bir **ürün/tasarım
kararı** — bu belge yalnızca mevcut durumu belgeliyor, karar vermiyor.

> **Sayfa sayfa tam kaynak kodu + Google Stitch brief'leri için:**
> [`planning/frontend-pages-full-source.md`](frontend-pages-full-source.md) —
> bu belgedeki §6 yalnızca özet; 15 sayfanın tamamının TSX kaynağı, her
> sayfa için "ne görünüyor" düzyazı anlatımı ve durum/etkileşim envanteri
> orada.

### `api.ts` deseni — yeniden yazımda tekrarlanması gereken sözleşme

- Tek dosyada tüm `interface` tanımları + `api = {...}` nesnesi altında tüm
  çağrılar — sayfa bileşenleri asla `fetch` çağırmıyor, hep `api.xxx()`
  üzerinden.
  ekleniyor).
- `get/post/postDosya` üç yardımcı fonksiyon her şeyi sarmalıyor (CSRF,
  credentials, hata normalize etme — bkz. §3).
- Yorum satırları hangi backend dosyasının hangi alanı ürettiğini iz sürüyor
  (`// bkz. api/services.py::degerlendir`) — bu izlenebilirlik yeni
  frontend'de de faydalı bir alışkanlık.

### Bilinen quirk'ler / tuzaklar (yeniden yazımda tekrar düşülmemesi gerekenler)

1. **CSRF çerezi** `auth/ben` çağrılmadan asla set edilmez — ilk POST'tan
   önce mutlaka bir GET/`ben()` çağrısı yapılmalı (mevcut kod bunu her
   layout'un `useEffect`'inde otomatik yapıyor).
2. **Multipart upload'ta `Content-Type` elle set edilmemeli** (§3).
3. **`vite.config.ts` proxy'si `127.0.0.1:8000` kullanıyor, `localhost`
   değil** — bazı ortamlarda Node `localhost`'u `::1`'e çözüp Django'nun
   yalnızca IPv4'te dinlediği durumlarda bağlantı hatası veriyordu.
4. **`mod: "llm-arac"` tip eksikliği** (§4.1'de detaylı).
5. **Anonim `/api/csv-skorla` yanıtında `sahiplik_bayraklari` her zaman
   boş dizi** — portal yüklemesiyle karıştırılmamalı, UI'da farklı
   davranmalı (biri kimliksiz demo, biri kimlikli gerçek kullanıcı).

---

## 7. Agent / LLM katmanı — frontend'in göstermesi gereken "iz"

Ürünün jüriye kanıtladığı iddia: LLM **asla** karar motoru değil, yalnızca
tanımlı araçlarla veri okuyan bir "danışman" katmanı. Frontend bunu
**görünür kılmalı**:

- `POST /api/asistan` yanıtındaki `arac_cagrilari` alanı (`[{arac, girdi,
  cikti}, ...]`) — bir "Agent İzi" / "Tool Trace" paneli olarak
  gösterilmeli (mevcut `IntelligencePage.tsx` bunu kısmen yapıyor).
- `CsvSkorSonuc.belge_meta.iz` — `BelgeAgent`'ın çok-stratejili karar
  sürecinin insan-okur cümleleri (`["Format tespiti: ...", "Strateji
  seçimi: ...", "Kalite kontrolü: ..."]`) — belge yükleme sonuç ekranında
  bir "Nasıl işlendi?" açılır paneli olarak gösterilebilir.
- `anlati_reddedildi: true` dönerse (LLM metninde araç çıktılarıyla
  eşleşmeyen bir sayı bulundu, deterministik yanıta düşüldü) — bu bir HATA
  değil, ürünün güvenlik mekanizmasının çalıştığının kanıtı; istenirse
  küçük bir "doğrulanmış kural motoruna düşüldü" notu gösterilebilir ama
  zorunlu değil.

`ANTHROPIC_API_KEY` bugün **boş** (bkz. §8) — bu yüzden bugün her yanıt
`mod: "kural"` ve `arac_cagrilari: []` dönüyor. Anahtar eklenince (OQ-48)
`mod: "llm-arac"` ve dolu `arac_cagrilari` görülecek; frontend her iki
durumu da düzgün render edecek şekilde yazılmalı (boş dizi = "araç
kullanılmadı", dolu dizi = "işte hangi veriye baktı").

---

## 8. Ortam değişkenleri (.env) — neyin dolu, neyin boş, neyin gerekli olduğu

Dosya: `product/04-backend/.env` (git'e girmiyor, `.env.example` şablonu
var). **Şu an TÜM değerler boş** — sistem tamamen varsayılanlarla
(SQLite + in-memory cache + deterministik kural motoru) çalışıyor. Hiçbiri
teknik olarak zorunlu değil ("demo her koşulda çalışır" ilkesi), ama
aşağıdakiler **PO'nun aktif olarak beklediği** eklemeler:

| Değişken | Şu an | Ne yapar | Doldurulursa |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | boş | `danisman_llm.py` tool-calling agent'ını açar | **PO'nun ekleyeceği** (OQ-48) — eklenince `/api/asistan` canlı Claude tool-calling'e geçer, sıfır kod değişikliği gerekmez. Model sabit `claude-sonnet-5`. |
| `GEMINI_API_KEY` | boş | Eski, ikincil zenginleştirme yolu (`asistan.py`) — yalnızca `ANTHROPIC_API_KEY` yoksa denenir | İsteğe bağlı, öncelik `ANTHROPIC_API_KEY`'de |
| `AKS_PEPPER` | boş → `SECRET_KEY`'e düşer | Telefon hash'lemede kullanılan HMAC anahtarı (`kimlik/telefon.py`) | **Prod'a çıkmadan önce** ayrı, rotasyona açık bir sır olarak set edilmeli — `SECRET_KEY`'den bağımsız olmalı |
| `DATABASE_URL` | boş → yerel SQLite | Supabase/Postgres bağlantısı | Prod'da Supabase connection string |
| `SUPABASE_URL` / `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` | boş | Şu an KOD TARAFINDA hiçbir yerde okunmuyor (yalnızca `.env.example`'da belgelenmiş bir gelecek-kullanım notu) — asıl DB bağlantısı `DATABASE_URL` üzerinden | Yalnızca Supabase'in kendi client SDK'sı kullanılacaksa gerekir; bugünkü Django ORM yolu için gereksiz |
| `REDIS_URL` | boş → in-memory cache | Upstash Redis | Prod'da birden fazla worker/process arasında cache paylaşımı gerekiyorsa |
| `DJANGO_SECRET_KEY` | dev placeholder | Django imzalama anahtarı | **Prod'a çıkmadan önce mutlaka** rastgele, gizli bir değerle değiştirilmeli |
| `DJANGO_DEBUG` | `true` | Hata sayfalarında tam traceback | **Prod'da `false` olmalı** |
| `AKS_OTP_DEMO_KOD` | `false` | `true` iken OTP kodu API yanıtında görünür (`demo_kod`) — SMS sağlayıcısı yok, `DEBUG`'tan KASITLI OLARAK ayrı (bu ortamda `DJANGO_DEBUG=false` ama OTP akışının yine de test edilebilmesi gerekiyordu) | **Prod'da `false` olmalı** — aksi halde OTP kodları herkese açık döner |
| `DJANGO_ALLOWED_HOSTS` | localhost/127.0.0.1 | Django `ALLOWED_HOSTS` | Prod domain(ler)i eklenmeli |
| `CORS_ALLOWED_ORIGINS` | Vite dev portları (5173/5174) | CORS + `CSRF_TRUSTED_ORIGINS` (aynı liste) | Yeni frontend başka bir origin'den (ör. ayrı bir prod domain) servis edilecekse bu listeye eklenmeli — **yeni frontend'in kendi origin'i buraya girmezse CSRF/CORS sessizce başarısız olur** |
| `AKS_DATA_DIR` / `AKS_MODEL` | boş → paket-içi varsayılan | `aks_core` veri/model yolu override'ı | Yalnızca model dosyaları paket dışına taşınırsa gerekir |

**Frontend'in kendi ortam değişkeni:** `product/03-frontend`'de
`VITE_API_BASE` (`api.ts:7`) — boşsa `/api` (aynı origin, Vite proxy)
kullanılır. Yeni frontend ayrı bir origin'den deploy edilecekse bu,
backend'in tam URL'sine set edilmeli VE backend'de `CORS_ALLOWED_ORIGINS`/
`CSRF_TRUSTED_ORIGINS`'e o origin eklenmeli — ikisi birlikte yapılmazsa
oturum/CSRF sessizce kırılır.

**Özet — "agent yapısını kurup çalıştırmak" için PO'nun yapması gereken tek
şey:** `product/04-backend/.env` içine `ANTHROPIC_API_KEY=sk-ant-...`
yazmak, backend'i yeniden başlatmak. Kod tarafında ek kurulum yok — modül
zaten anahtarın varlığını runtime'da kontrol ediyor (`services.py::asistan_yanit`).
Anahtar eklendikten sonra doğrulanması gereken tek şey OQ-48: canlı
tool-calling'in gerçekten `arac_cagrilari` doldurduğu ve `_dogrula()`
guard'ının uydurma bir sayı karşısında gerçekten devreye girdiğinin
uçtan uca kanıtı (bugüne kadar yalnızca anahtarsız/deterministik yol test
edildi).

---

## 9. Test ve regresyon güvencesi (yeni frontend backend'i bozmamalı)

Backend'e dokunulmuyorsa bile, yeni frontend'in beklediği sözleşmeyi
doğrulamak için:

```bash
cd product/02-ai-agents && python -m pytest tests/ -q     # aks_core (89 test)
cd product/04-backend && python manage.py test -v 2       # Django (66 test)
```

Bu testler API yanıt şekillerini (ör. `HamIslemSaklamaTesti`,
kiracılık/rıza sınır testleri) zaten kanıtlıyor — yeni frontend
geliştirilirken bu testlerin kırılmaması, sözleşmenin değişmediğinin en
güçlü kanıtı olur. Yeni frontend'in KENDİ test/typecheck komutu
(`npm run build` → `tsc --noEmit && vite build`) de CI'da bu şekilde
kalmalı.

---

## 10. Açık kalan, PO kararı gereken sorular (frontend'i etkileyenler)

`execution.md`'deki tam liste kaynak — burada yalnızca frontend'i
doğrudan ilgilendirenler özetlendi:

- **OQ-47 (SMS sağlayıcısı yok):** telefon doğrulama bugün yalnızca
  `AKS_OTP_DEMO_KOD=true` iken `demo_kod` ile çalışıyor. Prod'da gerçek bir SMS
  sağlayıcısı bağlanana kadar telefon doğrulama akışı canlıda kullanılamaz
  — yeni frontend bunu bir "demo modu" rozeti ile açıkça işaretlemeli.
- **OQ-48 (canlı `ANTHROPIC_API_KEY` testi):** §7/§8'de detaylı.
- **OQ-49 (bankanın demo/araştırma sayfalarının kaderi):** Intelligence/
  Portfolio/Audit/Customers sayfaları jüriye model kanıtı olarak gerekli
  mi kalacak yoksa yeni frontend'de küçültülüp arka plana mı atılacak —
  PO kararı bekliyor, bu belge bir yön önermiyor.
- **OQ-52 (pencere normalizasyonu):** model 180 günlük pencerede eğitildi;
  3 aylık bir ekstre yüklenirse `belge_meta.pencere_uyumlu: false` döner.
  Yeni frontend bu uyarıyı MUTLAKA göstermeli, sessizce yutmamalı.

---

## 11. Yeni frontend için önerilen kapsam kontrol listesi

Bu bir görev listesi değil, "aşağıdakilerin hepsini hâlâ karşılıyor mu"
kontrolü için:

- [ ] Herkese açık ana sayfa (`/`) + 3 girişli yüzey (banka içi/**yönetici**,
      portal/müşteri, kurum/personel), her birinin kendi oturum kapısı
- [ ] Banka içi yüzey `yonetici` bayrağı olmayan hesaba (giriş yapmış olsa
      bile) hiçbir veri göstermiyor — kendi yüzeyine geri yönlendiriyor
- [ ] `auth/ben` → CSRF çerezi → sonraki her POST'ta `X-CSRFToken`
- [ ] Multipart upload'ta `Content-Type` elle set edilmiyor
- [ ] Yükleme boyutu sınırı (10 MB, backend zaten uyguluyor) aşıldığında
      backend'in döndürdüğü mesaj olduğu gibi gösteriliyor
- [ ] `klasik_skor` her zaman gösteriliyor, hiçbir yerde gizlenmiyor/ezilmiyor
- [ ] `veri_kaynagi: "dongusel"` + `uyari` alanları her göründükleri yerde
      render ediliyor (portföy, adalet, risk iştahı, segmentasyon, genelleme)
- [ ] `sahiplik_bayraklari` / `anomali_bayrak` / `pencere_uyumlu` gibi
      bayraklar KARARI gizlemeden, yalnızca ek şeffaflık sinyali olarak
      gösteriliyor
- [ ] Agent izi (`arac_cagrilari`, `belge_meta.iz`) görünür bir panelde
- [ ] Kurum tarafı yalnızca `kurumMusteriler()`'in döndürdüğü aktif-rızalı
      müşterileri listeliyor, başka hiçbir müşteri arama/görüntüleme yolu yok
- [ ] `npm run build` (`tsc --noEmit && vite build`) temiz geçiyor
