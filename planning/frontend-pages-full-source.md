# AKS — Frontend Sayfa Sayfa Tam Kaynak Kodu (Google Stitch girdisi)

> Bu dosya `frontend-rebuild-handoff.md`'yi tamamlar: burada API sözleşmesi
> değil, **her sayfanın gerçek kodu + ne gösterdiğinin düzyazı anlatımı**
> var. Amaç: Google Stitch'e (veya başka bir tasarım/kodlama aracına)
> "bu ekranı yeniden tasarla" derken hem görsel/UX niyeti hem tam veri
> sözleşmesini kaybetmeden aktarabilmek. Her sayfa için üç şey var:
> **(1) Stitch'e yazılabilecek düzyazı brief**, **(2) durum/etkileşim
> envanteri**, **(3) tam TSX kaynağı**. Tasarım artık değişecek —
> **kod (veri akışı, state, API çağrıları) değişmiyor**, bu yüzden Stitch'e
> "şu görünsün" derken kod bloklarındaki değişkenlerin/koşulların aynı
> kalması gerektiğini unutmayın.

> **Güncellik (Phase 7.11/7.12 sonrası).** Bu tur üç yapısal değişiklik
> getirdi, Stitch'e verilecek brief'lerde bunlar KORUNMALI:
> **(1)** Site kökü `/` artık herkese açık **ana sayfa** (`AnaSayfaPage`);
> banka panelinin ana ekranı `/panel`e taşındı — diğer panel yolları
> (`/portfolio`, `/customers`, …) yerinde kaldı.
> **(2)** Banka içi araştırma yüzeyi artık **oturumsuz değil**: yalnızca
> yönetici (`is_staff`) hesaplara açık, hem arayüzde (`Layout`) hem her API
> ucunda (`YoneticiKullanici`) zorlanıyor.
> **(3)** Site geneli giriş kapısı `/giris` (`GirisPage`) — Kullanıcı/Kurum
> kutucukları, giriş sonrası role göre yönlendirme.

Ortak alt yapı (her sayfa bunları kullanır, tekrar yazılmıyor):
`src/api.ts` (tam API istemcisi — bkz. `frontend-rebuild-handoff.md` §4),
`src/lib/skor.ts`, `src/components/Icon.tsx`, üç `Layout` bileşeni, tasarım
sistemi (`tailwind.config.js`, `index.css`, `index.html`) — hepsi bu
belgenin sonunda, §0'da.

---

## 0. Ortak alt yapı — tam kaynak

### `src/index.html` (font/ikon yükleme)
```html
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AKS Intelligence — Alternatif Kapasite Skoru</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&family=Geist:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```
İki font ailesi (**Geist** gövde/başlık, **JetBrains Mono** etiket/kod) +
**Material Symbols Outlined** ikon fontu Google Fonts'tan yükleniyor.

### `src/main.tsx`
```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### `src/index.css` (Stitch tasarım sisteminden birebir taşınan yardımcı sınıflar)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: #020617;
  color: #e5e1e4;
}

.ai-glow {
  box-shadow: 0 0 15px -5px rgba(79, 70, 229, 0.4);
}
.hairline-border {
  border: 1px solid rgba(70, 69, 85, 0.3);
}
.glass-header {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.05), transparent);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.glass-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 0.5px solid rgba(145, 143, 161, 0.2);
}
.card-surface {
  background-color: #0f172a;
  border: 1px solid rgba(70, 69, 85, 0.3);
}
.inner-shadow-subtle {
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.05);
}
.command-table-row:hover {
  background-color: rgba(79, 70, 229, 0.05);
  box-shadow: inset 2px 0 0 #4f46e5;
}
.ai-pulse {
  animation: pulse-indigo 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse-indigo {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
@keyframes shimmer {
  100% { transform: translateX(100%); }
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #353437; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #4f46e5; }
```
Tasarım dili: **koyu tema, cam-panel (glassmorphism), indigo/mor ai-glow
efektleri, monospace etiketler** — "terminal/komuta merkezi" hissi veren bir
fintik/analitik estetik. Stitch'e "koyu tema, camsı paneller, neon-indigo
vurgular, monospace data etiketleri, komuta-merkezi/terminal hissi" gibi
ifadelerle brief verilebilir.

### `src/components/Icon.tsx`
```tsx
// Material Symbols Outlined — index.html'de font olarak yüklü.
export function Icon({ name, className = "" }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>;
}
```
Kullanım: `<Icon name="upload_file" className="text-primary" />` — `name`
Google'ın [Material Symbols](https://fonts.google.com/icons) adlarından
biri (`upload_file`, `check_circle`, `warning`, `account_balance`,
`logout`, `chevron_right` vb. — kod boyunca ~30 farklı ikon adı geçiyor,
her sayfanın kod bloğunda görülebilir).

### `src/lib/skor.ts` (paylaşılan skor/format yardımcıları)
```ts
import { api } from "../api";

let _esikler = { klasik_esik: 680, aks_esik: 650 };
let _yuklendi = false;

export function politikaEsikleriniYukle(): void {
  if (_yuklendi) return;
  _yuklendi = true;
  api
    .politika()
    .then((p) => {
      if (p.portfoy_esikleri) _esikler = p.portfoy_esikleri;
    })
    .catch(() => {});
}

export type Durum = "kurtarildi" | "onaylandi" | "reddedildi";

export function durumBelirle(klasikSkor: number | null, aksSkor: number): Durum {
  const klasikRed = klasikSkor != null && klasikSkor < _esikler.klasik_esik;
  const aksOnay = aksSkor >= _esikler.aks_esik;
  if (klasikRed && aksOnay) return "kurtarildi";
  if (aksOnay) return "onaylandi";
  return "reddedildi";
}

export const DURUM_ETIKET: Record<Durum, string> = {
  kurtarildi: "Kurtarıldı",
  onaylandi: "Onaylandı",
  reddedildi: "Reddedildi",
};

export function skorDeltaYuzde(klasikSkor: number | null, aksSkor: number): number | null {
  if (klasikSkor == null || klasikSkor === 0) return null;
  return ((aksSkor - klasikSkor) / klasikSkor) * 100;
}

export function kapasiteYuzdesi(aksSkor: number): number {
  return Math.round(((aksSkor - 300) / (850 - 300)) * 100);
}

export function paraFormat(deger: number | null | undefined): string {
  if (deger == null) return "—";
  return `${deger.toLocaleString("tr-TR")} TL`;
}
```
`durumBelirle` üç etiketten birini üretir — **"Kurtarıldı"** (klasik skor
reddetmiş ama AKS onaylamış — ürünün ana pazarlama iddiası), "Onaylandı",
"Reddedildi". Eşikler `/api/politika`'dan çekilir, hardcode değildir.

### Üç `Layout` bileşeni — tam kaynak `frontend-rebuild-handoff.md` §6'da

| Bileşen | Yüzey | Kapı mantığı |
|---|---|---|
| `Layout.tsx` | Banka içi araştırma | `api.ben()` → oturum yoksa `/giris`; oturum var ama `yonetici` değilse kendi yüzeyine (`kurum_uyesi` ? `/kurum/musteriler` : `/portal`). Top + bottom nav, üstte e-posta + Çıkış. |
| `PortalLayout.tsx` | Müşteri portalı | `api.ben()` → `aks_no` yoksa `/portal/giris` |
| `KurumLayout.tsx` | Kurum paneli | `api.kurumBen()` → hata (401/403) alırsa `/kurum/giris` |

Üçü de aynı koyu/glass tasarım dilini paylaşır ama ayrı marka/nav taşır.
`AnaSayfaPage` ve `GirisPage` **hiçbir layout kullanmaz** — kendi tam-sayfa
düzenlerini kurarlar (§0.1 ve §0.2).

### `src/App.tsx` — tam rota tanımı
```tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import PortalLayout from "./components/PortalLayout";
import KurumLayout from "./components/KurumLayout";
import AnaSayfaPage from "./pages/AnaSayfaPage";
import GirisPage from "./pages/GirisPage";
import IntelligencePage from "./pages/IntelligencePage";
import PortfolioPage from "./pages/PortfolioPage";
import AuditPage from "./pages/AuditPage";
import CustomersPage from "./pages/CustomersPage";
import CustomerDetailPage from "./pages/CustomerDetailPage";
import CsvUploadPage from "./pages/CsvUploadPage";
import BulunamadiPage from "./pages/BulunamadiPage";
import PortalLoginPage from "./pages/portal/PortalLoginPage";
import PortalPage from "./pages/portal/PortalPage";
import PortalProfilPage from "./pages/portal/PortalProfilPage";
import PortalTaleplerPage from "./pages/portal/PortalTaleplerPage";
import PortalRizaPage from "./pages/portal/PortalRizaPage";
import KurumLoginPage from "./pages/kurum/KurumLoginPage";
import KurumMusterilerPage from "./pages/kurum/KurumMusterilerPage";
import KurumMusteriDetayPage from "./pages/kurum/KurumMusteriDetayPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Herkese açık ana sayfa — site kökü. Veri gösteren hiçbir şey yok,
            yalnızca ürünü anlatır ve doğru kapıya yönlendirir. */}
        <Route index element={<AnaSayfaPage />} />

        {/* Site geneli giriş — banka içi arayüzün önündeki zorunlu kapı */}
        <Route path="giris" element={<GirisPage />} />

        {/* Banka arayüzü (iç kullanım — demo/araştırma), YALNIZCA yönetici (bkz. Layout.tsx).
            Panel ana ekranı `/` iken `/panel`e taşındı (kök artık ana sayfa); diğer
            panel yolları geriye dönük uyumluluk için yerinde bırakıldı. */}
        <Route element={<Layout />}>
          <Route path="panel" element={<IntelligencePage />} />
          <Route path="portfolio" element={<PortfolioPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
          <Route path="upload" element={<CsvUploadPage />} />
        </Route>

        {/* Kullanıcı portalı (§3b Phase 6/7) — ayrı giriş + nav */}
        <Route path="portal/giris" element={<PortalLoginPage />} />
        <Route element={<PortalLayout />}>
          <Route path="portal" element={<PortalPage />} />
          <Route path="portal/profilim" element={<PortalProfilPage />} />
          <Route path="portal/erisim-talepleri" element={<PortalTaleplerPage />} />
          <Route path="portal/riza-defterim" element={<PortalRizaPage />} />
        </Route>

        {/* Kurum (banka) arayüzü (§3b Phase 7/7.2/7.4) — rıza-tabanlı gerçek müşteri erişimi */}
        <Route path="kurum/giris" element={<KurumLoginPage />} />
        <Route element={<KurumLayout />}>
          <Route path="kurum/musteriler" element={<KurumMusterilerPage />} />
          <Route path="kurum/musteri/:aksNo" element={<KurumMusteriDetayPage />} />
        </Route>

        {/* Eşleşmeyen her yol: aksi halde bomboş bir sayfa render ediliyordu. */}
        <Route path="*" element={<BulunamadiPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## Kısım G — Giriş kapıları (layout'suz, tam sayfa)

Bu iki sayfa hiçbir `Layout` kullanmaz; kendi tam-sayfa düzenlerini kurar.
İkisi de sitenin "önü" — Stitch'te en çok görsel özgürlük burada, çünkü
veri sözleşmesi neredeyse yok.

### G1. `AnaSayfaPage.tsx` — rota `/` (herkese açık ana sayfa)

**Stitch brief:** Klasik bir ürün landing page'i. Üstte ince bir header
(solda "AKS" kelime markası, sağda tek bir birincil buton). Ortada geniş
nefes alanlı bir hero: büyük başlık "Alternatif Kapasite Skoru", altında
ürünün ne yaptığını anlatan 3–4 satırlık bir paragraf, altında iki buton
("Başla" birincil, "Projeyi incele" ikincil/çerçeveli). Hero'nun altında
2×2 kart ızgarası (mobilde tek sütun): her kartta bir ikon, kısa başlık ve
2–3 satır açıklama. En altta ince bir footer: yasal/dürüstlük şerhi.

Ton: sakin, teknik-güven veren, koyu tema. Bu sayfa **veri göstermez** —
grafik, sayı, tablo YOK. Tek dinamik şey sağ üstteki buton.

**Durum/etkileşim envanteri:**

| Durum | Nereden | Etkisi |
|---|---|---|
| `kullanici` | `api.ben()` (sessiz; 401 normaldir, hata gösterilmez) | `null` → buton "Giriş / Kayıt" → `/giris`. Dolu → buton "Panelime git" → role göre `/panel` \| `/kurum/musteriler` \| `/portal` |

**Kritik davranış:** Bu sayfa **zorunlu yönlendirme yapmaz.** Giriş yapmış
kullanıcı da ana sayfayı görebilmeli — zorunlu kapı `/giris`'in ve üç
`Layout`'un işi. Stitch'te "girişliyse otomatik panele at" gibi bir davranış
EKLENMEMELİ.

```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "../components/Icon";

// Site kökü (`/`) — herkese açık ana sayfa. Bilinçli olarak İNCE tutuldu:
// ürünün ne olduğunu bir ekranda anlatır ve doğru kapıya yönlendirir, başka
// hiçbir iş yapmaz. Veri gösteren her yüzey (banka paneli, portal, kurum)
// kendi oturum kapısının ARKASINDA — bkz. execution.md §3b Phase 7/7.11.
//
// Buradan yönlendirme YAPILMAZ (giriş yapmış kullanıcı da ana sayfayı
// görebilmeli); yalnızca oturum varsa üstteki buton "Panelime git"e dönüşür.
// Zorunlu yönlendirme `/giris`'in işi.

const OZELLIKLER = [
  {
    ikon: "receipt_long",
    baslik: "Ekstre → kapasite skoru",
    metin: "PDF, Excel veya CSV hesap ekstresi yüklenir; 9 davranışsal özellik çıkarılıp 300–850 aralığında bir AKS skoru üretilir.",
  },
  {
    ikon: "compare_arrows",
    baslik: "Bankanın skorunu ezmez",
    metin: "AKS tamamlayıcıdır. Klasik skor her değerlendirmede olduğu gibi, değiştirilmeden değiştirilemez denetim izine yazılır.",
  },
  {
    ikon: "verified_user",
    baslik: "Erişim müşterinin onayıyla",
    metin: "Kurum, AKS numarasıyla erişim talebi açar; müşteri portalinden onaylar. Onay sürelidir, her an iptal edilebilir.",
  },
  {
    ikon: "insights",
    baslik: "Neden bu skor",
    metin: "Her sonuç SHAP gerekçe kodlarıyla gelir — hangi faktör skoru ne yönde etkiledi, açıkça gösterilir.",
  },
];

