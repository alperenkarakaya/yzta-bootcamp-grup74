import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { Icon } from "./Icon";
import { politikaEsikleriniYukle } from "../lib/skor";
import { api, type KullaniciBilgisi } from "../api";

const NAV_LINKS = [
  { to: "/panel", label: "Intelligence", end: true },
  { to: "/portfolio", label: "Portföy" },
  { to: "/audit", label: "Denetim Defteri" },
  { to: "/customers", label: "Müşteriler" },
  { to: "/upload", label: "Belge Yükle" },
];

const BOTTOM_LINKS = [
  { to: "/panel", icon: "terminal", label: "Komut", end: true },
  { to: "/customers", icon: "sensors", label: "Sinyal" },
  { to: "/upload", icon: "upload_file", label: "Yükle" },
  { to: "/audit", icon: "account_balance_wallet", label: "Kasa" },
  { to: "/portfolio", icon: "support_agent", label: "Destek" },
];

// Giriş zorunlu (PO kararı): giriş yapılmamışsa banka içi arayüz yerine
// `/giris` landing sayfasına yönlendirilir. Portal/kurum girişiyle AYNI
// oturum sistemini (`/api/auth/*`) kullanır — yeni bir kimlik doğrulama
// akışı İCAT EDİLMEDİ (bkz. PortalLayout/GirisPage'in aynı deseni).
//
// YETKİ (Phase 7 güvenlik düzeltmesi): bu yüzey TÜM demo popülasyonunu,
// portföy/adalet istatistiklerini ve değerlendirme geçmişini gösterir —
// yani "herkesi gören" tek yüzey. Bu yüzden yalnızca YÖNETİCİ (`is_staff`)
// hesaplara açıktır. Sıradan kullanıcı kendi portalına, kurum personeli kendi
// paneline yönlendirilir. Bu yalnızca arayüz katmanı; uçların kendisi de
// `YoneticiKullanici` izniyle korunur (bayrağı tarayıcıda taklit etmek
// hiçbir veri getirmez, sadece 403 alınır).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_intelligence_panel
// ("AKS Terminal" — sabit üst nav + mobilde yüzen hap-şekilli alt nav).
export default function Layout() {
  const [kullanici, setKullanici] = useState<KullaniciBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    politikaEsikleriniYukle();
    api
      .ben()
      .then(setKullanici)
      .catch(() => setKullanici(null))
      .finally(() => setYukleniyor(false));
  }, []);

  async function cikisYap() {
    try {
      await api.cikisYap();
    } catch {
      /* oturum zaten düşmüş olabilir */
    }
    navigate("/giris");
  }

  if (yukleniyor) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Yükleniyor…</p>
      </div>
    );
  }
  if (!kullanici) {
    return <Navigate to="/giris" replace />;
  }
  if (!kullanici.yonetici) {
    // Giriş yapmış ama yönetici değil — kendi yüzeyine gönder (banka içi
    // araştırma sayfaları başka kullanıcıların verisini içerir).
    return <Navigate to={kullanici.kurum_uyesi ? "/kurum/musteriler" : "/portal"} replace />;
  }

  return (
    <div className="bg-surface text-on-surface min-h-screen flex flex-col font-body-md text-body-md overflow-x-hidden">
      {/* TopNavBar */}
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 md:px-grid-margin h-16 bg-surface-dim border-b border-outline-variant">
        <div className="flex items-center gap-6 min-w-0">
          <h1 className="text-headline-md font-headline-md font-bold text-primary tracking-tighter shrink-0">
            AKS Intelligence
          </h1>
          <nav className="hidden md:flex items-center gap-6 mt-1">
            {NAV_LINKS.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                end={l.end}
                className={({ isActive }) =>
                  `pb-1 text-mono-label-sm font-mono-label-sm transition-colors duration-200 ${
                    isActive ? "text-primary border-b-2 border-primary" : "text-on-surface-variant hover:text-primary"
                  }`
                }
              >
                {l.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="hidden md:flex items-center gap-4">
          <span className="text-on-surface-variant text-mono-label-sm font-mono-label-sm">{kullanici.email}</span>
          <button
            onClick={cikisYap}
            className="bg-primary-container text-on-primary-container px-4 py-2 rounded text-mono-label-sm font-mono-label-sm font-bold hover:bg-primary-fixed transition-colors duration-200"
          >
            Çıkış
          </button>
        </div>
        <button onClick={cikisYap} className="md:hidden text-on-surface-variant p-2" title="Çıkış yap">
          <Icon name="logout" />
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-grow pt-24 px-4 md:px-grid-margin pb-24 md:pb-8 flex flex-col gap-6 max-w-7xl mx-auto w-full">
        <Outlet />
      </main>

      {/* BottomNavBar (Mobile) */}
      <nav className="md:hidden fixed bottom-6 left-0 right-0 z-50 flex justify-around items-center px-4 py-2 mx-auto max-w-md bg-surface-container-high/90 border border-outline-variant backdrop-blur-md shadow-2xl rounded-full">
        {BOTTOM_LINKS.map((l) => (
          <NavLink
            key={l.label}
            to={l.to}
            end={l.end}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center p-2 rounded-full transition-transform duration-150 active:scale-95 ${
                isActive ? "text-secondary bg-secondary-container/20 scale-95" : "text-on-surface-variant hover:bg-surface-variant"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon name={l.icon} className="text-xl" filled={isActive} />
                <span className="text-mono-label-sm font-mono-label-sm mt-1">{l.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
