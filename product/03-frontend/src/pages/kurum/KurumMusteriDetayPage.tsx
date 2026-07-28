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

// §3b Phase 7/7.4 — 3 seviyeli risk iştahı kartları: aynı müşteri, bankanın
// seçtiği risk profiline göre onaylanır ya da onaylanmaz. Sentetik/held-out
// benchmarkta üretildi (bkz. risk_istahi.py) — "nihai politika" değil, öneri.
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_m_teri_detay_1
// ("B2B Staff Portal" — sol kenar-vurgulu twin-score, risk iştahı kartları).
// Mockup'ın "Sistem Logları & Otorizasyon" bölümü sahte hash/log satırlarıydı
// (0x8f4a2b..., KKB sorgusu) — hiçbiri gerçek bir uçtan gelmiyor, bu yüzden
// KULLANILMADI; yerine gerçek SHAP gerekçe kodları korundu.
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

  const maxEtki = detay?.aciklama
    ? Math.max(
        0.01,
        ...detay.aciklama.riski_azaltan.map((f) => Math.abs(f.etki)),
        ...detay.aciklama.riski_artiran.map((f) => Math.abs(f.etki))
      )
    : 0.01;

  return (
    <div className="flex flex-col gap-stack-default">
      <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant flex items-center gap-2">
        <Link to="/kurum/musteriler" className="hover:text-on-surface flex items-center gap-1">
          <Icon name="chevron_left" className="text-[16px]" /> Müşteriler
        </Link>
        <Icon name="chevron_right" className="text-[14px]" />
        <span className="text-primary">Detay</span>
      </div>

      {yukleniyor ? (
        <p className="font-body-md text-body-md text-on-surface-variant">Yükleniyor…</p>
      ) : hata ? (
        <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-4 font-body-md text-body-md">
          {hata}
        </div>
      ) : !detay ? null : !detay.degerlendirme_var ? (
        <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-8 text-center">
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-2">{detay.aks_no}</h1>
          <p className="font-body-md text-body-md text-on-surface-variant">{detay.not ?? "Henüz bir belge yüklenmemiş."}</p>
        </div>
      ) : (
        <>
          <header className="flex justify-between items-end flex-wrap gap-2">
            <div>
              <h1 className="font-headline-lg text-headline-lg text-on-surface flex items-center gap-3">
                <Icon name="account_circle" className="text-[32px] text-primary-container" />
                Müşteri: {detay.aks_no}
              </h1>
              <p className="font-mono-data-md text-mono-data-md text-on-surface-variant mt-1">
                Son değerlendirme: {detay.created_at?.replace("T", " ")} · Kaynak: {detay.kaynak_format?.toUpperCase()}
              </p>
            </div>
          </header>

          {(detay.sahiplik_bayraklari ?? []).map((b) => (
            <div key={b} className="caveat-banner border rounded-DEFAULT px-4 py-3 flex gap-3 items-start">
              <Icon name="warning" className="text-caveat" filled />
              <div>
                <div className="font-mono-label-sm text-mono-label-sm text-caveat font-bold mb-1">Dikkat</div>
                <div className="font-body-md text-body-md text-on-surface">{BAYRAK_METNI[b] ?? b}</div>
              </div>
            </div>
          ))}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
            {/* Left Column: Scores & SHAP */}
            <div className="lg:col-span-8 flex flex-col gap-gutter">
              <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-6 flex flex-col md:flex-row gap-8">
                <div className="flex-1 border-l-4 border-surface-variant pl-4">
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mb-2">KARAR</div>
                  <div className="font-body-md text-body-md text-on-surface mb-1">{detay.karar}</div>
                  <div className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Önerilen limit: {paraFormat(detay.onerilen_limit ?? null)}</div>
                </div>
                <div className="flex-1 border-l-4 border-primary-container pl-4">
                  <div className="font-mono-label-sm text-mono-label-sm text-primary-container mb-2">AKS SKORU</div>
                  <div className="font-mono-score-lg text-mono-score-lg text-on-surface mb-1">{detay.aks_skor}</div>
                  <div className="font-body-md text-body-md text-secondary">{detay.risk_seviyesi}</div>
                </div>
              </div>

              {detay.aciklama && (
                <div className="bg-surface-container-low border border-outline-variant rounded-DEFAULT p-6">
                  <h2 className="font-headline-md text-headline-md text-on-surface mb-6 border-b border-outline-variant pb-2">
                    Gerekçe Kodları (SHAP)
                  </h2>
                  <div className="flex flex-col gap-4 font-mono-label-sm text-mono-label-sm">
                    {detay.aciklama.riski_azaltan.map((f) => (
                      <div className="flex items-center gap-4" key={f.kod}>
                        <div className="w-40 text-right text-on-surface-variant truncate" title={f.faktor}>
                          {f.faktor}
                        </div>
                        <div className="flex-1 flex items-center">
                          <div className="w-1/2 border-r border-outline-variant h-6" />
                          <div className="w-1/2 flex items-center">
                            <div className="shap-positive h-4 rounded-r" style={{ width: `${Math.min(95, (Math.abs(f.etki) / maxEtki) * 100)}%` }} />
                            {/* `f.etki` ZATEN işaretli gelir (riski_azaltan
                                negatif, riski_artiran pozitif) — elle "+"/"-"
                                eklemek çift işaret üretir. */}
                            <span className="ml-2 text-secondary">{f.etki.toFixed(3)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                    {detay.aciklama.riski_artiran.map((f) => (
                      <div className="flex items-center gap-4" key={f.kod}>
                        <div className="w-40 text-right text-on-surface-variant truncate" title={f.faktor}>
                          {f.faktor}
                        </div>
                        <div className="flex-1 flex items-center">
                          <div className="w-1/2 flex items-center justify-end border-r border-outline-variant h-6">
                            <span className="mr-2 text-error">+{f.etki.toFixed(3)}</span>
                            <div className="shap-negative h-4 rounded-l" style={{ width: `${Math.min(95, (Math.abs(f.etki) / maxEtki) * 100)}%` }} />
                          </div>
                          <div className="w-1/2" />
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="font-mono-label-sm text-[10px] text-on-surface-variant mt-4">
                    AKS bankanın klasik skorunu/segmentini değiştirmez — yalnızca davranışsal kanıt sunar.
                  </p>
                </div>
              )}
            </div>

            {/* Right Column: Risk Appetite */}
            <div className="lg:col-span-4 flex flex-col gap-gutter">
              <div className="bg-surface-container-low border border-outline-variant border-t-2 border-t-primary-container rounded-DEFAULT p-6 h-full">
                <h2 className="font-headline-md text-headline-md text-on-surface mb-6">Risk İştahı Profillerine Göre Karar</h2>
                {!detay.risk_istahi ? (
                  <p className="font-body-md text-body-md text-on-surface-variant">Risk iştahı raporu henüz üretilmedi.</p>
                ) : (
                  <div className="flex flex-col gap-4">
                    {PROFIL_SIRA.map((p) => {
                      const sonuc = detay.risk_istahi![p];
                      return (
                        <div
                          key={p}
                          className={`bg-surface-container-high rounded-DEFAULT p-4 flex flex-col gap-2 ${
                            sonuc.onaylanir_mi ? "border-l-2 border-primary-container" : ""
                          }`}
                        >
                          <div className="flex justify-between items-center">
                            <span className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase">{sonuc.ad}</span>
                            <Icon
                              name={sonuc.onaylanir_mi ? "check_circle" : "cancel"}
                              className={sonuc.onaylanir_mi ? "text-secondary" : "text-error"}
                              filled
                            />
                          </div>
                          <div className={`font-body-md text-body-md ${sonuc.onaylanir_mi ? "text-primary-container font-semibold" : "text-on-surface"}`}>
                            {sonuc.onaylanir_mi ? "Onaylanabilir" : "Onaylanmaz"}
                          </div>
                          <div className="font-mono-data-md text-mono-data-md text-on-surface-variant mt-2 border-t border-outline-variant pt-2">
                            Eşik: {sonuc.esik}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <p className="font-mono-label-sm text-[10px] text-on-surface-variant mt-4">
                  Sentetik/dekuple veri üzerinde, held-out benchmarkta üretildi — nihai politika değil, önerilen
                  başlangıç noktası.
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
