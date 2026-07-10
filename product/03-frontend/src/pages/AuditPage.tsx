import { useEffect, useState } from "react";
import { api, PERSONA_ETIKET, type Adalet, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";

const AGENT_AUDIT = [
  { ad: "VeriAgent", gecti: false, verdict: "Değil — deterministik özellik çıkarımı, saf fonksiyon." },
  { ad: "SkorlamaAgent", gecti: false, verdict: "Değil — predict_proba() + ölçekleme, bir skorlama servisi." },
  { ad: "DanismanAgent", gecti: false, verdict: "Değil (ve bu doğru) — şablonlu NLG; denetime-yakın bir yüzeyde LLM'den daha denetlenebilir." },
  { ad: "Orkestrator", gecti: false, verdict: "Değil — sıralı koordinasyon + bellek-içi log." },
  { ad: "AsistanAgent", gecti: true, verdict: "Evet — beş sorunun tamamını geçiyor: açık uçlu NL arayüzü, klasik kod çözemez, LLM doğru araç, değeri ölçülebilir, doğrulanabilir." },
];

export default function AuditPage() {
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [hata, setHata] = useState("");

  const [incelemeId, setIncelemeId] = useState<number>(1);
  const [inceleme, setInceleme] = useState<SkorSonuc | null>(null);
  const [incelemeYukleniyor, setIncelemeYukleniyor] = useState(false);
  const [incelemeHata, setIncelemeHata] = useState("");

  useEffect(() => {
    api.adalet().then(setAdalet).catch((e) => setHata(String(e)));
  }, []);

  async function incele() {
    setIncelemeYukleniyor(true);
    setIncelemeHata("");
    try {
      setInceleme(await api.skorlaDemo(incelemeId));
    } catch (e) {
      setIncelemeHata(String(e));
      setInceleme(null);
    } finally {
      setIncelemeYukleniyor(false);
    }
  }

  useEffect(() => {
    incele();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const personalar = adalet ? Object.entries(adalet.aks_skor.gruplar) : [];
  const maxOnay = personalar.length ? Math.max(...personalar.map(([, g]) => g.onay_orani)) : 1;
  const parite = adalet ? 1 - adalet.aks_skor.equal_opportunity_boslugu : null;

  return (
    <div className="flex flex-col gap-stack-lg">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-stack-md">
        <div>
          <h1 className="font-display-lg text-display-lg text-on-background mb-2">Fairness &amp; Bias Audit</h1>
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-2xl">
            AKS'nin equal-opportunity metriğiyle gruplar arası davranışını gösterir. Bu bir yasal görüş değildir —
            düzenleyici duruş için execution.md §8'e bakınız.
          </p>
        </div>
        <div className="flex items-center gap-stack-sm bg-surface-container rounded-lg p-2 border border-outline-variant/30">
          <div className="flex flex-col items-end px-3">
            <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Kaynak</span>
            <span className="font-label-mono text-label-mono text-primary">/api/adalet</span>
          </div>
          <div className="h-8 w-px bg-outline-variant/30" />
          <div className="flex flex-col items-end px-3">
            <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Durum</span>
            <span className="font-label-mono text-label-mono text-secondary flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${hata ? "bg-error" : "bg-secondary animate-pulse"}`} />
              {hata ? "HATA" : "CANLI"}
            </span>
          </div>
        </div>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        {/* Adalet Parity Gauge */}
        <section className="md:col-span-4 glass-panel rounded-xl p-6 relative overflow-hidden flex flex-col justify-between ai-glow border-primary/20">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h2 className="font-headline-md text-headline-md">Adalet Parity</h2>
              <p className="font-label-mono text-label-mono text-on-surface-variant">AKS eşit-fırsat parity</p>
            </div>
            <Icon name="balance" className="text-primary" />
          </div>
          <div className="relative py-12 flex flex-col items-center justify-center">
            <div className="relative w-48 h-48">
              <svg className="w-full h-full transform -rotate-90">
                <circle className="text-surface-container-high" cx="96" cy="96" fill="transparent" r="88" stroke="currentColor" strokeWidth="8" />
                <circle
                  className="text-primary transition-all duration-1000"
                  cx="96"
                  cy="96"
                  fill="transparent"
                  r="88"
                  stroke="currentColor"
                  strokeDasharray="552.92"
                  strokeDashoffset={parite != null ? 552.92 * (1 - parite) : 552.92}
                  strokeWidth="8"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-display-sm text-display-sm text-on-background">
                  {parite != null ? (parite * 100).toFixed(1) : "—"}%
                </span>
                <span className="font-label-mono text-label-mono text-secondary">PARITY</span>
              </div>
            </div>
            <div className="mt-8 grid grid-cols-2 gap-4 w-full">
              <div className="flex flex-col">
                <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">AKS Boşluğu</span>
                <span className="font-headline-md text-headline-md text-on-surface">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">Klasik Boşluğu</span>
                <span className="font-headline-md text-headline-md text-error">
                  {adalet ? adalet.klasik_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
            </div>
          </div>
          <div className="bg-surface-container-highest/30 rounded p-3 mt-4 border border-outline-variant/20">
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-tight">
              <span className="text-primary font-bold italic">Not:</span> Boşluk = kredibl onay oranının persona'lar
              arası max-min farkı (0 = tam adil). Bu sayı gerçek /api/adalet çıktısıdır, sabit bir hedef eşiği henüz
              onaylanmadı.
            </p>
          </div>
        </section>

        {/* Equal Opportunity Monitor */}
        <section className="md:col-span-8 glass-panel rounded-xl p-6 flex flex-col">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded bg-secondary/10 flex items-center justify-center text-secondary border border-secondary/20">
                <Icon name="groups" />
              </div>
              <div>
                <h2 className="font-headline-md text-headline-md">Equal Opportunity Monitor</h2>
                <p className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
                  AKS onay oranı — persona bazında parity
                </p>
              </div>
            </div>
          </div>
          <div className="flex-grow space-y-6">
            {personalar.map(([persona, g]) => {
              const oran = maxOnay > 0 ? g.onay_orani / maxOnay : 0;
              return (
                <div className="space-y-2" key={persona}>
                  <div className="flex justify-between items-end">
                    <span className="font-body-lg text-body-lg text-on-surface">{PERSONA_ETIKET[persona] ?? persona}</span>
                    <span className="font-label-mono text-label-mono text-primary">
                      {oran.toFixed(2)} Parity · n={g.n}
                    </span>
                  </div>
                  <div className="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden flex">
                    <div className="h-full bg-primary-container" style={{ width: `${oran * 100}%` }} />
                    <div className="h-full bg-error" style={{ width: `${(1 - oran) * 100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Reason Code Inspector — real SHAP */}
        <section className="md:col-span-5 glass-panel rounded-xl p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <Icon name="psychology" className="text-on-surface-variant" />
            <h2 className="font-headline-md text-headline-md">Reason Code Inspector</h2>
          </div>
          <div className="flex items-center gap-2 mb-6">
            <input
              type="number"
              min={1}
              value={incelemeId}
              onChange={(e) => setIncelemeId(Number(e.target.value))}
              className="bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-label-mono text-label-mono text-on-surface w-28 focus:outline-none focus:border-primary"
            />
            <button
              onClick={incele}
              disabled={incelemeYukleniyor}
              className="px-4 py-2 rounded bg-primary-container text-on-primary-container font-label-mono text-label-mono hover:brightness-110 transition-all disabled:opacity-50"
            >
              {incelemeYukleniyor ? "…" : "İncele"}
            </button>
          </div>
          {incelemeHata && <p className="text-error font-label-mono text-label-mono mb-2">{incelemeHata}</p>}
          {inceleme && (
            <div className="space-y-4 overflow-y-auto pr-2 flex-grow max-h-[360px]">
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Müşteri #{incelemeId} — {PERSONA_ETIKET[inceleme.persona] ?? inceleme.persona} — AKS {inceleme.aks_skor}/850
              </p>
              {inceleme.aciklama.riski_azaltan.map((f) => (
                <div className="p-3 rounded bg-surface-container border-l-2 border-secondary" key={f.kod}>
                  <div className="flex justify-between mb-1">
                    <span className="font-label-mono text-label-mono text-secondary">{f.kod}</span>
                    <span className="font-label-mono text-label-mono text-on-surface-variant">{f.etki.toFixed(3)}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface">{f.faktor} — riski azaltıyor</p>
                </div>
              ))}
              {inceleme.aciklama.riski_artiran.map((f) => (
                <div className="p-3 rounded bg-surface-container border-l-2 border-error" key={f.kod}>
                  <div className="flex justify-between mb-1">
                    <span className="font-label-mono text-label-mono text-error">{f.kod}</span>
                    <span className="font-label-mono text-label-mono text-on-surface-variant">+{f.etki.toFixed(3)}</span>
                  </div>
                  <p className="font-body-sm text-body-sm text-on-surface">{f.faktor} — riski artırıyor</p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Boundary Integrity */}
        <section className="md:col-span-7 glass-panel rounded-xl overflow-hidden border-outline-variant/30">
          <div className="p-4 flex items-center justify-between border-b border-outline-variant/20">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary" />
              <h2 className="font-label-mono text-label-mono text-on-surface font-bold uppercase tracking-widest">
                Sınır Bütünlüğü (Boundary Integrity)
              </h2>
            </div>
          </div>
          <div className="p-6 flex flex-col gap-4">
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
              AKS bankanın klasik skorunu/segmentini <span className="text-primary font-semibold">asla ezmez veya değiştirmez</span> —
              yalnızca tamamlar. Bu, koddaki bir gerçektir: her skorlama, klasik skoru{" "}
              <span className="text-on-surface font-semibold">değiştirilmeden</span> kaydeden değiştirilemez bir
              denetim satırı (<code className="font-label-mono">AuditLog</code>) üretir.
            </p>
            <div className="grid grid-cols-2 gap-4 font-label-mono text-label-mono">
              <div className="p-3 rounded bg-surface-container-lowest border border-outline-variant/20">
                <div className="text-on-surface-variant text-[10px] uppercase mb-1">Yazma modeli</div>
                <div className="text-on-surface">Django admin: salt-okunur</div>
              </div>
              <div className="p-3 rounded bg-surface-container-lowest border border-outline-variant/20">
                <div className="text-on-surface-variant text-[10px] uppercase mb-1">Korunan alan</div>
                <div className="text-on-surface">klasik_skor (DEĞİŞTİRİLMEDİ)</div>
              </div>
            </div>
            <p className="font-label-mono text-[10px] text-on-surface-variant opacity-70">
              Bkz. architecture.md §9 — audit/models.py: Customer, Assessment, AuditLog.
            </p>
          </div>
        </section>

        {/* Agent Honesty Audit */}
        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Icon name="terminal" className="text-tertiary" />
            <h2 className="font-headline-md text-headline-md">Agent Beş-Soru Denetimi</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-gutter">
            {AGENT_AUDIT.map((a) => (
              <div
                key={a.ad}
                className={`p-4 rounded bg-surface-container-lowest border transition-all ${
                  a.gecti ? "border-secondary/50" : "border-outline-variant/20"
                }`}
              >
                <div className="flex justify-between items-start mb-3">
                  <span
                    className={`font-label-mono text-label-mono text-[10px] px-1.5 py-0.5 rounded ${
                      a.gecti ? "text-secondary bg-secondary/10" : "text-on-surface-variant bg-outline-variant/10"
                    }`}
                  >
                    {a.gecti ? "AGENT" : "PIPELINE STAGE"}
                  </span>
                </div>
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-2">{a.ad}</div>
                <p className="font-body-sm text-body-sm text-on-surface-variant">{a.verdict}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
