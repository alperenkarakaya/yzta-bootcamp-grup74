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
    <div className="flex flex-col gap-stack-lg pb-8 max-w-4xl mx-auto">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Belge / Ekstre Yükleme</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kendi işlem ekstrenizi (CSV, Excel ya da PDF) yükleyin — AKS aynı davranışsal model ile (dekuple/LR
          eğitimli) canlı bir skor üretir. Bu yol demo popülasyonundan bağımsızdır; her istek{" "}
          <code className="font-label-mono text-[11px] bg-surface-container px-1 rounded">POST /api/csv-skorla</code>{" "}
          uç noktasına gider.
        </p>
      </header>

      {/* Format bilgisi */}
      <section className="card-surface rounded-lg p-6">
        <div className="flex justify-between items-start gap-4 flex-wrap">
          <div>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-2">
              CSV İçin Beklenen Kolonlar (Excel/PDF Otomatik Tanınır)
            </h2>
            <div className="flex flex-wrap gap-2">
              {["tarih (YYYY-AA-GG)", "islem_tipi (gelir/gider)", "kategori", "tutar", "aciklama (opsiyonel)"].map(
                (k) => (
                  <span
                    key={k}
                    className="font-label-mono text-[11px] bg-surface-container-high border border-outline-variant/30 px-2 py-1 rounded-DEFAULT text-on-surface"
                  >
                    {k}
                  </span>
                )
              )}
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-3">
              Gider tutarları <strong>negatif</strong> yazılmalı (örn. <code>-850</code>). En az 5 işlem gerekir.
            </p>
          </div>
          <button
            onClick={ornekIndir}
            className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
          >
            <Icon name="download" className="text-[16px]" />
            Örnek CSV indir
          </button>
        </div>
      </section>

      {/* Upload alanı */}
      <section
        className={`card-surface rounded-lg p-8 border-2 border-dashed transition-colors ${
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
            <>
              <div className="font-body-sm text-body-sm text-on-surface">
                CSV, Excel ya da PDF dosyasını buraya sürükleyin veya seçin
              </div>
              <div className="font-label-mono text-[11px] text-on-surface-variant">.csv / .xlsx / .pdf</div>
            </>
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
              disabled={!dosya || yukleniyor}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40"
            >
              {yukleniyor ? "Skorlanıyor…" : "Skorla"}
            </button>
          </div>
        </div>
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
              Bu ekstre, İzolasyon Ormanı'na (denetimsiz OOD tespiti) göre eğitim dağılımının tipik aralığının
              dışında bir profil gösteriyor — skoru değiştirmez, yalnızca modele diğer profillere göre biraz daha
              az güvenilmesi gerektiğini işaret eder (tipiklik skoru: {sonuc.anomali_skoru}).
            </div>
          )}
          {(sonuc.belge_meta?.bayraklar ?? []).map((b) => (
            <div
              key={b}
              className="col-span-1 md:col-span-12 bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2"
            >
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BELGE_BAYRAK_METNI[b] ?? b}
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
            <span className="font-display-sm text-display-sm text-on-background">
              {paraFormat(sonuc.onerilen_limit)}
            </span>
            <span className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              {sonuc.islem_sayisi} işlemden hesaplandı
            </span>
          </div>

          <div className="col-span-1 md:col-span-4 bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col justify-center">
            <p className="font-label-mono text-[10px] text-on-surface-variant leading-relaxed">
              Bu yükleme yolunda banka/klasik skor bilinmiyor, bu yüzden Formülasyon B (PD-Gap / Kapasite Sinyali)
              hesaplanmaz — yalnızca demo müşterileri için (klasik skor bilindiğinde) üretilir.
            </p>
          </div>

          <div className="col-span-1 md:col-span-8 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Davranışsal Faktörler (SHAP)
            </h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {sonuc.aciklama.riski_azaltan.map((f) => (
                <div
                  className="bg-surface-container-low border border-emerald-400/20 p-3 rounded-lg"
                  key={f.kod}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-emerald-400">RİSKİ AZALTIR</span>
                    <span className="font-label-mono text-label-mono text-on-surface">{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
              {sonuc.aciklama.riski_artiran.map((f) => (
                <div className="bg-surface-container-low border border-error/20 p-3 rounded-lg" key={f.kod}>
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-label-mono text-[10px] text-error">RİSKİ ARTIRIR</span>
                    <span className="font-label-mono text-label-mono text-on-surface">+{f.etki.toFixed(3)}</span>
                  </div>
                  <div className="font-body-sm text-body-sm text-on-background">{f.faktor}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-1 md:col-span-4 bg-surface-container hairline-border rounded-xl p-6">
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Danışman Özeti
            </h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mb-4">{sonuc.danisman.ozet}</p>
            {sonuc.danisman.oneriler.length > 0 && (
              <ul className="space-y-2">
                {sonuc.danisman.oneriler.map((o, i) => (
                  <li key={i} className="font-body-sm text-body-sm text-on-surface-variant flex gap-2">
                    <Icon name="arrow_right" className="text-primary text-sm shrink-0" />
                    {o}
                  </li>
                ))}
              </ul>
            )}
          </div>

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
    </div>
  );
}
