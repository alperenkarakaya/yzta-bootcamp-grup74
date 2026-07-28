import { useRef, useState } from "react";
import { api, type CsvSkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { paraFormat } from "../lib/skor";

const BELGE_BAYRAK_METNI: Record<string, string> = {
  pencere_uyumsuz: "Ekstre süresi, modelin eğitildiği ~6 aylık pencereden belirgin şekilde sapıyor.",
  dusuk_kategori_guveni: "İşlem kategorileri güvenle tahmin edilemedi — sonuç daha az kesin olabilir.",
  yuksek_atlanan_satir_orani: "Dosyadaki satırların önemli bir kısmı okunamadı.",
  bos_belge: "Belgeden hiç işlem çıkarılamadı.",
};

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

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_belge_y_kleme
// ("AKS Terminal" — geniş sürükle-bırak alanı + yanında beklenen şema paneli).
export default function CsvUploadPage() {
  const [dosya, setDosya] = useState<File | null>(null);
  const [suruklemede, setSuruklemede] = useState(false);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [hata, setHata] = useState("");
  const [sonuc, setSonuc] = useState<CsvSkorSonuc | null>(null);
  const girisRef = useRef<HTMLInputElement>(null);

  function dosyaSec(f: File | null) {
    setSonuc(null);
    setHata("");
    setDosya(f);
  }

  async function gonder() {
    if (!dosya) return;
    setYukleniyor(true);
    setHata("");
    setSonuc(null);
    try {
      const r = await api.csvSkorla(dosya);
      setSonuc(r);
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setYukleniyor(false);
    }
  }

  return (
    <div className="flex flex-col gap-stack-default pb-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-headline-lg font-headline-lg text-on-surface">Veri Enjeksiyonu</h1>
        <p className="text-body-md font-body-md text-on-surface-variant">
          Kendi işlem ekstrenizi (CSV, Excel ya da PDF) yükleyin — AKS aynı davranışsal model ile (dekuple/LR
          eğitimli) canlı bir skor üretir. Her istek{" "}
          <code className="font-mono-data-md text-[11px] bg-surface-container px-1">POST /api/csv-skorla</code>{" "}
          uç noktasına gider.
        </p>
      </header>

      {/* Upload & Schema */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
        <div
          className={`lg:col-span-2 bg-surface-container-low border-2 border-dashed rounded flex flex-col items-center justify-center p-12 text-center transition-colors cursor-pointer ${
            suruklemede ? "border-primary bg-primary-container/10" : "border-outline hover:border-primary-container"
          }`}
          onClick={() => girisRef.current?.click()}
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
          <Icon name="cloud_upload" className="text-4xl text-outline-variant mb-4" />
          {dosya ? (
            <>
              <p className="text-body-md font-body-md text-on-surface mb-1">{dosya.name}</p>
              <p className="text-mono-label-sm font-mono-label-sm text-outline">{(dosya.size / 1024).toFixed(1)} KB</p>
            </>
          ) : (
            <>
              <p className="text-body-md font-body-md text-on-surface text-center mb-2">
                Ekstrenizi buraya sürükleyin veya <span className="text-primary-container underline">göz atın</span>
              </p>
              <p className="text-mono-label-sm font-mono-label-sm text-outline">(CSV, XLSX, PDF) — Max 10MB</p>
            </>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              gonder();
            }}
            disabled={!dosya || yukleniyor}
            className="mt-6 px-6 py-2 bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold rounded-DEFAULT hover:bg-primary-fixed transition-colors disabled:opacity-40"
          >
            {yukleniyor ? "Skorlanıyor…" : "Skorla"}
          </button>
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded p-6 flex flex-col gap-6">
          <div>
            <h3 className="text-mono-label-sm font-mono-label-sm text-outline uppercase tracking-wider mb-4 border-b border-outline-variant pb-2">
              Beklenen Kolon Şeması
            </h3>
            <div className="flex flex-wrap gap-2">
              {["tarih (YYYY-AA-GG)", "islem_tipi (gelir/gider)", "kategori", "tutar", "aciklama (opsiyonel)"].map((k) => (
                <span
                  key={k}
                  className="px-2 py-1 bg-surface-dim border border-outline-variant rounded-DEFAULT text-mono-label-sm font-mono-label-sm text-on-surface"
                >
                  {k}
                </span>
              ))}
            </div>
            <p className="text-body-md font-body-md text-on-surface-variant mt-3">
              Gider tutarları <strong>negatif</strong> yazılmalı (örn. <code>-850</code>). En az 5 işlem gerekir.
              Excel/PDF'te kolonlar otomatik tanınır.
            </p>
          </div>
          <div className="mt-auto">
            <button
              onClick={ornekIndir}
              className="w-full py-2 bg-surface-dim border border-outline-variant rounded-DEFAULT text-mono-label-sm font-mono-label-sm text-on-surface hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2"
            >
              <Icon name="download" className="text-[16px]" />
              Örnek CSV İndir
            </button>
          </div>
        </div>
      </section>

      {hata && (
        <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-4 font-body-md text-body-md">
          {hata}
        </div>
      )}

      {sonuc && (
        <section className="flex flex-col gap-gutter">
          {sonuc.anomali_bayrak && (
            <div className="border caveat-banner text-caveat rounded p-4 flex gap-3 items-start">
              <Icon name="warning" className="shrink-0" filled />
              <p className="text-body-md font-body-md">
                Bu ekstre, İzolasyon Ormanı'na (denetimsiz OOD tespiti) göre eğitim dağılımının tipik aralığının
                dışında bir profil gösteriyor — skoru değiştirmez, yalnızca modele diğer profillere göre biraz daha
                az güvenilmesi gerektiğini işaret eder (tipiklik skoru: {sonuc.anomali_skoru}).
              </p>
            </div>
          )}
          {(sonuc.belge_meta?.bayraklar ?? []).map((b) => (
            <div key={b} className="border caveat-banner text-caveat rounded p-4 flex gap-3 items-start">
              <Icon name="warning" className="shrink-0" filled />
              <p className="text-body-md font-body-md">{BELGE_BAYRAK_METNI[b] ?? b}</p>
            </div>
          ))}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
            <div className="bg-surface-container-low border border-outline-variant rounded p-6 flex flex-col justify-center text-center">
              <span className="text-mono-label-sm font-mono-label-sm text-on-surface-variant mb-2">AKS Skoru</span>
              <span className="text-mono-score-lg font-mono-score-lg text-primary">{sonuc.aks_skor}</span>
              <span className="text-mono-label-sm font-mono-label-sm text-secondary mt-3">{sonuc.risk_seviyesi}</span>
              <span className="text-body-md font-body-md text-on-surface-variant mt-1">{sonuc.karar}</span>
            </div>

            <div className="bg-surface-container-low border border-outline-variant rounded p-6 flex flex-col justify-center text-center">
              <span className="text-mono-label-sm font-mono-label-sm text-on-surface-variant mb-2">Önerilen Limit</span>
              <span className="text-headline-lg font-headline-lg text-on-background">{paraFormat(sonuc.onerilen_limit)}</span>
              <span className="text-[10px] font-mono-label-sm text-on-surface-variant mt-3">
                {sonuc.islem_sayisi} işlemden hesaplandı
              </span>
            </div>

            <div className="bg-surface-container-low border border-outline-variant rounded p-6 flex flex-col justify-center">
              <p className="text-[10px] font-mono-label-sm text-on-surface-variant leading-relaxed">
                Bu yükleme yolunda banka/klasik skor bilinmiyor, bu yüzden Formülasyon B (PD-Gap / Kapasite Sinyali)
                hesaplanmaz — yalnızca demo müşterileri için (klasik skor bilindiğinde) üretilir.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
            <div className="lg:col-span-2 bg-surface-container-low border border-outline-variant rounded p-6">
              <h3 className="text-mono-label-sm font-mono-label-sm text-outline uppercase tracking-wider mb-6">
                Davranışsal Faktörler (SHAP)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sonuc.aciklama.riski_azaltan.map((f) => (
                  <div className="bg-surface-container border border-shap-positive/20 rounded-lg p-3" key={f.kod}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-mono-label-sm text-shap-positive">RİSKİ AZALTIR</span>
                      <span className="text-mono-label-sm font-mono-label-sm text-on-surface">{f.etki.toFixed(3)}</span>
                    </div>
                    <div className="text-body-md font-body-md text-on-background">{f.faktor}</div>
                  </div>
                ))}
                {sonuc.aciklama.riski_artiran.map((f) => (
                  <div className="bg-surface-container border border-shap-negative/20 rounded-lg p-3" key={f.kod}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-mono-label-sm text-shap-negative">RİSKİ ARTIRIR</span>
                      <span className="text-mono-label-sm font-mono-label-sm text-on-surface">+{f.etki.toFixed(3)}</span>
                    </div>
                    <div className="text-body-md font-body-md text-on-background">{f.faktor}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-surface-container-low border border-outline-variant rounded p-6">
              <h3 className="text-mono-label-sm font-mono-label-sm text-outline uppercase tracking-wider mb-4">
                Danışman Özeti
              </h3>
              <p className="text-body-md font-body-md text-on-surface-variant mb-4">{sonuc.danisman.ozet}</p>
              {sonuc.danisman.oneriler.length > 0 && (
                <ul className="space-y-2">
                  {sonuc.danisman.oneriler.map((o, i) => (
                    <li key={i} className="text-body-md font-body-md text-on-surface-variant flex gap-2">
                      <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                      {o}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {!!sonuc.belge_meta?.iz?.length && (
            <details className="bg-surface-container-low border border-outline-variant rounded p-6">
              <summary className="text-mono-label-sm font-mono-label-sm text-outline uppercase tracking-wider cursor-pointer">
                Belge Agent İzi ({sonuc.belge_meta.kaynak_format?.toUpperCase()})
              </summary>
              <ol className="mt-4 space-y-1.5">
                {sonuc.belge_meta.iz.map((adim, i) => (
                  <li key={i} className="text-[11px] font-mono-label-sm text-on-surface-variant flex gap-2">
                    <span className="text-primary shrink-0">{i + 1}.</span>
                    {adim}
                  </li>
                ))}
              </ol>
            </details>
          )}
        </section>
      )}
    </div>
  );
}
