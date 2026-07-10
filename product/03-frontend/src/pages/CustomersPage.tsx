import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, PERSONA_ETIKET, HEDEF_PERSONALAR, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, kapasiteYuzdesi, skorDeltaYuzde, type Durum } from "../lib/skor";

interface Satir extends SkorSonuc {
  id: number;
}

const ADET_PER_PERSONA = 6;

type Filtre = "hepsi" | "kurtarildi" | "reddedildi" | "hedef";

export default function CustomersPage() {
  const [satirlar, setSatirlar] = useState<Satir[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [evrenBuyuklugu, setEvrenBuyuklugu] = useState<number | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");
  const [filtre, setFiltre] = useState<Filtre>("hepsi");
  const [arama, setArama] = useState("");

  useEffect(() => {
    let iptal = false;
    setYukleniyor(true);
    setSatirlar([]);
    setLog([]);
    api
      .bilgi()
      .then((b) => !iptal && setEvrenBuyuklugu(b.demo_musteri_sayisi))
      .catch(() => {});
    api
      .demoMusteriler(ADET_PER_PERSONA)
      .then(async (grup) => {
        const ids = Object.values(grup).flat();
        setLog((l) => [...l, `[INFO] ${ids.length} demo müşteri kimliği alındı`]);
        await Promise.all(
          ids.map(async (id) => {
            try {
              const s = await api.skorlaDemo(id);
              if (iptal) return;
              setSatirlar((prev) => [...prev, { ...s, id }].sort((a, b) => a.id - b.id));
              setLog((l) => [...l.slice(-30), `[OK] #${id} skorlandı → AKS ${s.aks_skor}`]);
            } catch {
              setLog((l) => [...l.slice(-30), `[ERR] #${id} skorlanamadı`]);
            }
          })
        );
      })
      .catch((e) => setHata(String(e)))
      .finally(() => !iptal && setYukleniyor(false));
    return () => {
      iptal = true;
    };
  }, []);

  const filtreli = useMemo(() => {
    return satirlar.filter((s) => {
      const durum: Durum = durumBelirle(s.klasik_skor, s.aks_skor);
      if (filtre === "kurtarildi" && durum !== "kurtarildi") return false;
      if (filtre === "reddedildi" && durum !== "reddedildi") return false;
      if (filtre === "hedef" && !HEDEF_PERSONALAR.includes(s.persona)) return false;
      if (arama) {
        const q = arama.toLowerCase();
        const hit = String(s.id).includes(q) || (PERSONA_ETIKET[s.persona] ?? s.persona).toLowerCase().includes(q);
        if (!hit) return false;
      }
      return true;
    });
  }, [satirlar, filtre, arama]);

  const kurtarilanSayisi = satirlar.filter((s) => durumBelirle(s.klasik_skor, s.aks_skor) === "kurtarildi").length;
  const ortKapasite = satirlar.length
    ? Math.round(satirlar.reduce((sum, s) => sum + kapasiteYuzdesi(s.aks_skor), 0) / satirlar.length)
    : 0;

  return (
    <div className="flex flex-col gap-stack-md">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-stack-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className={`flex h-2 w-2 rounded-full ${yukleniyor ? "bg-secondary ai-pulse" : "bg-secondary"}`} />
            <span className="font-label-mono text-label-mono text-secondary uppercase tracking-widest">
              {yukleniyor ? "Skorlanıyor…" : "Canlı Değerlendirme Kuyruğu"}
            </span>
          </div>
          <h1 className="font-display-sm text-display-sm">Customer Intelligence</h1>
        </div>
        <div className="flex gap-gutter overflow-x-auto pb-2">
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Kurtarılan</span>
            <span className="font-display-sm text-display-sm text-primary">{kurtarilanSayisi}</span>
          </div>
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Yüklenen</span>
            <span className="font-display-sm text-display-sm">{satirlar.length}</span>
          </div>
          <div className="flex flex-col border-l border-outline-variant/30 pl-4">
            <span className="font-label-mono text-label-mono text-on-surface-variant uppercase">Ort. Kapasite</span>
            <span className="font-display-sm text-display-sm">{ortKapasite}%</span>
          </div>
        </div>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      {/* Filters */}
      <div className="bg-surface-container-lowest/50 border border-outline-variant/30 rounded-xl p-4 backdrop-blur-md flex flex-wrap items-center gap-stack-md">
        <div className="flex items-center gap-stack-sm mr-auto flex-wrap">
          {([
            ["hepsi", "Tümü"],
            ["kurtarildi", "Kurtarılan"],
            ["reddedildi", "Reddedilen"],
            ["hedef", "Hedef Segment"],
          ] as [Filtre, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setFiltre(key)}
              className={`px-4 py-1.5 rounded-full font-label-mono text-label-mono transition-transform hover:scale-105 active:scale-95 ${
                filtre === key ? "bg-primary-container text-on-primary-container" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 font-label-mono text-label-mono bg-surface-container px-3 py-1.5 rounded border border-outline-variant/20">
          <Icon name="search" className="text-sm" />
          <input
            value={arama}
            onChange={(e) => setArama(e.target.value)}
            placeholder="ID veya persona ara…"
            className="bg-transparent outline-none placeholder:text-on-surface-variant/60 w-40"
          />
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface-container border border-outline-variant/30 rounded-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="glass-header text-on-surface-variant font-label-mono text-label-mono uppercase tracking-widest">
                <th className="py-4 px-6 font-medium">Kimlik / Persona</th>
                <th className="py-4 px-6 font-medium">Kapasite Sinyali</th>
                <th className="py-4 px-6 font-medium">Skor Değişimi</th>
                <th className="py-4 px-6 font-medium">Klasik Skor</th>
                <th className="py-4 px-6 font-medium">AKS Skoru</th>
                <th className="py-4 px-6 font-medium text-right">İşlem</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filtreli.map((s) => {
                const durum = durumBelirle(s.klasik_skor, s.aks_skor);
                const delta = skorDeltaYuzde(s.klasik_skor, s.aks_skor);
                const kapasite = kapasiteYuzdesi(s.aks_skor);
                const renk = durum === "kurtarildi" ? "text-secondary" : durum === "reddedildi" ? "text-error" : "text-primary";
                return (
                  <tr className="command-table-row transition-all duration-150" key={s.id}>
                    <td className="py-4 px-6">
                      <div className="flex flex-col">
                        <span className="font-bold text-on-surface">CST-{String(s.id).padStart(4, "0")}</span>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          <span className="bg-tertiary-container/30 text-tertiary px-2 py-0.5 rounded text-[10px] uppercase font-bold border border-tertiary-container/50">
                            {PERSONA_ETIKET[s.persona]?.split(" ")[0] ?? s.persona}
                          </span>
                          {durum === "kurtarildi" && (
                            <span className="bg-secondary-container/30 text-secondary px-2 py-0.5 rounded text-[10px] uppercase font-bold border border-secondary-container/50">
                              Kurtarıldı
                            </span>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-1 bg-surface-container-highest rounded-full overflow-hidden min-w-[80px]">
                          <div className={`h-full ${renk.replace("text-", "bg-")}`} style={{ width: `${kapasite}%` }} />
                        </div>
                        <span className={`font-label-mono text-label-mono ${renk}`}>{kapasite}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <span className={`font-bold font-label-mono ${delta != null && delta >= 0 ? "text-secondary" : "text-error"}`}>
                        {delta != null ? `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%` : "—"}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-label-mono opacity-60">{s.klasik_skor ?? "—"}</td>
                    <td className={`py-4 px-6 font-label-mono font-bold ${renk}`}>{s.aks_skor}</td>
                    <td className="py-4 px-6 text-right">
                      <Link to={`/customers/${s.id}`} className="text-on-surface-variant hover:text-primary transition-colors">
                        <Icon name="open_in_new" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="glass-header p-4 flex items-center justify-between font-label-mono text-label-mono text-on-surface-variant flex-wrap gap-2">
          <div className="flex items-center gap-4">
            <span>
              Gösterilen {filtreli.length} / yüklenen {satirlar.length}
              {evrenBuyuklugu != null && ` · demo evreni ${evrenBuyuklugu}`}
            </span>
          </div>
        </div>
      </div>

      {/* Live activity log */}
      <div className="hidden xl:block fixed right-container-padding bottom-32 w-80 bg-surface-container-high border border-outline-variant/50 rounded-xl shadow-2xl overflow-hidden">
        <div className="bg-surface-container-highest px-4 py-2 border-b border-outline-variant/30 flex items-center justify-between">
          <span className="font-label-mono text-label-mono text-on-surface">Etkinlik Günlüğü</span>
        </div>
        <div className="p-4 font-label-mono text-[11px] space-y-1.5 leading-relaxed h-56 overflow-y-auto">
          {log.slice(-12).map((l, i) => (
            <p key={i} className={l.startsWith("[ERR]") ? "text-error" : l.startsWith("[OK]") ? "text-on-surface-variant" : "text-primary"}>
              {l}
            </p>
          ))}
          {!yukleniyor && <p className="text-on-surface-variant opacity-40">&gt; hazır</p>}
        </div>
      </div>
    </div>
  );
}
