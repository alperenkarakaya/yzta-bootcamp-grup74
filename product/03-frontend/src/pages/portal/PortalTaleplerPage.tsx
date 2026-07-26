import { useEffect, useState } from "react";
import { api, type ErisimTalebiKaydi } from "../../api";
import { Icon } from "../../components/Icon";

const DURUM_STIL: Record<string, string> = {
  bekliyor: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  onaylandi: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
  reddedildi: "text-error bg-error/10 border-error/30",
  iptal_edildi: "text-on-surface-variant bg-surface-container-high border-outline-variant/30",
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
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Erişim Talepleri</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kurumlar yalnızca AKS numaranızı bilerek talep açabilir — verinize erişmeleri için SİZİN onayınız
          gerekir.
        </p>
      </header>

      {hata && (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      )}

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : talepler.length === 0 ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir erişim talebi yok.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {talepler.map((t) => (
            <div key={t.id} className="bg-surface-container hairline-border rounded-xl p-5 flex flex-col gap-3">
              <div className="flex justify-between items-start flex-wrap gap-2">
                <div>
                  <div className="font-body-sm text-body-sm text-on-surface font-semibold">{t.kurum}</div>
                  <div className="font-label-mono text-[11px] text-on-surface-variant mt-1">{t.amac}</div>
                </div>
                <span className={`font-label-mono text-[10px] px-2 py-1 rounded-DEFAULT border ${DURUM_STIL[t.durum]}`}>
                  {DURUM_ETIKET[t.durum]}
                </span>
              </div>
              <div className="font-label-mono text-[10px] text-on-surface-variant">
                Talep: {t.created_at.replace("T", " ")}
                {t.gecerlilik_bitis && ` · Geçerlilik: ${t.gecerlilik_bitis.replace("T", " ").slice(0, 16)}`}
                {t.aktif_mi && <span className="text-emerald-400 ml-2">● şu an aktif</span>}
              </div>

              {t.durum === "bekliyor" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => aksiyon(t.id, api.erisimTalebiOnayla)}
                    disabled={isleniyorId === t.id}
                    className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                  >
                    <Icon name="check" className="text-[16px]" /> Onayla (30 gün)
                  </button>
                  <button
                    onClick={() => aksiyon(t.id, api.erisimTalebiReddet)}
                    disabled={isleniyorId === t.id}
                    className="flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container-high disabled:opacity-40"
                  >
                    <Icon name="close" className="text-[16px]" /> Reddet
                  </button>
                </div>
              )}
              {t.durum === "onaylandi" && (
                <button
                  onClick={() => aksiyon(t.id, api.erisimTalebiIptal)}
                  disabled={isleniyorId === t.id}
                  className="self-start flex items-center gap-1 px-3 py-2 rounded-DEFAULT border border-error/40 text-error font-label-mono text-label-mono hover:bg-error/10 disabled:opacity-40"
                >
                  <Icon name="block" className="text-[16px]" /> Erişimi İptal Et
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
