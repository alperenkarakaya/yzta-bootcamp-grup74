import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "./Icon";

const PORTAL_NAV = [
  { to: "/portal", label: "Yükle", icon: "upload_file", end: true },
  { to: "/portal/profilim", label: "Profilim", icon: "account_circle" },
  { to: "/portal/erisim-talepleri", label: "Erişim Talepleri", icon: "key" },
  { to: "/portal/riza-defterim", label: "Rıza Defterim", icon: "history_edu" },
];

// §3b Phase 6 — kullanıcı portalı: banka arayüzünden (Layout.tsx) tamamen ayrı
// nav/marka + oturum kapısı. `/portal/*` altındaki tüm sayfalar buradan geçer;
// giriş yoksa /portal/giris'e yönlendirir.
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_ana_sayfa
// ("AKS Terminal" — masaüstünde sabit sol kenar nav, mobilde üst bar + ikinci
// satır sekme nav). Orijinal mockup'ın mobil satırında "Rıza Defterim" eksikti
// (yalnızca 3/4 öğe) — dördü de eklendi, aksi halde mobilde o sayfaya gitmenin
// hiçbir yolu olmazdı.
export default function PortalLayout() {
  const [kullanici, setKullanici] = useState<KullaniciBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
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
      /* oturum zaten düşmüş olabilir — yine de giriş sayfasına dön */
    }
    navigate("/portal/giris");
  }

  if (yukleniyor) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Yükleniyor…</p>
      </div>
    );
  }

  // `aks_no` yoksa kullanıcı bir müşteri hesabı değil (ör. kurum personeli —
  // `Profil`'i yoktur). Portal içine alınırsa her sayfa 403 alıp ham hata
  // gösterir; giriş ekranına yönlendirmek doğru davranış.
  if (!kullanici?.aks_no) {
    return <Navigate to="/portal/giris" replace />;
  }

  return (
    <div className="font-body-md text-body-md min-h-screen flex flex-col md:flex-row bg-surface">
      {/* Desktop SideNav */}
      <nav className="h-full w-64 fixed left-0 top-0 hidden lg:flex flex-col border-r border-outline-variant bg-surface-container z-40 p-gutter gap-stack-default">
        <div className="mb-8 mt-4 flex items-center gap-3">
          <Icon name="analytics" className="text-primary text-3xl" filled />
          <div>
            <h1 className="font-headline-md text-headline-md text-primary tracking-tighter">AKS Portal</h1>
            <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Müşteri Paneli</p>
          </div>
        </div>
        <div className="flex-1 flex flex-col gap-2 mt-4">
          {PORTAL_NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-full transition-all active:scale-[0.98] ${
                  isActive
                    ? "bg-secondary-container text-on-secondary-container border-l-4 border-primary"
                    : "text-on-surface-variant hover:bg-surface-container-highest"
                }`
              }
            >
              <Icon name={n.icon} />
              <span className="font-mono-label-sm text-mono-label-sm">{n.label}</span>
            </NavLink>
          ))}
        </div>
        <div className="mt-auto">
          <button
            onClick={cikisYap}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 border border-outline-variant rounded-lg text-on-surface hover:bg-surface-container-highest transition-colors font-mono-label-sm text-mono-label-sm"
          >
            <Icon name="logout" className="text-sm" />
            Çıkış
          </button>
        </div>
      </nav>

      {/* Mobile TopNavBar */}
      <nav className="fixed top-0 w-full z-50 border-b border-outline-variant bg-surface lg:hidden flex flex-col">
        <div className="flex justify-between items-center h-16 px-gutter w-full">
          <h1 className="font-headline-md text-headline-md font-bold text-primary tracking-tighter flex items-center gap-2">
            <Icon name="analytics" filled /> AKS Portal
          </h1>
          <button onClick={cikisYap} className="text-on-surface-variant p-2" title="Çıkış yap">
            <Icon name="logout" />
          </button>
        </div>
        <div className="flex justify-around items-center h-12 bg-surface-container-low border-t border-outline-variant overflow-x-auto px-4">
          {PORTAL_NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                `pb-1 font-mono-label-sm text-mono-label-sm whitespace-nowrap px-3 transition-all duration-200 active:scale-95 ${
                  isActive
                    ? "text-primary border-b-2 border-primary"
                    : "text-on-surface-variant hover:text-on-surface"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Main Content Canvas */}
      <main className="flex-1 w-full lg:ml-64 pt-32 lg:pt-8 p-4 lg:p-grid-margin lg:px-8 max-w-6xl mx-auto flex flex-col gap-8">
        <Outlet context={kullanici} />
      </main>
    </div>
  );
}
