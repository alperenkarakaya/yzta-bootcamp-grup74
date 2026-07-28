import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type KurumMusteriOzet } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kurum tarafı: AKS numarasıyla erişim talebi açar, müşteri
// onaylarsa burada listelenir. Rızası olmayan HİÇBİR müşteri burada görünmez
// (backend `izinler.aktif_riza()` ile zorlanır — bkz. kimlik/kurum_views.py).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_m_teriler
// ("B2B Staff Portal" — sol sütun talep formu + sağ sütun aktif erişim
// tablosu). Mockup'ın 5 sahte satırı (Ahmet Yılmaz vb.) yerine gerçek
// `musteriler` listesi kullanılıyor; "filter_list" butonu gibi hiçbir yere
// bağlı olmayan süs butonlar eklenmedi, "refresh" gerçekten `yenile()`'yi
// çağırıyor.
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
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
      {/* Left Column: Access Request Form */}
      <section className="lg:col-span-4 flex flex-col gap-gutter">
        <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-grid-margin flex flex-col gap-stack-default">
          <h2 className="font-headline-md text-headline-md text-on-surface mb-stack-compact">Yeni Erişim Talebi</h2>
          <p className="font-body-md text-body-md text-on-surface-variant mb-stack-default">
            Müşteri verilerine erişim sağlamak için onay talebi gönderin. Bu işlem, müşterinin kendi portalına bir
            onay bildirimi iletecektir.
          </p>
          <form onSubmit={talepGonder} className="flex flex-col gap-stack-default">
            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-outline" htmlFor="aksNumber">
                AKS Numarası
              </label>
              <input
                id="aksNumber"
                value={aksNo}
                onChange={(e) => setAksNo(e.target.value)}
                pattern="AKS-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{2}"
                placeholder="AKS-XXXX-XXXX-XC"
                required
                className="bg-surface-dim border border-outline-variant rounded-DEFAULT px-3 py-2 font-mono-data-md text-mono-data-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors"
              />
              <span className="font-mono-label-sm text-mono-label-sm text-on-surface-variant text-[10px]">
                Format: AKS-XXXX-XXXX-XC
              </span>
            </div>
            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-outline" htmlFor="statedPurpose">
                Gerekçe
              </label>
              <textarea
                id="statedPurpose"
                value={amac}
                onChange={(e) => setAmac(e.target.value)}
                rows={4}
                required
                placeholder="Erişim talebinizin nedenini detaylı olarak açıklayın..."
                className="bg-surface-dim border border-outline-variant rounded-DEFAULT px-3 py-2 font-body-md text-body-md text-on-surface focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors resize-none"
              />
            </div>
            <button
              type="submit"
              disabled={gonderiliyor}
              className="mt-stack-default w-full bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold py-3 rounded-DEFAULT border border-primary-container hover:bg-primary-fixed transition-colors flex justify-center items-center gap-2 disabled:opacity-50"
            >
              <Icon name="send" className="text-[18px]" />
              {gonderiliyor ? "Gönderiliyor…" : "Talep Gönder"}
            </button>
          </form>
          {talepMesaj && (
            <div className="border border-secondary p-3 bg-secondary/10 rounded-DEFAULT flex items-start gap-2">
              <Icon name="check_circle" className="text-secondary text-[20px]" />
              <p className="font-body-md text-body-md text-on-surface">{talepMesaj}</p>
            </div>
          )}
          {talepHata && (
            <div className="border border-error/40 bg-error-container/20 text-error p-3 rounded-DEFAULT font-body-md text-body-md">
              {talepHata}
            </div>
          )}
        </div>

        <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-grid-margin">
          <div className="flex items-center gap-2 mb-stack-default">
            <Icon name="info" className="text-secondary" />
            <h3 className="font-mono-label-sm text-mono-label-sm text-on-surface">Erişim Protokolü</h3>
          </div>
          <ul className="font-body-md text-body-md text-on-surface-variant space-y-2 list-disc list-inside">
            <li>Erişim onayı, müşterinin onayladığı süre boyunca geçerlidir (varsayılan 30 gün).</li>
            <li>Tüm işlemler kalıcı olarak loglanmaktadır (değiştirilemez rıza defteri).</li>
            <li>Yalnızca müşterinin onayladığı süre içinde, ilgili müşterinin verisine erişilebilir.</li>
          </ul>
        </div>
      </section>

      {/* Right Column: Active Consents Table */}
      <section className="lg:col-span-8 flex flex-col">
        <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT flex flex-col h-full overflow-hidden">
          <div className="p-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-highest">
            <h2 className="font-headline-md text-headline-md text-on-surface">Aktif Erişimler</h2>
            <button
              onClick={yenile}
              className="text-outline hover:text-primary transition-colors p-1 border border-transparent hover:border-outline-variant rounded-DEFAULT"
              title="Yenile"
            >
              <Icon name="refresh" className="text-[20px]" />
            </button>
          </div>
          <div className="flex-1 overflow-auto">
            {yukleniyor ? (
              <p className="font-body-md text-body-md text-on-surface-variant p-6">Yükleniyor…</p>
            ) : musteriler.length === 0 ? (
              <p className="font-body-md text-body-md text-on-surface-variant p-6">
                Henüz onaylanmış bir erişiminiz yok — soldan talep gönderin.
              </p>
            ) : (
              <table className="w-full text-left border-collapse">
                <thead className="sticky top-0 bg-surface-container-highest border-b border-outline-variant z-10">
                  <tr>
                    <th className="py-2 px-4 font-mono-label-sm text-mono-label-sm text-outline font-medium w-1/4">
                      AKS Numarası
                    </th>
                    <th className="py-2 px-4 font-mono-label-sm text-mono-label-sm text-outline font-medium">Gerekçe</th>
                    <th className="py-2 px-4 font-mono-label-sm text-mono-label-sm text-outline font-medium w-1/4 text-right">
                      Onay Bitişi
                    </th>
                    <th className="py-2 px-2 w-10" />
                  </tr>
                </thead>
                <tbody className="font-mono-data-md text-mono-data-md text-on-surface divide-y divide-outline-variant/30">
                  {musteriler.map((m) => (
                    <tr key={m.aks_no} className="zebra-row hover:bg-white/5 cursor-pointer transition-colors group">
                      <td className="py-3 px-4 text-primary">
                        <Link to={`/kurum/musteri/${m.aks_no}`} className="block">
                          {m.aks_no}
                        </Link>
                      </td>
                      <td className="py-3 px-4 text-on-surface-variant font-body-md truncate max-w-xs">{m.amac}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <span className="w-2 h-2 rounded-full bg-secondary" />
                          {m.gecerlilik_bitis.replace("T", " ").slice(0, 16)}
                        </div>
                      </td>
                      <td className="py-3 px-2 text-center text-outline group-hover:text-primary">
                        <Link to={`/kurum/musteri/${m.aks_no}`}>
                          <Icon name="chevron_right" className="text-[20px]" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          <div className="p-3 border-t border-outline-variant bg-surface-container-highest flex justify-between items-center">
            <span className="font-mono-label-sm text-mono-label-sm text-outline">
              Toplam: {musteriler.length} aktif bağlantı
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}
