import { useEffect, useState } from "react";
import { Navigate, Outlet, useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "./Icon";

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

  if (!kullanici) {
    return <Navigate to="/portal/giris" replace />;
  }

  return (
    <div className="min-h-screen bg-background text-on-background font-body-sm text-body-sm antialiased">
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-xl border-b border-outline-variant/30">
        <div className="flex justify-between items-center h-16 px-4 md:px-container-padding max-w-[1000px] mx-auto">
          <span className="font-display-sm text-display-sm font-bold tracking-tighter text-on-background">
            AKS Portal
          </span>
          <div className="flex items-center gap-4">
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
      </nav>
      <main className="pt-24 pb-16 px-4 md:px-container-padding max-w-[1000px] mx-auto min-h-screen">
        <Outlet context={kullanici} />
      </main>
    </div>
  );
}
