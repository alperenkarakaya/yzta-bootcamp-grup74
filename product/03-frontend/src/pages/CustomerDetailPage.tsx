import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, PERSONA_ETIKET, type SkorSonuc, type GecmisKayit } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, paraFormat } from "../lib/skor";

export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const musteriId = Number(id);

  const [sonuc, setSonuc] = useState<SkorSonuc | null>(null);
  const [gecmis, setGecmis] = useState<GecmisKayit[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");

  const [soru, setSoru] = useState("");
  const [yanit, setYanit] = useState<string | null>(null);
  const [soruYukleniyor, setSoruYukleniyor] = useState(false);

  useEffect(() => {
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    setYanit(null);
    Promise.all([api.skorlaDemo(musteriId), api.gecmis(musteriId).catch(() => null)])
      .then(([s, g]) => {
        setSonuc(s);
        setGecmis(g?.gecmis ?? []);
      })
      .catch((e) => setHata(String(e)))
      .finally(() => setYukleniyor(false));
  }, [musteriId]);

  async function sorSor() {
    if (!soru.trim() || !sonuc) return;
    setSoruYukleniyor(true);
    try {
      const r = await api.asistan(soru, {
        aks_skor: sonuc.aks_skor,
        klasik_skor: sonuc.klasik_skor,
        risk_seviyesi: sonuc.risk_seviyesi,
        onerilen_limit: sonuc.onerilen_limit,
        aciklama: sonuc.aciklama,
        danisman: sonuc.danisman,
      });
      setYanit(r.yanit);
    } catch (e) {
      setYanit(`Hata: ${e}`);
    } finally {
      setSoruYukleniyor(false);
    }
  }

  if (yukleniyor) {
    return <p className="font-body-sm text-body-sm text-on-surface-variant p-8">Yükleniyor…</p>;
  }

  if (hata || !sonuc) {
    return (
      <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-6 font-label-mono text-label-mono">
        Müşteri #{musteriId} bulunamadı ya da backend'e ulaşılamadı: {hata}
        <div className="mt-4">
          <Link to="/customers" className="text-primary hover:underline">
            ← Müşteri kuyruğuna dön
          </Link>
        </div>
      </div>
    );
  }

  const durum = durumBelirle(sonuc.klasik_skor, sonuc.aks_skor);
  const delta = sonuc.klasik_skor != null ? sonuc.aks_skor - sonuc.klasik_skor : null;

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-stack-md hairline-border bg-surface-container-low p-6 rounded-xl">
        <div className="flex items-center gap-6">
          <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center border border-outline-variant/50 relative">
            <Icon name="person" className="text-4xl text-secondary" />
          </div>
          <div>
            <h1 className="font-headline-md text-headline-md md:font-display-sm md:text-display-sm text-on-background">
              Müşteri #{musteriId}
            </h1>
            <div className="flex gap-4 mt-2 flex-wrap">
              <span className="font-label-mono text-label-mono text-secondary px-2 py-1 bg-secondary/10 rounded-DEFAULT border border-secondary/20">
                {PERSONA_ETIKET[sonuc.persona] ?? sonuc.persona}
              </span>
              {durum === "kurtarildi" && (
                <span className="font-label-mono text-label-mono text-emerald-400 px-2 py-1 bg-emerald-400/10 rounded-DEFAULT border border-emerald-400/20 flex items-center gap-1">
                  <Icon name="verified" className="text-[12px]" /> {DURUM_ETIKET[durum]}
                </span>
              )}
            </div>
          </div>
        </div>
        <Link
          to="/customers"
          className="px-4 py-2 bg-transparent border border-outline-variant/50 rounded-DEFAULT font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
        >
          ← Kuyruğa Dön
        </Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-stack-md">
        {/* Calibration Map */}
        <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6 relative overflow-hidden ai-glow flex flex-col justify-between">
          <div className="glass-header absolute top-0 left-0 w-full p-4 flex justify-between items-center z-10">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Kalibrasyon Haritası</h2>
            <Icon name="radar" className="text-primary-fixed-dim" />
          </div>
          <div className="mt-12 flex-1 flex flex-col items-center justify-center relative">
            <div className="flex items-center justify-center gap-stack-lg w-full relative z-20">
              <div className="text-center">
                <span className="font-label-mono text-label-mono text-on-surface-variant block mb-2">Klasik Skor</span>
                <span className="font-display-lg text-display-lg text-error">{sonuc.klasik_skor ?? "—"}</span>
              </div>
              <div className="h-[2px] w-32 bg-gradient-to-r from-error/50 via-outline-variant/50 to-primary/50 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-surface-container px-2">
                  <Icon name="arrow_forward" className="text-outline" />
                </div>
              </div>
              <div className="text-center">
                <span className="font-label-mono text-label-mono text-on-surface-variant block mb-2">AKS Skoru</span>
                <span className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_10px_rgba(195,192,255,0.5)]">
                  {sonuc.aks_skor}
                </span>
                <span className="font-body-sm text-body-sm text-primary/80 block mt-1">
                  {delta != null ? `${delta >= 0 ? "+" : ""}${delta} pts` : ""}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Suggested Limit */}
        <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 border-b border-outline-variant/20 pb-2">
              Önerilen Limit
            </h2>
            <div className="mt-8 text-center">
              <span className="font-label-mono text-label-mono text-secondary mb-2 block">{sonuc.karar}</span>
              <div className="font-display-sm text-display-sm text-on-background">{paraFormat(sonuc.onerilen_limit)}</div>
            </div>
          </div>
          <p className="mt-8 text-center font-label-mono text-[10px] text-on-surface-variant">
            Bu değerlendirme /api/skorla/{musteriId} ile denetim izine (AuditLog) otomatik kaydedildi.
          </p>
        </div>

        {/* Pipeline Trace */}
        <div className="col-span-1 md:col-span-4 bg-surface-container hairline-border rounded-xl p-6">
          <div className="glass-header w-full pb-4 mb-4 flex justify-between items-center">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Pipeline İzi</h2>
            <Icon name="account_tree" className="text-on-surface-variant text-sm" />
          </div>
          <div className="relative pl-6 border-l border-outline-variant/30 space-y-6">
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-secondary rounded-full" />
              <div className="font-label-mono text-label-mono text-secondary">VeriAgent (pipeline aşaması)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
                9 davranışsal özellik ham işlemlerden çıkarıldı.
              </p>
            </div>
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-primary-container rounded-full" />
              <div className="font-label-mono text-label-mono text-primary">SkorlamaAgent (pipeline aşaması)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
                Risk seviyesi: {sonuc.risk_seviyesi}. Karar: {sonuc.karar}.
              </p>
            </div>
            <div className="relative">
              <div className="absolute -left-[31px] top-1 w-3 h-3 bg-emerald-400 rounded-full" />
              <div className="font-label-mono text-label-mono text-emerald-400">DanismanAgent (şablonlu)</div>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">{sonuc.danisman.ozet}</p>
            </div>
          </div>
        </div>

        {/* SHAP */}
        <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6">
          <div className="glass-header w-full pb-4 mb-6 flex justify-between items-center">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">Davranışsal Faktörler (SHAP)</h2>
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {sonuc.aciklama.riski_azaltan.map((f) => (
              <div className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg hover:border-emerald-400/50 transition-colors" key={f.kod}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-label-mono text-[10px] text-emerald-400">AZALTAN</span>
                  <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                </div>
                <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
              </div>
            ))}
            {sonuc.aciklama.riski_artiran.map((f) => (
              <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg hover:border-error/50 transition-colors" key={f.kod}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-label-mono text-[10px] text-error">ARTIRAN</span>
                  <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                </div>
                <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
              </div>
            ))}
          </div>
          {sonuc.danisman.oneriler.length > 0 && (
            <div className="mt-6 pt-6 border-t border-outline-variant/20">
              <h3 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-3">Öneriler</h3>
              <ul className="space-y-2">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* History */}
        <div className="col-span-1 md:col-span-6 bg-surface-container hairline-border rounded-xl p-6">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">Değerlendirme Geçmişi</h2>
          {gecmis.length === 0 ? (
            <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz kayıtlı geçmiş yok (ilk değerlendirme).</p>
          ) : (
            <ul className="space-y-2 font-label-mono text-label-mono">
              {gecmis.map((g, i) => (
                <li key={i} className="flex justify-between border-b border-outline-variant/10 pb-2">
                  <span className="text-on-surface-variant">{g.zaman}</span>
                  <span className="text-primary">AKS {g.aks_skor}</span>
                  <span className="text-on-surface-variant">{g.risk_seviyesi}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* AKS Assistant */}
        <div className="col-span-1 md:col-span-6 bg-surface-container hairline-border rounded-xl p-6">
          <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
            <Icon name="smart_toy" className="text-sm" /> AKS Asistanı
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <input
              value={soru}
              onChange={(e) => setSoru(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sorSor()}
              placeholder="Skoru nasıl yükseltirim?"
              className="flex-1 bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
            <button
              onClick={sorSor}
              disabled={soruYukleniyor}
              className="px-4 py-2 rounded bg-primary-container text-on-primary-container font-label-mono text-label-mono hover:brightness-110 transition-all disabled:opacity-50"
            >
              {soruYukleniyor ? "…" : "Sor"}
            </button>
          </div>
          {yanit && <p className="font-body-sm text-body-sm text-on-surface-variant whitespace-pre-line">{yanit}</p>}
        </div>
      </div>
    </div>
  );
}
