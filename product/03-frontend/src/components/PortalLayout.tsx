import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "./Icon";

const PORTAL_NAV = [
  { to: "/portal", label: "Yükle", uc: true },
  { to: "/portal/profilim", label: "Profilim" },
  { to: "/portal/erisim-talepleri", label: "Erişim Talepleri" },
  { to: "/portal/riza-defterim", label: "Rıza Defterim" },
];

// §3b Phase 6 — kullanıcı portalı: banka arayüzünden (Layout.tsx) tamamen ayrı
// nav/marka + oturum kapısı. `/portal/*` altındaki tüm sayfalar buradan geçer;
// giriş yoksa /portal/giris'e yönlendirir.
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
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  // `aks_no` yoksa kullanıcı bir müşteri hesabı değil (ör. kurum personeli —
  // `Profil`'i yoktur). Portal içine alınırsa her sayfa 403 alıp ham hata
  // gösterir; giriş ekranına yönlendirmek doğru davranış.
  if (!kullanici?.aks_no) {
    return <Navigate to="/portal/giris" replace />;
  }

  return (
    <div className="min-h-screen bg-background text-on-background font-body-sm text-body-sm antialiased">
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-xl border-b border-outline-variant/30">
        <div className="flex justify-between items-center h-16 px-4 md:px-container-padding max-w-[1000px] mx-auto gap-4">
          <div className="flex items-center gap-6 min-w-0">
            <span className="font-display-sm text-display-sm font-bold tracking-tighter text-on-background shrink-0">
              AKS Portal
            </span>
            <div className="hidden md:flex items-center gap-1">
              {PORTAL_NAV.map((n) => (
                <NavLink
                  key={n.to}
                  to={n.to}
                  end={n.uc}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-DEFAULT font-label-mono text-label-mono transition-colors ${
                      isActive ? "bg-surface-container-high text-on-background" : "text-on-surface-variant hover:bg-surface-container"
                    }`
                  }
                >
                  {n.label}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-4 shrink-0">
            <span className="font-label-mono text-label-mono text-on-surface-variant hidden sm:inline">
              {kullanici.ad}
            </span>
            <button
              onClick={cikisYap}
              className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
            >
              <Icon name="logout" className="text-[16px]" />
              Çıkış
            </button>
          </div>
        </div>
        <div className="flex md:hidden gap-1 px-4 pb-2 overflow-x-auto">
          {PORTAL_NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.uc}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-DEFAULT font-label-mono text-[11px] whitespace-nowrap transition-colors ${
                  isActive ? "bg-surface-container-high text-on-background" : "text-on-surface-variant hover:bg-surface-container"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </div>
      </nav>
      <main className="pt-24 pb-16 px-4 md:px-container-padding max-w-[1000px] mx-auto min-h-screen">
        <Outlet context={kullanici} />
      </main>
    </div>
  );
}
