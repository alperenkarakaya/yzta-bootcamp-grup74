import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Bilgi, type MetriklerRaporu } from "../api";
import { Icon } from "../components/Icon";

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_intelligence_panel
// ("AKS Terminal" — komuta merkezi: 3 durum kartı + hızlı erişim ızgarası).
// Nav'ın kendisi Layout.tsx'te; bu sayfa yalnızca <main> içeriği. Stitch
// mockup'ı sabit sayılar (0.862, 2,000, ONLINE) gösteriyordu — burada gerçek
// API verisiyle besleniyor (bilgi/metrikler, ikisi de opsiyonel/503 olabilir,
// demo çevrimdışıyken sayfa kırılmasın diye .catch(() => null) ile).
const HIZLI_ERISIM = [
  { ikon: "pie_chart", baslik: "Portföy Analizi", aciklama: "Risk dağılımı ve segmentasyon", to: "/portfolio" },
  { ikon: "history_edu", baslik: "Denetim Defteri", aciklama: "Sistem logları ve karar izleri", to: "/audit" },
  { ikon: "recent_actors", baslik: "Müşteri Listesi", aciklama: "Bireysel skorlama detayları", to: "/customers" },
  { ikon: "upload_file", baslik: "Yeni Ekstre Yükle", aciklama: "Toplu veri işleme kuyruğu", to: "/upload" },
];

export default function IntelligencePage() {
  const [bilgi, setBilgi] = useState<Bilgi | null>(null);
  const [metrikler, setMetrikler] = useState<MetriklerRaporu | null>(null);
  const [gecikmeMs, setGecikmeMs] = useState<number | null>(null);
  const [cevrimici, setCevrimici] = useState<boolean | null>(null);

  useEffect(() => {
    const baslangic = performance.now();
    api
      .bilgi()
      .then((b) => {
        setBilgi(b);
        setGecikmeMs(Math.round(performance.now() - baslangic));
        setCevrimici(true);
      })
      .catch(() => setCevrimici(false));
    api.metrikler().then(setMetrikler).catch(() => setMetrikler(null));
  }, []);

  const model = metrikler?.modeller[0];

  return (
    <>
      {/* Header Metrics */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
        <div className="bg-surface-container-low border border-outline-variant p-4 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <span className="text-on-surface-variant text-mono-label-sm font-mono-label-sm">MODEL_ACCURACY</span>
            <Icon name="query_stats" className="text-outline text-sm" />
          </div>
          <div>
            <div className="text-mono-score-lg font-mono-score-lg text-primary">
              {model ? model.roc_auc.ortalama.toFixed(3) : "—"}
            </div>
            <div className="text-mono-label-sm font-mono-label-sm text-secondary mt-1">
              {model ? `AUC | %95 GA [${model.roc_auc.ci95[0].toFixed(2)}, ${model.roc_auc.ci95[1].toFixed(2)}]` : "Henüz üretilmedi"}
            </div>
          </div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant p-4 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <span className="text-on-surface-variant text-mono-label-sm font-mono-label-sm">POPULATION</span>
            <Icon name="group" className="text-outline text-sm" />
          </div>
          <div>
            <div className="text-mono-score-lg font-mono-score-lg text-on-surface">
              {bilgi ? bilgi.demo_musteri_sayisi.toLocaleString("tr-TR") : "—"}
            </div>
            <div className="text-mono-label-sm font-mono-label-sm text-on-surface-variant mt-1">Demo Müşteri</div>
          </div>
        </div>

        <div className="bg-surface-container-low border border-outline-variant p-4 flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <span className="text-on-surface-variant text-mono-label-sm font-mono-label-sm">SYSTEM_STATUS</span>
            <Icon name="dns" className="text-outline text-sm" />
          </div>
          <div className="flex items-end justify-between">
            <div>
              <div className={`text-mono-score-lg font-mono-score-lg ${cevrimici ? "text-secondary" : "text-error"}`}>
                {cevrimici == null ? "…" : cevrimici ? "ONLINE" : "OFFLINE"}
              </div>
              <div className="text-mono-label-sm font-mono-label-sm text-on-surface-variant mt-1">
                {gecikmeMs != null ? `Latency: ${gecikmeMs}ms` : "—"}
              </div>
            </div>
            {cevrimici && <div className="w-3 h-3 bg-secondary rounded-full pulse-dot mb-2" />}
          </div>
        </div>
      </section>

      {/* Quick Access Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-gutter mt-4">
        {HIZLI_ERISIM.map((h) => (
          <Link
            key={h.to}
            to={h.to}
            className="group bg-surface-container border border-outline-variant p-6 flex items-center justify-between hover:border-primary hover:bg-surface-container-high transition-colors duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 border border-outline-variant flex items-center justify-center bg-surface-dim group-hover:border-primary transition-colors">
                <Icon name={h.ikon} className="text-on-surface" />
              </div>
              <div>
                <div className="text-mono-data-md font-mono-data-md text-on-surface">{h.baslik}</div>
                <div className="text-mono-label-sm font-mono-label-sm text-on-surface-variant mt-1">{h.aciklama}</div>
              </div>
            </div>
            <Icon name="arrow_forward" className="text-outline group-hover:text-primary transition-colors" />
          </Link>
        ))}
      </section>
    </>
  );
}