export default function AnaSayfaPage() {
  const [kullanici, setKullanici] = useState<KullaniciBilgisi | null>(null);

  useEffect(() => {
    // Sessizce dener — oturum yoksa 401 normaldir, hata gösterilmez.
    api.ben().then(setKullanici).catch(() => setKullanici(null));
  }, []);

  const panelYolu = kullanici?.yonetici
    ? "/panel"
    : kullanici?.kurum_uyesi
      ? "/kurum/musteriler"
      : "/portal";

  return (
    <div className="min-h-screen bg-background text-on-background">
      <header className="border-b border-outline-variant/30">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="font-display-sm text-display-sm font-bold tracking-tighter">AKS</span>
          {kullanici ? (
            <Link
              to={panelYolu}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Panelime git
            </Link>
          ) : (
            <Link
              to="/giris"
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Giriş / Kayıt
            </Link>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4">
        <section className="py-20 text-center">
          <h1 className="font-display-lg text-display-lg tracking-tighter max-w-2xl mx-auto">
            Alternatif Kapasite Skoru
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-4 max-w-xl mx-auto leading-relaxed">
            Klasik kredi skoru ince dosyalı kişileri görmez: düzenli geliri ve sağlam ödeme
            davranışı olan biri, yalnızca kredi geçmişi kısa diye reddedilebilir. AKS, hesap
            hareketlerinden okunan davranışsal kapasiteyi bankanın kendi skorunun{" "}
            <em>yanına</em> koyar — yerine değil.
          </p>
          <div className="flex flex-wrap gap-3 justify-center mt-8">
            <Link
              to="/giris"
              className="px-5 py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Başla
            </Link>
            <a
              href="https://github.com/alperenkarakaya/yzta-bootcamp-grup74"
              target="_blank"
              rel="noreferrer"
              className="px-5 py-2.5 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono hover:bg-surface-container transition-colors"
            >
              Projeyi incele
            </a>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-20">
          {OZELLIKLER.map((o) => (
            <div key={o.baslik} className="bg-surface-container-low hairline-border rounded-xl p-6">
              <Icon name={o.ikon} className="text-2xl text-primary" />
              <h2 className="font-headline-md text-headline-md mt-2">{o.baslik}</h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-2 leading-relaxed">{o.metin}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="border-t border-outline-variant/30">
        <div className="max-w-5xl mx-auto px-4 py-8 font-label-mono text-[11px] text-on-surface-variant/70 text-center leading-relaxed">
          AKS bir araştırma/bootcamp projesidir; gerçek bir kredi kararı vermez ve yatırım ya da
          finansal tavsiye içermez. Model sentetik veri üzerinde eğitilmiştir.
        </div>
      </footer>
    </div>
  );
}
```

---

### G2. `GirisPage.tsx` — rota `/giris` (site geneli giriş kapısı)

**Stitch brief:** Ortalanmış, iki sütunlu bir "giriş türünü seç" ekranı.
Üstte küçük bir hero (ikon + "AKS — Alternatif Kapasite Skoru" + tek satır
açıklama). Altında yan yana iki eşit kart (mobilde alt alta):

- **Kullanıcı kartı:** ikon, başlık, açıklama, sonra Giriş/Kayıt arasında
  geçiş yapan iki sekmeli bir segment kontrol, altında e-posta + şifre
  alanları ve tek bir birincil buton. Kartın altında küçük gri yazıyla
  demo hesap bilgileri (örnek kullanıcı + yönetici).
- **Kurum kartı:** ikon, başlık, açıklama, sonra doğrudan e-posta + şifre
  ve birincil buton. **Kayıt sekmesi YOK** — kurum üyeliği kasıtlı olarak
  provizyonlanır, öz-kayıt yoktur. Kartın altında demo kurum bilgisi.

En altta tek satır gri yazı: erişim/rıza modelini özetleyen şerh.

**Durum/etkileşim envanteri:**

| Durum | Tip | Not |
|---|---|---|
| `kontrolEdiliyor` | `boolean` | Açılışta `api.ben()` denenir; oturum varsa `varisYolu()` ile hemen yönlendirilir, form hiç görünmez |
| `kMod` | `"giris" \| "kayit"` | Kullanıcı kartındaki segment kontrol |
| `kEmail`/`kSifre`/`kHata`/`kYukleniyor` | Kullanıcı kartı formu | Şifre `minLength={8}` (backend `MinimumLengthValidator` ile aynı) |
| `uEmail`/`uSifre`/`uHata`/`uYukleniyor` | Kurum kartı formu | — |

**Kritik davranış — kurum girişi iki adımlıdır:** `api.girisYap()` başarılı
olsa bile hesap bir kuruma üye olmayabilir. Bu yüzden hemen ardından
`api.kurumBen()` çağrılır; başarısızsa hata gösterilir **ve
`api.cikisYap()` ile oturum geri alınır** — aksi halde kullanıcı "giriş
yaptım ama hiçbir yere giremiyorum" durumunda kalırdı. Bu mantık
`KurumLoginPage.tsx` ile birebir aynıdır.

**Kritik davranış — rol bazlı yönlendirme:** `varisYolu()` giriş/kayıt
sonrası varışı belirler (yönetici → `/panel`, kurum üyesi →
`/kurum/musteriler`, diğer → `/portal`). Bu bayraklar yalnızca YÖNLENDİRME
içindir; gerçek yetki her uçta sunucuda zorlanır.

```tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "../components/Icon";

// Giriş sonrası doğru yüzey: yönetici → banka içi araştırma arayüzü (TÜM demo
// popülasyonunu görür), kurum personeli → kurum paneli (yalnızca rıza verilen
// müşteriler), sıradan kullanıcı → kendi portalı (yalnızca kendi yüklemeleri).
function varisYolu(k: KullaniciBilgisi): string {
  if (k.yonetici) return "/panel";
  if (k.kurum_uyesi) return "/kurum/musteriler";
  return "/portal";
}

// Site geneli giriş — küçük bir landing page: üstte kısa bir tanıtım, altında
// iki kutucuk (Kullanıcı / Kurum) — giren kişi giriş şeklini KENDİSİ seçer.
// Her kutucuğun altında doğrudan giriş alanları var (ayrı bir sayfaya
// geçmeye gerek yok). İkisi de AYNI oturum sistemini (`/api/auth/*`)
// kullanır — Kurum tarafı `kurumBen()` ile üyeliğini doğrular (KurumLoginPage
// ile birebir aynı mantık). Giriş sonrası varış `varisYolu()` ile role göre
// belirlenir. Herkese açık ana sayfa ayrı bir sayfadır (`/`, AnaSayfaPage).
export default function GirisPage() {
  const navigate = useNavigate();
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);

  // Kullanıcı kutucuğu
  const [kMod, setKMod] = useState<"giris" | "kayit">("giris");
  const [kEmail, setKEmail] = useState("");
  const [kSifre, setKSifre] = useState("");
  const [kHata, setKHata] = useState("");
  const [kYukleniyor, setKYukleniyor] = useState(false);

  // Kurum kutucuğu — öz-kayıt yok (kurum üyeliği kasıtlı provizyonlanır,
  // bkz. KurumLoginPage.tsx), yalnızca giriş.
  const [uEmail, setUEmail] = useState("");
  const [uSifre, setUSifre] = useState("");
  const [uHata, setUHata] = useState("");
  const [uYukleniyor, setUYukleniyor] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const k = await api.ben();
        navigate(varisYolu(k), { replace: true });
        return;
      } catch {
        /* oturum yok — landing page gösterilecek */
      }
      setKontrolEdiliyor(false);
    })();
  }, [navigate]);

  async function kullaniciGonder(e: React.FormEvent) {
    e.preventDefault();
    setKHata("");
    setKYukleniyor(true);
    try {
      const k = kMod === "giris" ? await api.girisYap(kEmail, kSifre) : await api.kayitOl(kEmail, kSifre);
      navigate(varisYolu(k));
    } catch (err) {
      setKHata(String(err instanceof Error ? err.message : err));
    } finally {
      setKYukleniyor(false);
    }
  }

  async function kurumGonder(e: React.FormEvent) {
    e.preventDefault();
    setUHata("");
    setUYukleniyor(true);
    try {
      await api.girisYap(uEmail, uSifre);
      await api.kurumBen(); // bu hesap gerçekten bir kuruma üye mi?
      navigate("/kurum/musteriler");
    } catch (err) {
      setUHata(
        String(err instanceof Error ? err.message : err) +
          " (bu hesabın bir kuruma üyeliği yoksa kurum girişi kullanılamaz)"
      );
      await api.cikisYap().catch(() => {});
    } finally {
      setUYukleniyor(false);
    }
  }

  if (kontrolEdiliyor) {
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-4 py-16">
      {/* Hero */}
      <div className="text-center max-w-lg mb-10">
        <Icon name="insights" className="text-5xl text-primary" />
        <h1 className="font-display-sm text-display-sm text-on-background mt-3">AKS — Alternatif Kapasite Skoru</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2">
          Banka skorunu tamamlayan davranışsal kredi kapasitesi platformu. Devam etmek için giriş türünüzü seçin.
        </p>
      </div>

      {/* İki kutucuk: Kullanıcı / Kurum */}
      <div className="w-full max-w-3xl grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Kullanıcı kutucuğu */}
        <div className="bg-surface-container-low hairline-border rounded-xl p-6 flex flex-col">
          <div className="text-center mb-4">
            <Icon name="account_circle" className="text-3xl text-primary" />
            <h2 className="font-headline-md text-headline-md text-on-background mt-1">Kullanıcı</h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
              Kendi ekstrenizi yükleyip kapasite analizinizi görün. Yalnızca kendi verinize erişirsiniz.
            </p>
          </div>

          <div className="flex mb-4 rounded-DEFAULT border border-outline-variant/30 overflow-hidden">
            <button
              type="button"
              onClick={() => setKMod("giris")}
              className={`flex-1 py-1.5 font-label-mono text-label-mono transition-colors ${
                kMod === "giris" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Giriş Yap
            </button>
            <button
              type="button"
              onClick={() => setKMod("kayit")}
              className={`flex-1 py-1.5 font-label-mono text-label-mono transition-colors ${
                kMod === "kayit" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Kayıt Ol
            </button>
          </div>

          <form onSubmit={kullaniciGonder} className="flex flex-col gap-3">
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
              <input
                type="email"
                required
                value={kEmail}
                onChange={(e) => setKEmail(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="ornek@eposta.com"
              />
            </div>
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
              <input
                type="password"
                required
                minLength={8}
                value={kSifre}
                onChange={(e) => setKSifre(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="En az 8 karakter"
              />
            </div>

            {kHata && (
              <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-2.5 font-body-sm text-body-sm">
                {kHata}
              </div>
            )}

            <button
              type="submit"
              disabled={kYukleniyor}
              className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-1"
            >
              {kYukleniyor ? "…" : kMod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
            </button>
          </form>

          <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-3 text-center leading-relaxed">
            Örnek kullanıcı: <span className="text-on-surface-variant">ornek@aks.com</span> /{" "}
            <span className="text-on-surface-variant">OrnekSifre123</span>
            <br />
            Yönetici (araştırma paneli):{" "}
            <span className="text-on-surface-variant">admin@aks.com</span> /{" "}
            <span className="text-on-surface-variant">AdminSifre123</span>
          </p>
        </div>

        {/* Kurum kutucuğu */}
        <div className="bg-surface-container-low hairline-border rounded-xl p-6 flex flex-col">
          <div className="text-center mb-4">
            <Icon name="account_balance" className="text-3xl text-primary" />
            <h2 className="font-headline-md text-headline-md text-on-background mt-1">Kurum</h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
              Banka/kurum personeli oturumu — müşteri verisine yalnızca rızalı erişimle ulaşılır.
            </p>
          </div>

          <form onSubmit={kurumGonder} className="flex flex-col gap-3 mt-auto">
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
              <input
                type="email"
                required
                value={uEmail}
                onChange={(e) => setUEmail(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="kurum@demo.aks"
              />
            </div>
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
              <input
                type="password"
                required
                value={uSifre}
                onChange={(e) => setUSifre(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="••••••••"
              />
            </div>

            {uHata && (
              <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-2.5 font-body-sm text-body-sm">
                {uHata}
              </div>
            )}

            <button
              type="submit"
              disabled={uYukleniyor}
              className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-1"
            >
              {uYukleniyor ? "…" : "Giriş Yap"}
            </button>
          </form>

          <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-3 text-center">
            Örnek kurum: <span className="text-on-surface-variant">kurum@demo.aks</span> /{" "}
            <span className="text-on-surface-variant">DemoKurum123!</span>
          </p>
        </div>
      </div>

      <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-8 text-center max-w-lg">
        Her hesap yalnızca kendi verisini görür. Kurumlar bir müşterinin verisine ancak o müşteri
        portalinden erişim talebini onayladıktan sonra, onayın süresi dolana kadar erişebilir.
      </p>
    </div>
  );
}
```

---

## Kısım A — Banka içi demo/araştırma arayüzü (`Layout`, YALNIZCA yönetici)

### A1. `IntelligencePage.tsx` — rota `/panel`

**Stitch brief:** Bir "komuta merkezi" ana sayfası. Üstte durum başlığı
(sistem online/offline, model adı, versiyon) ve bir "SYNC DATA" butonu.
Altında 12 kolonluk grid: solda geniş bir **"Live Engine Feed"** kartı —
son skorlanan 4 demo müşteriyi ikon+persona+"Kurtarıldı" rozetiyle liste
halinde gösterir, her satır tıklanabilir (müşteri detayına gider). Sağda
dar bir **"Pipeline HUD"** kartı — 3 pipeline aşamasının (VeriAgent/
SkorlamaAgent/DanismanAgent) canlı/boşta durumunu nabız animasyonuyla
gösterir. Altta iki eşit kart: solda persona başına "kurtarılan müşteri"
sayısını gösteren bar chart, sağda hedef 2 personanın kredibl onay
oranını (%) büyük rakamla gösteren iki kutu.

**Veri/durum:** mount'ta `api.bilgi()`, `api.portfoy()`, `api.adalet()`,
`api.demoMusteriler(1)` paralel çekilir, sonra ilk 4 demo ID `api.skorlaDemo()`
ile skorlanır. `syncing` state'i buton/HUD animasyonunu tetikler. Hata
durumunda üstte kırmızı banner.

```tsx
import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api, PERSONA_ETIKET, HEDEF_PERSONALAR, type Bilgi, type Portfoy, type Adalet, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, kapasiteYuzdesi } from "../lib/skor";

interface FeedOge extends SkorSonuc {
  id: number;
}

export default function IntelligencePage() {
  const [bilgi, setBilgi] = useState<Bilgi | null>(null);
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [feed, setFeed] = useState<FeedOge[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [hata, setHata] = useState("");

  const sync = useCallback(async () => {
    setSyncing(true);
    setHata("");
    try {
      const [b, p, a, demo] = await Promise.all([
        api.bilgi(),
        api.portfoy().catch(() => null),
        api.adalet().catch(() => null),
        api.demoMusteriler(1),
      ]);
      setBilgi(b);
      setPortfoy(p);
      setAdalet(a);

      const ids = Object.values(demo).flat().slice(0, 4);
      const skorlar = await Promise.all(ids.map((id) => api.skorlaDemo(id)));
      setFeed(skorlar.map((s, i) => ({ ...s, id: ids[i] })));
    } catch (e) {
      setHata(String(e));
    } finally {
      setSyncing(false);
    }
  }, []);

  useEffect(() => {
    sync();
  }, [sync]);

  const maxKirilim = portfoy ? Math.max(1, ...Object.values(portfoy.persona_kirilimi)) : 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
      {/* Header */}
      <div className="col-span-1 md:col-span-12 mb-4 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="font-headline-md text-headline-md text-on-background">Terminal Overview</h1>
          <p className="font-label-mono text-label-mono text-on-surface-variant mt-1">
            SYS.STATUS: {hata ? "OFFLINE" : "ONLINE"} | MODEL: {bilgi?.model ?? "—"} | SÜRÜM: {bilgi?.surum ?? "—"}
          </p>
        </div>
        <button
          onClick={sync}
          disabled={syncing}
          className="bg-primary-container text-white font-label-mono text-label-mono px-4 py-2 rounded-DEFAULT inner-shadow-subtle hover:bg-inverse-primary transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <Icon name="refresh" className={`text-[16px] ${syncing ? "animate-spin" : ""}`} />
          {syncing ? "SENKRONİZE EDİLİYOR" : "SYNC DATA"}
        </button>
      </div>

      {hata && (
        <div className="col-span-1 md:col-span-12 bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Sunucuya bağlanılamadı: {hata}
        </div>
      )}

      {/* Live Engine Feed */}
      <section className="col-span-1 md:col-span-8 card-surface rounded-lg flex flex-col overflow-hidden min-h-[400px]">
        <div className="glass-header px-4 py-3 flex justify-between items-center">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse" />
            LIVE ENGINE FEED
          </h2>
          <span className="font-label-mono text-[10px] text-on-surface-variant">
            {bilgi ? `${bilgi.demo_musteri_sayisi} DEMO MÜŞTERİ` : "—"}
          </span>
        </div>
        <div className="p-4 flex-1 overflow-y-auto flex flex-col gap-2">
          {feed.length === 0 && !syncing && (
            <p className="text-on-surface-variant font-body-sm text-body-sm p-4">Henüz veri yok.</p>
          )}
          {feed.map((m) => {
            const durum = durumBelirle(m.klasik_skor, m.aks_skor);
            const renk =
              durum === "kurtarildi" ? "text-primary" : durum === "onaylandi" ? "text-secondary-container" : "text-error";
            return (
              <Link
                key={m.id}
                to={`/customers/${m.id}`}
                className="bg-surface-container rounded-DEFAULT p-3 border border-outline-variant/30 flex justify-between items-center relative overflow-hidden group hover:border-primary/40 transition-colors"
              >
                <div className="flex items-center gap-4 relative z-10">
                  <div className="w-10 h-10 rounded-full bg-[#1E293B] flex items-center justify-center border border-outline-variant/30">
                    <Icon
                      name={durum === "kurtarildi" ? "psychology" : durum === "onaylandi" ? "person" : "warning"}
                      className={renk}
                    />
                  </div>
                  <div>
                    <div className="font-body-sm text-body-sm font-semibold text-on-surface flex items-center gap-2">
                      ID: #{m.id}
                      {durum === "kurtarildi" && (
                        <span className="text-[10px] bg-primary-container/20 text-primary px-2 py-0.5 rounded-full border border-primary/30">
                          RESCUED
                        </span>
                      )}
                    </div>
                    <div className="font-label-mono text-[10px] text-on-surface-variant mt-0.5">
                      Persona: {PERSONA_ETIKET[m.persona] ?? m.persona}
                    </div>
                  </div>
                </div>
                <div className="text-right relative z-10">
                  <div className={`font-body-sm text-body-sm font-semibold ${renk}`}>{DURUM_ETIKET[durum]}</div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant">
                    Klasik {m.klasik_skor ?? "—"} → AKS {m.aks_skor}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Agent HUD */}
      <section className="col-span-1 md:col-span-4 card-surface rounded-lg flex flex-col min-h-[400px]">
        <div className="glass-header px-4 py-3 border-b border-outline-variant/30">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">PIPELINE HUD</h2>
        </div>
        <div className="p-4 flex-1 flex flex-col gap-4">
          {[
            { ad: "VeriAgent", aciklama: "özellik çıkarımı" },
            { ad: "SkorlamaAgent", aciklama: "model skorlama" },
            { ad: "DanismanAgent", aciklama: "öneri üretimi" },
          ].map((a) => (
            <div className="flex items-center gap-3" key={a.ad}>
              <div className={`w-2 h-2 rounded-full ${syncing ? "bg-primary-container animate-pulse ai-glow" : "bg-secondary-container"}`} />
              <div className="flex-1">
                <div className="flex justify-between items-end mb-1">
                  <span className="font-label-mono text-label-mono text-on-surface">{a.ad}</span>
                  <span className={`font-label-mono text-[10px] ${syncing ? "text-primary" : "text-secondary-container"}`}>
                    {syncing ? "ACTIVE" : "IDLE"}
                  </span>
                </div>
                <div className="w-full bg-[#1E293B] h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full relative overflow-hidden ${syncing ? "bg-primary-container w-full" : "bg-secondary-container w-full"}`}
                  >
                    {syncing && (
                      <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
                    )}
                  </div>
                </div>
                <div className="font-label-mono text-[9px] text-on-surface-variant mt-0.5">{a.aciklama}</div>
              </div>
            </div>
          ))}
          <div className="mt-auto pt-4 border-t border-outline-variant/20">
            <p className="font-label-mono text-[9px] text-on-surface-variant leading-relaxed">
              Veri/Skorlama/Danışman deterministik pipeline aşamalarıdır (agent değil). Ayrıca üç gerçek agent
              çalışıyor: AsistanAgent, BelgeAgent ve Claude tool-calling danışmanı.
            </p>
          </div>
        </div>
      </section>

      {/* Portfolio Pulse */}
      <section className="col-span-1 md:col-span-6 card-surface rounded-lg flex flex-col h-[350px]">
        <div className="glass-header px-4 py-3 flex justify-between items-center">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">PORTFÖY NABZI</h2>
          <span className="font-label-mono text-[10px] text-on-surface-variant">Kurtarılan / persona</span>
        </div>
        <div className="p-4 flex-1 relative flex items-end justify-center">
          {portfoy ? (
            <div className="w-full h-full flex items-end justify-between px-2 gap-3">
              {Object.entries(portfoy.persona_kirilimi).map(([persona, adet]) => (
                <div className="flex-1 flex flex-col justify-end items-center gap-1 group h-full" key={persona}>
                  <span className="font-label-mono text-[10px] text-on-surface-variant opacity-0 group-hover:opacity-100">
                    {adet}
                  </span>
                  <div
                    className="w-full bg-gradient-to-t from-primary-container to-secondary-container rounded-t-sm shadow-[0_0_10px_rgba(79,70,229,0.3)] transition-all"
                    style={{ height: `${Math.max(6, (adet / maxKirilim) * 100)}%` }}
                  />
                  <span className="font-label-mono text-[9px] text-on-surface-variant text-center mt-1">
                    {(PERSONA_ETIKET[persona] ?? persona).split(" ")[0]}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-on-surface-variant font-body-sm text-body-sm">Portföy verisi yükleniyor…</p>
          )}
        </div>
      </section>

      {/* Segment Alpha Metrics */}
      <section className="col-span-1 md:col-span-6 card-surface rounded-lg flex flex-col h-[350px] relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-primary-container/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/4 pointer-events-none" />
        <div className="glass-header px-4 py-3">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">HEDEF SEGMENT KURTARMA ORANI</h2>
        </div>
        <div className="p-6 flex-1 flex flex-col justify-center gap-6 z-10">
          <div className="grid grid-cols-2 gap-4">
            {HEDEF_PERSONALAR.map((persona) => {
              const tpr = adalet?.aks_skor.gruplar[persona]?.kredibl_onay_orani_tpr;
              return (
                <div className="bg-[#1E293B]/50 p-4 rounded-DEFAULT border border-outline-variant/20" key={persona}>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mb-1 uppercase">
                    {PERSONA_ETIKET[persona]}
                  </div>
                  <div className="font-display-sm text-display-sm text-on-surface flex items-baseline gap-1">
                    {tpr != null ? (tpr * 100).toFixed(1) : "—"}
                    <span className="text-body-sm text-secondary-container">%</span>
                  </div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mt-2">
                    kredibl onay oranı (TPR)
                  </div>
                </div>
              );
            })}
          </div>
          <div className="text-body-sm text-on-surface-variant border-l-2 border-primary-container pl-3">
            AKS eşiğinde ({"≥650"}) hedef segmentteki kredibl müşterilerin onaylanma oranı — davranışsal modelin
            asıl iddia ettiği yerde ölçülen gerçek performans.
          </div>
        </div>
      </section>
    </div>
  );
}
```

### A2. `PortfolioPage.tsx` — rota `/portfolio`

**Stitch brief:** Üstte başlık + "LIVE" rozeti + iki büyük rakam (kurtarılan
sayısı, kurtarma oranı %). Altında döngüsel-veri uyarı banner'ı (varsa).
Ana grid: solda geniş bir **gruplu bar chart** (persona başına klasik vs.
AKS onay oranı, iki renkli çubuk yan yana, hover'da yüzde etiketi çıkar);
sağda dar bir **dairesel gauge** (eşit-fırsat boşluğu — SVG circle stroke
animasyonuyla). Altında tam genişlik bir **segment performans tablosu**
(persona, n, klasik onay, AKS onay, kurtarma etkisi rozeti, yanlış onay,
kredibl TPR ilerleme çubuğu). En altta "illüstratif getiri" özet şeridi
(potansiyel kazanç/beklenen kayıp/net, 3 büyük rakam).

**Veri:** mount'ta `api.portfoy()` + `api.adalet()` paralel.

```tsx
import { useEffect, useState } from "react";
import { api, PERSONA_ETIKET, type Portfoy, type Adalet } from "../api";
import { paraFormat } from "../lib/skor";

export default function PortfolioPage() {
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [hata, setHata] = useState("");

  useEffect(() => {
    Promise.all([api.portfoy(), api.adalet()])
      .then(([p, a]) => {
        setPortfoy(p);
        setAdalet(a);
      })
      .catch((e) => setHata(String(e)));
  }, []);

  const personalar = adalet ? Object.keys(adalet.aks_skor.gruplar) : [];

  return (
    <div className="flex flex-col gap-stack-lg">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-label-mono text-label-mono text-primary px-2 py-0.5 bg-primary-container/20 rounded-full border border-primary/30">
              LIVE
            </span>
            <span className="font-label-mono text-label-mono text-on-surface-variant opacity-60">
              /api/portfoy · /api/adalet
            </span>
          </div>
          <h1 className="font-display-lg text-display-lg tracking-tighter text-on-background">Portfolio Analysis</h1>
        </div>
        {portfoy && (
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="font-label-mono text-label-mono text-on-surface-variant">KURTARILAN</span>
              <span className="font-display-sm text-display-sm text-primary">
                {portfoy.kurtarilan}/{portfoy.kredibl_red}
              </span>
            </div>
            <div className="w-px h-10 bg-outline-variant/30 mx-2" />
            <div className="flex flex-col items-end">
              <span className="font-label-mono text-label-mono text-on-surface-variant">KURTARMA ORANI</span>
              <span className="font-display-sm text-display-sm text-secondary">
                {(portfoy.kurtarma_orani * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      {portfoy?.veri_kaynagi === "dongusel" && (
        <div className="bg-secondary-container/10 border border-secondary/30 text-on-surface-variant rounded-DEFAULT p-3 font-body-sm text-body-sm">
          <span className="text-secondary font-semibold">Not:</span> {portfoy.uyari}
        </div>
      )}

      <div className="grid grid-cols-12 gap-gutter">
        <section className="col-span-12 lg:col-span-8 bg-surface-container-low hairline-border rounded-xl overflow-hidden ai-glow flex flex-col min-h-[440px]">
          <div className="glass-header px-6 py-4 flex items-center justify-between">
            <div>
              <h3 className="font-headline-md text-headline-md">Segment Onay Karşılaştırması</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">Klasik vs. Davranışsal onay oranı (persona bazında)</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary" />
                <span className="font-label-mono text-label-mono">Davranışsal (AKS)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-outline" />
                <span className="font-label-mono text-label-mono">Klasik</span>
              </div>
            </div>
          </div>
          <div className="flex-grow relative p-6">
            {adalet ? (
              <div className="absolute inset-6 flex items-end justify-between gap-6">
                {personalar.map((persona) => {
                  const klasik = adalet.klasik_skor.gruplar[persona]?.onay_orani ?? 0;
                  const aks = adalet.aks_skor.gruplar[persona]?.onay_orani ?? 0;
                  return (
                    <div className="w-full flex flex-col items-center justify-end group" key={persona}>
                      <div className="w-full flex items-end justify-center gap-1 h-56">
                        <div
                          className="w-1/2 bg-outline/30 rounded-t-sm relative group-hover:bg-outline/50 transition-all"
                          style={{ height: `${klasik * 100}%` }}
                        >
                          <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-label-mono text-[10px] opacity-0 group-hover:opacity-100 whitespace-nowrap">
                            {(klasik * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div
                          className="w-1/2 bg-gradient-to-t from-primary-container to-primary rounded-t-sm relative shadow-[0_0_10px_rgba(79,70,229,0.3)] group-hover:brightness-110 transition-all"
                          style={{ height: `${aks * 100}%` }}
                        >
                          <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-label-mono text-[10px] opacity-0 group-hover:opacity-100 whitespace-nowrap">
                            {(aks * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      <span className="font-label-mono text-[10px] opacity-60 mt-2 text-center">
                        {PERSONA_ETIKET[persona] ?? persona}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-on-surface-variant font-body-sm text-body-sm">Yükleniyor…</p>
            )}
          </div>
        </section>

        <section className="col-span-12 lg:col-span-4 bg-surface-container-low hairline-border rounded-xl min-h-[440px] flex flex-col">
          <div className="glass-header px-6 py-4">
            <h3 className="font-headline-md text-headline-md">Eşit-Fırsat Boşluğu</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Δ Klasik vs. Davranışsal (equal opportunity gap)</p>
          </div>
          <div className="flex-grow p-6 flex flex-col justify-center items-center relative overflow-hidden">
            <div className="relative z-10 w-full aspect-square max-w-[240px]">
              <div className="absolute inset-0 rounded-full border border-primary/20" />
              <div className="absolute inset-4 rounded-full border border-primary/10" />
              <div className="absolute inset-12 rounded-full border border-primary/5" />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="font-display-sm text-display-sm text-on-background">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
                <span className="font-label-mono text-label-mono text-primary">AKS BOŞLUĞU</span>
              </div>
            </div>
            <div className="mt-8 w-full space-y-3 font-label-mono text-label-mono">
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Klasik skor boşluğu</span>
                <span className="text-error">
                  {adalet ? adalet.klasik_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">AKS boşluğu</span>
                <span className="text-primary">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <p className="text-[10px] text-on-surface-variant opacity-70 pt-2 leading-relaxed">
                Boşluk = kredibl onay oranının persona'lar arası max-min farkı. Düşük = adil. 0'a yakın gruplar
                arası eşit muamele anlamına gelir.
              </p>
            </div>
          </div>
        </section>

        <section className="col-span-12 bg-surface-container hairline-border rounded-xl">
          <div className="glass-header px-6 py-4">
            <h3 className="font-headline-md text-headline-md">Segment Performansı</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Gerçek 4 davranışsal persona üzerinde kurtarma ve risk metrikleri.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant/30">
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">SEGMENT</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">N</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KLASİK ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">AKS ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KURTARMA ETKİSİ</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">YANLIŞ ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KREDİBL TPR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {personalar.map((persona) => {
                  const k = adalet!.klasik_skor.gruplar[persona];
                  const a = adalet!.aks_skor.gruplar[persona];
                  const etki = (a.onay_orani - k.onay_orani) * 100;
                  return (
                    <tr className="hover:bg-surface-container-highest/50 transition-colors" key={persona}>
                      <td className="px-6 py-5 font-body-lg text-on-background">{PERSONA_ETIKET[persona] ?? persona}</td>
                      <td className="px-6 py-5 font-label-mono text-label-mono">{a.n}</td>
                      <td className="px-6 py-5 font-label-mono text-label-mono text-on-surface-variant">
                        {(k.onay_orani * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-5 font-label-mono text-label-mono text-primary">
                        {(a.onay_orani * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-5">
                        <span
                          className={`px-2 py-1 rounded font-label-mono text-label-mono border ${
                            etki >= 0
                              ? "bg-secondary/10 text-secondary border-secondary/20"
                              : "bg-error/10 text-error border-error/20"
                          }`}
                        >
                          {etki >= 0 ? "+" : ""}
                          {etki.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-5 font-label-mono text-label-mono">{(a.yanlis_onay_orani * 100).toFixed(1)}%</td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-surface-container-highest rounded-full">
                            <div className="h-full bg-primary rounded-full" style={{ width: `${a.kredibl_onay_orani_tpr * 100}%` }} />
                          </div>
                          <span className="font-label-mono text-label-mono">{(a.kredibl_onay_orani_tpr * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {portfoy && (
          <section className="col-span-12 bg-surface-container hairline-border rounded-xl p-6 flex flex-wrap gap-8 items-center justify-between">
            <div>
              <h3 className="font-headline-md text-headline-md mb-1">İllüstratif Getiri</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant max-w-xl">
                Varsayımlar: ort. kredi {paraFormat(portfoy.illustratif_getiri.varsayimlar.ort_kredi)}, getiri oranı{" "}
                {(portfoy.illustratif_getiri.varsayimlar.getiri_orani * 100).toFixed(0)}%, zarar oranı{" "}
                {(portfoy.illustratif_getiri.varsayimlar.zarar_orani * 100).toFixed(0)}% — illüstratiftir, doğrulanmış
                gerçek para birimi tahmini değildir.
              </p>
            </div>
            <div className="flex gap-8">
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Potansiyel Kazanç</div>
                <div className="font-display-sm text-display-sm text-secondary">
                  {paraFormat(portfoy.illustratif_getiri.potansiyel_kazanc)}
                </div>
              </div>
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Beklenen Kayıp</div>
                <div className="font-display-sm text-display-sm text-error">
                  {paraFormat(portfoy.illustratif_getiri.beklenen_kayip)}
                </div>
              </div>
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Net</div>
                <div className="font-display-sm text-display-sm text-primary">{paraFormat(portfoy.illustratif_getiri.net)}</div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
```

### A3. `AuditPage.tsx` — rota `/audit`

**Stitch brief:** Sayfanın en yoğun olanı — 7 ayrı panel dikey akışta.
(1) Başlık + "canlı/hata" durum rozeti. (2) Döngüsel-veri uyarısı. (3) 12
kolonlu grid: solda dairesel "Adalet Parity" gauge'u + iki rakam, sağda
persona başına yatay parity çubukları ("Equal Opportunity Monitor"). (4)
"Reason Code Inspector" — müşteri ID giren bir input + "İncele" butonu,
SHAP faktörlerini (riski azaltan yeşil / artıran kırmızı kart listesi)
gösterir. (5) "Sınır Bütünlüğü" açıklama kartı (statik metin — AKS'nin
bankanın skorunu asla ezmediği iddiası + audit log referansı). (6) "Model
Validity" — her model için ROC-AUC/ECE/Brier + persona bazında AUC kartları,
üstte kalın bir "bu doğrulanmış değildir" uyarısı. (7) "Segmentasyon" —
K-Means küme kartları (n, ampirik temerrüt oranı, persona dağılımı). (8)
"Genelleme & Sağlamlık" — 3 kart yan yana (persona-dışı genelleme, ince
dosya stres testi tablosu, oyunlanabilirlik duyarlılığı bar'ları). (9) En
altta "Agent Beş-Soru Denetimi" — 5 kartlık bir ızgara, her biri bir
bileşenin (VeriAgent/SkorlamaAgent/DanismanAgent/Orkestrator/AsistanAgent)
"gerçek agent mi değil mi" dürüstlük değerlendirmesini gösterir.

**Veri:** mount'ta `api.adalet()`, `api.metrikler()`, `api.segmentasyon()`,
`api.genellemeSaglamlik()` ayrı ayrı (birbirini bloklamaz — biri 404 dönerse
diğerleri yine render olur), + `api.skorlaDemo(1)` ilk yüklemede otomatik.

```tsx
import { useEffect, useState } from "react";
import {
  api,
  PERSONA_ETIKET,
  type Adalet,
  type SkorSonuc,
  type MetriklerRaporu,
  type SegmentasyonRaporu,
  type GenellemeSaglamlikRaporu,
} from "../api";
import { Icon } from "../components/Icon";

const AGENT_AUDIT = [
  { ad: "VeriAgent", gecti: false, verdict: "Değil — deterministik özellik çıkarımı, saf fonksiyon." },
  { ad: "SkorlamaAgent", gecti: false, verdict: "Değil — predict_proba() + ölçekleme, bir skorlama servisi." },
  { ad: "DanismanAgent", gecti: false, verdict: "Değil (ve bu doğru) — şablonlu NLG; denetime-yakın bir yüzeyde LLM'den daha denetlenebilir." },
  { ad: "Orkestrator", gecti: false, verdict: "Değil — sıralı koordinasyon + bellek-içi log." },
  { ad: "AsistanAgent", gecti: true, verdict: "Evet — beş sorunun tamamını geçiyor: açık uçlu NL arayüzü, klasik kod çözemez, LLM doğru araç, değeri ölçülebilir, doğrulanabilir." },
];

export default function AuditPage() {
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [hata, setHata] = useState("");

  const [incelemeId, setIncelemeId] = useState<number>(1);
  const [inceleme, setInceleme] = useState<SkorSonuc | null>(null);
  const [incelemeYukleniyor, setIncelemeYukleniyor] = useState(false);
  const [incelemeHata, setIncelemeHata] = useState("");

  const [metrikler, setMetrikler] = useState<MetriklerRaporu | null>(null);
  const [metriklerHata, setMetriklerHata] = useState("");

  const [segmentasyon, setSegmentasyon] = useState<SegmentasyonRaporu | null>(null);
  const [segmentasyonHata, setSegmentasyonHata] = useState("");

  const [genelleme, setGenelleme] = useState<GenellemeSaglamlikRaporu | null>(null);
  const [genellemeHata, setGenellemeHata] = useState("");

  useEffect(() => {
    api.adalet().then(setAdalet).catch((e) => setHata(String(e)));
    api.metrikler().then(setMetrikler).catch((e) => setMetriklerHata(String(e)));
    api.segmentasyon().then(setSegmentasyon).catch((e) => setSegmentasyonHata(String(e)));
    api.genellemeSaglamlik().then(setGenelleme).catch((e) => setGenellemeHata(String(e)));
  }, []);

  async function incele() {
    setIncelemeYukleniyor(true);
    setIncelemeHata("");
    try {
      setInceleme(await api.skorlaDemo(incelemeId));
    } catch (e) {
      setIncelemeHata(String(e));
      setInceleme(null);
    } finally {
      setIncelemeYukleniyor(false);
    }
  }

  useEffect(() => {
    incele();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const personalar = adalet ? Object.entries(adalet.aks_skor.gruplar) : [];
  const maxOnay = personalar.length ? Math.max(...personalar.map(([, g]) => g.onay_orani)) : 1;
  const parite = adalet ? 1 - adalet.aks_skor.equal_opportunity_boslugu : null;

  return (
    <div className="flex flex-col gap-stack-lg">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-stack-md">
        <div>
          <h1 className="font-display-lg text-display-lg text-on-background mb-2">Fairness &amp; Bias Audit</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
            AKS'nin equal-opportunity metriğiyle gruplar arası davranışını gösterir. Bu bir yasal görüş değildir.
          </p>
        </div>
        <div className="flex items-center gap-stack-sm bg-surface-container rounded-lg p-2 border border-outline-variant/30">
          <div className="flex flex-col items-end px-3">
            <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Kaynak</span>
            <span className="font-label-mono text-label-mono text-primary">/api/adalet</span>
          </div>
          <div className="h-8 w-px bg-outline-variant/30" />
          <div className="flex flex-col items-end px-3">
            <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Durum</span>
            <span className="font-label-mono text-label-mono text-secondary flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${hata ? "bg-error" : "bg-secondary animate-pulse"}`} />
              {hata ? "HATA" : "CANLI"}
            </span>
          </div>
        </div>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      {adalet?.veri_kaynagi === "dongusel" && (
        <div className="bg-secondary-container/10 border border-secondary/30 text-on-surface-variant rounded-DEFAULT p-3 font-body-sm text-body-sm">
          <span className="text-secondary font-semibold">Not:</span> {adalet.uyari}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        <section className="md:col-span-4 glass-panel rounded-xl p-6 relative overflow-hidden flex flex-col justify-between ai-glow border-primary/20">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-headline-md text-headline-md">Adalet Parity</h2>
              <p className="font-label-mono text-label-mono text-on-surface-variant">AKS eşit-fırsat parity</p>
            </div>
            <Icon name="balance" className="text-primary" />
          </div>
          <div className="relative py-12 flex flex-col items-center justify-center">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-surface-container-high" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" strokeWidth="8" />
                <circle
                  className="text-primary transition-all duration-1000"
                  cx="96"
                  cy="96"
                  fill="transparent"
                  r="88"
                  stroke="currentColor"
                  strokeDasharray="552.92"
                  strokeDashoffset={parite != null ? 552.92 * (1 - parite) : 552.92}
                  strokeWidth="8"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-display-sm text-display-sm text-on-background">
                  {parite != null ? (parite * 100).toFixed(1) : "—"}%
                </span>
                <span className="font-label-mono text-label-mono text-secondary">PARITY</span>
              </div>
            </div>
            <div className="mt-8 grid grid-cols-2 gap-4 w-full">
              <div className="flex flex-col">
                <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">AKS Boşluğu</span>
                <span className="font-headline-md text-headline-md text-on-surface">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Klasik Boşluğu</span>
                <span className="font-headline-md text-headline-md text-error">
                  {adalet ? adalet.klasik_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
            </div>
          </div>
          <div className="bg-surface-container-highest/30 rounded p-3 mt-4 border border-outline-variant/20">
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-tight">
              <span className="text-primary font-bold italic">Not:</span> Boşluk = kredibl onay oranının persona'lar
              arası max-min farkı (0 = tam adil). Bu sayı gerçek /api/adalet çıktısıdır, sabit bir hedef eşiği henüz
              onaylanmadı.
            </p>
          </div>
        </section>

        <section className="md:col-span-8 glass-panel rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded bg-secondary/10 flex items-center justify-center text-secondary border border-secondary/20">
                <Icon name="groups" />
              </div>
              <div>
                <h2 className="font-headline-md text-headline-md">Equal Opportunity Monitor</h2>
                <p className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
                  AKS onay oranı — persona bazında parity
                </p>
              </div>
            </div>
          </div>
          <div className="flex-grow space-y-6">
            {personalar.map(([persona, g]) => {
              const oran = maxOnay > 0 ? g.onay_orani / maxOnay : 0;
              return (
                <div className="space-y-2" key={persona}>
                  <div className="flex justify-between items-end">
                    <span className="font-body-lg text-body-lg text-on-surface">{PERSONA_ETIKET[persona] ?? persona}</span>
                    <span className="font-label-mono text-label-mono text-primary">
                      {oran.toFixed(2)} Parity · n={g.n}
                    </span>
                  </div>
                  <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden flex">
                    <div className="h-full bg-primary-container" style={{ width: `${oran * 100}%` }} />
                    <div className="h-full bg-error" style={{ width: `${(1 - oran) * 100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="md:col-span-5 glass-panel rounded-xl p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <Icon name="psychology" className="text-on-surface-variant" />
            <h2 className="font-headline-md text-headline-md">Reason Code Inspector</h2>
          </div>
          <div className="flex items-center gap-2 mb-6">
            <input
              type="number"
              min={1}
              value={incelemeId}
              onChange={(e) => setIncelemeId(Number(e.target.value))}
              className="bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-label-mono text-label-mono text-on-surface w-28 focus:outline-none focus:border-primary"
            />
            <button
              onClick={incele}
              disabled={incelemeYukleniyor}
              className="px-4 py-2 rounded bg-primary-container text-on-primary-container font-label-mono text-label-mono hover:brightness-110 transition-all disabled:opacity-50"
            >
              {incelemeYukleniyor ? "…" : "İncele"}
            </button>
          </div>
          {incelemeHata && <p className="text-error font-label-mono text-label-mono mb-2">{incelemeHata}</p>}
          {inceleme && (
            <div className="space-y-4 overflow-y-auto pr-2 flex-grow max-h-[360px]">
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Müşteri #{incelemeId} — {PERSONA_ETIKET[inceleme.persona] ?? inceleme.persona} — AKS {inceleme.aks_skor}/850
              </p>
              {inceleme.aciklama.riski_azaltan.map((f) => (
                <div className="p-3 rounded bg-surface-container border-l-2 border-secondary" key={f.kod}>
                  <div className="flex justify-between mb-1">
                    <span className="font-label-mono text-label-mono text-secondary">{f.kod}</span>
                    <span className="font-label-mono text-label-mono text-on-surface-variant">{f.etki.toFixed(3)}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface">{f.faktor} — riski azaltıyor</p>
                </div>
              ))}
              {inceleme.aciklama.riski_artiran.map((f) => (
                <div className="p-3 rounded bg-surface-container border-l-2 border-error" key={f.kod}>
                  <div className="flex justify-between mb-1">
                    <span className="font-label-mono text-label-mono text-error">{f.kod}</span>
                    <span className="font-label-mono text-label-mono text-on-surface-variant">+{f.etki.toFixed(3)}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface">{f.faktor} — riski artırıyor</p>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="md:col-span-7 glass-panel rounded-xl overflow-hidden border-outline-variant/30">
          <div className="p-4 flex items-center justify-between border-b border-outline-variant/20">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <h2 className="font-label-mono text-label-mono text-on-surface font-bold uppercase tracking-widest">
                Sınır Bütünlüğü (Boundary Integrity)
              </h2>
            </div>
          </div>
          <div className="p-6 flex flex-col gap-4">
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
              AKS bankanın klasik skorunu/segmentini <span className="text-primary font-semibold">asla ezmez veya değiştirmez</span> —
              yalnızca tamamlar. Bu, koddaki bir gerçektir: her skorlama, klasik skoru{" "}
              <span className="text-on-surface font-semibold">değiştirilmeden</span> kaydeden değiştirilemez bir
              denetim satırı (<code className="font-label-mono">AuditLog</code>) üretir.
            </p>
            <div className="grid grid-cols-2 gap-4 font-label-mono text-label-mono">
              <div className="p-3 rounded bg-surface-container-lowest border border-outline-variant/20">
                <div className="text-on-surface-variant text-[10px] uppercase mb-1">Yazma modeli</div>
                <div className="text-on-surface">Django admin: salt-okunur</div>
              </div>
              <div className="p-3 rounded bg-surface-container-lowest border border-outline-variant/20">
                <div className="text-on-surface-variant text-[10px] uppercase mb-1">Korunan alan</div>
                <div className="text-on-surface">klasik_skor (DEĞİŞTİRİLMEDİ)</div>
              </div>
            </div>
          </div>
        </section>

        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Icon name="query_stats" className="text-primary" />
              <h2 className="font-headline-md text-headline-md">Model Validity</h2>
            </div>
            {metrikler && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                {metrikler.n_musteri} müşteri · veri: {metrikler.veri_kaynagi}
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            Repeated stratified k-fold ROC-AUC/PR-AUC (bootstrap %95 CI), Brier skoru ve ECE (kalibrasyon hatası).
            <span className="text-primary font-semibold"> Bu, gerçek veriyle doğrulanmış bir sonuç değildir</span> —
            sentetik/dekuple bir benchmark üzerinde ölçülmüştür. Bu sayılar bir iş tezini kanıtlamaz, yalnızca bu
            benchmark üzerindeki istatistiksel davranışı gösterir.
          </p>
          {metriklerHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {metrikler && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
              {metrikler.modeller.map((m) => (
                <div key={m.ad} className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                  <div className="font-label-mono text-label-mono text-on-surface font-bold mb-3">{m.ad}</div>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">ROC-AUC</div>
                      <div className="font-headline-md text-headline-md text-primary">{m.roc_auc.ortalama.toFixed(3)}</div>
                      <div className="text-[10px] text-on-surface-variant font-label-mono">
                        %95 CI [{m.roc_auc.ci95[0].toFixed(3)}, {m.roc_auc.ci95[1].toFixed(3)}]
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">ECE (kalibrasyon)</div>
                      <div className="font-headline-md text-headline-md text-secondary">{m.ece_oof.toFixed(3)}</div>
                      <div className="text-[10px] text-on-surface-variant font-label-mono">Brier {m.brier_oof.toFixed(3)}</div>
                    </div>
                  </div>
                  {Object.keys(m.persona_metrik).length > 0 && (
                    <div className="space-y-1">
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono mb-1">Persona bazında AUC</div>
                      {Object.entries(m.persona_metrik).map(([persona, pm]) => (
                        <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                          <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                          <span className="text-on-surface">{pm.auc.toFixed(3)} (n={pm.n})</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <Icon name="scatter_plot" className="text-tertiary" />
              <h2 className="font-headline-md text-headline-md">Segmentasyon (Denetimsiz Keşif)</h2>
            </div>
            {segmentasyon && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                k={segmentasyon.k} · silhouette {segmentasyon.silhouette_skoru.toFixed(3)} · n={segmentasyon.n_musteri}
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            K-Means ile davranışsal özellikler üzerinde denetimsiz kümeleme — sabit 4 persona etiketi yerine,
            verinin kendisi kaç doğal grup önerdiğine (silhouette skoruna göre) bakar.{" "}
            <span className="text-primary font-semibold">Bu bir karar bileşeni değildir</span> — hiçbir
            skorlama/karar yoluna beslenmez, yalnızca araştırma/şeffaflık amaçlıdır.
          </p>
          {segmentasyonHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {segmentasyon && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-4">
                {Object.entries(segmentasyon.kume_profilleri)
                  .sort(([, a], [, b]) => b.n - a.n)
                  .map(([kume, prof]) => (
                    <div key={kume} className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                      <div className="flex justify-between items-baseline mb-3">
                        <span className="font-label-mono text-label-mono text-on-surface font-bold">Küme {kume}</span>
                        <span className="font-label-mono text-[10px] text-on-surface-variant">n={prof.n}</span>
                      </div>
                      <div className="mb-3">
                        <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">Ampirik temerrüt oranı</div>
                        <div className="font-headline-md text-headline-md text-secondary">{(prof.temerrut_orani * 100).toFixed(1)}%</div>
                      </div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono mb-1">Persona dağılımı</div>
                      <div className="space-y-1">
                        {Object.entries(prof.persona_dagilimi)
                          .sort(([, a], [, b]) => b - a)
                          .map(([persona, adet]) => (
                            <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                              <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                              <span className="text-on-surface">{adet}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))}
              </div>
              <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">{segmentasyon.not}</p>
            </>
          )}
        </section>

        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <Icon name="rule" className="text-tertiary" />
              <h2 className="font-headline-md text-headline-md">Genelleme &amp; Sağlamlık</h2>
            </div>
            {genelleme && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                referans model: {genelleme.model_adi_referans} · {genelleme.n_musteri} müşteri
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            Rastgele k-fold CV'nin (Model Validity paneli) test edemediği üç soru: model hiç görmediği bir davranış
            profiline genelleşiyor mu, ince işlem geçmişinde zarifçe mi kararsızlaşıyor yoksa güvenle mi yanılıyor,
            ve nedensel özelliklerden hangisi en kolay "oyunlanıyor".
          </p>
          {genellemeHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {genelleme && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R8 — Persona-dışı genelleme
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  Her persona sırayla eğitimden tamamen çıkarılıp test edildi — "hiç görmedim" testi.
                </p>
                <div className="space-y-2 mb-4">
                  {Object.entries(genelleme.persona_disi_genelleme.sonuc).map(([persona, s]) => (
                    <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                      <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                      <span className="text-on-surface">{s.auc != null ? s.auc.toFixed(3) : "—"} (n={s.n_test})</span>
                    </div>
                  ))}
                </div>
                <div className="pt-3 border-t border-outline-variant/20">
                  <div className="text-[10px] text-amber-400 uppercase font-label-mono mb-1">Out-of-time split</div>
                  <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">
                    {genelleme.out_of_time_split.durum} — {genelleme.out_of_time_split.gerekce}
                  </p>
                </div>
              </div>

              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R10 — İnce dosya stres testi
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  Geçmiş ilk K işleme kırpıldığında skor sapması ve anomali bayrağı oranı.
                </p>
                <table className="w-full font-label-mono text-[11px]">
                  <thead>
                    <tr className="text-on-surface-variant text-left">
                      <th className="font-normal pb-1">K</th>
                      <th className="font-normal pb-1 text-right">Ort. Sapma</th>
                      <th className="font-normal pb-1 text-right">Anomali %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(genelleme.ince_dosya_stres_testi.sonuc).map(([k, s]) => (
                      <tr key={k} className="border-t border-outline-variant/10">
                        <td className="py-1 text-on-surface">{k.replace("ilk_", "").replace("_islem", "")}</td>
                        <td className="py-1 text-right text-on-surface">{s.ort_mutlak_sapma}</td>
                        <td className="py-1 text-right text-amber-400">
                          {s.anomali_bayrak_orani != null ? `${(s.anomali_bayrak_orani * 100).toFixed(0)}%` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R11 — Oyunlanabilirlik duyarlılığı
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  %25 "iyileştirme" karşılığında ortalama AKS puan kazancı — yüksek olan, düşük çabayla en çok skor
                  satın alıyor demektir.
                </p>
                <div className="space-y-2">
                  {Object.entries(genelleme.oyunlanabilirlik_duyarliligi.sonuc)
                    .sort(([, a], [, b]) => b.ort_skor_kazanci - a.ort_skor_kazanci)
                    .map(([feat, s]) => (
                      <div key={feat}>
                        <div className="flex justify-between font-label-mono text-label-mono text-[11px] mb-0.5">
                          <span className="text-on-surface-variant">{feat}</span>
                          <span className={s.ort_skor_kazanci > 20 ? "text-error" : "text-on-surface"}>
                            +{s.ort_skor_kazanci}
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            className={`h-full ${s.ort_skor_kazanci > 20 ? "bg-error" : "bg-secondary-container"}`}
                            style={{ width: `${Math.min(100, Math.max(2, (s.ort_skor_kazanci / 100) * 100))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </section>

        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Icon name="terminal" className="text-tertiary" />
            <h2 className="font-headline-md text-headline-md">Agent Beş-Soru Denetimi</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-gutter">
            {AGENT_AUDIT.map((a) => (
              <div
                key={a.ad}
                className={`p-4 rounded bg-surface-container-lowest border transition-all ${
                  a.gecti ? "border-secondary/50" : "border-outline-variant/20"
                }`}
              >
                <div className="flex justify-between items-start mb-3">
                  <span
                    className={`font-label-mono text-label-mono text-[10px] px-1.5 py-0.5 rounded ${
                      a.gecti ? "text-secondary bg-secondary/10" : "text-on-surface-variant bg-outline-variant/10"
                    }`}
                  >
                    {a.gecti ? "AGENT" : "PIPELINE STAGE"}
                  </span>
                </div>
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-2">{a.ad}</div>
                <p className="font-body-sm text-body-sm text-on-surface-variant">{a.verdict}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
```

### A4. `CustomersPage.tsx` — rota `/customers`

**Stitch brief:** Bir "canlı değerlendirme kuyruğu" tablo sayfası. Üstte
başlık + nabız animasyonlu "Skorlanıyor…/Canlı Değerlendirme Kuyruğu"
etiketi + 3 özet rakam (kurtarılan, yüklenen, ort. kapasite). Altında bir
filtre çubuğu: 4 pill-buton (Tümü/Kurtarılan/Reddedilen/Hedef Segment) +
sağda bir arama kutusu (ID veya persona). Ana gövde: geniş bir tablo
(Kimlik/Persona rozetleri, kapasite sinyali ilerleme çubuğu, skor değişim
yüzdesi, klasik skor, AKS skor, "aç" ikonu). Sağ altta (yalnızca geniş
ekranda) sabit-konumlu, yarı saydam bir **"Etkinlik Günlüğü"** paneli —
her müşteri skorlanırken `[OK]`/`[ERR]` satırları canlı akar (dekoratif
telemetri hissi).

**Veri/durum:** mount'ta `api.bilgi()` (evren büyüklüğü) + `api.demoMusteriler(6)`
→ her ID için ayrı ayrı `api.skorlaDemo(id)` çağrılır ve sonuçlar geldikçe
tabloya teker teker eklenir (hepsi birden değil — kademeli doluş efekti).
Filtre/arama `useMemo` ile client-side.

```tsx
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, PERSONA_ETIKET, HEDEF_PERSONALAR, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, kapasiteYuzdesi, skorDeltaYuzde, type Durum } from "../lib/skor";

interface Satir extends SkorSonuc {
  id: number;
}

const ADET_PER_PERSONA = 6;

type Filtre = "hepsi" | "kurtarildi" | "reddedildi" | "hedef";

export default function CustomersPage() {
  const [satirlar, setSatirlar] = useState<Satir[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [evrenBuyuklugu, setEvrenBuyuklugu] = useState<number | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");
  const [filtre, setFiltre] = useState<Filtre>("hepsi");
  const [arama, setArama] = useState("");

  useEffect(() => {
    let iptal = false;
    setYukleniyor(true);
    setSatirlar([]);
    setLog([]);
    api
      .bilgi()
      .then((b) => !iptal && setEvrenBuyuklugu(b.demo_musteri_sayisi))
      .catch(() => {});
    api
      .demoMusteriler(ADET_PER_PERSONA)
      .then(async (grup) => {
        const ids = Object.values(grup).flat();
        setLog((l) => [...l, `[INFO] ${ids.length} demo müşteri kimliği alındı`]);
        await Promise.all(
          ids.map(async (id) => {
            try {
              const s = await api.skorlaDemo(id);
              if (iptal) return;
              setSatirlar((prev) => [...prev, { ...s, id }].sort((a, b) => a.id - b.id));
              setLog((l) => [...l.slice(-30), `[OK] #${id} skorlandı → AKS ${s.aks_skor}`]);
            } catch {
              setLog((l) => [...l.slice(-30), `[ERR] #${id} skorlanamadı`]);
            }
          })
        );
      })
      .catch((e) => setHata(String(e)))
      .finally(() => !iptal && setYukleniyor(false));
    return () => {
      iptal = true;
    };
  }, []);

  const filtreli = useMemo(() => {
    return satirlar.filter((s) => {
      const durum: Durum = durumBelirle(s.klasik_skor, s.aks_skor);
      if (filtre === "kurtarildi" && durum !== "kurtarildi") return false;
      if (filtre === "reddedildi" && durum !== "reddedildi") return false;
      if (filtre === "hedef" && !HEDEF_PERSONALAR.includes(s.persona)) return false;
      if (arama) {
        const q = arama.toLowerCase();
        const hit = String(s.id).includes(q) || (PERSONA_ETIKET[s.persona] ?? s.persona).toLowerCase().includes(q);
        if (!hit) return false;
      }
      return true;
    });
  }, [satirlar, filtre, arama]);

  const kurtarilanSayisi = satirlar.filter((s) => durumBelirle(s.klasik_skor, s.aks_skor) === "kurtarildi").length;
  const ortKapasite = satirlar.length
    ? Math.round(satirlar.reduce((sum, s) => sum + kapasiteYuzdesi(s.aks_skor), 0) / satirlar.length)
    : 0;

  return (
    <div className="flex flex-col gap-stack-md">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-stack-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className={`flex h-2 w-2 rounded-full ${yukleniyor ? "bg-secondary ai-pulse" : "bg-secondary"}`} />
            <span className="font-label-mono text-label-mono text-secondary uppercase tracking-widest">
              {yukleniyor ? "Skorlanıyor…" : "Canlı Değerlendirme Kuyruğu"}
            </span>
          </div>
          <h1 className="font-display-sm text-display-sm">Customer Intelligence</h1>
        </div>
        <div className="flex gap-gutter overflow-x-auto pb-2">
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Kurtarılan</span>
            <span className="font-display-sm text-display-sm text-primary">{kurtarilanSayisi}</span>
          </div>
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Yüklenen</span>
            <span className="font-display-sm text-display-sm">{satirlar.length}</span>
          </div>
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Ort. Kapasite</span>
            <span className="font-display-sm text-display-sm">{ortKapasite}%</span>
          </div>
        </div>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      <div className="bg-surface-container-lowest/50 border border-outline-variant/30 rounded-xl p-4 backdrop-blur-md flex flex-wrap items-center gap-stack-md">
        <div className="flex items-center gap-stack-sm mr-auto flex-wrap">
          {([
            ["hepsi", "Tümü"],
            ["kurtarildi", "Kurtarılan"],
            ["reddedildi", "Reddedilen"],
            ["hedef", "Hedef Segment"],
          ] as [Filtre, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setFiltre(key)}
              className={`px-4 py-1.5 rounded-full font-label-mono text-label-mono transition-transform hover:scale-105 active:scale-95 ${
                filtre === key ? "bg-primary-container text-on-primary-container" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 font-label-mono text-label-mono bg-surface-container px-3 py-1.5 rounded border border-outline-variant/20">
          <Icon name="search" className="text-sm" />
          <input
            value={arama}
            onChange={(e) => setArama(e.target.value)}
            placeholder="ID veya persona ara…"
            className="bg-transparent outline-none placeholder:text-on-surface-variant/60 w-40"
          />
        </div>
      </div>

      <div className="bg-surface-container border border-outline-variant/30 rounded-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="glass-header text-on-surface-variant font-label-mono text-label-mono uppercase tracking-widest">
                <th className="py-4 px-6 font-medium">Kimlik / Persona</th>
                <th className="py-4 px-6 font-medium">Kapasite Sinyali</th>
                <th className="py-4 px-6 font-medium">Skor Değişimi</th>
                <th className="py-4 px-6 font-medium">Klasik Skor</th>
                <th className="py-4 px-6 font-medium">AKS Skoru</th>
                <th className="py-4 px-6 font-medium text-right">İşlem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filtreli.map((s) => {
                const durum = durumBelirle(s.klasik_skor, s.aks_skor);
                const delta = skorDeltaYuzde(s.klasik_skor, s.aks_skor);
                const kapasite = kapasiteYuzdesi(s.aks_skor);
                const renk = durum === "kurtarildi" ? "text-secondary" : durum === "reddedildi" ? "text-error" : "text-primary";
                return (
                  <tr className="command-table-row transition-all duration-150" key={s.id}>
                    <td className="py-4 px-6">
                      <div className="flex flex-col">
                        <span className="font-bold text-on-surface">CST-{String(s.id).padStart(4, "0")}</span>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          <span className="bg-tertiary-container/30 text-tertiary px-2 py-0.5 rounded text-[10px] uppercase font-bold border border-tertiary-container/50">
                            {PERSONA_ETIKET[s.persona]?.split(" ")[0] ?? s.persona}
                          </span>
                          {durum === "kurtarildi" && (
                            <span className="bg-secondary-container/30 text-secondary px-2 py-0.5 rounded text-[10px] uppercase font-bold border border-secondary-container/50">
                              Kurtarıldı
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-1 bg-surface-container-highest rounded-full overflow-hidden min-w-[80px]">
                          <div className={`h-full ${renk.replace("text-", "bg-")}`} style={{ width: `${kapasite}%` }} />
                        </div>
                        <span className={`font-label-mono text-label-mono ${renk}`}>{kapasite}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`font-bold font-label-mono ${delta != null && delta >= 0 ? "text-secondary" : "text-error"}`}>
                        {delta != null ? `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%` : "—"}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-label-mono opacity-60">{s.klasik_skor ?? "—"}</td>
                    <td className={`py-4 px-6 font-label-mono font-bold ${renk}`}>{s.aks_skor}</td>
                    <td className="py-4 px-6 text-right">
                      <Link to={`/customers/${s.id}`} className="text-on-surface-variant hover:text-primary transition-colors">
                        <Icon name="open_in_new" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="glass-header p-4 flex items-center justify-between font-label-mono text-label-mono text-on-surface-variant flex-wrap gap-2">
          <div className="flex items-center gap-4">
            <span>
              Gösterilen {filtreli.length} / yüklenen {satirlar.length}
              {evrenBuyuklugu != null && ` · demo evreni ${evrenBuyuklugu}`}
            </span>
          </div>
        </div>
      </div>

      <div className="hidden xl:block fixed right-container-padding bottom-6 w-80 bg-surface-container-high/95 backdrop-blur border border-outline-variant/50 rounded-xl shadow-2xl overflow-hidden pointer-events-none">
        <div className="bg-surface-container-highest px-4 py-2 border-b border-outline-variant/30 flex items-center justify-between">
          <span className="font-label-mono text-label-mono text-on-surface">Etkinlik Günlüğü</span>
        </div>
        <div className="p-4 font-label-mono text-[11px] space-y-1.5 leading-relaxed h-56 overflow-y-auto">
          {log.slice(-12).map((l, i) => (
            <p key={i} className={l.startsWith("[ERR]") ? "text-error" : l.startsWith("[OK]") ? "text-on-surface-variant" : "text-primary"}>
              {l}
            </p>
          ))}
          {!yukleniyor && <p className="text-on-surface-variant opacity-40">&gt; hazır</p>}
        </div>
      </div>
    </div>
  );
}
```

### A5. `CustomerDetailPage.tsx` — rota `/customers/:id`

**Stitch brief:** En zengin sayfa — bir müşterinin tam dosyası. Üst
başlıkta avatar-daire + "Müşteri #ID" + persona rozeti + varsa "Kurtarıldı"
ve "Atipik Profil (OOD)" rozetleri, sağda geri dönüş linki. Grid: (1) geniş
bir **"Kalibrasyon Haritası"** kartı — klasik skor solda kırmızı, ok
ortada, AKS skoru sağda mor/glow, altında (varsa) PD-Gap satırı; (2) dar
bir **"Önerilen Limit"** kartı — karar metni + büyük TL rakamı; (3) dar bir
**"Pipeline İzi"** kartı — dikey zaman çizelgesi (VeriAgent→SkorlamaAgent→
DanismanAgent, her biri renkli nokta + açıklama); (4) geniş bir **SHAP
faktör ızgarası** (yeşil/kırmızı kartlar) + öneri listesi; (5) tam genişlik
**"Senaryo Simülatörü (What-If)"** — 9 özellik için range-slider'lar,
altında canlı "Mevcut Skor → Senaryo Skoru" karşılaştırması (400ms
debounce ile backend'e gider); (6) **"Değerlendirme Geçmişi"** listesi; (7)
**"AKS Asistanı"** — serbest metin soru kutusu + "Sor" butonu + yanıt metni.

**Veri/durum:** mount'ta `api.skorlaDemo(id)` + `api.gecmis(id)` paralel.
Slider değişince 400ms debounce sonrası `api.simulasyon(id, degisenler)`.
"Sor" butonunda `api.asistan(soru, baglam)` — bağlam mevcut skor/açıklama/
danışman verisinden inşa edilir (uydurma yok, sunucudan gelen gerçek
veriler tekrar gönderiliyor).

```tsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, PERSONA_ETIKET, type SkorSonuc, type GecmisKayit, type SimulasyonSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, paraFormat } from "../lib/skor";

const SENARYO_OZELLIKLERI: { kod: string; etiket: string; min: number; max: number; adim: number }[] = [
  { kod: "toplam_gelir_hacmi", etiket: "Toplam gelir hacmi (TL)", min: 0, max: 250000, adim: 1000 },
  { kod: "toplam_gider_hacmi", etiket: "Toplam gider hacmi (TL)", min: 0, max: 250000, adim: 1000 },
  { kod: "gelir_islem_sayisi", etiket: "Gelir işlem sayısı", min: 0, max: 30, adim: 1 },
  { kod: "gelir_kaynagi_sayisi", etiket: "Gelir kaynağı çeşitliliği", min: 0, max: 6, adim: 1 },
  { kod: "gelir_duzenliligi", etiket: "Gelir düzenliliği", min: 0, max: 1, adim: 0.05 },
  { kod: "gider_gelir_orani", etiket: "Gider/gelir oranı", min: 0, max: 4.5, adim: 0.05 },
  { kod: "bakiye_trendi", etiket: "Bakiye trendi (tasarruf eğilimi)", min: -35, max: 80, adim: 1 },
  { kod: "fatura_odeme_duzeni", etiket: "Fatura ödeme düzeni", min: 0, max: 1, adim: 0.05 },
  { kod: "hesap_hareket_yogunlugu", etiket: "Hesap hareket yoğunluğu", min: 0, max: 1.5, adim: 0.01 },
];

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const musteriId = Number(id);

  const [sonuc, setSonuc] = useState<SkorSonuc | null>(null);
  const [gecmis, setGecmis] = useState<GecmisKayit[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");

  const [soru, setSoru] = useState("");
  const [yanit, setYanit] = useState<string | null>(null);
  const [soruYukleniyor, setSoruYukleniyor] = useState(false);

  const [senaryoDegerler, setSenaryoDegerler] = useState<Record<string, number> | null>(null);
  const [simSonuc, setSimSonuc] = useState<SimulasyonSonuc | null>(null);
  const [simYukleniyor, setSimYukleniyor] = useState(false);
  const [simHata, setSimHata] = useState("");

  useEffect(() => {
    if (sonuc) setSenaryoDegerler(sonuc.ozellikler);
  }, [sonuc]);

  useEffect(() => {
    if (!sonuc || !senaryoDegerler) return;
    const degisen: Record<string, number> = {};
    for (const { kod } of SENARYO_OZELLIKLERI) {
      if (senaryoDegerler[kod] !== sonuc.ozellikler[kod]) degisen[kod] = senaryoDegerler[kod];
    }
    if (Object.keys(degisen).length === 0) {
      setSimSonuc(null);
      setSimHata("");
      return;
    }
    const zamanlayici = setTimeout(() => {
      setSimYukleniyor(true);
      setSimHata("");
      api
        .simulasyon(musteriId, degisen)
        .then(setSimSonuc)
        .catch((e) => setSimHata(String(e instanceof Error ? e.message : e)))
        .finally(() => setSimYukleniyor(false));
    }, 400);
    return () => clearTimeout(zamanlayici);
  }, [senaryoDegerler, sonuc, musteriId]);

  useEffect(() => {
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    setYanit(null);
    Promise.all([api.skorlaDemo(musteriId), api.gecmis(musteriId).catch(() => null)])
      .then(([s, g]) => {
        setSonuc(s);
        setGecmis(g?.gecmis ?? []);
      })
      .catch((e) => setHata(String(e)))
      .finally(() => setYukleniyor(false));
  }, [musteriId]);

  async function sorSor() {
    if (!soru.trim() || !sonuc) return;
    setSoruYukleniyor(true);
    try {
      const r = await api.asistan(soru, {
        aks_skor: sonuc.aks_skor,
        klasik_skor: sonuc.klasik_skor,
        risk_seviyesi: sonuc.risk_seviyesi,
        onerilen_limit: sonuc.onerilen_limit,
        aciklama: sonuc.aciklama,
        danisman: sonuc.danisman,
      });
      setYanit(r.yanit);
    } catch (e) {
      setYanit(`Hata: ${e}`);
    } finally {
      setSoruYukleniyor(false);
    }
  }

  if (yukleniyor) {
    return <p className="font-body-sm text-body-sm text-on-surface-variant p-8">Yükleniyor…</p>;
  }

  if (hata || !sonuc) {
    return (
      <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-6 font-label-mono text-label-mono">
        Müşteri #{musteriId} bulunamadı ya da backend'e ulaşılamadı: {hata}
        <div className="mt-4">
          <Link to="/customers" className="text-primary hover:underline">
            ← Müşteri kuyruğuna dön
          </Link>
        </div>
      </div>
    );
  }

  const durum = durumBelirle(sonuc.klasik_skor, sonuc.aks_skor);
  const delta = sonuc.klasik_skor != null ? sonuc.aks_skor - sonuc.klasik_skor : null;

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-stack-md hairline-border bg-surface-container-low p-6 rounded-xl">
        <div className="flex items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center border border-outline-variant/50 relative">
            <Icon name="person" className="text-4xl text-secondary" />
          </div>
          <div>
            <h1 className="font-headline-md text-headline-md md:font-display-sm md:text-display-sm text-on-background">
              Müşteri #{musteriId}
            </h1>
            <div className="flex gap-4 mt-2 flex-wrap">
              <span className="font-label-mono text-label-mono text-secondary px-2 py-1 bg-secondary/10 rounded-DEFAULT border border-secondary/20">
                {PERSONA_ETIKET[sonuc.persona] ?? sonuc.persona}
              </span>
              {durum === "kurtarildi" && (
                <span className="font-label-mono text-label-mono text-emerald-400 px-2 py-1 bg-emerald-400/10 rounded-DEFAULT border border-emerald-400/20 flex items-center gap-1">
                  <Icon name="verified" className="text-[12px]" /> {DURUM_ETIKET[durum]}
                </span>
              )}
              {sonuc.anomali_bayrak && (
                <span
                  className="font-label-mono text-label-mono text-amber-400 px-2 py-1 bg-amber-400/10 rounded-DEFAULT border border-amber-400/20 flex items-center gap-1"
                  title={`Tipiklik skoru: ${sonuc.anomali_skoru} — negatife yaklaştıkça daha aykırı`}
                >
                  <Icon name="warning" className="text-[12px]" /> Atipik Profil (OOD)
                </span>
              )}
            </div>
            {sonuc.anomali_bayrak && (
              <p className="font-body-sm text-body-sm text-amber-400/90 mt-2 max-w-md">
                Bu profil, eğitim dağılımının tipik aralığının dışında — skoru DEĞİŞTİRMEZ, yalnızca modele diğer
                profillere göre biraz daha az güvenilmesi gerektiğini işaret eder.
              </p>
            )}
          </div>
        </div>
        <Link
          to="/customers"
          className="px-4 py-2 bg-transparent border border-outline-variant/50 rounded-DEFAULT font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
        >
          ← Kuyruğa Dön
        </Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-stack-md">
        <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6 relative overflow-hidden ai-glow flex flex-col justify-between">
          <div className="glass-header absolute top-0 left-0 w-full p-4 flex justify-between items-center z-10">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Kalibrasyon Haritası</h2>
            <Icon name="radar" className="text-primary-fixed-dim" />
          </div>
          <div className="mt-12 flex-1 flex flex-col items-center justify-center relative">
            <div className="flex items-center justify-center gap-stack-lg w-full relative z-20">
              <div className="text-center">
                <span className="font-label-mono text-label-mono text-on-surface-variant block mb-2">Klasik Skor</span>
                <span className="font-display-lg text-display-lg text-error">{sonuc.klasik_skor ?? "—"}</span>
              </div>
              <div className="h-[2px] w-32 bg-gradient-to-r from-error/50 via-outline-variant/50 to-primary/50 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container px-2">
                  <Icon name="arrow_forward" className="text-outline" />
                </div>
              </div>
              <div className="text-center">
                <span className="font-label-mono text-label-mono text-on-surface-variant block mb-2">AKS Skoru</span>
                <span className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_10px_rgba(195,192,255,0.5)]">
                  {sonuc.aks_skor}
                </span>
                <span className="font-body-sm text-body-sm text-primary/80 block mt-1">
                  {delta != null ? `${delta >= 0 ? "+" : ""}${delta} pts` : ""}
                </span>
              </div>
            </div>
          </div>
          {sonuc.pd_fark != null && (
            <div className="mt-6 pt-4 border-t border-outline-variant/20 flex items-center justify-center gap-stack-lg relative z-20">
              <div className="text-center">
                <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">Geleneksel Bant PD</span>
                <span className="font-body-lg text-body-lg text-on-surface">{(sonuc.pd_geleneksel_bant! * 100).toFixed(1)}%</span>
              </div>
              <div className="text-center">
                <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">PD-Gap</span>
                <span className={`font-headline-md text-headline-md ${sonuc.pd_fark >= 0 ? "text-emerald-400" : "text-error"}`}>
                  {sonuc.pd_fark >= 0 ? "+" : ""}
                  {(sonuc.pd_fark * 100).toFixed(1)}pp
                </span>
              </div>
              <div className="text-center">
                <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">Kapasite Sinyali</span>
                <span className="font-body-lg text-body-lg text-primary">{sonuc.kapasite_sinyali}/100</span>
              </div>
            </div>
          )}
          <p className="font-label-mono text-[10px] text-on-surface-variant mt-3 relative z-20 text-center">
            Pozitif PD-Gap: davranışsal kanıt, geleneksel bandın ima ettiğinden daha fazla kapasite gösteriyor.
            Bankanın skorunu değiştirmez, yalnızca tamamlar.
          </p>
        </div>

        <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 border-b border-outline-variant/20 pb-2">
              Önerilen Limit
            </h2>
            <div className="mt-8 text-center">
              <span className="font-label-mono text-label-mono text-secondary mb-2 block">{sonuc.karar}</span>
              <div className="font-display-sm text-display-sm text-on-background">{paraFormat(sonuc.onerilen_limit)}</div>
            </div>
          </div>
          <p className="mt-8 text-center font-label-mono text-[10px] text-on-surface-variant">
            Bu değerlendirme, değiştirilemez denetim iziyle otomatik olarak kaydedildi.
          </p>
        </div>

        <div className="col-span-1 md:col-span-4 bg-surface-container hairline-border rounded-xl p-6">
          <div className="glass-header w-full pb-4 mb-4 flex justify-between items-center">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Pipeline İzi</h2>
            <Icon name="account_tree" className="text-on-surface-variant text-sm" />
          </div>
          <div className="relative pl-6 border-l border-outline-variant/30 space-y-6">
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-secondary rounded-full" />
              <div className="font-label-mono text-label-mono text-secondary">VeriAgent (pipeline aşaması)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
                9 davranışsal özellik ham işlemlerden çıkarıldı.
              </p>
            </div>
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-primary-container rounded-full" />
              <div className="font-label-mono text-label-mono text-primary">SkorlamaAgent (pipeline aşaması)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
                Risk seviyesi: {sonuc.risk_seviyesi}. Karar: {sonuc.karar}.
              </p>
            </div>
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-emerald-400 rounded-full" />
              <div className="font-label-mono text-label-mono text-emerald-400">DanismanAgent (şablonlu)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">{sonuc.danisman.ozet}</p>
            </div>
          </div>
        </div>

        <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6">
          <div className="glass-header w-full pb-4 mb-6 flex justify-between items-center">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Davranışsal Faktörler (SHAP)</h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {sonuc.aciklama.riski_azaltan.map((f) => (
              <div className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg hover:border-emerald-400/50 transition-colors" key={f.kod}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-label-mono text-[10px] text-emerald-400">RİSKİ AZALTIR</span>
                  <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                </div>
                <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
              </div>
            ))}
            {sonuc.aciklama.riski_artiran.map((f) => (
              <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg hover:border-error/50 transition-colors" key={f.kod}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-label-mono text-[10px] text-error">RİSKİ ARTIRIR</span>
                  <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                </div>
                <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
              </div>
            ))}
          </div>
          {sonuc.danisman.oneriler.length > 0 && (
            <div className="mt-6 pt-6 border-t border-outline-variant/20">
              <h3 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-3">Öneriler</h3>
              <ul className="space-y-2">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
          <div className="glass-header w-full pb-4 mb-6 flex justify-between items-center flex-wrap gap-2">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
              Senaryo Simülatörü (What-If)
            </h2>
            <button
              onClick={() => sonuc && setSenaryoDegerler(sonuc.ozellikler)}
              className="px-3 py-1.5 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-[10px] text-on-surface hover:bg-surface-container-high transition-colors"
            >
              Sıfırla
            </button>
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6">
            Davranışsal özellikleri elle değiştirip skorun nasıl tepki verdiğini gözlemleyin —{" "}
            <code className="font-label-mono text-[11px] bg-surface-container-high px-1 rounded">POST /api/simulasyon</code>{" "}
            ile canlı model üzerinden hesaplanır (yeniden eğitim değil, aynı modelin farklı bir girdiyle tahmini).
            Bu, gerçek işlemleri değiştirmez; yalnızca "ne olurdu" sorusuna cevap verir.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5 mb-6">
            {senaryoDegerler &&
              SENARYO_OZELLIKLERI.map(({ kod, etiket, min, max, adim }) => (
                <div key={kod}>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="font-label-mono text-[11px] text-on-surface-variant">{etiket}</label>
                    <span className="font-label-mono text-[11px] text-primary">
                      {senaryoDegerler[kod]?.toLocaleString("tr-TR")}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={min}
                    max={max}
                    step={adim}
                    value={senaryoDegerler[kod] ?? 0}
                    onChange={(e) =>
                      setSenaryoDegerler((prev) => ({ ...(prev ?? {}), [kod]: Number(e.target.value) }))
                    }
                    className="w-full accent-primary"
                  />
                </div>
              ))}
          </div>

          {simHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-body-sm text-body-sm mb-4">
              {simHata}
            </div>
          )}

          <div className="flex items-center justify-center gap-stack-lg bg-surface-container-low rounded-lg p-6 border border-outline-variant/20">
            <div className="text-center">
              <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">Mevcut Skor</span>
              <span className="font-display-sm text-display-sm text-on-surface">
                {simSonuc?.mevcut_skor ?? sonuc.aks_skor}
              </span>
            </div>
            <Icon name="arrow_forward" className="text-outline" />
            <div className="text-center">
              <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">Senaryo Skoru</span>
              <span className="font-display-sm text-display-sm text-primary">
                {simYukleniyor ? "…" : (simSonuc?.senaryo_skor ?? sonuc.aks_skor)}
              </span>
            </div>
            {simSonuc && (
              <div className="text-center">
                <span className="font-label-mono text-[10px] text-on-surface-variant uppercase block mb-1">Değişim</span>
                <span
                  className={`font-headline-md text-headline-md ${
                    simSonuc.skor_degisimi >= 0 ? "text-emerald-400" : "text-error"
                  }`}
                >
                  {simSonuc.skor_degisimi >= 0 ? "+" : ""}
                  {simSonuc.skor_degisimi}
                </span>
                <span className="font-label-mono text-[10px] text-on-surface-variant block mt-1">
                  {simSonuc.senaryo_karar}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="col-span-1 md:col-span-6 bg-surface-container hairline-border rounded-xl p-6">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">Değerlendirme Geçmişi</h2>
          {gecmis.length === 0 ? (
            <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz kayıtlı geçmiş yok (ilk değerlendirme).</p>
          ) : (
            <ul className="space-y-2 font-label-mono text-label-mono">
              {gecmis.map((g, i) => (
                <li key={i} className="flex justify-between border-b border-outline-variant/10 pb-2">
                  <span className="text-on-surface-variant">{g.zaman}</span>
                  <span className="text-primary">AKS {g.aks_skor}</span>
                  <span className="text-on-surface-variant">{g.risk_seviyesi}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="col-span-1 md:col-span-6 bg-surface-container hairline-border rounded-xl p-6">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
            <Icon name="smart_toy" className="text-sm" /> AKS Asistanı
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <input
              value={soru}
              onChange={(e) => setSoru(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sorSor()}
              placeholder="Skoru nasıl yükseltirim?"
              className="flex-1 bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
            <button
              onClick={sorSor}
              disabled={soruYukleniyor}
              className="px-4 py-2 rounded bg-primary-container text-on-primary-container font-label-mono text-label-mono hover:brightness-110 transition-all disabled:opacity-50"
            >
              {soruYukleniyor ? "…" : "Sor"}
            </button>
          </div>
          {yanit && <p className="font-body-sm text-body-sm text-on-surface-variant whitespace-pre-line">{yanit}</p>}
        </div>
      </div>
    </div>
  );
}
```

### A6. `CsvUploadPage.tsx` — rota `/upload`

**Stitch brief:** Belge yükleme sayfası — `Layout` altında olduğu için artık
**yalnızca yönetici** görür (bkz. §7.11: `api/csv-skorla` `YoneticiKullanici`
ile korunuyor; son kullanıcının karşılığı ayrı bir uç, `/api/portal/yukle`,
`PortalPage`'de). Üstte başlık + açıklama. Bir "beklenen kolonlar" bilgi
kartı (kolon rozetleri + "örnek CSV indir" butonu). Ortada büyük bir
**sürükle-bırak yükleme alanı** (dosya seçiliyken ad+boyut gösterir,
sürüklenirken kenarlık mora döner; 10 MB üstü dosya backend'den anlamlı bir
hata mesajıyla reddedilir). Altta sonuç geldiğinde: kalite/OOD uyarı
banner'ları, 3 özet kutu (AKS skoru büyük rakam, önerilen limit,
"Formülasyon B hesaplanmadı" notu), SHAP ızgarası + danışman özeti, ve
açılır bir "Belge Agent İzi" detay paneli (`<details>`).

**Veri/durum:** dosya state'i sürükle-bırak veya dosya seçici ile
doldurulur; "Skorla" butonu `api.csvSkorla(dosya)` çağırır. Kimlik/rıza
katmanı yine yok (bu uç kimlik doğrulaması gerektirmez, ama sayfaya erişim
`Layout`'un yönetici kapısından geçer).

```tsx
import { useRef, useState } from "react";
import { api, type CsvSkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { paraFormat } from "../lib/skor";

const BELGE_BAYRAK_METNI: Record<string, string> = {
  pencere_uyumsuz: "Ekstre süresi, modelin eğitildiği ~6 aylık pencereden belirgin şekilde sapıyor.",
  dusuk_kategori_guveni: "İşlem kategorileri güvenle tahmin edilemedi — sonuç daha az kesin olabilir.",
  yuksek_atlanan_satir_orani: "Dosyadaki satırların önemli bir kısmı okunamadı.",
  bos_belge: "Belgeden hiç işlem çıkarılamadı.",
};

const ORNEK_CSV = `tarih,islem_tipi,kategori,tutar,aciklama
2026-01-02,gelir,maas_odemesi,18000,Ocak maaşı
2026-01-09,gider,yeme_icme,-1400,market
2026-01-15,gider,ulasim,-850,otobüs
2026-01-29,gider,fatura,-900,elektrik
2026-02-02,gelir,maas_odemesi,18000,Şubat maaşı
2026-02-11,gider,fatura,-950,su
`;

function ornekIndir() {
  const blob = new Blob([ORNEK_CSV], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "aks_ornek_ekstre.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export default function CsvUploadPage() {
  const [dosya, setDosya] = useState<File | null>(null);
  const [suruklemede, setSuruklemede] = useState(false);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");
  const [sonuc, setSonuc] = useState<CsvSkorSonuc | null>(null);
  const girisRef = useRef<HTMLInputElement>(null);

  function dosyaSec(f: File | null) {
    setSonuc(null);
    setHata("");
    setDosya(f);
  }

  async function gonder() {
    if (!dosya) return;
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    try {
      const r = await api.csvSkorla(dosya);
      setSonuc(r);
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="flex flex-col gap-stack-lg pb-8 max-w-4xl mx-auto">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Belge / Ekstre Yükleme</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kendi işlem ekstrenizi (CSV, Excel ya da PDF) yükleyin — AKS aynı davranışsal model ile (dekuple/LR
          eğitimli) canlı bir skor üretir. Bu yol demo popülasyonundan bağımsızdır; her istek{" "}
          <code className="font-label-mono text-[11px] bg-surface-container px-1 rounded">POST /api/csv-skorla</code>{" "}
          uç noktasına gider.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6">
        <div className="flex justify-between items-start gap-4 flex-wrap">
          <div>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-2">
              CSV İçin Beklenen Kolonlar (Excel/PDF Otomatik Tanınır)
            </h2>
            <div className="flex flex-wrap gap-2">
              {["tarih (YYYY-AA-GG)", "islem_tipi (gelir/gider)", "kategori", "tutar", "aciklama (opsiyonel)"].map(
                (k) => (
                  <span
                    key={k}
                    className="font-label-mono text-[11px] bg-surface-container-high border border-outline-variant/30 px-2 py-1 rounded-DEFAULT text-on-surface"
                  >
                    {k}
                  </span>
                )
              )}
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-3">
              Gider tutarları <strong>negatif</strong> yazılmalı (örn. <code>-850</code>). En az 5 işlem gerekir.
            </p>
          </div>
          <button
            onClick={ornekIndir}
            className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
          >
            <Icon name="download" className="text-[16px]" />
            Örnek CSV indir
          </button>
        </div>
      </section>

      <section
        className={`card-surface rounded-lg p-8 border-2 border-dashed transition-colors ${
          suruklemede ? "border-primary bg-primary-container/10" : "border-outline-variant/40"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setSuruklemede(true);
        }}
        onDragLeave={() => setSuruklemede(false)}
        onDrop={(e) => {
          e.preventDefault();
          setSuruklemede(false);
          const f = e.dataTransfer.files?.[0];
          if (f) dosyaSec(f);
        }}
      >
        <input
          ref={girisRef}
          type="file"
          accept=".csv,text/csv,.xlsx,.xls,.pdf,application/pdf"
          className="hidden"
          onChange={(e) => dosyaSec(e.target.files?.[0] ?? null)}
        />
        <div className="flex flex-col items-center text-center gap-3">
          <Icon name="upload_file" className="text-5xl text-primary" />
          {dosya ? (
            <>
              <div className="font-body-sm text-body-sm text-on-surface font-semibold">{dosya.name}</div>
              <div className="font-label-mono text-[11px] text-on-surface-variant">
                {(dosya.size / 1024).toFixed(1)} KB
              </div>
            </>
          ) : (
            <>
              <div className="font-body-sm text-body-sm text-on-surface">
                CSV, Excel ya da PDF dosyasını buraya sürükleyin veya seçin
              </div>
              <div className="font-label-mono text-[11px] text-on-surface-variant">.csv / .xlsx / .pdf</div>
            </>
          )}
          <div className="flex gap-3 mt-2">
            <button
              onClick={() => girisRef.current?.click()}
              className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
            >
              Dosya Seç
            </button>
            <button
              onClick={gonder}
              disabled={!dosya || yukleniyor}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40"
            >
              {yukleniyor ? "Skorlanıyor…" : "Skorla"}
            </button>
          </div>
        </div>
      </section>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      )}

      {sonuc && (
        <section className="grid grid-cols-1 md:grid-cols-12 gap-stack-md">
          {sonuc.anomali_bayrak && (
            <div className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2">
              <Icon name="warning" className="text-[16px] shrink-0" />
              Bu ekstre, İzolasyon Ormanı'na (denetimsiz OOD tespiti) göre eğitim dağılımının tipik aralığının
              dışında bir profil gösteriyor — skoru değiştirmez, yalnızca modele diğer profillere göre biraz daha
              az güvenilmesi gerektiğini işaret eder (tipiklik skoru: {sonuc.anomali_skoru}).
            </div>
          )}
          {(sonuc.belge_meta?.bayraklar ?? []).map((b) => (
            <div
              key={b}
              className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2"
            >
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BELGE_BAYRAK_METNI[b] ?? b}
            </div>
          ))}
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">AKS Skoru</span>
            <span className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_10px_rgba(195,192,255,0.5)]">
              {sonuc.aks_skor}
            </span>
            <span className="font-label-mono text-label-mono text-secondary mt-3">{sonuc.risk_seviyesi}</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant mt-1">{sonuc.karar}</span>
          </div>

          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Önerilen Limit</span>
            <span className="font-display-sm text-display-sm text-on-background">
              {paraFormat(sonuc.onerilen_limit)}
            </span>
            <span className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              {sonuc.islem_sayisi} işlemden hesaplandı
            </span>
          </div>

          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-center">
            <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">
              Bu yükleme yolunda banka/klasik skor bilinmiyor, bu yüzden Formülasyon B (PD-Gap / Kapasite Sinyali)
              hesaplanmaz — yalnızca demo müşterileri için (klasik skor bilindiğinde) üretilir.
            </p>
          </div>

          <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Davranışsal Faktörler (SHAP)
            </h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {sonuc.aciklama.riski_azaltan.map((f) => (
                <div
                  className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg"
                  key={f.kod}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-emerald-400">RİSKİ AZALTIR</span>
                    <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
              {sonuc.aciklama.riski_artiran.map((f) => (
                <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-error">RİSKİ ARTIRIR</span>
                    <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-1 md:col-span-4 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Danışman Özeti
            </h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-4">{sonuc.danisman.ozet}</p>
            {sonuc.danisman.oneriler.length > 0 && (
              <ul className="space-y-2">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {!!sonuc.belge_meta?.iz?.length && (
            <details className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
              <summary className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider cursor-pointer">
                Belge Agent İzi ({sonuc.belge_meta.kaynak_format?.toUpperCase()})
              </summary>
              <ol className="mt-4 space-y-1.5">
                {sonuc.belge_meta.iz.map((adim, i) => (
                  <li key={i} className="font-label-mono text-[11px] text-on-surface-variant flex gap-2">
                    <span className="text-primary shrink-0">{i + 1}.</span>
                    {adim}
                  </li>
                ))}
              </ol>
            </details>
          )}
        </section>
      )}
    </div>
  );
}
```

### A7. `BulunamadiPage.tsx` — rota `*` (404)

**Stitch brief:** Basit, ortalanmış 404 ekranı — büyük "404" rakamı, kısa
başlık/açıklama, ve dört dönüş linki: **Ana Sayfa** (birincil) + üç yüzeyin
girişleri (Banka Paneli `/panel`, Kullanıcı Portalı, Kurum Girişi). Sitenin
ayrı giriş kapıları olduğu için hepsi burada sunulur; ana sayfa birincil
buton, diğer üçü çerçeveli ikincil.

```tsx
import { Link } from "react-router-dom";

export default function BulunamadiPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <p className="font-display-lg text-display-lg text-primary">404</p>
        <h1 className="font-headline-md text-headline-md text-on-background mt-2">Sayfa bulunamadı</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2">
          Aradığınız adres mevcut değil ya da taşınmış olabilir.
        </p>
        <div className="flex flex-wrap gap-3 justify-center mt-6">
          <Link
            to="/"
            className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
          >
            Ana Sayfa
          </Link>
          <Link
            to="/panel"
            className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 text-on-surface font-label-mono text-label-mono hover:bg-surface-container transition-colors"
          >
            Banka Paneli
          </Link>
          <Link
            to="/portal"
            className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 text-on-surface font-label-mono text-label-mono hover:bg-surface-container transition-colors"
          >
            Kullanıcı Portalı
          </Link>
          <Link
            to="/kurum/musteriler"
            className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 text-on-surface font-label-mono text-label-mono hover:bg-surface-container transition-colors"
          >
            Kurum Girişi
          </Link>
        </div>
      </div>
    </div>
  );
}
```

---

## Kısım B — Müşteri portalı (`PortalLayout`, `ProfilSahibi`)

### B1. `PortalLoginPage.tsx` — rota `/portal/giris`

**Stitch brief:** Ortalanmış, dar bir kart — ikon + başlık + açıklama,
altında iki sekmeli (Giriş Yap / Kayıt Ol) bir form. Kayıt modunda ekstra
bir bilgi kutusu: "Ad, soyad ve TC kimlik numarası istenmez." E-posta +
şifre alanları, hata banner'ı, gönder butonu.

**Veri/durum:** mount'ta `api.ben()` — zaten girişliyse (ve `aks_no` varsa)
otomatik `/portal`'a yönlendirir. Submit'te moda göre `api.girisYap` veya
`api.kayitOl`.

```tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

export default function PortalLoginPage() {
  const [mod, setMod] = useState<"giris" | "kayit">("giris");
  const [email, setEmail] = useState("");
  const [sifre, setSifre] = useState("");
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .ben()
      .then((k) => {
        if (k.aks_no) navigate("/portal", { replace: true });
      })
      .catch(() => {})
      .finally(() => setKontrolEdiliyor(false));
  }, [navigate]);

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata("");
    setYukleniyor(true);
    try {
      if (mod === "giris") {
        await api.girisYap(email, sifre);
      } else {
        await api.kayitOl(email, sifre);
      }
      navigate("/portal");
    } catch (err) {
      setHata(String(err instanceof Error ? err.message : err));
    } finally {
      setYukleniyor(false);
    }
  }

  if (kontrolEdiliyor) {
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-surface-container-low hairline-border rounded-xl p-8">
        <div className="text-center mb-8">
          <Icon name="account_circle" className="text-5xl text-primary" />
          <h1 className="font-headline-md text-headline-md text-on-background mt-2">AKS Portal</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Kendi ekstrenizi yükleyip davranışsal kapasite analizinizi görün.
          </p>
        </div>

        <div className="flex mb-6 rounded-DEFAULT border border-outline-variant/30 overflow-hidden">
          <button
            type="button"
            onClick={() => setMod("giris")}
            className={`flex-1 py-2 font-label-mono text-label-mono transition-colors ${
              mod === "giris" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            Giriş Yap
          </button>
          <button
            type="button"
            onClick={() => setMod("kayit")}
            className={`flex-1 py-2 font-label-mono text-label-mono transition-colors ${
              mod === "kayit" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            Kayıt Ol
          </button>
        </div>

        <form onSubmit={gonder} className="flex flex-col gap-4">
          {mod === "kayit" && (
            <p className="font-body-sm text-body-sm text-on-surface-variant bg-surface-container rounded-DEFAULT p-3 border border-outline-variant/30">
              Ad, soyad ve T.C. kimlik numarası <strong className="text-on-surface">istenmez</strong>. Hesabınız
              yalnızca e-postanıza ve size özel üretilen AKS numarasına bağlanır.
            </p>
          )}
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="ornek@eposta.com"
            />
          </div>
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
            <input
              type="password"
              required
              minLength={8}
              value={sifre}
              onChange={(e) => setSifre(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="En az 8 karakter"
            />
          </div>

          {hata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-body-sm text-body-sm">
              {hata}
            </div>
          )}

          <button
            type="submit"
            disabled={yukleniyor}
            className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-2"
          >
            {yukleniyor ? "…" : mod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
          </button>
        </form>
      </div>
    </div>
  );
}
```

### B2. `PortalPage.tsx` — rota `/portal` (portal ana sayfası)

**Stitch brief:** `CsvUploadPage` ile neredeyse aynı yükleme UX'i, ama üç
farkla: (1) zorunlu bir **sahiplik beyanı checkbox'ı** ("bu ekstre bana
ait" — onaylanmadan "Analiz Et" butonu disabled), (2) sonuç kartlarında
`sahiplik_bayraklari` da gösterilir (çoklu-sahiplik şüphesi, profil
tutarsızlığı), (3) altta bir **"Geçmişim"** bölümü — her satır tıklanınca
açılıp o yüklemenin tam işlem tablosunu (tarih/kategori/açıklama/tutar)
gösterir (accordion pattern).

**Veri/durum:** `useOutletContext<KullaniciBilgisi>()` ile üstteki
`PortalLayout`'tan kullanıcıyı alır. Mount'ta `api.portalGecmis()`.
Yüklemede `api.portalYukle(dosya, beyan)`. Satır tıklanınca
`api.portalGecmisDetay(id)` (lazy, yalnızca açılınca çekilir).

```tsx
import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import {
  api,
  type CsvSkorSonuc,
  type KullaniciBilgisi,
  type PortalGecmisDetay,
  type PortalGecmisKayit,
} from "../../api";
import { Icon } from "../../components/Icon";
import { paraFormat } from "../../lib/skor";

const ORNEK_CSV = `tarih,islem_tipi,kategori,tutar,aciklama
2026-01-02,gelir,maas_odemesi,18000,Ocak maaşı
2026-01-09,gider,yeme_icme,-1400,market
2026-01-15,gider,ulasim,-850,otobüs
2026-01-29,gider,fatura,-900,elektrik
2026-02-02,gelir,maas_odemesi,18000,Şubat maaşı
2026-02-11,gider,fatura,-950,su
`;

function ornekIndir() {
  const blob = new Blob([ORNEK_CSV], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "aks_ornek_ekstre.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export default function PortalPage() {
  const kullanici = useOutletContext<KullaniciBilgisi>();

  const [dosya, setDosya] = useState<File | null>(null);
  const [suruklemede, setSuruklemede] = useState(false);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");
  const [sonuc, setSonuc] = useState<CsvSkorSonuc | null>(null);
  const [beyan, setBeyan] = useState(false);
  const girisRef = useRef<HTMLInputElement>(null);

  const [gecmis, setGecmis] = useState<PortalGecmisKayit[]>([]);
  const [gecmisYukleniyor, setGecmisYukleniyor] = useState(true);
  const [acikKayitId, setAcikKayitId] = useState<number | null>(null);
  const [detay, setDetay] = useState<PortalGecmisDetay | null>(null);
  const [detayYukleniyor, setDetayYukleniyor] = useState(false);

  function gecmisiYenile() {
    setGecmisYukleniyor(true);
    api
      .portalGecmis()
      .then((r) => setGecmis(r.gecmis))
      .catch(() => {})
      .finally(() => setGecmisYukleniyor(false));
  }

  useEffect(() => {
    gecmisiYenile();
  }, []);

  function kayitAcKapat(id: number) {
    if (acikKayitId === id) {
      setAcikKayitId(null);
      setDetay(null);
      return;
    }
    setAcikKayitId(id);
    setDetay(null);
    setDetayYukleniyor(true);
    api
      .portalGecmisDetay(id)
      .then(setDetay)
      .catch(() => setDetay(null))
      .finally(() => setDetayYukleniyor(false));
  }

  function dosyaSec(f: File | null) {
    setSonuc(null);
    setHata("");
    setDosya(f);
  }

  async function gonder() {
    if (!dosya || !beyan) return;
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    try {
      const r = await api.portalYukle(dosya, beyan);
      setSonuc(r);
      gecmisiYenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setYukleniyor(false);
    }
  }

  const BAYRAK_METNI: Record<string, string> = {
    coklu_sahiplik_supheli: "Bu ekstre içeriği başka bir hesap altında da yüklenmiş görünüyor.",
    profil_tutarsiz: "Bu yükleme, geçmiş yüklemelerinizden belirgin şekilde farklı bir gelir ölçeği gösteriyor.",
    pencere_uyumsuz: "Ekstre süresi, modelin eğitildiği ~6 aylık pencereden belirgin şekilde sapıyor.",
    dusuk_kategori_guveni: "İşlem kategorileri güvenle tahmin edilemedi — sonuç daha az kesin olabilir.",
    yuksek_atlanan_satir_orani: "Dosyadaki satırların önemli bir kısmı okunamadı.",
  };

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Merhaba, {kullanici.ad}</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kendi işlem ekstrenizi yükleyin, davranışsal kapasite skorunuzu görün — sonuçlar yalnızca size ait
          "Geçmişim" listesine kaydedilir.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6">
        <div className="flex justify-between items-start gap-4 flex-wrap mb-4">
          <div className="flex flex-wrap gap-2">
            {["tarih (YYYY-AA-GG)", "islem_tipi (gelir/gider)", "kategori", "tutar", "aciklama (opsiyonel)"].map((k) => (
              <span
                key={k}
                className="font-label-mono text-[11px] bg-surface-container-high border border-outline-variant/30 px-2 py-1 rounded-DEFAULT text-on-surface"
              >
                {k}
              </span>
            ))}
          </div>
          <button
            onClick={ornekIndir}
            className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
          >
            <Icon name="download" className="text-[16px]" />
            Örnek CSV indir
          </button>
        </div>

        <div
          className={`rounded-lg p-8 border-2 border-dashed transition-colors ${
            suruklemede ? "border-primary bg-primary-container/10" : "border-outline-variant/40"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setSuruklemede(true);
          }}
          onDragLeave={() => setSuruklemede(false)}
          onDrop={(e) => {
            e.preventDefault();
            setSuruklemede(false);
            const f = e.dataTransfer.files?.[0];
            if (f) dosyaSec(f);
          }}
        >
          <input
            ref={girisRef}
            type="file"
            accept=".csv,text/csv,.xlsx,.xls,.pdf,application/pdf"
            className="hidden"
            onChange={(e) => dosyaSec(e.target.files?.[0] ?? null)}
          />
          <div className="flex flex-col items-center text-center gap-3">
            <Icon name="upload_file" className="text-5xl text-primary" />
            {dosya ? (
              <>
                <div className="font-body-sm text-body-sm text-on-surface font-semibold">{dosya.name}</div>
                <div className="font-label-mono text-[11px] text-on-surface-variant">
                  {(dosya.size / 1024).toFixed(1)} KB
                </div>
              </>
            ) : (
              <div className="font-body-sm text-body-sm text-on-surface">
                CSV, Excel ya da PDF ekstrenizi sürükleyin veya seçin
              </div>
            )}
            <div className="flex gap-3 mt-2">
              <button
                onClick={() => girisRef.current?.click()}
                className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
              >
                Dosya Seç
              </button>
              <button
                onClick={gonder}
                disabled={!dosya || !beyan || yukleniyor}
                className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40"
              >
                {yukleniyor ? "Analiz ediliyor…" : "Analiz Et"}
              </button>
            </div>
          </div>
        </div>

        <label className="flex items-start gap-3 mt-4 px-1 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={beyan}
            onChange={(e) => setBeyan(e.target.checked)}
            className="mt-0.5 accent-primary"
          />
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            Bu ekstrenin <strong className="text-on-surface">bana ait</strong> olduğunu onaylıyorum. AKS isim/kimlik
            bilgisi tutmaz; sahiplik yalnızca bu beyan + otomatik tutarlılık kontrolleriyle izlenir. Beyanınız, saati
            ve IP adresinizle birlikte bu analizin değiştirilemez denetim kaydına yazılır. (Kurumların verinize
            erişimi ayrı bir onaya tabidir — bkz.{" "}
            <a href="/portal/riza-defterim" className="text-primary underline">
              rıza defterim
            </a>
            .)
          </span>
        </label>
      </section>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      )}

      {sonuc && (
        <section className="grid grid-cols-1 md:grid-cols-12 gap-stack-md">
          {sonuc.anomali_bayrak && (
            <div className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2">
              <Icon name="warning" className="text-[16px] shrink-0" />
              Bu ekstre, eğitim dağılımının tipik aralığının dışında bir profil gösteriyor — skoru değiştirmez,
              yalnızca sonuca biraz daha az güvenilmesi gerektiğini işaret eder.
            </div>
          )}
          {[...(sonuc.sahiplik_bayraklari ?? []), ...(sonuc.belge_meta?.bayraklar ?? [])].map((b) => (
            <div
              key={b}
              className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2"
            >
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BAYRAK_METNI[b] ?? b}
            </div>
          ))}
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">AKS Skoru</span>
            <span className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_10px_rgba(195,192,255,0.5)]">
              {sonuc.aks_skor}
            </span>
            <span className="font-label-mono text-label-mono text-secondary mt-3">{sonuc.risk_seviyesi}</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant mt-1">{sonuc.karar}</span>
          </div>
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Önerilen Limit</span>
            <span className="font-display-sm text-display-sm text-on-background">{paraFormat(sonuc.onerilen_limit)}</span>
            <span className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              {sonuc.islem_sayisi} işlemden hesaplandı
            </span>
          </div>
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-center">
            <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">{sonuc.danisman.ozet}</p>
          </div>
          <div className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Davranışsal Faktörler
            </h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {sonuc.aciklama.riski_azaltan.map((f) => (
                <div className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-emerald-400">OLUMLU</span>
                    <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
              {sonuc.aciklama.riski_artiran.map((f) => (
                <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-error">OLUMSUZ</span>
                    <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
            </div>
            {sonuc.danisman.oneriler.length > 0 && (
              <ul className="space-y-2 mt-6 pt-6 border-t border-outline-variant/20">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {!!sonuc.belge_meta?.iz?.length && (
            <details className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
              <summary className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider cursor-pointer">
                Belge Agent İzi ({sonuc.belge_meta.kaynak_format?.toUpperCase()})
              </summary>
              <ol className="mt-4 space-y-1.5">
                {sonuc.belge_meta.iz.map((adim, i) => (
                  <li key={i} className="font-label-mono text-[11px] text-on-surface-variant flex gap-2">
                    <span className="text-primary shrink-0">{i + 1}.</span>
                    {adim}
                  </li>
                ))}
              </ol>
            </details>
          )}
        </section>
      )}

      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Geçmişim
        </h2>
        {gecmisYukleniyor ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
        ) : gecmis.length === 0 ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir analiz yapmadınız.</p>
        ) : (
          <ul className="space-y-2 font-label-mono text-label-mono">
            {gecmis.map((g) => (
              <li key={g.id} className="border-b border-outline-variant/10 pb-2">
                <button
                  onClick={() => kayitAcKapat(g.id)}
                  className="w-full flex justify-between items-center flex-wrap gap-2 text-left hover:text-on-surface transition-colors"
                >
                  <span className="text-on-surface-variant">{g.zaman.replace("T", " ")}</span>
                  <span className="text-primary">AKS {g.aks_skor}</span>
                  <span className="text-on-surface-variant">{g.risk_seviyesi}</span>
                  <span className="text-on-surface">{paraFormat(g.onerilen_limit)}</span>
                  <span className="text-on-surface-variant flex items-center gap-1">
                    {g.islem_sayisi} işlem
                    <Icon
                      name={acikKayitId === g.id ? "expand_less" : "expand_more"}
                      className="text-[16px]"
                    />
                  </span>
                </button>
                {acikKayitId === g.id && (
                  <div className="mt-3 mb-1 bg-surface-container-low rounded-lg p-3 overflow-x-auto">
                    {detayYukleniyor ? (
                      <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
                    ) : !detay?.islemler.length ? (
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        Bu kayıt için saklanmış işlem bulunamadı.
                      </p>
                    ) : (
                      <table className="w-full text-[11px]">
                        <thead>
                          <tr className="text-on-surface-variant border-b border-outline-variant/20">
                            <th className="text-left font-normal pb-1 pr-3">Tarih</th>
                            <th className="text-left font-normal pb-1 pr-3">Kategori</th>
                            <th className="text-left font-normal pb-1 pr-3">Açıklama</th>
                            <th className="text-right font-normal pb-1">Tutar</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detay.islemler.map((i, idx) => (
                            <tr key={idx} className="border-b border-outline-variant/10 last:border-0">
                              <td className="py-1 pr-3 text-on-surface-variant whitespace-nowrap">{i.tarih}</td>
                              <td className="py-1 pr-3 text-on-surface-variant">{i.kategori}</td>
                              <td className="py-1 pr-3 text-on-surface-variant">{i.aciklama || "—"}</td>
                              <td
                                className={`py-1 text-right whitespace-nowrap ${
                                  i.tutar >= 0 ? "text-emerald-400" : "text-error"
                                }`}
                              >
                                {paraFormat(i.tutar)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
```

### B3. `PortalProfilPage.tsx` — rota `/portal/profilim`

**Stitch brief:** Üstte açıklama metni. Ortada, ortalanmış bir kart: büyük
mono-font AKS numarası + "Kopyala" butonu. Altta bir "Telefon Doğrulama"
kartı — doğrulanmışsa yeşil "Doğrulandı" rozeti; değilse iki aşamalı form
(numara gönder → SMS kodu gir), demo modda kod ekranda gösterilir (amber
uyarı metniyle).

```tsx
import { useEffect, useState } from "react";
import { api, type ProfilBilgisi } from "../../api";
import { Icon } from "../../components/Icon";

export default function PortalProfilPage() {
  const [profil, setProfil] = useState<ProfilBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [kopyalandi, setKopyalandi] = useState(false);

  const [telefon, setTelefon] = useState("");
  const [dogrulamaId, setDogrulamaId] = useState<number | null>(null);
  const [debugKod, setDebugKod] = useState<string | null>(null);
  const [kod, setKod] = useState("");
  const [hata, setHata] = useState("");
  const [mesaj, setMesaj] = useState("");
  const [isleniyor, setIsleniyor] = useState(false);

  function yenile() {
    setYukleniyor(true);
    api
      .profilim()
      .then(setProfil)
      .catch(() => setHata("Profil yüklenemedi"))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function kopyala() {
    if (!profil) return;
    await navigator.clipboard.writeText(profil.aks_no);
    setKopyalandi(true);
    setTimeout(() => setKopyalandi(false), 1500);
  }

  async function kodGonder() {
    setHata("");
    setMesaj("");
    setIsleniyor(true);
    try {
      const r = await api.telefonGonder(telefon);
      setDogrulamaId(r.dogrulama_id);
      setDebugKod(r.demo_kod ?? r.debug_kod ?? null);
      setMesaj(`Doğrulama kodu gönderildi (${r.gecerlilik_dakika} dakika geçerli).`);
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  async function kodDogrula() {
    if (dogrulamaId === null) return;
    setHata("");
    setIsleniyor(true);
    try {
      await api.telefonDogrula(dogrulamaId, kod);
      setMesaj("Telefon doğrulandı.");
      setDogrulamaId(null);
      yenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  if (yukleniyor) return <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  if (!profil) return <p className="font-body-sm text-body-sm text-error">{hata || "Profil bulunamadı"}</p>;

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Profilim</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kimlik bilgisi (isim/soyisim/TCKN) tutmuyoruz — yalnızca bu numara ile tanımlanıyorsunuz. Bir kuruma
          hesap açtırırken bu numarayı verebilirsiniz.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6 flex flex-col items-center text-center gap-3">
        <span className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
          AKS Numaranız
        </span>
        <span className="font-display-md text-display-md text-primary tracking-wider">{profil.aks_no}</span>
        <button
          onClick={kopyala}
          className="flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
        >
          <Icon name={kopyalandi ? "check" : "content_copy"} className="text-[16px]" />
          {kopyalandi ? "Kopyalandı" : "Kopyala"}
        </button>
      </section>

      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
          Telefon Doğrulama
          {profil.telefon_dogrulandi_mi && (
            <span className="text-emerald-400 flex items-center gap-1">
              <Icon name="verified" className="text-[16px]" /> Doğrulandı
            </span>
          )}
        </h2>

        {!profil.telefon_dogrulandi_mi && (
          <div className="flex flex-col gap-4 max-w-sm">
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Aynı telefon numarası yalnızca bir hesaba bağlanabilir — bu, birinin sizin adınıza ikinci bir hesap
              açmasını zorlaştırır.
            </p>
            {!dogrulamaId ? (
              <div className="flex gap-2">
                <input
                  value={telefon}
                  onChange={(e) => setTelefon(e.target.value)}
                  placeholder="+905551112233"
                  className="flex-1 bg-surface-container-low border border-outline-variant/40 rounded-DEFAULT px-3 py-2 font-body-sm text-body-sm text-on-surface"
                />
                <button
                  onClick={kodGonder}
                  disabled={!telefon || isleniyor}
                  className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                >
                  Kod Gönder
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  value={kod}
                  onChange={(e) => setKod(e.target.value)}
                  placeholder="6 haneli kod"
                  className="flex-1 bg-surface-container-low border border-outline-variant/40 rounded-DEFAULT px-3 py-2 font-body-sm text-body-sm text-on-surface"
                />
                <button
                  onClick={kodDogrula}
                  disabled={!kod || isleniyor}
                  className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                >
                  Doğrula
                </button>
              </div>
            )}
            {debugKod && (
              <p className="font-label-mono text-[11px] text-amber-400">
                Demo modu — doğrulama kodunuz: {debugKod}
              </p>
            )}
            {mesaj && <p className="font-label-mono text-[11px] text-emerald-400">{mesaj}</p>}
            {hata && <p className="font-label-mono text-[11px] text-error">{hata}</p>}
          </div>
        )}
      </section>
    </div>
  );
}
```

### B4. `PortalTaleplerPage.tsx` — rota `/portal/erisim-talepleri`

**Stitch brief:** Bir talep listesi — her kart: kurum adı + amaç, sağ üstte
renkli durum rozeti (bekliyor=amber, onaylandı=yeşil, reddedildi=kırmızı,
iptal=gri), altta tarih/geçerlilik bilgisi + "şu an aktif" göstergesi.
Bekleyen taleplerde "Onayla (30 gün)" / "Reddet" butonları; onaylanmış
taleplerde tek bir kırmızı "Erişimi İptal Et" butonu.

```tsx
import { useEffect, useState } from "react";
import { api, type ErisimTalebiKaydi } from "../../api";
import { Icon } from "../../components/Icon";

const DURUM_STIL: Record<string, string> = {
  bekliyor: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  onaylandi: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  reddedildi: "text-error bg-error/10 border-error/30",
  iptal_edildi: "text-on-surface-variant bg-surface-container-high border-outline-variant/30",
};

const DURUM_ETIKET: Record<string, string> = {
  bekliyor: "Bekliyor",
  onaylandi: "Onaylandı",
  reddedildi: "Reddedildi",
  iptal_edildi: "İptal Edildi",
};

export default function PortalTaleplerPage() {
  const [talepler, setTalepler] = useState<ErisimTalebiKaydi[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [isleniyorId, setIsleniyorId] = useState<number | null>(null);
  const [hata, setHata] = useState("");

  function yenile() {
    setYukleniyor(true);
    api
      .erisimTalepleri()
      .then((r) => setTalepler(r.talepler))
      .catch(() => setHata("Talepler yüklenemedi"))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function aksiyon(id: number, fn: (id: number) => Promise<unknown>) {
    setIsleniyorId(id);
    setHata("");
    try {
      await fn(id);
      yenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyorId(null);
    }
  }

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Erişim Talepleri</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kurumlar yalnızca AKS numaranızı bilerek talep açabilir — verinize erişmeleri için SİZİN onayınız
          gerekir.
        </p>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      )}

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : talepler.length === 0 ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir erişim talebi yok.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {talepler.map((t) => (
            <div key={t.id} className="bg-surface-container hairline-border rounded-xl p-5 flex flex-col gap-3">
              <div className="flex justify-between items-start flex-wrap gap-2">
                <div>
                  <div className="font-body-sm text-body-sm text-on-surface font-semibold">{t.kurum}</div>
                  <div className="font-label-mono text-[11px] text-on-surface-variant mt-1">{t.amac}</div>
                </div>
                <span className={`font-label-mono text-[10px] px-2 py-1 rounded-DEFAULT border ${DURUM_STIL[t.durum]}`}>
                  {DURUM_ETIKET[t.durum]}
                </span>
              </div>
              <div className="font-label-mono text-[10px] text-on-surface-variant">
                Talep: {t.created_at.replace("T", " ")}
                {t.gecerlilik_bitis && ` · Geçerlilik: ${t.gecerlilik_bitis.replace("T", " ").slice(0, 16)}`}
                {t.aktif_mi && <span className="text-emerald-400 ml-2">● şu an aktif</span>}
              </div>

              {t.durum === "bekliyor" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => aksiyon(t.id, api.erisimTalebiOnayla)}
                    disabled={isleniyorId === t.id}
                    className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                  >
                    <Icon name="check" className="text-[16px]" /> Onayla (30 gün)
                  </button>
                  <button
                    onClick={() => aksiyon(t.id, api.erisimTalebiReddet)}
                    disabled={isleniyorId === t.id}
                    className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container-high disabled:opacity-40"
                  >
                    <Icon name="close" className="text-[16px]" /> Reddet
                  </button>
                </div>
              )}
              {t.durum === "onaylandi" && (
                <button
                  onClick={() => aksiyon(t.id, api.erisimTalebiIptal)}
                  disabled={isleniyorId === t.id}
                  className="self-start flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-error/40 text-error font-label-mono text-label-mono hover:bg-error/10 disabled:opacity-40"
                >
                  <Icon name="block" className="text-[16px]" /> Erişimi İptal Et
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### B5. `PortalRizaPage.tsx` — rota `/portal/riza-defterim`

**Stitch brief:** Salt-okunur, kronolojik bir olay listesi (append-only
defterin doğrudan görünümü) — her satır: olay etiketi + kurum adı + amaç,
sağda zaman damgası. Boş durumda "Henüz bir kayıt yok."

```tsx
import { useEffect, useState } from "react";
import { api, type RizaDefteriKaydi } from "../../api";

const OLAY_ETIKET: Record<string, string> = {
  talep_olusturuldu: "Talep oluşturuldu",
  onaylandi: "Onayladınız",
  reddedildi: "Reddettiniz",
  iptal_edildi: "İptal ettiniz",
  erisim_kullanildi: "Kurum verinize erişti",
};

export default function PortalRizaPage() {
  const [kayitlar, setKayitlar] = useState<RizaDefteriKaydi[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    api
      .rizaDefterim()
      .then((r) => setKayitlar(r.kayitlar))
      .finally(() => setYukleniyor(false));
  }, []);

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Rıza Defterim</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Verinize dair her olay (talep, onay, ret, iptal, erişim) buraya değiştirilemez şekilde yazılır.
        </p>
      </header>

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir kayıt yok.</p>
      ) : (
        <ol className="flex flex-col gap-2">
          {kayitlar.map((k) => (
            <li
              key={k.id}
              className="bg-surface-container hairline-border rounded-lg p-4 flex justify-between items-center flex-wrap gap-2"
            >
              <div>
                <div className="font-body-sm text-body-sm text-on-surface">
                  {OLAY_ETIKET[k.olay] ?? k.olay} — <span className="text-on-surface-variant">{k.kurum}</span>
                </div>
                <div className="font-label-mono text-[10px] text-on-surface-variant mt-1">{k.amac}</div>
              </div>
              <span className="font-label-mono text-[10px] text-on-surface-variant">
                {k.created_at.replace("T", " ")}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
```

---

## Kısım C — Kurum (banka personeli) arayüzü (`KurumLayout`)

### C1. `KurumLoginPage.tsx` — rota `/kurum/giris`

**Stitch brief:** `PortalLoginPage` ile aynı kart/form deseni ama
tek-sekmeli (giriş-only, öz-kayıt yok) ve farklı ikon/başlık ("Kurum
Girişi" + banka ikonu). Yanlış hesapla giriş denenirse (kuruma üye değilse)
hem hata gösterilir hem otomatik çıkış yapılır (yanlışlıkla yarı-oturumda
kalınmasın diye).

```tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

export default function KurumLoginPage() {
  const [email, setEmail] = useState("");
  const [sifre, setSifre] = useState("");
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .kurumBen()
      .then(() => navigate("/kurum/musteriler", { replace: true }))
      .catch(() => {})
      .finally(() => setKontrolEdiliyor(false));
  }, [navigate]);

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata("");
    setYukleniyor(true);
    try {
      await api.girisYap(email, sifre);
      await api.kurumBen(); // bu hesap gerçekten bir kuruma üye mi?
      navigate("/kurum/musteriler");
    } catch (err) {
      setHata(
        String(err instanceof Error ? err.message : err) +
          " (bu hesabın bir kuruma üyeliği yoksa kurum paneline giremezsiniz)"
      );
      await api.cikisYap().catch(() => {});
    } finally {
      setYukleniyor(false);
    }
  }

  if (kontrolEdiliyor) {
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-surface-container-low hairline-border rounded-xl p-8">
        <div className="text-center mb-8">
          <Icon name="account_balance" className="text-5xl text-primary" />
          <h1 className="font-headline-md text-headline-md text-on-background mt-2">Kurum Girişi</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Banka/kurum personeli oturumu — müşteri verisine yalnızca rızalı erişimle ulaşılır.
          </p>
        </div>

        <form onSubmit={gonder} className="flex flex-col gap-4">
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="kurum@demo.aks"
            />
          </div>
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
            <input
              type="password"
              required
              value={sifre}
              onChange={(e) => setSifre(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          {hata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-body-sm text-body-sm">
              {hata}
            </div>
          )}

          <button
            type="submit"
            disabled={yukleniyor}
            className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-2"
          >
            {yukleniyor ? "…" : "Giriş Yap"}
          </button>
        </form>
      </div>
    </div>
  );
}
```

### C2. `KurumMusterilerPage.tsx` — rota `/kurum/musteriler`

**Stitch brief:** Üstte "Yeni Erişim Talebi" formu (AKS numarası + amaç
input'u yan yana, "Talep Gönder" butonu, başarı/hata mesajı). Altta "Aktif
Erişimler" listesi — her satır tıklanabilir bir kart (AKS no + amaç solda,
geçerlilik tarihi + ok ikonu sağda), müşteri detayına gider.

```tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type KurumMusteriOzet } from "../../api";
import { Icon } from "../../components/Icon";

export default function KurumMusterilerPage() {
  const [musteriler, setMusteriler] = useState<KurumMusteriOzet[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  const [aksNo, setAksNo] = useState("");
  const [amac, setAmac] = useState("");
  const [talepHata, setTalepHata] = useState("");
  const [talepMesaj, setTalepMesaj] = useState("");
  const [gonderiliyor, setGonderiliyor] = useState(false);

  function yenile() {
    setYukleniyor(true);
    api
      .kurumMusteriler()
      .then((r) => setMusteriler(r.musteriler))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function talepGonder(e: React.FormEvent) {
    e.preventDefault();
    setTalepHata("");
    setTalepMesaj("");
    setGonderiliyor(true);
    try {
      await api.kurumErisimTalebiOlustur(aksNo.trim().toUpperCase(), amac);
      setTalepMesaj("Talep gönderildi — müşterinin onayı bekleniyor.");
      setAksNo("");
      setAmac("");
    } catch (err) {
      setTalepHata(String(err instanceof Error ? err.message : err));
    } finally {
      setGonderiliyor(false);
    }
  }

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Müşteriler</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Yalnızca size erişim izni vermiş müşteriler burada görünür.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Yeni Erişim Talebi
        </h2>
        <form onSubmit={talepGonder} className="flex flex-col md:flex-row gap-3 items-end">
          <div className="flex-1 min-w-0">
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">AKS Numarası</label>
            <input
              value={aksNo}
              onChange={(e) => setAksNo(e.target.value)}
              placeholder="AKS-XXXX-XXXX-XC"
              required
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-label-mono text-label-mono text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
          <div className="flex-1 min-w-0">
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Amaç</label>
            <input
              value={amac}
              onChange={(e) => setAmac(e.target.value)}
              placeholder="kredi başvurusu değerlendirmesi"
              required
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
          <button
            type="submit"
            disabled={gonderiliyor}
            className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40 shrink-0"
          >
            Talep Gönder
          </button>
        </form>
        {talepMesaj && <p className="font-label-mono text-[11px] text-emerald-400 mt-3">{talepMesaj}</p>}
        {talepHata && <p className="font-label-mono text-[11px] text-error mt-3">{talepHata}</p>}
      </section>

      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Aktif Erişimler
        </h2>
        {yukleniyor ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
        ) : musteriler.length === 0 ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Henüz onaylanmış bir erişiminiz yok — yukarıdan talep gönderin.
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {musteriler.map((m) => (
              <Link
                key={m.aks_no}
                to={`/kurum/musteri/${m.aks_no}`}
                className="flex justify-between items-center bg-surface-container-low hairline-border rounded-lg p-4 hover:bg-surface-container-high transition-colors flex-wrap gap-2"
              >
                <div>
                  <div className="font-label-mono text-label-mono text-primary">{m.aks_no}</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">{m.amac}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-label-mono text-[10px] text-on-surface-variant">
                    {m.gecerlilik_bitis.replace("T", " ").slice(0, 16)} kadar
                  </span>
                  <Icon name="chevron_right" className="text-on-surface-variant" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
```

### C3. `KurumMusteriDetayPage.tsx` — rota `/kurum/musteri/:aksNo`

**Stitch brief:** Geri linki + başlıkta AKS numarası. Değerlendirme yoksa
tek bir "henüz belge yüklenmemiş" kartı. Varsa: sahiplik bayrak
banner'ları, 3 özet kutu (AKS skoru, karar, önerilen limit), sonra **3
kartlık risk-iştahı ızgarası** (ihtiyatlı/dengeli/atak — her biri kendi
rengiyle: yeşilimsi/amber/kırmızımsı arka plan, onay/red ikonu, "Onaylanır/
Onaylanmaz" metni, eşik değeri), altında bir dürüstlük notu. En altta SHAP
gerekçe kodları ızgarası.

```tsx
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type KurumMusteriDetay } from "../../api";
import { Icon } from "../../components/Icon";
import { paraFormat } from "../../lib/skor";

const BAYRAK_METNI: Record<string, string> = {
  coklu_sahiplik_supheli: "Bu ekstre içeriği başka bir hesap altında da yüklenmiş görünüyor.",
  profil_tutarsiz: "Bu yükleme, müşterinin geçmiş yüklemelerinden belirgin şekilde farklı bir gelir ölçeği gösteriyor.",
};

const PROFIL_SIRA: Array<"ihtiyatli" | "dengeli" | "atak"> = ["ihtiyatli", "dengeli", "atak"];
const PROFIL_RENK: Record<string, string> = {
  ihtiyatli: "border-emerald-400/30 bg-emerald-400/5",
  dengeli: "border-amber-400/30 bg-amber-400/5",
  atak: "border-error/30 bg-error/5",
};

export default function KurumMusteriDetayPage() {
  const { aksNo } = useParams<{ aksNo: string }>();
  const [detay, setDetay] = useState<KurumMusteriDetay | null>(null);
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    if (!aksNo) return;
    setYukleniyor(true);
    api
      .kurumMusteriDetay(aksNo)
      .then(setDetay)
      .catch((e) => setHata(String(e instanceof Error ? e.message : e)))
      .finally(() => setYukleniyor(false));
  }, [aksNo]);

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <Link to="/kurum/musteriler" className="font-label-mono text-label-mono text-on-surface-variant hover:text-on-surface flex items-center gap-1 w-fit">
        <Icon name="chevron_left" className="text-[16px]" /> Müşteriler
      </Link>

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : hata ? (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      ) : !detay ? null : !detay.degerlendirme_var ? (
        <div className="bg-surface-container hairline-border rounded-xl p-8 text-center">
          <h1 className="font-headline-md text-headline-md text-on-background mb-2">{detay.aks_no}</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">{detay.not ?? "Henüz bir belge yüklenmemiş."}</p>
        </div>
      ) : (
        <>
          <header>
            <h1 className="font-headline-md text-headline-md text-on-background">{detay.aks_no}</h1>
            <p className="font-label-mono text-[11px] text-on-surface-variant mt-1">
              Son değerlendirme: {detay.created_at?.replace("T", " ")} · Kaynak: {detay.kaynak_format?.toUpperCase()}
            </p>
          </header>

          {(detay.sahiplik_bayraklari ?? []).map((b) => (
            <div key={b} className="bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2">
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BAYRAK_METNI[b] ?? b}
            </div>
          ))}

          <section className="grid grid-cols-1 md:grid-cols-3 gap-stack-md">
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">AKS Skoru</span>
              <span className="font-display-lg text-display-lg text-primary">{detay.aks_skor}</span>
              <span className="font-label-mono text-label-mono text-secondary mt-2">{detay.risk_seviyesi}</span>
            </div>
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Karar</span>
              <span className="font-body-sm text-body-sm text-on-background">{detay.karar}</span>
            </div>
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Önerilen Limit</span>
              <span className="font-display-sm text-display-sm text-on-background">{paraFormat(detay.onerilen_limit ?? null)}</span>
            </div>
          </section>

          <section>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Risk İştahı Profillerine Göre Karar
            </h2>
            {!detay.risk_istahi ? (
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Risk iştahı raporu henüz üretilmedi.
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-stack-md">
                {PROFIL_SIRA.map((p) => {
                  const sonuc = detay.risk_istahi![p];
                  return (
                    <div key={p} className={`rounded-xl border p-6 flex flex-col items-center text-center gap-2 ${PROFIL_RENK[p]}`}>
                      <span className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
                        {sonuc.ad}
                      </span>
                      <Icon
                        name={sonuc.onaylanir_mi ? "check_circle" : "cancel"}
                        className={`text-4xl ${sonuc.onaylanir_mi ? "text-emerald-400" : "text-error"}`}
                      />
                      <span className="font-body-sm text-body-sm text-on-background font-semibold">
                        {sonuc.onaylanir_mi ? "Onaylanabilir" : "Onaylanmaz"}
                      </span>
                      <span className="font-label-mono text-[10px] text-on-surface-variant">Eşik: {sonuc.esik}</span>
                    </div>
                  );
                })}
              </div>
            )}
            <p className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              Sentetik/dekuple veri üzerinde, held-out benchmarkta üretildi — nihai politika değil, önerilen
              başlangıç noktası.
            </p>
          </section>

          {detay.aciklama && (
            <section className="bg-surface-container hairline-border rounded-xl p-6">
              <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
                Gerekçe Kodları (SHAP)
              </h2>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                {detay.aciklama.riski_azaltan.map((f) => (
                  <div className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg" key={f.kod}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-label-mono text-[10px] text-emerald-400">RİSKİ AZALTIR</span>
                      <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                    </div>
                    <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                  </div>
                ))}
                {detay.aciklama.riski_artiran.map((f) => (
                  <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg" key={f.kod}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-label-mono text-[10px] text-error">RİSKİ ARTIRIR</span>
                      <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                    </div>
                    <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                  </div>
                ))}
              </div>
              <p className="font-label-mono text-[10px] text-on-surface-variant mt-4">
                AKS bankanın klasik skorunu/segmentini değiştirmez — yalnızca davranışsal kanıt sunar.
              </p>
            </section>
          )}
        </>
      )}
    </div>
  );
}
```

---

## Sayfa envanteri özeti (hızlı referans)

| # | Sayfa | Rota | Yüzey | Oturum |
|---|---|---|---|---|
| G1 | AnaSayfaPage | `/` | Herkese açık | Yok (isteğe bağlı — buton değişir) |
| G2 | GirisPage | `/giris` | Herkese açık | Yok (giriş öncesi) |
| A1 | IntelligencePage | `/panel` | Banka içi | **Yönetici** (`is_staff`) |
| A2 | PortfolioPage | `/portfolio` | Banka içi | **Yönetici** |
| A3 | AuditPage | `/audit` | Banka içi | **Yönetici** |
| A4 | CustomersPage | `/customers` | Banka içi | **Yönetici** |
| A5 | CustomerDetailPage | `/customers/:id` | Banka içi | **Yönetici** |
| A6 | CsvUploadPage | `/upload` | Banka içi | **Yönetici** |
| A7 | BulunamadiPage | `*` | Ortak | Yok |
| B1 | PortalLoginPage | `/portal/giris` | Portal | Yok (giriş öncesi) |
| B2 | PortalPage | `/portal` | Portal | Müşteri (`ProfilSahibi`) |
| B3 | PortalProfilPage | `/portal/profilim` | Portal | Müşteri |
| B4 | PortalTaleplerPage | `/portal/erisim-talepleri` | Portal | Müşteri |
| B5 | PortalRizaPage | `/portal/riza-defterim` | Portal | Müşteri |
| C1 | KurumLoginPage | `/kurum/giris` | Kurum | Yok (giriş öncesi) |
| C2 | KurumMusterilerPage | `/kurum/musteriler` | Kurum | Kurum personeli (`KurumUyesi`) |
| C3 | KurumMusteriDetayPage | `/kurum/musteri/:aksNo` | Kurum | Kurum personeli |

Toplam **17 sayfa + 3 layout + 1 ikon bileşeni + 1 API istemcisi + 1 skor
yardımcı modülü** — bu dosyadaki her kod bloğu birebir mevcut
`product/03-frontend/src/` içeriğidir (commit `30ba931` durumu, execution.md
§3b Phase 7/7.11–7.12). Stitch'te yeniden tasarlarken **class isimleri/görsel
stil değişebilir, ama her `useState`/`useEffect`/`api.xxx()` çağrısı ve
koşullu render (`sonuc &&`, `hata &&`, `yukleniyor ?`) aynı davranışı
üretmeli** — aksi halde sayfa görsel olarak güzel ama işlevsel olarak
bozuk çıkar.

**"Oturum" sütunu ikinci bir katmandır, ilki değil.** `KullaniciBilgisi`
üzerindeki `yonetici`/`kurum_uyesi` bayrakları yalnızca hangi sayfanın
gösterileceğini belirler (yönlendirme); gerçek yetki HER ZAMAN sunucuda,
ilgili DRF izin sınıfında zorlanır. Stitch'te yeni bir sayfa/ekran eklenirse
"bu veriye kim erişebilir" sorusunun cevabı frontend'te değil backend'de
yazılmalı — aksi halde execution.md §3b Phase 7/7.11'de bulunanla aynı sınıf
bir güvenlik açığı tekrarlanır.
