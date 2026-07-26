import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, type KurumMusteriDetay } from "../../api";
import { Icon } from "../../components/Icon";
import { paraFormat } from "../../lib/skor";

const BAYRAK_METNI: Record<string, string> = {
  coklu_sahiplik_supheli: "Bu ekstre içeriği başka bir hesap altında da yüklenmiş görünüyor.",
  profil_tutarsiz: "Bu yükleme, müşterinin geçmiş yüklemelerinden belirgin şekilde farklı bir gelir ölçeği gösteriyor.",
};

const PROFIL_SIRA: Array<"ihtiyatli" | "dengeli" | "atak"> = ["ihtiyatli", "dengeli", "atak"];
const PROFIL_RENK: Record<string, string> = {
  ihtiyatli: "border-emerald-400/30 bg-emerald-400/5",
  dengeli: "border-amber-400/30 bg-amber-400/5",
  atak: "border-error/30 bg-error/5",
};

// §3b Phase 7/7.4 — 3 seviyeli risk iştahı kartları: aynı müşteri, bankanın
// seçtiği risk profiline göre onaylanır ya da onaylanmaz. Sentetik/held-out
// benchmarkta üretildi (bkz. risk_istahi.py) — "nihai politika" değil, öneri.
export default function KurumMusteriDetayPage() {
  const { aksNo } = useParams<{ aksNo: string }>();
  const [detay, setDetay] = useState<KurumMusteriDetay | null>(null);
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    if (!aksNo) return;
    setYukleniyor(true);
    api
      .kurumMusteriDetay(aksNo)
      .then(setDetay)
      .catch((e) => setHata(String(e instanceof Error ? e.message : e)))
      .finally(() => setYukleniyor(false));
  }, [aksNo]);

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <Link to="/kurum/musteriler" className="font-label-mono text-label-mono text-on-surface-variant hover:text-on-surface flex items-center gap-1 w-fit">
        <Icon name="chevron_left" className="text-[16px]" /> Müşteriler
      </Link>

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : hata ? (
        <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-4 font-body-sm text-body-sm">
          {hata}
        </div>
      ) : !detay ? null : !detay.degerlendirme_var ? (
        <div className="bg-surface-container hairline-border rounded-xl p-8 text-center">
          <h1 className="font-headline-md text-headline-md text-on-background mb-2">{detay.aks_no}</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">{detay.not ?? "Henüz bir belge yüklenmemiş."}</p>
        </div>
      ) : (
        <>
          <header>
            <h1 className="font-headline-md text-headline-md text-on-background">{detay.aks_no}</h1>
            <p className="font-label-mono text-[11px] text-on-surface-variant mt-1">
              Son değerlendirme: {detay.created_at?.replace("T", " ")} · Kaynak: {detay.kaynak_format?.toUpperCase()}
            </p>
          </header>

          {(detay.sahiplik_bayraklari ?? []).map((b) => (
            <div key={b} className="bg-amber-400/10 border border-amber-400/30 text-amber-400 rounded-DEFAULT p-3 font-body-sm text-body-sm flex items-center gap-2">
              <Icon name="warning" className="text-[16px] shrink-0" />
              {BAYRAK_METNI[b] ?? b}
            </div>
          ))}

          <section className="grid grid-cols-1 md:grid-cols-3 gap-stack-md">
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">AKS Skoru</span>
              <span className="font-display-lg text-display-lg text-primary">{detay.aks_skor}</span>
              <span className="font-label-mono text-label-mono text-secondary mt-2">{detay.risk_seviyesi}</span>
            </div>
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Karar</span>
              <span className="font-body-sm text-body-sm text-on-background">{detay.karar}</span>
            </div>
            <div className="bg-surface-container-high hairline-border rounded-xl p-6 flex flex-col items-center text-center">
              <span className="font-label-mono text-label-mono text-on-surface-variant mb-2">Önerilen Limit</span>
              <span className="font-display-sm text-display-sm text-on-background">{paraFormat(detay.onerilen_limit ?? null)}</span>
            </div>
          </section>

          <section>
            <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4">
              Risk İştahı Profillerine Göre Karar
            </h2>
            {!detay.risk_istahi ? (
              <p className="font-body-sm text-body-sm text-on-surface-variant">
                Risk iştahı raporu henüz üretilmedi (<code>python -m aks_core.model.risk_istahi</code>).
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-stack-md">
                {PROFIL_SIRA.map((p) => {
                  const sonuc = detay.risk_istahi![p];
                  return (
                    <div key={p} className={`rounded-xl border p-6 flex flex-col items-center text-center gap-2 ${PROFIL_RENK[p]}`}>
                      <span className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
                        {sonuc.ad}
                      </span>
                      <Icon
                        name={sonuc.onaylanir_mi ? "check_circle" : "cancel"}
                        className={`text-4xl ${sonuc.onaylanir_mi ? "text-emerald-400" : "text-error"}`}
                      />
                      <span className="font-body-sm text-body-sm text-on-background font-semibold">
                        {sonuc.onaylanir_mi ? "Onaylanabilir" : "Onaylanmaz"}
                      </span>
                      <span className="font-label-mono text-[10px] text-on-surface-variant">Eşik: {sonuc.esik}</span>
                    </div>
                  );
                })}
              </div>
            )}
            <p className="font-label-mono text-[10px] text-on-surface-variant mt-3">
              Sentetik/dekuple veri üzerinde, held-out benchmarkta üretildi — nihai politika değil, önerilen
              başlangıç noktası.
            </p>
          </section>
        </>
      )}
    </div>
  );
}
