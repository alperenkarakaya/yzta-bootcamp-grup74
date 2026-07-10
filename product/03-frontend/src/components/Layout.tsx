import { NavLink, Outlet } from "react-router-dom";
import { Icon } from "./Icon";

const NAV_LINKS = [
  { to: "/", label: "Intelligence", end: true },
  { to: "/portfolio", label: "Portfolio" },
  { to: "/audit", label: "Audit" },
  { to: "/customers", label: "Customers" },
];

const BOTTOM_LINKS = [
  { to: "/", icon: "terminal", label: "Command", end: true },
  { to: "/customers", icon: "sensors", label: "Signals" },
  { to: "/audit", icon: "shield_with_heart", label: "Vault" },
  { to: "/portfolio", icon: "smart_toy", label: "Support" },
];

export default function Layout() {
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
            <button
              className="hover:bg-surface-container/50 p-2 rounded-full transition-all active:scale-95"
              title="Sistem canlı — Django API'ye bağlı"
            >
              <Icon name="bolt" />
            </button>
            <div className="w-8 h-8 rounded-full bg-surface-variant border border-outline-variant/30 flex items-center justify-center inner-shadow-subtle text-primary">
              <Icon name="account_circle" />
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile fallback header */}
      <header className="md:hidden fixed top-0 w-full z-50 bg-background/90 backdrop-blur-xl border-b border-outline-variant/30 h-16 flex items-center px-4 justify-center">
        <span className="font-display-sm-mobile text-display-sm-mobile font-bold tracking-tighter text-on-background">
          AKS Intelligence
        </span>
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
