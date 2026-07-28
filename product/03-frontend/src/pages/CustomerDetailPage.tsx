import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, PERSONA_ETIKET, type SkorSonuc, type GecmisKayit, type SimulasyonSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, DURUM_ETIKET, paraFormat } from "../lib/skor";

// §3b/U23 — /api/simulasyon'un kabul ettiği 9 özellik için kaydırıcı meta verisi.
// Aralıklar sentetik demo dağılımından (min/maks gözlemlenen değerler, biraz pay
// bırakılarak) türetildi — üretim/gerçek veri geldiğinde yeniden kalibre edilmeli.
const SENARYO_OZELLIKLERI: { kod: string; etiket: string; min: number; max: number; adim: number }[] = [
  { kod: "toplam_gelir_hacmi", etiket: "Toplam gelir hacmi (TL)", min: 0, max: 250000, adim: 1000 },
  { kod: "toplam_gider_hacmi", etiket: "Toplam gider hacmi (TL)", min: 0, max: 250000, adim: 1000 },
  { kod: "gelir_islem_sayisi", etiket: "Gelir işlem sayısı", min: 0, max: 30, adim: 1 },
  { kod: "gelir_kaynagi_sayisi", etiket: "Gelir kaynağı çeşitliliği", min: 0, max: 6, adim: 1 },
  { kod: "gelir_duzenliligi", etiket: "Gelir düzenliliği", min: 0, max: 1, adim: 0.05 },
  { kod: "gider_gelir_orani", etiket: "Gider/gelir oranı", min: 0, max: 4.5, adim: 0.05 },
  { kod: "bakiye_trendi", etiket: "Bakiye trendi (tasarruf eğilimi)", min: -35, max: 80, adim: 1 },
  { kod: "fatura_odeme_duzeni", etiket: "Fatura ödeme düzeni", min: 0, max: 1, adim: 0.05 },
  { kod: "hesap_hareket_yogunlugu", etiket: "Hesap hareket yoğunluğu", min: 0, max: 1.5, adim: 0.01 },
];

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_m_teri_detay_2
// ("AKS Terminal" — dairesel twin-score kartları, karar/limit şeridi, diverging
// SHAP çubukları, açılır-kapanır "Agent İzi" paneli). Stitch mockup'ının Agent
// İzi içeriği UYDURMAYDI (sahte tensor/ModelRunner log satırları, sahte
// imza) — o kısım burada GERÇEK pipeline iziyle (VeriAgent/SkorlamaAgent/
// DanismanAgent, gerçek risk_seviyesi/karar/danisman.ozet) dolduruldu, yalnızca
// görsel kabuk (açılır terminal-stili log paneli) korunuyor.
export default function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const musteriId = Number(id);

  const [sonuc, setSonuc] = useState<SkorSonuc | null>(null);
  const [gecmis, setGecmis] = useState<GecmisKayit[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");
  const [izAcik, setIzAcik] = useState(false);

  const [soru, setSoru] = useState("");
  const [yanit, setYanit] = useState<string | null>(null);
  const [soruYukleniyor, setSoruYukleniyor] = useState(false);

  // §3b/U23 — What-if senaryo simülatörü (POST /api/simulasyon)
  const [senaryoDegerler, setSenaryoDegerler] = useState<Record<string, number> | null>(null);
  const [simSonuc, setSimSonuc] = useState<SimulasyonSonuc | null>(null);
  const [simYukleniyor, setSimYukleniyor] = useState(false);
  const [simHata, setSimHata] = useState("");

  useEffect(() => {
    if (sonuc) setSenaryoDegerler(sonuc.ozellikler);
  }, [sonuc]);

  useEffect(() => {
    if (!sonuc || !senaryoDegerler) return;
    const degisen: Record<string, number> = {};
    for (const { kod } of SENARYO_OZELLIKLERI) {
      if (senaryoDegerler[kod] !== sonuc.ozellikler[kod]) degisen[kod] = senaryoDegerler[kod];
    }
    if (Object.keys(degisen).length === 0) {
      setSimSonuc(null);
      setSimHata("");
      return;
    }
    const zamanlayici = setTimeout(() => {
      setSimYukleniyor(true);
      setSimHata("");
      api
        .simulasyon(musteriId, degisen)
        .then(setSimSonuc)
        .catch((e) => setSimHata(String(e instanceof Error ? e.message : e)))
        .finally(() => setSimYukleniyor(false));
    }, 400);
    return () => clearTimeout(zamanlayici);
  }, [senaryoDegerler, sonuc, musteriId]);

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
    return <p className="font-body-md text-body-md text-on-surface-variant p-8">Yükleniyor…</p>;
  }

  if (hata || !sonuc) {
    return (
      <div className="border border-error/40 bg-error-container/20 text-error p-6 font-mono-label-sm text-mono-label-sm">
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
  const maxEtki = Math.max(
    0.01,
    ...sonuc.aciklama.riski_azaltan.map((f) => Math.abs(f.etki)),
    ...sonuc.aciklama.riski_artiran.map((f) => Math.abs(f.etki))
  );

  return (
    <div className="flex flex-col gap-stack-default pb-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-headline-lg font-headline-lg text-on-surface flex items-center gap-3">
            <Icon name="person" className="text-secondary" />
            Müşteri #{musteriId}
          </h1>
          <div className="flex gap-2 mt-2 flex-wrap items-center">
            <span className="text-mono-label-sm font-mono-label-sm text-secondary px-2 py-1 bg-secondary/10 border border-secondary/20">
              {PERSONA_ETIKET[sonuc.persona] ?? sonuc.persona}
            </span>
            {durum === "kurtarildi" && (
              <span className="text-mono-label-sm font-mono-label-sm text-secondary px-2 py-1 bg-secondary/10 border border-secondary/20 flex items-center gap-1">
                <Icon name="verified" className="text-[12px]" filled /> {DURUM_ETIKET[durum]}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {sonuc.anomali_bayrak && (
            <div
              className="border border-error-container bg-error-container/10 px-4 py-2 flex items-center gap-2"
              title={`Tipiklik skoru: ${sonuc.anomali_skoru} — negatife yaklaştıkça daha aykırı`}
            >
              <Icon name="warning" className="text-error" filled />
              <span className="text-mono-label-sm font-mono-label-sm font-bold text-error">ATİPİK PROFİL</span>
            </div>
          )}
          <Link
            to="/customers"
            className="px-4 py-2 border border-outline-variant font-mono-label-sm text-mono-label-sm text-on-surface hover:bg-surface-container transition-colors"
          >
            ← Kuyruğa Dön
          </Link>
        </div>
      </header>

      {sonuc.anomali_bayrak && (
        <p className="font-body-md text-body-md text-caveat max-w-2xl">
          Bu profil, eğitim dağılımının tipik aralığının dışında — skoru DEĞİŞTİRMEZ, yalnızca modele diğer
          profillere göre biraz daha az güvenilmesi gerektiğini işaret eder.
        </p>
      )}

      {/* Twin-Score Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
        <div className="bg-surface-container-low border border-outline-variant p-8 flex flex-col items-center justify-center relative">
          <div className="absolute top-4 left-4 text-mono-label-sm font-mono-label-sm text-on-surface-variant uppercase">
            Klasik Skor
          </div>
          <div className="w-40 h-40 rounded-full border-4 border-error/50 flex items-center justify-center mb-4">
            <span className="text-mono-score-lg font-mono-score-lg text-error">{sonuc.klasik_skor ?? "—"}</span>
          </div>
          <div className="text-mono-data-md font-mono-data-md text-on-surface-variant">
            {delta != null ? `AKS ile fark: ${delta >= 0 ? "+" : ""}${delta} pts` : "Klasik bant bilinmiyor"}
          </div>
        </div>
        <div className="bg-surface-container-low border border-outline-variant border-l-4 border-l-primary p-8 flex flex-col items-center justify-center relative">
          <div className="absolute top-4 left-4 text-mono-label-sm font-mono-label-sm text-primary uppercase">AKS Skoru</div>
          <div className="w-40 h-40 rounded-full border-4 border-primary flex items-center justify-center mb-4 shadow-[0_0_30px_rgba(195,192,255,0.2)]">
            <span className="text-mono-score-lg font-mono-score-lg text-primary">{sonuc.aks_skor}</span>
          </div>
          <div className="text-mono-data-md font-mono-data-md text-primary-container">{sonuc.risk_seviyesi}</div>
        </div>
      </section>

      {/* Karar & Limit */}
      <section className="bg-surface-container-low border border-secondary/50 p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Icon name="check_circle" className="text-secondary text-4xl" filled />
          <div>
            <div className="text-mono-label-sm font-mono-label-sm text-on-surface-variant uppercase">Karar Modülü Çıktısı</div>
            <div className="text-headline-md font-headline-md text-secondary">{sonuc.karar}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-mono-label-sm font-mono-label-sm text-on-surface-variant uppercase">Önerilen Limit</div>
          <div className="text-headline-lg font-headline-lg text-on-surface">{paraFormat(sonuc.onerilen_limit)}</div>
        </div>
      </section>

      {/* Formülasyon B (PD-gap) */}
      {sonuc.pd_fark != null && (
        <section className="bg-surface-container-low border border-outline-variant p-6 flex items-center justify-center gap-stack-default flex-wrap">
          <div className="text-center">
            <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">Geleneksel Bant PD</span>
            <span className="font-body-md text-body-md text-on-surface">{(sonuc.pd_geleneksel_bant! * 100).toFixed(1)}%</span>
          </div>
          <div className="text-center">
            <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">PD-Gap</span>
            <span className={`font-headline-md text-headline-md ${sonuc.pd_fark >= 0 ? "text-secondary" : "text-error"}`}>
              {sonuc.pd_fark >= 0 ? "+" : ""}
              {(sonuc.pd_fark * 100).toFixed(1)}pp
            </span>
          </div>
          <div className="text-center">
            <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">Kapasite Sinyali</span>
            <span className="font-body-md text-body-md text-primary">{sonuc.kapasite_sinyali}/100</span>
          </div>
          <p className="text-[10px] font-mono-label-sm text-on-surface-variant w-full text-center mt-1">
            Pozitif PD-Gap: davranışsal kanıt, geleneksel bandın ima ettiğinden daha fazla kapasite gösteriyor.
            Bankanın skorunu değiştirmez, yalnızca tamamlar.
          </p>
        </section>
      )}

      {/* SHAP Factor Bars */}
      <section className="bg-surface-container-low border border-outline-variant p-6">
        <h2 className="text-mono-data-md font-mono-data-md text-on-surface-variant mb-6 uppercase border-b border-outline-variant pb-2">
          Davranışsal Faktörler (SHAP Analizi)
        </h2>
        {/* Diverging çubuklar: konteyner ortadan ikiye bölünür, ortadaki
            dikey çizgi sıfır noktasıdır. Riski AZALTAN faktörler (negatif
            SHAP) soldan sıfıra doğru, riski ARTIRAN (pozitif) sıfırdan sağa
            uzar. `f.etki` zaten işaretli gelir (bkz. aciklama.py) — elle
            "+"/"-" eklemek "+-0.722" gibi çift işaret üretiyordu.
            Stitch mockup'ı burada `absolute right-full` kullanıyordu; o,
            çubuğu konteynerin TAMAMEN dışına (ekranın soluna) taşırıyordu —
            canlı denetimde görüldü, ikiye-bölme desenine geçildi (kurum
            müşteri detayındaki mockup'ın kendi çözümü). */}
        <div className="space-y-4">
          {sonuc.aciklama.riski_azaltan.map((f) => (
            <div className="flex items-center gap-4" key={f.kod}>
              <div className="w-1/3 text-mono-label-sm font-mono-label-sm text-on-surface text-right truncate" title={f.faktor}>
                {f.faktor}
              </div>
              <div className="flex-1 flex items-center">
                <div className="w-1/2 flex items-center justify-end border-r border-outline-variant h-6">
                  <span className="mr-2 text-mono-label-sm font-mono-label-sm text-shap-positive">{f.etki.toFixed(3)}</span>
                  <div
                    className="h-4 bg-shap-positive"
                    style={{ width: `${Math.min(90, (Math.abs(f.etki) / maxEtki) * 100)}%` }}
                  />
                </div>
                <div className="w-1/2" />
              </div>
            </div>
          ))}
          {sonuc.aciklama.riski_artiran.map((f) => (
            <div className="flex items-center gap-4" key={f.kod}>
              <div className="w-1/3 text-mono-label-sm font-mono-label-sm text-on-surface text-right truncate" title={f.faktor}>
                {f.faktor}
              </div>
              <div className="flex-1 flex items-center">
                <div className="w-1/2 border-r border-outline-variant h-6" />
                <div className="w-1/2 flex items-center">
                  <div
                    className="h-4 bg-shap-negative"
                    style={{ width: `${Math.min(90, (Math.abs(f.etki) / maxEtki) * 100)}%` }}
                  />
                  <span className="ml-2 text-mono-label-sm font-mono-label-sm text-shap-negative">+{f.etki.toFixed(3)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        {sonuc.danisman.oneriler.length > 0 && (
          <div className="mt-6 pt-6 border-t border-outline-variant">
            <h3 className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase tracking-wider mb-3">Öneriler</h3>
            <ul className="space-y-2">
              {sonuc.danisman.oneriler.map((o, i) => (
                <li key={i} className="font-body-md text-body-md text-on-surface-variant flex gap-2">
                  <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                  {o}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {/* Agent İzi Panel — GERÇEK pipeline izi (VeriAgent/SkorlamaAgent/DanismanAgent) */}
      <section className="bg-surface-container border border-outline-variant flex flex-col">
        <button
          onClick={() => setIzAcik((v) => !v)}
          className="w-full p-4 flex justify-between items-center bg-surface-dim hover:bg-surface-container-low transition-colors border-b border-outline-variant"
        >
          <div className="flex items-center gap-2 text-mono-label-sm font-mono-label-sm text-primary">
            <Icon name="terminal" className="text-sm" />
            <span>AGENT İZİ (PIPELINE LOGU)</span>
          </div>
          <Icon
            name="expand_more"
            className={`text-on-surface-variant transition-transform duration-200 ${izAcik ? "rotate-180" : ""}`}
          />
        </button>
        <div className={`agent-log ${izAcik ? "open" : ""} p-4 bg-surface-dim font-mono-data-md text-xs text-on-surface-variant`}>
          <div className="mb-2">
            <span className="text-secondary/80">VeriAgent</span> (pipeline aşaması) → 9 davranışsal özellik ham
            işlemlerden çıkarıldı.
          </div>
          <div className="mb-2">
            <span className="text-primary/80">SkorlamaAgent</span> (pipeline aşaması) → risk_seviyesi=
            {sonuc.risk_seviyesi}, karar={sonuc.karar}
          </div>
          <div className="mb-2">
            <span className="text-secondary/80">DanismanAgent</span> (şablonlu NLG) → {sonuc.danisman.ozet}
          </div>
          <div className="text-primary">&gt;&gt; Bu, değiştirilemez denetim iziyle otomatik olarak kaydedildi.</div>
        </div>
      </section>

      {/* What-If Simulator (§3b/U23) */}
      <section className="bg-surface-container-low border border-outline-variant p-6">
        <div className="w-full pb-4 mb-6 flex justify-between items-center flex-wrap gap-2 border-b border-outline-variant">
          <h2 className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase tracking-wider">
            Senaryo Simülatörü (What-If)
          </h2>
          <button
            onClick={() => sonuc && setSenaryoDegerler(sonuc.ozellikler)}
            className="px-3 py-1.5 border border-outline-variant font-mono-label-sm text-[10px] text-on-surface hover:bg-surface-container-high transition-colors"
          >
            Sıfırla
          </button>
        </div>
        <p className="font-body-md text-body-md text-on-surface-variant mb-6">
          Davranışsal özellikleri elle değiştirip skorun nasıl tepki verdiğini gözlemleyin —{" "}
          <code className="font-mono-data-md text-[11px] bg-surface-container-high px-1">POST /api/simulasyon</code>{" "}
          ile canlı model üzerinden hesaplanır (yeniden eğitim değil, aynı modelin farklı bir girdiyle tahmini). Bu,
          gerçek işlemleri değiştirmez; yalnızca "ne olurdu" sorusuna cevap verir.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5 mb-6">
          {senaryoDegerler &&
            SENARYO_OZELLIKLERI.map(({ kod, etiket, min, max, adim }) => (
              <div key={kod}>
                <div className="flex justify-between items-baseline mb-1">
                  <label className="font-mono-label-sm text-[11px] text-on-surface-variant">{etiket}</label>
                  <span className="font-mono-label-sm text-[11px] text-primary">
                    {senaryoDegerler[kod]?.toLocaleString("tr-TR")}
                  </span>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={adim}
                  value={senaryoDegerler[kod] ?? 0}
                  onChange={(e) => setSenaryoDegerler((prev) => ({ ...(prev ?? {}), [kod]: Number(e.target.value) }))}
                  className="w-full accent-primary-container"
                />
              </div>
            ))}
        </div>

        {simHata && (
          <div className="border border-error/40 bg-error-container/20 text-error p-3 font-body-md text-body-md mb-4">
            {simHata}
          </div>
        )}

        <div className="flex items-center justify-center gap-stack-default bg-surface-container p-6 border border-outline-variant flex-wrap">
          <div className="text-center">
            <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">Mevcut Skor</span>
            <span className="font-headline-lg text-headline-lg text-on-surface">{simSonuc?.mevcut_skor ?? sonuc.aks_skor}</span>
          </div>
          <Icon name="arrow_forward" className="text-outline" />
          <div className="text-center">
            <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">Senaryo Skoru</span>
            <span className="font-headline-lg text-headline-lg text-primary">
              {simYukleniyor ? "…" : (simSonuc?.senaryo_skor ?? sonuc.aks_skor)}
            </span>
          </div>
          {simSonuc && (
            <div className="text-center">
              <span className="text-[10px] font-mono-label-sm text-on-surface-variant uppercase block mb-1">Değişim</span>
              <span className={`font-headline-md text-headline-md ${simSonuc.skor_degisimi >= 0 ? "text-secondary" : "text-error"}`}>
                {simSonuc.skor_degisimi >= 0 ? "+" : ""}
                {simSonuc.skor_degisimi}
              </span>
              <span className="text-[10px] font-mono-label-sm text-on-surface-variant block mt-1">{simSonuc.senaryo_karar}</span>
            </div>
          )}
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
        {/* History */}
        <section className="bg-surface-container-low border border-outline-variant p-6">
          <h2 className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase tracking-wider mb-4">
            Değerlendirme Geçmişi
          </h2>
          {gecmis.length === 0 ? (
            <p className="font-body-md text-body-md text-on-surface-variant">Henüz kayıtlı geçmiş yok (ilk değerlendirme).</p>
          ) : (
            <ul className="space-y-2 font-mono-label-sm text-mono-label-sm">
              {gecmis.map((g, i) => (
                <li key={i} className="flex justify-between border-b border-outline-variant/30 pb-2">
                  <span className="text-on-surface-variant">{g.zaman}</span>
                  <span className="text-primary">AKS {g.aks_skor}</span>
                  <span className="text-on-surface-variant">{g.risk_seviyesi}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* AKS Assistant */}
        <section className="bg-surface-container-low border border-outline-variant p-6">
          <h2 className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
            <Icon name="smart_toy" className="text-sm" /> AKS Asistanı
          </h2>
          <div className="flex items-center gap-2 mb-4">
            <input
              value={soru}
              onChange={(e) => setSoru(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sorSor()}
              placeholder="Skoru nasıl yükseltirim?"
              className="flex-1 bg-surface border border-outline-variant rounded-DEFAULT px-3 py-2 font-body-md text-body-md text-on-surface focus:outline-none focus:border-primary"
            />
            <button
              onClick={sorSor}
              disabled={soruYukleniyor}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold hover:bg-primary-fixed transition-colors disabled:opacity-50"
            >
              {soruYukleniyor ? "…" : "Sor"}
            </button>
          </div>
          {yanit && <p className="font-body-md text-body-md text-on-surface-variant whitespace-pre-line">{yanit}</p>}
        </section>
      </div>
    </div>
  );
}
