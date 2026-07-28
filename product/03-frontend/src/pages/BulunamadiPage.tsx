import { Link } from "react-router-dom";
import { Icon } from "../components/Icon";

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_404_bulunamad
// ("AKS Terminal" — glitch efektli 404, tarama çizgisi, ızgara arka plan).
// Efektler bu sayfaya özel olduğu için index.css'e değil, buraya scoped
// <style> olarak taşındı — başka hiçbir ekranda kullanılmıyor.
const NAV = [
  { to: "/", label: "Ana Sayfa", ikon: "home" },
  { to: "/panel", label: "Banka Paneli", ikon: "account_balance" },
  { to: "/portal", label: "Kullanıcı Portalı", ikon: "person" },
  { to: "/kurum/musteriler", label: "Kurum Girişi", ikon: "business" },
];

export default function BulunamadiPage() {
  return (
    <div className="min-h-screen flex items-center justify-center relative bg-surface-dim text-on-surface overflow-hidden">
      <style>{`
        .aks-404-scan-line {
          position: absolute; top: 0; left: 0; width: 100%; height: 10px;
          background: rgba(195, 192, 255, 0.1); opacity: 0.4;
          animation: aks-404-scan 4s linear infinite; pointer-events: none; z-index: 10;
        }
        @keyframes aks-404-scan { 0% { transform: translateY(-100%); } 100% { transform: translateY(100vh); } }
        .aks-404-glitch { position: relative; display: inline-block; }
        .aks-404-glitch::before, .aks-404-glitch::after {
          content: attr(data-text); position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0.8;
        }
        .aks-404-glitch::before {
          left: 2px; text-shadow: -2px 0 #c3c0ff; clip: rect(44px, 450px, 56px, 0);
          animation: aks-404-glitch-a 5s infinite linear alternate-reverse;
        }
        .aks-404-glitch::after {
          left: -2px; text-shadow: -2px 0 #45dfa4; clip: rect(44px, 450px, 56px, 0);
          animation: aks-404-glitch-b 5s infinite linear alternate-reverse;
        }
        @keyframes aks-404-glitch-a {
          0% { clip: rect(61px, 9999px, 52px, 0); } 20% { clip: rect(62px, 9999px, 86px, 0); }
          40% { clip: rect(11px, 9999px, 84px, 0); } 60% { clip: rect(9px, 9999px, 77px, 0); }
          80% { clip: rect(66px, 9999px, 92px, 0); } 100% { clip: rect(82px, 9999px, 73px, 0); }
        }
        @keyframes aks-404-glitch-b {
          0% { clip: rect(65px, 9999px, 100px, 0); } 20% { clip: rect(67px, 9999px, 61px, 0); }
          40% { clip: rect(23px, 9999px, 98px, 0); } 60% { clip: rect(30px, 9999px, 16px, 0); }
          80% { clip: rect(47px, 9999px, 73px, 0); } 100% { clip: rect(38px, 9999px, 49px, 0); }
        }
        .aks-404-grid-bg {
          background-image: linear-gradient(#1e293b 1px, transparent 1px), linear-gradient(90deg, #1e293b 1px, transparent 1px);
          background-size: 40px 40px; background-position: center center; opacity: 0.1;
        }
      `}</style>
      <div className="absolute inset-0 aks-404-grid-bg z-0" />
      <div className="aks-404-scan-line" />

      <main className="relative z-10 w-full max-w-2xl px-6 flex flex-col items-center justify-center text-center py-16">
        <h1
          className="text-[100px] md:text-[160px] leading-none font-bold text-primary font-mono-data-md aks-404-glitch tracking-tighter mb-stack-default"
          data-text="404"
        >
          404
        </h1>

        <div className="mb-grid-margin bg-surface-container-low border border-outline-variant rounded-DEFAULT p-stack-default inline-block">
          <p className="font-mono-data-md text-mono-data-md text-on-surface-variant flex items-center gap-2">
            <Icon name="terminal" className="text-error text-[18px]" />
            &gt;_ Aradığınız sayfa terminalde bulunamadı.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-stack-default w-full max-w-md">
          {NAV.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className="group relative bg-surface flex items-center justify-between p-stack-default border border-outline-variant rounded-DEFAULT hover:border-primary transition-colors duration-200"
            >
              <span className="font-mono-label-sm text-mono-label-sm text-on-surface group-hover:text-primary transition-colors">
                {n.label}
              </span>
              <Icon name={n.ikon} className="text-outline-variant group-hover:text-primary transition-colors" />
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
