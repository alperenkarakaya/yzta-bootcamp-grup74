import { useEffect, useState } from "react";
import { api, type ErisimTalebiKaydi } from "../../api";
import { Icon } from "../../components/Icon";

const DURUM_STIL: Record<string, string> = {
  bekliyor: "bg-surface-variant text-on-surface-variant border-outline-variant",
  onaylandi: "bg-secondary-container/20 text-secondary border-secondary/50",
  reddedildi: "bg-error-container/20 text-error border-error/50",
  iptal_edildi: "bg-surface-container-highest text-on-surface-variant border-outline-variant",
};

const DURUM_NOKTA: Record<string, string> = {
  bekliyor: "bg-outline",
  onaylandi: "bg-secondary",
  reddedildi: "",
  iptal_edildi: "",
};

const DURUM_ETIKET: Record<string, string> = {
  bekliyor: "Bekliyor",
  onaylandi: "Onaylandı",
  reddedildi: "Reddedildi",
  iptal_edildi: "İptal Edildi",
};

// §3b Phase 7/7.2 — "müşteri onayı ile erişim" (PO kararı): bir kurum AKS
// numaranızla erişim talebi açtığında burada görürsünüz; onay SÜRELİ ve
// İSTEDİĞİNİZ AN iptal edilebilir. Her aksiyon değiştirilemez rıza defterine
// yazılır (bkz. /portal/riza-defterim).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_eri_im_talepleri
// ("AKS Terminal" — kart ızgarası, durum bazlı renk). Mockup'ın 4 kartı sahte
// kurum isimleriydi (FinansBank A.Ş. vb.) — burada gerçek `t.kurum`/`t.amac`
// kullanılıyor, sabit "TOTAL: 04 REQ" yerine gerçek `talepler.length`.
export default function PortalTaleplerPage() {
  const [talepler, setTalepler] = useState<ErisimTalebiKaydi[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [isleniyorId, setIsleniyorId] = useState<number | null>(null);
  const [hata, setHata] = useState("");

  function yenile() {
    setYukleniyor(true);
    api
      .erisimTalepleri()
      .then((r) => setTalepler(r.talepler))
      .catch(() => setHata("Talepler yüklenemedi"))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function aksiyon(id: number, fn: (id: number) => Promise<unknown>) {
    setIsleniyorId(id);
    setHata("");
    try {
      await fn(id);
      yenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyorId(null);
    }
  }

  return (
    <div className="flex flex-col gap-stack-default">
      <div className="p-stack-default border caveat-banner rounded-DEFAULT flex items-start gap-3">
        <Icon name="warning" className="text-caveat" filled />
        <div>
          <h4 className="font-body-md text-body-md font-bold text-caveat">Regülatif Bilgilendirme</h4>
          <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-1">
            Bu ekrandaki erişim onayları, 6698 sayılı KVKK kapsamında işlenmektedir. Onaylanan taleplerin kalıcı log
            kayıtları Rıza Defterim üzerinden izlenebilir.
          </p>
        </div>
      </div>

      <header className="flex justify-between items-end border-b border-outline-variant pb-4 flex-wrap gap-2">
        <div>
          <h1 className="font-headline-lg text-headline-lg text-on-surface">Erişim Talepleri</h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-1">
            Kurumlar yalnızca AKS numaranızı bilerek talep açabilir — verinize erişmeleri için SİZİN onayınız
            gerekir.
          </p>
        </div>
        <div className="font-mono-data-md text-mono-data-md text-primary-fixed bg-surface-container-high px-3 py-1 rounded-DEFAULT border border-outline-variant">
          TOPLAM: {String(talepler.length).padStart(2, "0")}
        </div>
      </header>

      {hata && (
        <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-4 font-body-md text-body-md">
          {hata}
        </div>
      )}

      {yukleniyor ? (
        <p className="font-body-md text-body-md text-on-surface-variant">Yükleniyor…</p>
      ) : talepler.length === 0 ? (
        <p className="font-body-md text-body-md text-on-surface-variant">Henüz bir erişim talebi yok.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-stack-default">
          {talepler.map((t) => (
            <div
              key={t.id}
              className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-stack-default flex flex-col justify-between relative overflow-hidden hover:border-primary-container transition-colors"
            >
              {t.durum === "onaylandi" && <div className="absolute left-0 top-0 bottom-0 w-1 bg-secondary opacity-50" />}
              <div>
                <div className="flex justify-between items-start mb-4 gap-2 flex-wrap">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-surface-container-highest border border-outline-variant flex items-center justify-center shrink-0">
                      <Icon name="account_balance" className="text-on-surface-variant text-[18px]" />
                    </div>
                    <h3 className="font-body-md text-body-md font-bold text-on-surface">{t.kurum}</h3>
                  </div>
                  <span className={`font-mono-label-sm text-mono-label-sm px-2 py-1 border rounded-DEFAULT flex items-center gap-1 ${DURUM_STIL[t.durum]}`}>
                    {DURUM_NOKTA[t.durum] && <span className={`w-1.5 h-1.5 rounded-full ${DURUM_NOKTA[t.durum]}`} />}
                    {DURUM_ETIKET[t.durum]}
                  </span>
                </div>
                <div className="mb-4">
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mb-1 uppercase tracking-widest">
                    Erişim Amacı
                  </div>
                  <div
                    className={`font-body-md text-body-md bg-surface-container-lowest p-2 border border-outline-variant rounded-DEFAULT ${
                      t.durum === "reddedildi" ? "text-on-surface-variant line-through opacity-70" : "text-on-surface"
                    }`}
                  >
                    {t.amac}
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between mt-2 pt-4 border-t border-outline-variant/50 flex-wrap gap-2">
                <div className="font-mono-data-md text-mono-data-md text-on-surface-variant">
                  {t.created_at.replace("T", " ").slice(0, 16)}
                  {t.gecerlilik_bitis && ` → ${t.gecerlilik_bitis.replace("T", " ").slice(0, 16)}`}
                  {t.aktif_mi && <span className="text-secondary ml-2">● şu an aktif</span>}
                </div>

                {t.durum === "bekliyor" && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => aksiyon(t.id, api.erisimTalebiReddet)}
                      disabled={isleniyorId === t.id}
                      className="font-mono-label-sm text-mono-label-sm font-bold bg-error text-on-error px-4 py-2 rounded-DEFAULT flex items-center gap-1 hover:brightness-110 active:scale-95 transition-all disabled:opacity-40"
                    >
                      <Icon name="close" className="text-[16px]" /> Reddet
                    </button>
                    <button
                      onClick={() => aksiyon(t.id, api.erisimTalebiOnayla)}
                      disabled={isleniyorId === t.id}
                      className="font-mono-label-sm text-mono-label-sm font-bold bg-secondary text-on-secondary px-4 py-2 rounded-DEFAULT flex items-center gap-1 hover:brightness-110 active:scale-95 transition-all disabled:opacity-40"
                    >
                      <Icon name="check" className="text-[16px]" /> Onayla (30 gün)
                    </button>
                  </div>
                )}
                {t.durum === "onaylandi" && (
                  <button
                    onClick={() => aksiyon(t.id, api.erisimTalebiIptal)}
                    disabled={isleniyorId === t.id}
                    className="font-mono-label-sm text-mono-label-sm font-bold border border-error text-error px-4 py-2 rounded-DEFAULT flex items-center gap-1 hover:bg-error-container hover:text-on-error-container active:scale-95 transition-all disabled:opacity-40"
                  >
                    <Icon name="block" className="text-[16px]" /> Erişimi İptal Et
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
