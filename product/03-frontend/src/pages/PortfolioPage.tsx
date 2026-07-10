import { useEffect, useState } from "react";
import { api, PERSONA_ETIKET, type Portfoy, type Adalet } from "../api";
import { paraFormat } from "../lib/skor";

export default function PortfolioPage() {
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [hata, setHata] = useState("");

  useEffect(() => {
    Promise.all([api.portfoy(), api.adalet()])
      .then(([p, a]) => {
        setPortfoy(p);
        setAdalet(a);
      })
      .catch((e) => setHata(String(e)));
  }, []);

  const personalar = adalet ? Object.keys(adalet.aks_skor.gruplar) : [];

  return (
    <div className="flex flex-col gap-stack-lg">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="font-label-mono text-label-mono text-primary px-2 py-0.5 bg-primary-container/20 rounded-full border border-primary/30">
              LIVE
            </span>
            <span className="font-label-mono text-label-mono text-on-surface-variant opacity-60">
              /api/portfoy · /api/adalet
            </span>
          </div>
          <h1 className="font-display-lg text-display-lg tracking-tighter text-on-background">Portfolio Analysis</h1>
        </div>
        {portfoy && (
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="font-label-mono text-label-mono text-on-surface-variant">KURTARILAN</span>
              <span className="font-display-sm text-display-sm text-primary">
                {portfoy.kurtarilan}/{portfoy.kredibl_red}
              </span>
            </div>
            <div className="w-px h-10 bg-outline-variant/30 mx-2" />
            <div className="flex flex-col items-end">
              <span className="font-label-mono text-label-mono text-on-surface-variant">KURTARMA ORANI</span>
              <span className="font-display-sm text-display-sm text-secondary">
                {(portfoy.kurtarma_orani * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        )}
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-label-mono text-label-mono">
          Backend hatası: {hata}
        </div>
      )}

      <div className="grid grid-cols-12 gap-gutter">
        {/* Segment Alpha Comparison */}
        <section className="col-span-12 lg:col-span-8 bg-surface-container-low hairline-border rounded-xl overflow-hidden ai-glow flex flex-col min-h-[440px]">
          <div className="glass-header px-6 py-4 flex items-center justify-between">
            <div>
              <h3 className="font-headline-md text-headline-md">Segment Onay Karşılaştırması</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant">Klasik vs. Davranışsal onay oranı (persona bazında)</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-primary" />
                <span className="font-label-mono text-label-mono">Davranışsal (AKS)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-outline" />
                <span className="font-label-mono text-label-mono">Klasik</span>
              </div>
            </div>
          </div>
          <div className="flex-grow relative p-6">
            {adalet ? (
              <div className="absolute inset-6 flex items-end justify-between gap-6">
                {personalar.map((persona) => {
                  const klasik = adalet.klasik_skor.gruplar[persona]?.onay_orani ?? 0;
                  const aks = adalet.aks_skor.gruplar[persona]?.onay_orani ?? 0;
                  return (
                    <div className="w-full flex flex-col items-center justify-end group" key={persona}>
                      <div className="w-full flex items-end justify-center gap-1 h-56">
                        <div
                          className="w-1/2 bg-outline/30 rounded-t-sm relative group-hover:bg-outline/50 transition-all"
                          style={{ height: `${klasik * 100}%` }}
                        >
                          <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-label-mono text-[10px] opacity-0 group-hover:opacity-100 whitespace-nowrap">
                            {(klasik * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div
                          className="w-1/2 bg-gradient-to-t from-primary-container to-primary rounded-t-sm relative shadow-[0_0_10px_rgba(79,70,229,0.3)] group-hover:brightness-110 transition-all"
                          style={{ height: `${aks * 100}%` }}
                        >
                          <div className="absolute -top-6 left-1/2 -translate-x-1/2 font-label-mono text-[10px] opacity-0 group-hover:opacity-100 whitespace-nowrap">
                            {(aks * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      <span className="font-label-mono text-[10px] opacity-60 mt-2 text-center">
                        {PERSONA_ETIKET[persona] ?? persona}
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-on-surface-variant font-body-sm text-body-sm">Yükleniyor…</p>
            )}
          </div>
        </section>

        {/* Equal-opportunity gap */}
        <section className="col-span-12 lg:col-span-4 bg-surface-container-low hairline-border rounded-xl min-h-[440px] flex flex-col">
          <div className="glass-header px-6 py-4">
            <h3 className="font-headline-md text-headline-md">Eşit-Fırsat Boşluğu</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Δ Klasik vs. Davranışsal (equal opportunity gap)</p>
          </div>
          <div className="flex-grow p-6 flex flex-col justify-center items-center relative overflow-hidden">
            <div className="relative z-10 w-full aspect-square max-w-[240px]">
              <div className="absolute inset-0 rounded-full border border-primary/20" />
              <div className="absolute inset-4 rounded-full border border-primary/10" />
              <div className="absolute inset-12 rounded-full border border-primary/5" />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="font-display-sm text-display-sm text-on-background">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
                <span className="font-label-mono text-label-mono text-primary">AKS BOŞLUĞU</span>
              </div>
            </div>
            <div className="mt-8 w-full space-y-3 font-label-mono text-label-mono">
              <div className="flex justify-between">
                <span className="text-on-surface-variant">Klasik skor boşluğu</span>
                <span className="text-error">
                  {adalet ? adalet.klasik_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-on-surface-variant">AKS boşluğu</span>
                <span className="text-primary">
                  {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                </span>
              </div>
              <p className="text-[10px] text-on-surface-variant opacity-70 pt-2 leading-relaxed">
                Boşluk = kredibl onay oranının persona'lar arası max-min farkı. Düşük = adil. 0'a yakın gruplar
                arası eşit muamele anlamına gelir.
              </p>
            </div>
          </div>
        </section>

        {/* Alpha Segments Performance */}
        <section className="col-span-12 bg-surface-container hairline-border rounded-xl">
          <div className="glass-header px-6 py-4">
            <h3 className="font-headline-md text-headline-md">Segment Performansı</h3>
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Gerçek 4 davranışsal persona üzerinde kurtarma ve risk metrikleri.
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-outline-variant/30">
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">SEGMENT</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">N</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KLASİK ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">AKS ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KURTARMA ETKİSİ</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">YANLIŞ ONAY</th>
                  <th className="px-6 py-4 font-label-mono text-label-mono text-on-surface-variant opacity-70">KREDİBL TPR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {personalar.map((persona) => {
                  const k = adalet!.klasik_skor.gruplar[persona];
                  const a = adalet!.aks_skor.gruplar[persona];
                  const etki = (a.onay_orani - k.onay_orani) * 100;
                  return (
                    <tr className="hover:bg-surface-container-highest/50 transition-colors" key={persona}>
                      <td className="px-6 py-5 font-body-lg text-on-background">{PERSONA_ETIKET[persona] ?? persona}</td>
                      <td className="px-6 py-5 font-label-mono text-label-mono">{a.n}</td>
                      <td className="px-6 py-5 font-label-mono text-label-mono text-on-surface-variant">
                        {(k.onay_orani * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-5 font-label-mono text-label-mono text-primary">
                        {(a.onay_orani * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-5">
                        <span
                          className={`px-2 py-1 rounded font-label-mono text-label-mono border ${
                            etki >= 0
                              ? "bg-secondary/10 text-secondary border-secondary/20"
                              : "bg-error/10 text-error border-error/20"
                          }`}
                        >
                          {etki >= 0 ? "+" : ""}
                          {etki.toFixed(1)}%
                        </span>
                      </td>
                      <td className="px-6 py-5 font-label-mono text-label-mono">{(a.yanlis_onay_orani * 100).toFixed(1)}%</td>
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-surface-container-highest rounded-full">
                            <div className="h-full bg-primary rounded-full" style={{ width: `${a.kredibl_onay_orani_tpr * 100}%` }} />
                          </div>
                          <span className="font-label-mono text-label-mono">{(a.kredibl_onay_orani_tpr * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {portfoy && (
          <section className="col-span-12 bg-surface-container hairline-border rounded-xl p-6 flex flex-wrap gap-8 items-center justify-between">
            <div>
              <h3 className="font-headline-md text-headline-md mb-1">İllüstratif Getiri</h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant max-w-xl">
                Varsayımlar: ort. kredi {paraFormat(portfoy.illustratif_getiri.varsayimlar.ort_kredi)}, getiri oranı{" "}
                {(portfoy.illustratif_getiri.varsayimlar.getiri_orani * 100).toFixed(0)}%, zarar oranı{" "}
                {(portfoy.illustratif_getiri.varsayimlar.zarar_orani * 100).toFixed(0)}% — illüstratiftir, doğrulanmış
                gerçek para birimi tahmini değildir (bkz. architecture.md §5.1).
              </p>
            </div>
            <div className="flex gap-8">
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Potansiyel Kazanç</div>
                <div className="font-display-sm text-display-sm text-secondary">
                  {paraFormat(portfoy.illustratif_getiri.potansiyel_kazanc)}
                </div>
              </div>
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Beklenen Kayıp</div>
                <div className="font-display-sm text-display-sm text-error">
                  {paraFormat(portfoy.illustratif_getiri.beklenen_kayip)}
                </div>
              </div>
              <div className="text-center">
                <div className="font-label-mono text-label-mono text-on-surface-variant">Net</div>
                <div className="font-display-sm text-display-sm text-primary">{paraFormat(portfoy.illustratif_getiri.net)}</div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
