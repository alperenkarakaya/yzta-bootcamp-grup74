import { useEffect, useState } from "react";
import { Navigate, Outlet, useNavigate } from "react-router-dom";
import { api, type KurumBilgisi } from "../api";

// §3b Phase 7/7.2 — kurum (banka) arayüzü: banka arayüzünden (Layout.tsx,
// demo/araştırma sayfaları) ve kullanıcı portalinden (PortalLayout.tsx)
// TAMAMEN ayrı, kendi oturum kapısı. `api.kurumBen()` 403 dönerse (giriş
// yapmış ama kuruma üye değil) veya 401 dönerse (giriş yapmamış) girişe atar.
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_m_teriler
// ("B2B Staff Portal" — sade tek satır üst nav, tek nav öğesi Müşteriler).
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
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Yükleniyor…</p>
      </div>
    );
  }
  if (!kurum) {
    return <Navigate to="/kurum/giris" replace />;
  }

  return (
    <div className="bg-background text-on-background font-body-md text-body-md h-screen flex flex-col overflow-hidden">
      {/* TopNavBar */}
      <nav className="bg-surface-dim flex justify-between items-center px-4 md:px-grid-margin h-16 w-full border-b border-outline-variant shrink-0">
        <div className="flex items-center gap-6 min-w-0">
          <span className="font-headline-md text-headline-md font-semibold text-primary truncate">{kurum.kurum}</span>
          <ul className="hidden md:flex items-center h-full pt-1 space-x-6">
            <li>
              <span className="inline-block text-primary font-bold border-b-2 border-primary pb-1">Müşteriler</span>
            </li>
          </ul>
        </div>
        <button
          onClick={cikisYap}
          className="font-mono-label-sm text-mono-label-sm text-on-surface-variant hover:text-primary transition-colors duration-200"
        >
          Çıkış
        </button>
      </nav>

      {/* Main Content Canvas */}
      <main className="flex-1 overflow-y-auto p-4 md:p-grid-margin bg-surface-dim">
        <Outlet context={kurum} />
      </main>
    </div>
  );
}
