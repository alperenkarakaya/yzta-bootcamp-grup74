import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type KurumMusteriOzet } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kurum tarafı: AKS numarasıyla erişim talebi açar, müşteri
// onaylarsa burada listelenir. Rızası olmayan HİÇBİR müşteri burada görünmez
// (backend `izinler.aktif_riza()` ile zorlanır — bkz. kimlik/kurum_views.py).
export default function KurumMusterilerPage() {
  const [musteriler, setMusteriler] = useState<KurumMusteriOzet[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  const [aksNo, setAksNo] = useState("");
  const [amac, setAmac] = useState("");
  const [talepHata, setTalepHata] = useState("");
  const [talepMesaj, setTalepMesaj] = useState("");
  const [gonderiliyor, setGonderiliyor] = useState(false);

  function yenile() {
    setYukleniyor(true);
    api
      .kurumMusteriler()
      .then((r) => setMusteriler(r.musteriler))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function talepGonder(e: React.FormEvent) {
    e.preventDefault();
    setTalepHata("");
    setTalepMesaj("");
    setGonderiliyor(true);
    try {
      await api.kurumErisimTalebiOlustur(aksNo.trim().toUpperCase(), amac);
      setTalepMesaj("Talep gönderildi — müşterinin onayı bekleniyor.");
      setAksNo("");
      setAmac("");
    } catch (err) {
      setTalepHata(String(err instanceof Error ? err.message : err));
    } finally {
      setGonderiliyor(false);
    }
  }

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Müşteriler</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Yalnızca size erişim izni vermiş müşteriler burada görünür.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Yeni Erişim Talebi
        </h2>
        <form onSubmit={talepGonder} className="flex flex-col md:flex-row gap-3 items-end">
          <div className="flex-1 min-w-0">
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">AKS Numarası</label>
            <input
              value={aksNo}
              onChange={(e) => setAksNo(e.target.value)}
              placeholder="AKS-XXXX-XXXX-XC"
              required
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-label-mono text-label-mono text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
          <div className="flex-1 min-w-0">
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Amaç</label>
            <input
              value={amac}
              onChange={(e) => setAmac(e.target.value)}
              placeholder="kredi başvurusu değerlendirmesi"
              required
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
            />
          </div>
          <button
            type="submit"
            disabled={gonderiliyor}
            className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-40 shrink-0"
          >
            Talep Gönder
          </button>
        </form>
        {talepMesaj && <p className="font-label-mono text-[11px] text-emerald-400 mt-3">{talepMesaj}</p>}
        {talepHata && <p className="font-label-mono text-[11px] text-error mt-3">{talepHata}</p>}
      </section>

      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
          Aktif Erişimler
        </h2>
        {yukleniyor ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
        ) : musteriler.length === 0 ? (
          <p className="font-body-sm text-body-sm text-on-surface-variant">
            Henüz onaylanmış bir erişiminiz yok — yukarıdan talep gönderin.
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {musteriler.map((m) => (
              <Link
                key={m.aks_no}
                to={`/kurum/musteri/${m.aks_no}`}
                className="flex justify-between items-center bg-surface-container-low hairline-border rounded-lg p-4 hover:bg-surface-container-high transition-colors flex-wrap gap-2"
              >
                <div>
                  <div className="font-label-mono text-label-mono text-primary">{m.aks_no}</div>
                  <div className="font-body-sm text-body-sm text-on-surface-variant mt-0.5">{m.amac}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="font-label-mono text-[10px] text-on-surface-variant">
                    {m.gecerlilik_bitis.replace("T", " ").slice(0, 16)} kadar
                  </span>
                  <Icon name="chevron_right" className="text-on-surface-variant" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
