import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kurum girişi LOGIN-ONLY: kurum üyeliği öz-kayıt değil,
// kasıtlı olarak provizyonlanır (bkz. `kimlik/management/commands/bootstrap_kurum.py`
// ve execution.md'deki ilgili OQ — gerçek kurum onboarding süreci henüz tanımsız).
// Aynı Django session auth'unu (`/api/auth/giris`) kullanır; ayrım `KurumUyeligi`
// kaydının var olup olmamasıdır (`izinler.KurumUyesi`).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_kurum_giri
// ("B2B Staff Portal" — dairesel ikon rozeti, ikon+etiket alanlı input).
export default function KurumLoginPage() {
  const [email, setEmail] = useState("");
  const [sifre, setSifre] = useState("");
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .kurumBen()
      .then(() => navigate("/kurum/musteriler", { replace: true }))
      .catch(() => {})
      .finally(() => setKontrolEdiliyor(false));
  }, [navigate]);

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata("");
    setYukleniyor(true);
    try {
      await api.girisYap(email, sifre);
      await api.kurumBen(); // bu hesap gerçekten bir kuruma üye mi?
      navigate("/kurum/musteriler");
    } catch (err) {
      setHata(
        String(err instanceof Error ? err.message : err) +
          " (bu hesabın bir kuruma üyeliği yoksa kurum paneline giremezsiniz)"
      );
      await api.cikisYap().catch(() => {});
    } finally {
      setYukleniyor(false);
    }
  }

  if (kontrolEdiliyor) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Yükleniyor…</p>
      </div>
    );
  }

  return (
    <div className="bg-background text-on-background min-h-screen flex items-center justify-center p-container-padding font-body-md antialiased selection:bg-primary-container selection:text-on-primary-container">
      <main className="w-full max-w-md flex flex-col gap-stack-default">
        <div className="bg-surface-container border border-outline-variant p-grid-margin rounded-DEFAULT flex flex-col gap-6">
          <div className="flex flex-col items-center justify-center gap-stack-compact text-center">
            <div className="w-12 h-12 bg-surface-container-high border border-outline-variant rounded-full flex items-center justify-center mb-2">
              <Icon name="account_balance" className="text-primary text-2xl" />
            </div>
            <h1 className="font-headline-lg text-headline-lg text-primary tracking-tight">Kurum Girişi</h1>
            <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant uppercase">B2B Staff Portal</p>
          </div>

          <form onSubmit={gonder} className="flex flex-col gap-gutter mt-2">
            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="email">
                Kurumsal E-posta
              </label>
              <div className="relative">
                <Icon name="mail" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]" />
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-surface-dim border border-outline-variant text-on-surface font-mono-data-md text-mono-data-md pl-10 pr-3 py-2 rounded-DEFAULT focus:ring-0 focus:border-primary transition-colors placeholder:text-outline-variant/50"
                  placeholder="kurum@demo.aks"
                />
              </div>
            </div>

            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="password">
                Parola
              </label>
              <div className="relative">
                <Icon name="lock" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]" />
                <input
                  id="password"
                  type="password"
                  required
                  value={sifre}
                  onChange={(e) => setSifre(e.target.value)}
                  className="w-full bg-surface-dim border border-outline-variant text-on-surface font-mono-data-md text-mono-data-md pl-10 pr-3 py-2 rounded-DEFAULT focus:ring-0 focus:border-primary transition-colors placeholder:text-outline-variant/50"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="border border-caveat/50 bg-caveat/10 p-3 mt-2 rounded-DEFAULT flex items-start gap-2">
              <Icon name="info" className="text-caveat text-[16px] mt-0.5 shrink-0" />
              <p className="font-mono-label-sm text-mono-label-sm text-caveat/90 leading-relaxed">
                Yetkisiz erişim denemeleri kaydedilmektedir.
              </p>
            </div>

            {hata && (
              <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-3 font-body-md text-body-md">
                {hata}
              </div>
            )}

            <button
              type="submit"
              disabled={yukleniyor}
              className="w-full bg-primary-container text-on-primary-container hover:bg-primary-fixed font-mono-label-sm text-mono-label-sm font-bold py-3 mt-2 rounded-DEFAULT transition-colors duration-200 border border-primary-container flex justify-center items-center gap-2 disabled:opacity-50"
            >
              <span>{yukleniyor ? "…" : "Giriş Yap"}</span>
              {!yukleniyor && <Icon name="arrow_forward" className="text-[16px]" />}
            </button>
          </form>
        </div>

        <div className="text-center px-4">
          <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant/70 inline-flex items-center gap-1.5 flex-wrap justify-center">
            <Icon name="gavel" className="text-[14px]" />
            Banka personeli oturumu — müşteri verisine yalnızca rızalı erişimle ulaşılır.
          </p>
        </div>
      </main>
    </div>
  );
}
