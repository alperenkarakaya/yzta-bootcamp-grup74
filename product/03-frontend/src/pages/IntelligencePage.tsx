import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api, PERSONA_ETIKET, HEDEF_PERSONALAR, type Bilgi, type Portfoy, type Adalet, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, kapasiteYuzdesi } from "../lib/skor";

interface FeedOge extends SkorSonuc {
  id: number;
}

export default function IntelligencePage() {
  const [bilgi, setBilgi] = useState<Bilgi | null>(null);
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [feed, setFeed] = useState<FeedOge[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [hata, setHata] = useState("");

  const sync = useCallback(async () => {
    setSyncing(true);
    setHata("");
    try {
      const [b, p, a, demo] = await Promise.all([
        api.bilgi(),
        api.portfoy().catch(() => null),
        api.adalet().catch(() => null),
        api.demoMusteriler(1),
      ]);
      setBilgi(b);
      setPortfoy(p);
      setAdalet(a);

      const ids = Object.values(demo).flat().slice(0, 4);
      const skorlar = await Promise.all(ids.map((id) => api.skorlaDemo(id)));
      setFeed(skorlar.map((s, i) => ({ ...s, id: ids[i] })));
    } catch (e) {
      setHata(String(e));
    } finally {
      setSyncing(false);
    }
  }, []);

  useEffect(() => {
    sync();
  }, [sync]);

  const maxKirilim = portfoy ? Math.max(1, ...Object.values(portfoy.persona_kirilimi)) : 1;

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
      {/* Header */}
      <div className="col-span-1 md:col-span-12 mb-4 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="font-headline-md text-headline-md text-on-background">Terminal Overview</h1>
          <p className="font-label-mono text-label-mono text-on-surface-variant mt-1">
            SYS.STATUS: {hata ? "OFFLINE" : "ONLINE"} | MODEL: {bilgi?.model ?? "—"} | SÜRÜM: {bilgi?.surum ?? "—"}
          </p>
        </div>
        <button
          onClick={sync}
          disabled={syncing}
          className="bg-primary-container text-white font-label-mono text-label-mono px-4 py-2 rounded-DEFAULT inner-shadow-subtle hover:bg-inverse-primary transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <Icon name="refresh" className={`text-[16px] ${syncing ? "animate-spin" : ""}`} />
          {syncing ? "SENKRONİZE EDİLİYOR" : "SYNC DATA"}
        </button>
      </div>

      {hata && (
        <div className="col-span-1 md:col-span-12 bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend'e bağlanılamadı: {hata} — Django çalışıyor mu? (<code>python manage.py runserver</code>)
        </div>
      )}

      {/* Live Engine Feed */}
      <section className="col-span-1 md:col-span-8 card-surface rounded-lg flex flex-col overflow-hidden min-h-[400px]">
        <div className="glass-header px-4 py-3 flex justify-between items-center">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-secondary-container animate-pulse" />
            LIVE ENGINE FEED
          </h2>
          <span className="font-label-mono text-[10px] text-on-surface-variant">
            {bilgi ? `${bilgi.demo_musteri_sayisi} DEMO MÜŞTERİ` : "—"}
          </span>
        </div>
        <div className="p-4 flex-1 overflow-y-auto flex flex-col gap-2">
          {feed.length === 0 && !syncing && (
            <p className="text-on-surface-variant font-body-sm text-body-sm p-4">Henüz veri yok.</p>
          )}
          {feed.map((m) => {
            const durum = durumBelirle(m.klasik_skor, m.aks_skor);
            const renk =
              durum === "kurtarildi" ? "text-primary" : durum === "onaylandi" ? "text-secondary-container" : "text-error";
            return (
              <Link
                key={m.id}
                to={`/customers/${m.id}`}
                className="bg-surface-container rounded-DEFAULT p-3 border border-outline-variant/30 flex justify-between items-center relative overflow-hidden group hover:border-primary/40 transition-colors"
              >
                <div className="flex items-center gap-4 relative z-10">
                  <div className="w-10 h-10 rounded-full bg-[#1E293B] flex items-center justify-center border border-outline-variant/30">
                    <Icon
                      name={durum === "kurtarildi" ? "psychology" : durum === "onaylandi" ? "person" : "warning"}
                      className={renk}
                    />
                  </div>
                  <div>
                    <div className="font-body-sm text-body-sm font-semibold text-on-surface flex items-center gap-2">
                      ID: #{m.id}
                      {durum === "kurtarildi" && (
                        <span className="text-[10px] bg-primary-container/20 text-primary px-2 py-0.5 rounded-full border border-primary/30">
                          RESCUED
                        </span>
                      )}
                    </div>
                    <div className="font-label-mono text-[10px] text-on-surface-variant mt-0.5">
                      Persona: {PERSONA_ETIKET[m.persona] ?? m.persona}
                    </div>
                  </div>
                </div>
                <div className="text-right relative z-10">
                  <div className={`font-body-sm text-body-sm font-semibold ${renk}`}>{DURUM_ETIKET[durum]}</div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant">
                    Klasik {m.klasik_skor ?? "—"} → AKS {m.aks_skor}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Agent HUD */}
      <section className="col-span-1 md:col-span-4 card-surface rounded-lg flex flex-col min-h-[400px]">
        <div className="glass-header px-4 py-3 border-b border-outline-variant/30">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">PIPELINE HUD</h2>
        </div>
        <div className="p-4 flex-1 flex flex-col gap-4">
          {[
            { ad: "VeriAgent", aciklama: "özellik çıkarımı" },
            { ad: "SkorlamaAgent", aciklama: "model skorlama" },
            { ad: "DanismanAgent", aciklama: "öneri üretimi" },
          ].map((a) => (
            <div className="flex items-center gap-3" key={a.ad}>
              <div className={`w-2 h-2 rounded-full ${syncing ? "bg-primary-container animate-pulse ai-glow" : "bg-secondary-container"}`} />
              <div className="flex-1">
                <div className="flex justify-between items-end mb-1">
                  <span className="font-label-mono text-label-mono text-on-surface">{a.ad}</span>
                  <span className={`font-label-mono text-[10px] ${syncing ? "text-primary" : "text-secondary-container"}`}>
                    {syncing ? "ACTIVE" : "IDLE"}
                  </span>
                </div>
                <div className="w-full bg-[#1E293B] h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full relative overflow-hidden ${syncing ? "bg-primary-container w-full" : "bg-secondary-container w-full"}`}
                  >
                    {syncing && (
                      <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/40 to-transparent -translate-x-full animate-[shimmer_1.5s_infinite]" />
                    )}
                  </div>
                </div>
                <div className="font-label-mono text-[9px] text-on-surface-variant mt-0.5">{a.aciklama}</div>
              </div>
            </div>
          ))}
          <div className="mt-auto pt-4 border-t border-outline-variant/20">
            <p className="font-label-mono text-[9px] text-on-surface-variant leading-relaxed">
              Veri/Skorlama/Danışman deterministik pipeline aşamalarıdır (agent değil). Beş-soru testini geçen
              tek gerçek agent: AsistanAgent. Bkz. architecture.md §4.
            </p>
          </div>
        </div>
      </section>

      {/* Portfolio Pulse */}
      <section className="col-span-1 md:col-span-6 card-surface rounded-lg flex flex-col h-[350px]">
        <div className="glass-header px-4 py-3 flex justify-between items-center">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">PORTFÖY NABZI</h2>
          <span className="font-label-mono text-[10px] text-on-surface-variant">Kurtarılan / persona</span>
        </div>
        <div className="p-4 flex-1 relative flex items-end justify-center">
          {portfoy ? (
            <div className="w-full h-full flex items-end justify-between px-2 gap-3">
              {Object.entries(portfoy.persona_kirilimi).map(([persona, adet]) => (
                <div className="flex-1 flex flex-col justify-end items-center gap-1 group h-full" key={persona}>
                  <span className="font-label-mono text-[10px] text-on-surface-variant opacity-0 group-hover:opacity-100">
                    {adet}
                  </span>
                  <div
                    className="w-full bg-gradient-to-t from-primary-container to-secondary-container rounded-t-sm shadow-[0_0_10px_rgba(79,70,229,0.3)] transition-all"
                    style={{ height: `${Math.max(6, (adet / maxKirilim) * 100)}%` }}
                  />
                  <span className="font-label-mono text-[9px] text-on-surface-variant text-center mt-1">
                    {(PERSONA_ETIKET[persona] ?? persona).split(" ")[0]}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-on-surface-variant font-body-sm text-body-sm">Portföy verisi yükleniyor…</p>
          )}
        </div>
      </section>

      {/* Segment Alpha Metrics */}
      <section className="col-span-1 md:col-span-6 card-surface rounded-lg flex flex-col h-[350px] relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-primary-container/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/4 pointer-events-none" />
        <div className="glass-header px-4 py-3">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant">HEDEF SEGMENT KURTARMA ORANI</h2>
        </div>
        <div className="p-6 flex-1 flex flex-col justify-center gap-6 z-10">
          <div className="grid grid-cols-2 gap-4">
            {HEDEF_PERSONALAR.map((persona) => {
              const tpr = adalet?.aks_skor.gruplar[persona]?.kredibl_onay_orani_tpr;
              return (
                <div className="bg-[#1E293B]/50 p-4 rounded-DEFAULT border border-outline-variant/20" key={persona}>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mb-1 uppercase">
                    {PERSONA_ETIKET[persona]}
                  </div>
                  <div className="font-display-sm text-display-sm text-on-surface flex items-baseline gap-1">
                    {tpr != null ? (tpr * 100).toFixed(1) : "—"}
                    <span className="text-body-sm text-secondary-container">%</span>
                  </div>
                  <div className="font-label-mono text-[10px] text-on-surface-variant mt-2">
                    kredibl onay oranı (TPR)
                  </div>
                </div>
              );
            })}
          </div>
          <div className="text-body-sm text-on-surface-variant border-l-2 border-primary-container pl-3">
            AKS eşiğinde ({"≥650"}) hedef segmentteki kredibl müşterilerin onaylanma oranı — davranışsal modelin
            asıl iddia ettiği yerde ölçülen gerçek performans (bkz. architecture.md §6, per-persona bulgular).
          </div>
        </div>
      </section>
    </div>
  );
}
