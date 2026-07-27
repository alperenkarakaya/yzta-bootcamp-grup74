import { useEffect, useRef, useState } from "react";
import { useOutletContext } from "react-router-dom";
import {
  api,
  type CsvSkorSonuc,
  type KullaniciBilgisi,
  type PortalGecmisDetay,
  type PortalGecmisKayit,
} from "../../api";
import { Icon } from "../../components/Icon";
import { paraFormat } from "../../lib/skor";

const ORNEK_CSV = `tarih,islem_tipi,kategori,tutar,aciklama
2026-01-02,gelir,maas_odemesi,18000,Ocak maaşı
2026-01-09,gider,yeme_icme,-1400,market
2026-01-15,gider,ulasim,-850,otobüs
2026-01-29,gider,fatura,-900,elektrik
2026-02-02,gelir,maas_odemesi,18000,Şubat maaşı
2026-02-11,gider,fatura,-950,su
`;

function ornekIndir() {
  const blob = new Blob([ORNEK_CSV], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "aks_ornek_ekstre.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export default function PortalPage() {
  const kullanici = useOutletContext<KullaniciBilgisi>();

  const [dosya, setDosya] = useState<File | null>(null);
  const [suruklemede, setSuruklemede] = useState(false);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");
  const [sonuc, setSonuc] = useState<CsvSkorSonuc | null>(null);
  // §3b Phase 7/7.3 — zorunlu sahiplik beyanı: backend bu onay olmadan
  // yüklemeyi 400 ile reddeder (bkz. portal_views.py::portal_yukle).
  const [beyan, setBeyan] = useState(false);
  const girisRef = useRef<HTMLInputElement>(null);

  const [gecmis, setGecmis] = useState<PortalGecmisKayit[]>([]);
  const [gecmisYukleniyor, setGecmisYukleniyor] = useState(true);
  const [acikKayitId, setAcikKayitId] = useState<number | null>(null);
  const [detay, setDetay] = useState<PortalGecmisDetay | null>(null);
  const [detayYukleniyor, setDetayYukleniyor] = useState(false);

  function gecmisiYenile() {
    setGecmisYukleniyor(true);
    api
      .portalGecmis()
      .then((r) => setGecmis(r.gecmis))
      .catch(() => {})
      .finally(() => setGecmisYukleniyor(false));
  }

  useEffect(() => {
    gecmisiYenile();
  }, []);

  function kayitAcKapat(id: number) {
    if (acikKayitId === id) {
      setAcikKayitId(null);
      setDetay(null);
      return;
    }
    setAcikKayitId(id);
    setDetay(null);
    setDetayYukleniyor(true);
    api
      .portalGecmisDetay(id)
      .then(setDetay)
      .catch(() => setDetay(null))
      .finally(() => setDetayYukleniyor(false));
  }

  function dosyaSec(f: File | null) {
    setSonuc(null);
    setHata("");
    setDosya(f);
  }

  async function gonder() {
    if (!dosya || !beyan) return;
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    try {
      const r = await api.portalYukle(dosya, beyan);
      setSonuc(r);
      gecmisiYenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setYukleniyor(false);
    }
  }

  const BAYRAK_METNI: Record<string, string> = {
    coklu_sahiplik_supheli: "Bu ekstre içeriği başka bir hesap altında da yüklenmiş görünüyor.",
    profil_tutarsiz: "Bu yükleme, geçmiş yüklemelerinizden belirgin şekilde farklı bir gelir ölçeği gösteriyor.",
    pencere_uyumsuz: "Ekstre süresi, modelin eğitildiği ~6 aylık pencereden belirgin şekilde sapıyor.",
    dusuk_kategori_guveni: "İşlem kategorileri güvenle tahmin edilemedi — sonuç daha az kesin olabilir.",
    yuksek_atlanan_satir_orani: "Dosyadaki satırların önemli bir kısmı okunamadı.",
  };

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Merhaba, {kullanici.ad}</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kendi işlem ekstrenizi yükleyin, davranışsal kapasite skorunuzu görün — sonuçlar yalnızca size ait
          "Geçmişim" listesine kaydedilir.
        </p>
      </header>

      {/* Format bilgisi + upload */}
      <section className="card-surface rounded-lg p-6">
        <div className="flex justify-between items-start gap-4 flex-wrap mb-4">
          <div className="flex flex-wrap gap-2">
            {["tarih (YYYY-AA-GG)", "islem_tipi (gelir/gider)", "kategori", "tutar", "aciklama (opsiyonel)"].map((k) => (
              <span
                key={k}
                className="font-label-mono text-[11px] bg-surface-container-high border border-outline-variant/30 px-2 py-1 rounded-DEFAULT text-on-surface"
              >
                {k}
              </span>
            ))}
          </div>
          <button
            onClick={ornekIndir}
            className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
          >
            <Icon name="download" className="text-[16px]" />
            Örnek CSV indir
          </button>
        </div>

        <div
          className={`rounded-lg p-8 border-2 border-dashed transition-colors ${
            suruklemede ? "border-primary bg-primary-container/10" : "border-outline-variant/40"
          }`}
          onDragOver={(e) => {
            e.preventDefault();
            setSuruklemede(true);
          }}
          onDragLeave={() => setSuruklemede(false)}
          onDrop={(e) => {
            e.preventDefault();
            setSuruklemede(false);
            const f = e.dataTransfer.files?.[0];
            if (f) dosyaSec(f);
          }}
        >
          <input
            ref={girisRef}
            type="file"
            accept=".csv,text/csv,.xlsx,.xls,.pdf,application/pdf"
            className="hidden"
            onChange={(e) => dosyaSec(e.target.files?.[0] ?? null)}
          />
          <div className="flex flex-col items-center text-center gap-3">
            <Icon name="upload_file" className="text-5xl text-primary" />
            {dosya ? (
              <>
                <div className="font-body-sm text-body-sm text-on-surface font-semibold">{dosya.name}</div>
                <div className="font-label-mono text-[11px] text-on-surface-variant">
                  {(dosya.size / 1024).toFixed(1)} KB
                </div>
              </>
            ) : (
              <div className="font-body-sm text-body-sm text-on-surface">
                CSV, Excel ya da PDF ekstrenizi sürükleyin veya seçin
              </div>
            )}
            <div className="flex gap-3 mt-2">
              <button
                onClick={() => girisRef.current?.click()}
                className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
              >
                Dosya Seç
              </button>
              <button
                onClick={gonder}
                disabled={!dosya || !beyan || yukleniyor}
                className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40"
              >
                {yukleniyor ? "Analiz ediliyor…" : "Analiz Et"}
              </button>
            </div>
          </div>
        </div>

        {/* §3b Phase 7/7.3 — zorunlu sahiplik beyanı */}
        <label className="flex items-start gap-3 mt-4 px-1 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={beyan}
            onChange={(e) => setBeyan(e.target.checked)}
            className="mt-0.5 accent-primary"
          />
          <span className="font-body-sm text-body-sm text-on-surface-variant">
            Bu ekstrenin <strong className="text-on-surface">bana ait</strong> olduğunu onaylıyorum. AKS isim/kimlik
            bilgisi tutmaz; sahiplik yalnızca bu beyan + otomatik tutarlılık kontrolleriyle izlenir. Beyanınız, saati
            ve IP adresinizle birlikte bu analizin değiştirilemez denetim kaydına yazılır. (Kurumların verinize
            erişimi ayrı bir onaya tabidir — bkz.{" "}
            <a href="/portal/riza-defterim" className="text-primary underline">
              rıza defterim
            </a>
            .)
          </span>
        </label>
      </section>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      )}

      {sonuc && (
        <section className="grid grid-cols-1 md:grid-cols-12 gap-stack-md">
          {sonuc.anomali_bayrak && (
            <div className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2">
              <Icon name="warning" className="text-[16px] shrink-0" />
              Bu ekstre, eğitim dağılımının tipik aralığının dışında bir profil gösteriyor — skoru değiştirmez,
              yalnızca sonuca biraz daha az güvenilmesi gerektiğini işaret eder.
            </div>
          )}
          {/* §3b Phase 7/7.3 — sahiplik/kalite bayrakları: hepsi TESPİT amaçlı, karar mekanizmasını değiştirmez */}
          {[...(sonuc.sahiplik_bayraklari ?? []), ...(sonuc.belge_meta?.bayraklar ?? [])].map((b) => (
            <div
              key={b}
              className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2"
            >
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BAYRAK_METNI[b] ?? b}
            </div>
          ))}
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">AKS Skoru</span>
            <span className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_10px_rgba(195,192,255,0.5)]">
              {sonuc.aks_skor}
            </span>
            <span className="font-label-mono text-label-mono text-secondary mt-3">{sonuc.risk_seviyesi}</span>
            <span className="font-body-sm text-body-sm text-on-surface-variant mt-1">{sonuc.karar}</span>
          </div>
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center justify-center text-center">
            <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Önerilen Limit</span>
            <span className="font-display-sm text-display-sm text-on-background">{paraFormat(sonuc.onerilen_limit)}</span>
            <span className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              {sonuc.islem_sayisi} işlemden hesaplandı
            </span>
          </div>
          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-center">
            <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">{sonuc.danisman.ozet}</p>
          </div>
          <div className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Davranışsal Faktörler
            </h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {sonuc.aciklama.riski_azaltan.map((f) => (
                <div className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-emerald-400">OLUMLU</span>
                    <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
              {sonuc.aciklama.riski_artiran.map((f) => (
                <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-error">OLUMSUZ</span>
                    <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
            </div>
            {sonuc.danisman.oneriler.length > 0 && (
              <ul className="space-y-2 mt-6 pt-6 border-t border-outline-variant/20">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* §3b Phase 7/7.5 — belge_agent'ın çok-stratejili karar izi (gerçek agent kanıtı) */}
          {!!sonuc.belge_meta?.iz?.length && (
            <details className="col-span-1 md:col-span-12 bg-surface-container hairline-border rounded-xl p-6">
              <summary className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider cursor-pointer">
                Belge Agent İzi ({sonuc.belge_meta.kaynak_format?.toUpperCase()})
              </summary>
              <ol className="mt-4 space-y-1.5">
                {sonuc.belge_meta.iz.map((adim, i) => (
                  <li key={i} className="font-label-mono text-[11px] text-on-surface-variant flex gap-2">
                    <span className="text-primary shrink-0">{i + 1}.</span>
                    {adim}
                  </li>
                ))}
              </ol>
            </details>
          )}
        </section>
      )}

      {/* Geçmişim */}
      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Geçmişim
        </h2>
        {gecmisYukleniyor ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
        ) : gecmis.length === 0 ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir analiz yapmadınız.</p>
        ) : (
          <ul className="space-y-2 font-label-mono text-label-mono">
            {gecmis.map((g) => (
              <li key={g.id} className="border-b border-outline-variant/10 pb-2">
                <button
                  onClick={() => kayitAcKapat(g.id)}
                  className="w-full flex justify-between items-center flex-wrap gap-2 text-left hover:text-on-surface transition-colors"
                >
                  <span className="text-on-surface-variant">{g.zaman.replace("T", " ")}</span>
                  <span className="text-primary">AKS {g.aks_skor}</span>
                  <span className="text-on-surface-variant">{g.risk_seviyesi}</span>
                  <span className="text-on-surface">{paraFormat(g.onerilen_limit)}</span>
                  <span className="text-on-surface-variant flex items-center gap-1">
                    {g.islem_sayisi} işlem
                    <Icon
                      name={acikKayitId === g.id ? "expand_less" : "expand_more"}
                      className="text-[16px]"
                    />
                  </span>
                </button>
                {acikKayitId === g.id && (
                  <div className="mt-3 mb-1 bg-surface-container-low rounded-lg p-3 overflow-x-auto">
                    {detayYukleniyor ? (
                      <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
                    ) : !detay?.islemler.length ? (
                      <p className="font-body-sm text-body-sm text-on-surface-variant">
                        Bu kayıt için saklanmış işlem bulunamadı.
                      </p>
                    ) : (
                      <table className="w-full text-[11px]">
                        <thead>
                          <tr className="text-on-surface-variant border-b border-outline-variant/20">
                            <th className="text-left font-normal pb-1 pr-3">Tarih</th>
                            <th className="text-left font-normal pb-1 pr-3">Kategori</th>
                            <th className="text-left font-normal pb-1 pr-3">Açıklama</th>
                            <th className="text-right font-normal pb-1">Tutar</th>
                          </tr>
                        </thead>
                        <tbody>
                          {detay.islemler.map((i, idx) => (
                            <tr key={idx} className="border-b border-outline-variant/10 last:border-0">
                              <td className="py-1 pr-3 text-on-surface-variant whitespace-nowrap">{i.tarih}</td>
                              <td className="py-1 pr-3 text-on-surface-variant">{i.kategori}</td>
                              <td className="py-1 pr-3 text-on-surface-variant">{i.aciklama || "—"}</td>
                              <td
                                className={`py-1 text-right whitespace-nowrap ${
                                  i.tutar >= 0 ? "text-emerald-400" : "text-error"
                                }`}
                              >
                                {paraFormat(i.tutar)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
