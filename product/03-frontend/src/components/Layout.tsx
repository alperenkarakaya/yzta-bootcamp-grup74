import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { Icon } from "./Icon";
import { politikaEsikleriniYukle } from "../lib/skor";
import { api, type KullaniciBilgisi } from "../api";

const NAV_LINKS = [
  { to: "/", label: "Intelligence", end: true },
  { to: "/portfolio", label: "Portfolio" },
  { to: "/audit", label: "Audit" },
  { to: "/customers", label: "Customers" },
  { to: "/upload", label: "Upload" },
];

const BOTTOM_LINKS = [
  { to: "/", icon: "terminal", label: "Command", end: true },
  { to: "/customers", icon: "sensors", label: "Signals" },
  { to: "/upload", icon: "upload_file", label: "Upload" },
  { to: "/audit", icon: "shield_with_heart", label: "Vault" },
  { to: "/portfolio", icon: "smart_toy", label: "Support" },
];

// Giriş zorunlu (PO kararı): giriş yapılmamışsa banka içi arayüz yerine
// `/giris` landing sayfasına yönlendirilir. Portal/kurum girişiyle AYNI
// oturum sistemini (`/api/auth/*`) kullanır — yeni bir kimlik doğrulama
// akışı İCAT EDİLMEDİ (bkz. PortalLayout/GirisPage'in aynı deseni).
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
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }
  if (!kullanici) {
    return <Navigate to="/giris" replace />;
  }

  return (
    <div className="min-h-screen bg-background text-on-background font-body-sm text-body-sm antialiased selection:bg-primary-container selection:text-on-primary-container">
      {/* TopNavBar (desktop) */}
      <nav className="hidden md:block fixed top-0 w-full z-50 bg-background/80 backdrop-blur-xl border-b border-outline-variant/30 shadow-sm">
        <div className="flex justify-between items-center h-16 px-container-padding max-w-[1440px] mx-auto">
          <div className="flex items-center gap-stack-lg">
            <span className="font-display-sm text-display-sm font-bold tracking-tighter text-on-background">
              AKS Intelligence
            </span>
            <div className="flex items-center gap-gutter">
              {NAV_LINKS.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  end={l.end}
                  className={({ isActive }) =>
                    `pb-1 px-2 py-1 rounded font-label-mono text-label-mono transition-all active:scale-95 hover:bg-surface-container/50 ${
                      isActive
                        ? "text-primary border-b-2 border-primary font-semibold"
                        : "text-on-surface-variant hover:text-on-surface"
                    }`
                  }
                >
                  {l.label}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4 text-on-surface-variant">
            <NavLink
              to="/portal"
              className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-DEFAULT border border-outline-variant/30 font-label-mono text-label-mono hover:bg-surface-container/50 transition-colors"
              title="Kullanıcı Portalı — kendi ekstreni yükle"
            >
              <Icon name="open_in_new" className="text-[14px]" />
              Kullanıcı Portalı
            </NavLink>
            <NavLink
              to="/kurum/musteriler"
              className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-DEFAULT border border-outline-variant/30 font-label-mono text-label-mono hover:bg-surface-container/50 transition-colors"
              title="Kurum Girişi — rıza-tabanlı gerçek müşteri erişimi"
            >
              <Icon name="account_balance" className="text-[14px]" />
              Kurum Girişi
            </NavLink>
            <button
              className="hover:bg-surface-container/50 p-2 rounded-full transition-all active:scale-95"
              title="Sistem canlı — Django API'ye bağlı"
            >
              <Icon name="bolt" />
            </button>
            <span className="hidden lg:inline font-label-mono text-label-mono text-on-surface-variant/80">
              {kullanici.email}
            </span>
            <button
              onClick={cikisYap}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-DEFAULT border border-outline-variant/30 font-label-mono text-label-mono hover:bg-surface-container/50 transition-colors"
              title="Çıkış yap"
            >
              <Icon name="logout" className="text-[14px]" />
              Çıkış
            </button>
            <div className="w-8 h-8 rounded-full bg-surface-variant border border-outline-variant/30 flex items-center justify-center inner-shadow-subtle text-primary">
              <Icon name="account_circle" />
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile fallback header */}
      <header className="md:hidden fixed top-0 w-full z-50 bg-background/90 backdrop-blur-xl border-b border-outline-variant/30 h-16 flex items-center px-4 justify-between">
        <span className="font-display-sm-mobile text-display-sm-mobile font-bold tracking-tighter text-on-background">
          AKS Intelligence
        </span>
        <button onClick={cikisYap} className="p-2 text-on-surface-variant" title="Çıkış yap">
          <Icon name="logout" />
        </button>
      </header>

      <main className="pt-24 pb-32 md:pb-16 px-4 md:px-container-padding max-w-[1440px] mx-auto min-h-screen">
        <Outlet />
      </main>

      {/* BottomNavBar (mobile) */}
      <nav className="md:hidden fixed bottom-6 left-1/2 -translate-x-1/2 w-auto min-w-[320px] rounded-full border border-outline-variant/50 shadow-2xl shadow-primary-container/20 bg-surface-container/90 backdrop-blur-md z-50 flex items-center gap-stack-lg px-6 py-3 font-label-mono text-label-mono">
        {BOTTOM_LINKS.map((l) => (
          <NavLink
            key={l.label}
            to={l.to}
            end={l.end}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center rounded-full w-12 h-12 transition-transform hover:scale-110 active:scale-90 ${
                isActive
                  ? "bg-primary-container text-on-primary-container"
                  : "text-on-surface-variant hover:text-primary"
              }`
            }
          >
            <Icon name={l.icon} />
            <span className="text-[9px] mt-0.5">{l.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
