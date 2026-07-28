import { useEffect, useState } from "react";
import { api, PERSONA_ETIKET, type Portfoy, type Adalet } from "../api";
import { Icon } from "../components/Icon";
import { paraFormat } from "../lib/skor";

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portf_y_analizi.
// Stitch mockup'ı sabit/uydurma sayılar (538 kurtarılan, 13.4M TL, sabit
// %12/%34 segment oranları) gösteriyordu — burada TAMAMI gerçek `/api/portfoy`
// + `/api/adalet` verisiyle besleniyor. Eşik kaydırıcıları (mockup'ta yalnızca
// görsel, hiçbir yere bağlı değildi) gerçekten `api.portfoy(esikler)`'i yeniden
// çağırıyor — backend zaten `klasik_esik`/`aks_esik` query param'larını
// destekliyordu, önceden frontend'de hiç kullanılmıyordu.
//
// Eşit-fırsat boşluğu radyal göstergesi + tam segment performans tablosu +
// illüstratif getiri dökümü — Stitch'in sadeleştirilmiş mockup'ında YOK, ama
// gerçek, çalışan fonksiyonellik ve başka hiçbir ekranda karşılığı yok; aynı
// tasarım diliyle korunuyor (silinmedi).
export default function PortfolioPage() {
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [adalet, setAdalet] = useState<Adalet | null>(null);
  const [hata, setHata] = useState("");
  const [calisiyor, setCalisiyor] = useState(false);

  const [klasikEsik, setKlasikEsik] = useState(680);
  const [aksEsik, setAksEsik] = useState(650);

  async function yukle(esikler?: { klasik_esik: number; aks_esik: number }) {
    setCalisiyor(true);
    try {
      const [p, a] = await Promise.all([api.portfoy(esikler), api.adalet(esikler)]);
      setPortfoy(p);
      setAdalet(a);
      setHata("");
    } catch (e) {
      setHata(String(e));
    } finally {
      setCalisiyor(false);
    }
  }

  useEffect(() => {
    yukle();
  }, []);

  const personalar = adalet ? Object.keys(adalet.aks_skor.gruplar) : [];

  return (
    <div className="flex flex-col gap-stack-default">
      <header>
        <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tighter">Portföy Analizi</h1>
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-1 opacity-70">
          /api/portfoy · /api/adalet
        </p>
      </header>

      {hata && (
        <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-3 font-body-md text-body-md">
          Backend hatası: {hata}
        </div>
      )}

      {portfoy?.veri_kaynagi === "dongusel" && (
        <div className="border caveat-banner text-caveat px-container-padding py-3 flex items-center gap-3">
          <Icon name="warning" filled />
          <span className="font-mono-label-sm text-mono-label-sm uppercase tracking-wider">
            Dikkat: {portfoy.uyari}
          </span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        {/* Left Column: Controls */}
        <div className="md:col-span-4 flex flex-col gap-stack-default">
          <div className="bg-surface-container-low border border-outline-variant p-container-padding flex flex-col gap-6">
            <h2 className="font-headline-md text-headline-md text-on-surface">Simülasyon Parametreleri</h2>

            <div className="flex flex-col gap-2">
              <div className="flex justify-between items-end">
                <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Klasik Skor Eşiği</label>
                <span className="font-mono-data-md text-mono-data-md text-on-surface">{klasikEsik}</span>
              </div>
              <input
                type="range"
                min={300}
                max={850}
                value={klasikEsik}
                onChange={(e) => setKlasikEsik(Number(e.target.value))}
                className="w-full accent-primary-container"
              />
              <div className="flex justify-between text-on-surface-variant opacity-50 font-mono-label-sm text-[10px]">
                <span>300</span>
                <span>850</span>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex justify-between items-end">
                <label className="font-mono-label-sm text-mono-label-sm text-primary">AKS Skor Eşiği</label>
                <span className="font-mono-data-md text-mono-data-md text-primary">{aksEsik}</span>
              </div>
              <input
                type="range"
                min={300}
                max={850}
                value={aksEsik}
                onChange={(e) => setAksEsik(Number(e.target.value))}
                className="w-full accent-primary-container"
              />
              <div className="flex justify-between text-on-surface-variant opacity-50 font-mono-label-sm text-[10px]">
                <span>300</span>
                <span>850</span>
              </div>
            </div>

            <button
              onClick={() => yukle({ klasik_esik: klasikEsik, aks_esik: aksEsik })}
              disabled={calisiyor}
              className="mt-4 bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold py-2 px-4 border border-primary-container hover:bg-transparent hover:text-primary-container transition-colors duration-200 disabled:opacity-50"
            >
              {calisiyor ? "ÇALIŞIYOR…" : "SİMÜLASYONU ÇALIŞTIR"}
            </button>
          </div>

          {/* Equal-opportunity gap */}
          <div className="bg-surface-container-low border border-outline-variant flex flex-col">
            <div className="px-container-padding py-4 border-b border-outline-variant">
              <h3 className="font-headline-md text-headline-md text-on-surface">Eşit-Fırsat Boşluğu</h3>
              <p className="font-body-md text-body-md text-on-surface-variant">Δ Klasik vs. Davranışsal</p>
            </div>
            <div className="p-6 flex flex-col items-center gap-4">
              <div className="relative w-full aspect-square max-w-[180px]">
                <div className="absolute inset-0 rounded-full border border-primary/20" />
                <div className="absolute inset-4 rounded-full border border-primary/10" />
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span className="font-mono-score-lg text-mono-score-lg text-on-surface text-[28px]">
                    {adalet ? adalet.aks_skor.equal_opportunity_boslugu.toFixed(3) : "—"}
                  </span>
                  <span className="font-mono-label-sm text-mono-label-sm text-primary">AKS BOŞLUĞU</span>
                </div>
              </div>
              <div className="w-full space-y-2 font-mono-label-sm text-mono-label-sm">
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
              </div>
              <p className="text-[10px] font-mono-label-sm text-on-surface-variant opacity-70 leading-relaxed">
                Boşluk = kredibl onay oranının persona'lar arası max-min farkı. 0'a yakın = gruplar arası daha eşit
                muamele.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="md:col-span-8 flex flex-col gap-stack-default">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
            <div className="bg-surface-container-low border border-outline-variant p-container-padding flex flex-col justify-between min-h-[120px]">
              <span className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase">
                Kurtarılan Müşteri
              </span>
              <div className="flex items-baseline gap-2">
                <span className="font-mono-score-lg text-mono-score-lg text-secondary">
                  {portfoy ? portfoy.kurtarilan : "—"}
                </span>
                <span className="font-mono-label-sm text-mono-label-sm text-secondary">
                  {portfoy ? `/ ${portfoy.kredibl_red} (%${(portfoy.kurtarma_orani * 100).toFixed(1)})` : ""}
                </span>
              </div>
            </div>
            <div className="bg-surface-container-low border-l-2 border-l-primary border-y border-r border-outline-variant p-container-padding flex flex-col justify-between min-h-[120px]">
              <span className="font-mono-label-sm text-mono-label-sm text-primary uppercase">Tahmini Ek Getiri (net)</span>
              <div className="flex items-baseline gap-2">
                <span className="font-mono-score-lg text-mono-score-lg text-primary">
                  {portfoy ? paraFormat(portfoy.illustratif_getiri.net) : "—"}
                </span>
              </div>
            </div>
          </div>

          {/* Segment Comparison */}
          <div className="bg-surface-container-low border border-outline-variant p-container-padding">
            <h3 className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase mb-6 border-b border-outline-variant pb-2">
              Segment Bazlı Onay Oranları (Klasik vs AKS)
            </h3>
            {adalet ? (
              <div className="flex flex-col gap-6">
                {personalar.map((persona) => {
                  const klasik = adalet.klasik_skor.gruplar[persona]?.onay_orani ?? 0;
                  const aks = adalet.aks_skor.gruplar[persona]?.onay_orani ?? 0;
                  const delta = Math.max(0, aks - klasik);
                  return (
                    <div className="flex flex-col gap-1" key={persona}>
                      <div className="flex justify-between font-mono-label-sm text-mono-label-sm">
                        <span className="text-on-surface">{PERSONA_ETIKET[persona] ?? persona}</span>
                        <span className="text-on-surface-variant">
                          K: {(klasik * 100).toFixed(0)}% | <span className="text-primary">A: {(aks * 100).toFixed(0)}%</span>
                        </span>
                      </div>
                      <div className="relative w-full h-4 bg-surface-container-highest border border-outline-variant">
                        <div className="absolute left-0 top-0 h-full bg-outline-variant" style={{ width: `${klasik * 100}%` }} />
                        <div
                          className="absolute top-0 h-full bg-primary/40 border-l border-primary"
                          style={{ left: `${klasik * 100}%`, width: `${delta * 100}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-on-surface-variant font-body-md text-body-md">Yükleniyor…</p>
            )}
            <div className="mt-8 flex gap-4 font-mono-label-sm text-mono-label-sm text-on-surface-variant">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-outline-variant border border-outline-variant" /> Klasik Model Onayı
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-primary/40 border-l border-primary" /> AKS Ek Onay Kapasitesi
              </div>
            </div>
          </div>

          {/* Full Segment Performance Table */}
          <div className="bg-surface-container border border-outline-variant">
            <div className="px-container-padding py-4">
              <h3 className="font-headline-md text-headline-md text-on-surface">Segment Performansı</h3>
              <p className="font-body-md text-body-md text-on-surface-variant">
                Gerçek 4 davranışsal persona üzerinde kurtarma ve risk metrikleri.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-outline-variant zebra-row">
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">SEGMENT</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">N</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">KLASİK ONAY</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">AKS ONAY</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">KURTARMA ETKİSİ</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">YANLIŞ ONAY</th>
                    <th className="px-4 py-3 font-mono-label-sm text-mono-label-sm text-on-surface-variant">KREDİBL TPR</th>
                  </tr>
                </thead>
                <tbody className="font-mono-data-md text-mono-data-md">
                  {personalar.map((persona) => {
                    const k = adalet!.klasik_skor.gruplar[persona];
                    const a = adalet!.aks_skor.gruplar[persona];
                    const etki = (a.onay_orani - k.onay_orani) * 100;
                    return (
                      <tr className="zebra-row hover:bg-white/5 transition-colors border-b border-outline-variant/30" key={persona}>
                        <td className="px-4 py-3 font-body-md text-on-surface">{PERSONA_ETIKET[persona] ?? persona}</td>
                        <td className="px-4 py-3">{a.n}</td>
                        <td className="px-4 py-3 text-on-surface-variant">{(k.onay_orani * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-primary">{(a.onay_orani * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2 py-1 rounded-DEFAULT border ${
                              etki >= 0 ? "bg-secondary/10 text-secondary border-secondary/20" : "bg-error/10 text-error border-error/20"
                            }`}
                          >
                            {etki >= 0 ? "+" : ""}
                            {etki.toFixed(1)}%
                          </span>
                        </td>
                        <td className="px-4 py-3">{(a.yanlis_onay_orani * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-surface-container-highest">
                              <div className="h-full bg-primary" style={{ width: `${a.kredibl_onay_orani_tpr * 100}%` }} />
                            </div>
                            <span>{(a.kredibl_onay_orani_tpr * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {portfoy && (
            <div className="bg-surface-container border border-outline-variant p-container-padding flex flex-wrap gap-8 items-center justify-between">
              <div>
                <h3 className="font-headline-md text-headline-md text-on-surface mb-1">İllüstratif Getiri</h3>
                <p className="font-body-md text-body-md text-on-surface-variant max-w-xl">
                  Varsayımlar: ort. kredi {paraFormat(portfoy.illustratif_getiri.varsayimlar.ort_kredi)}, getiri
                  oranı {(portfoy.illustratif_getiri.varsayimlar.getiri_orani * 100).toFixed(0)}%, zarar oranı{" "}
                  {(portfoy.illustratif_getiri.varsayimlar.zarar_orani * 100).toFixed(0)}% — illüstratiftir,
                  doğrulanmış gerçek para birimi tahmini değildir.
                </p>
              </div>
              <div className="flex gap-8">
                <div className="text-center">
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Potansiyel Kazanç</div>
                  <div className="font-headline-md text-headline-md text-secondary">
                    {paraFormat(portfoy.illustratif_getiri.potansiyel_kazanc)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Beklenen Kayıp</div>
                  <div className="font-headline-md text-headline-md text-error">
                    {paraFormat(portfoy.illustratif_getiri.beklenen_kayip)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Net</div>
                  <div className="font-headline-md text-headline-md text-primary">
                    {paraFormat(portfoy.illustratif_getiri.net)}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
