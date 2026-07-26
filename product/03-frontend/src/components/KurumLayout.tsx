import { useEffect, useState } from "react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { api, type KurumBilgisi } from "../api";
import { Icon } from "./Icon";

const KURUM_NAV = [
  { to: "/kurum/musteriler", label: "Müşteriler", uc: true },
];

// §3b Phase 7/7.2 — kurum (banka) arayüzü: banka arayüzünden (Layout.tsx,
// demo/araştırma sayfaları) ve kullanıcı portalinden (PortalLayout.tsx)
// TAMAMEN ayrı, kendi oturum kapısı. `api.kurumBen()` 403 dönerse (giriş
// yapmış ama kuruma üye değil) veya 401 dönerse (giriş yapmamış) girişe atar.
export default function KurumLayout() {
  const [kurum, setKurum] = useState<KurumBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .kurumBen()
      .then(setKurum)
      .catch(() => setKurum(null))
      .finally(() => setYukleniyor(false));
  }, []);

  async function cikisYap() {
    try {
      await api.cikisYap();
    } catch {
      /* oturum zaten düşmüş olabilir */
    }
    navigate("/kurum/giris");
  }

  if (yukleniyor) {
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }
  if (!kurum) {
    return <Navigate to="/kurum/giris" replace />;
  }

  return (
    <div className="min-h-screen bg-background text-on-background font-body-sm text-body-sm antialiased">
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-xl border-b border-outline-variant/30">
        <div className="flex justify-between items-center h-16 px-4 md:px-container-padding max-w-[1200px] mx-auto gap-4">
          <div className="flex items-center gap-6 min-w-0">
            <span className="font-display-sm text-display-sm font-bold tracking-tighter text-on-background shrink-0 flex items-center gap-2">
              <Icon name="account_balance" className="text-primary" /> {kurum.kurum}
            </span>
            <div className="hidden md:flex items-center gap-1">
              {KURUM_NAV.map((n) => (
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
          <button
            onClick={cikisYap}
            className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors shrink-0"
          >
            <Icon name="logout" className="text-[16px]" />
            Çıkış
          </button>
        </div>
      </nav>
      <main className="pt-24 pb-16 px-4 md:px-container-padding max-w-[1200px] mx-auto min-h-screen">
        <Outlet context={kurum} />
      </main>
    </div>
  );
}
