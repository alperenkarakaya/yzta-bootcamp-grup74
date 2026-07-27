import { useEffect, useState } from "react";
import {
  api,
  PERSONA_ETIKET,
  type Adalet,
  type SkorSonuc,
  type MetriklerRaporu,
  type SegmentasyonRaporu,
  type GenellemeSaglamlikRaporu,
} from "../api";
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

  const [metrikler, setMetrikler] = useState<MetriklerRaporu | null>(null);
  const [metriklerHata, setMetriklerHata] = useState("");

  const [segmentasyon, setSegmentasyon] = useState<SegmentasyonRaporu | null>(null);
  const [segmentasyonHata, setSegmentasyonHata] = useState("");

  const [genelleme, setGenelleme] = useState<GenellemeSaglamlikRaporu | null>(null);
  const [genellemeHata, setGenellemeHata] = useState("");

  useEffect(() => {
    api.adalet().then(setAdalet).catch((e) => setHata(String(e)));
    api.metrikler().then(setMetrikler).catch((e) => setMetriklerHata(String(e)));
    api.segmentasyon().then(setSegmentasyon).catch((e) => setSegmentasyonHata(String(e)));
    api.genellemeSaglamlik().then(setGenelleme).catch((e) => setGenellemeHata(String(e)));
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
            AKS'nin equal-opportunity metriğiyle gruplar arası davranışını gösterir. Bu bir yasal görüş değildir.
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

      {adalet?.veri_kaynagi === "dongusel" && (
        <div className="bg-secondary-container/10 border border-secondary/30 text-on-surface-variant rounded-DEFAULT p-3 font-body-sm text-body-sm">
          <span className="text-secondary font-semibold">Not:</span> {adalet.uyari}
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
          </div>
        </section>

        {/* Model Validity — §3b/U20, /api/metrikler (degerlendirme.py's CV+CI harness) */}
        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <Icon name="query_stats" className="text-primary" />
              <h2 className="font-headline-md text-headline-md">Model Validity</h2>
            </div>
            {metrikler && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                {metrikler.n_musteri} müşteri · veri: {metrikler.veri_kaynagi}
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            Repeated stratified k-fold ROC-AUC/PR-AUC (bootstrap %95 CI), Brier skoru ve ECE (kalibrasyon hatası).
            <span className="text-primary font-semibold"> Bu, gerçek veriyle doğrulanmış bir sonuç değildir</span> —
            sentetik/dekuple bir benchmark üzerinde ölçülmüştür. Bu sayılar bir iş tezini kanıtlamaz, yalnızca bu
            benchmark üzerindeki istatistiksel davranışı gösterir.
          </p>
          {metriklerHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {metrikler && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
              {metrikler.modeller.map((m) => (
                <div key={m.ad} className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                  <div className="font-label-mono text-label-mono text-on-surface font-bold mb-3">{m.ad}</div>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">ROC-AUC</div>
                      <div className="font-headline-md text-headline-md text-primary">{m.roc_auc.ortalama.toFixed(3)}</div>
                      <div className="text-[10px] text-on-surface-variant font-label-mono">
                        %95 CI [{m.roc_auc.ci95[0].toFixed(3)}, {m.roc_auc.ci95[1].toFixed(3)}]
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">ECE (kalibrasyon)</div>
                      <div className="font-headline-md text-headline-md text-secondary">{m.ece_oof.toFixed(3)}</div>
                      <div className="text-[10px] text-on-surface-variant font-label-mono">Brier {m.brier_oof.toFixed(3)}</div>
                    </div>
                  </div>
                  {Object.keys(m.persona_metrik).length > 0 && (
                    <div className="space-y-1">
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono mb-1">Persona bazında AUC</div>
                      {Object.entries(m.persona_metrik).map(([persona, pm]) => (
                        <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                          <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                          <span className="text-on-surface">{pm.auc.toFixed(3)} (n={pm.n})</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Segmentasyon — §3b/U26, denetimsiz K-Means keşif */}
        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <Icon name="scatter_plot" className="text-tertiary" />
              <h2 className="font-headline-md text-headline-md">Segmentasyon (Denetimsiz Keşif)</h2>
            </div>
            {segmentasyon && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                k={segmentasyon.k} · silhouette {segmentasyon.silhouette_skoru.toFixed(3)} · n={segmentasyon.n_musteri}
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            K-Means ile davranışsal özellikler üzerinde denetimsiz kümeleme — sabit 4 persona etiketi yerine,
            verinin kendisi kaç doğal grup önerdiğine (silhouette skoruna göre) bakar.{" "}
            <span className="text-primary font-semibold">Bu bir karar bileşeni değildir</span> — hiçbir
            skorlama/karar yoluna beslenmez, yalnızca araştırma/şeffaflık amaçlıdır.
          </p>
          {segmentasyonHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {segmentasyon && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter mb-4">
                {Object.entries(segmentasyon.kume_profilleri)
                  .sort(([, a], [, b]) => b.n - a.n)
                  .map(([kume, prof]) => (
                    <div key={kume} className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                      <div className="flex justify-between items-baseline mb-3">
                        <span className="font-label-mono text-label-mono text-on-surface font-bold">Küme {kume}</span>
                        <span className="font-label-mono text-[10px] text-on-surface-variant">n={prof.n}</span>
                      </div>
                      <div className="mb-3">
                        <div className="text-[10px] text-on-surface-variant uppercase font-label-mono">Ampirik temerrüt oranı</div>
                        <div className="font-headline-md text-headline-md text-secondary">{(prof.temerrut_orani * 100).toFixed(1)}%</div>
                      </div>
                      <div className="text-[10px] text-on-surface-variant uppercase font-label-mono mb-1">Persona dağılımı</div>
                      <div className="space-y-1">
                        {Object.entries(prof.persona_dagilimi)
                          .sort(([, a], [, b]) => b - a)
                          .map(([persona, adet]) => (
                            <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                              <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                              <span className="text-on-surface">{adet}</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  ))}
              </div>
              <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">{segmentasyon.not}</p>
            </>
          )}
        </section>

        {/* Genelleme & Sağlamlık — §4 R8/R10/R11 */}
        <section className="md:col-span-12 glass-panel rounded-xl p-6">
          <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
            <div className="flex items-center gap-3">
              <Icon name="rule" className="text-tertiary" />
              <h2 className="font-headline-md text-headline-md">Genelleme &amp; Sağlamlık</h2>
            </div>
            {genelleme && (
              <span className="font-label-mono text-label-mono text-[10px] text-on-surface-variant uppercase">
                referans model: {genelleme.model_adi_referans} · {genelleme.n_musteri} müşteri
              </span>
            )}
          </div>
          <p className="font-body-sm text-body-sm text-on-surface-variant mb-6 max-w-3xl">
            Rastgele k-fold CV'nin (Model Validity paneli) test edemediği üç soru: model hiç görmediği bir davranış
            profiline genelleşiyor mu, ince işlem geçmişinde zarifçe mi kararsızlaşıyor yoksa güvenle mi yanılıyor,
            ve nedensel özelliklerden hangisi en kolay "oyunlanıyor".
          </p>
          {genellemeHata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono mb-4">
              Bu rapor henüz üretilmedi.
            </div>
          )}
          {genelleme && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
              {/* R8 */}
              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R8 — Persona-dışı genelleme
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  Her persona sırayla eğitimden tamamen çıkarılıp test edildi — "hiç görmedim" testi.
                </p>
                <div className="space-y-2 mb-4">
                  {Object.entries(genelleme.persona_disi_genelleme.sonuc).map(([persona, s]) => (
                    <div key={persona} className="flex justify-between font-label-mono text-label-mono text-[11px]">
                      <span className="text-on-surface-variant">{PERSONA_ETIKET[persona] ?? persona}</span>
                      <span className="text-on-surface">{s.auc != null ? s.auc.toFixed(3) : "—"} (n={s.n_test})</span>
                    </div>
                  ))}
                </div>
                <div className="pt-3 border-t border-outline-variant/20">
                  <div className="text-[10px] text-amber-400 uppercase font-label-mono mb-1">Out-of-time split</div>
                  <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">
                    {genelleme.out_of_time_split.durum} — {genelleme.out_of_time_split.gerekce}
                  </p>
                </div>
              </div>

              {/* R10 */}
              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R10 — İnce dosya stres testi
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  Geçmiş ilk K işleme kırpıldığında skor sapması ve anomali bayrağı oranı.
                </p>
                <table className="w-full font-label-mono text-[11px]">
                  <thead>
                    <tr className="text-on-surface-variant text-left">
                      <th className="font-normal pb-1">K</th>
                      <th className="font-normal pb-1 text-right">Ort. Sapma</th>
                      <th className="font-normal pb-1 text-right">Anomali %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(genelleme.ince_dosya_stres_testi.sonuc).map(([k, s]) => (
                      <tr key={k} className="border-t border-outline-variant/10">
                        <td className="py-1 text-on-surface">{k.replace("ilk_", "").replace("_islem", "")}</td>
                        <td className="py-1 text-right text-on-surface">{s.ort_mutlak_sapma}</td>
                        <td className="py-1 text-right text-amber-400">
                          {s.anomali_bayrak_orani != null ? `${(s.anomali_bayrak_orani * 100).toFixed(0)}%` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* R11 */}
              <div className="rounded-lg border border-outline-variant/30 bg-surface-container-lowest p-4">
                <div className="font-label-mono text-label-mono text-on-surface font-bold mb-1">
                  R11 — Oyunlanabilirlik duyarlılığı
                </div>
                <p className="font-label-mono text-[10px] text-on-surface-variant mb-3">
                  %25 "iyileştirme" karşılığında ortalama AKS puan kazancı — yüksek olan, düşük çabayla en çok skor
                  satın alıyor demektir.
                </p>
                <div className="space-y-2">
                  {Object.entries(genelleme.oyunlanabilirlik_duyarliligi.sonuc)
                    .sort(([, a], [, b]) => b.ort_skor_kazanci - a.ort_skor_kazanci)
                    .map(([feat, s]) => (
                      <div key={feat}>
                        <div className="flex justify-between font-label-mono text-label-mono text-[11px] mb-0.5">
                          <span className="text-on-surface-variant">{feat}</span>
                          <span className={s.ort_skor_kazanci > 20 ? "text-error" : "text-on-surface"}>
                            +{s.ort_skor_kazanci}
                          </span>
                        </div>
                        <div className="h-1.5 w-full bg-surface-container-highest rounded-full overflow-hidden">
                          <div
                            className={`h-full ${s.ort_skor_kazanci > 20 ? "bg-error" : "bg-secondary-container"}`}
                            style={{ width: `${Math.min(100, Math.max(2, (s.ort_skor_kazanci / 100) * 100))}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
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
