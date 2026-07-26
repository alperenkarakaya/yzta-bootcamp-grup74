import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kurum girişi LOGIN-ONLY: kurum üyeliği öz-kayıt değil,
// kasıtlı olarak provizyonlanır (bkz. `kimlik/management/commands/bootstrap_kurum.py`
// ve execution.md'deki ilgili OQ — gerçek kurum onboarding süreci henüz tanımsız).
// Aynı Django session auth'unu (`/api/auth/giris`) kullanır; ayrım `KurumUyeligi`
// kaydının var olup olmamasıdır (`izinler.KurumUyesi`).
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
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-surface-container-low hairline-border rounded-xl p-8">
        <div className="text-center mb-8">
          <Icon name="account_balance" className="text-5xl text-primary" />
          <h1 className="font-headline-md text-headline-md text-on-background mt-2">Kurum Girişi</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Banka/kurum personeli oturumu — müşteri verisine yalnızca rızalı erişimle ulaşılır.
          </p>
        </div>

        <form onSubmit={gonder} className="flex flex-col gap-4">
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="kurum@demo.aks"
            />
          </div>
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
            <input
              type="password"
              required
              value={sifre}
              onChange={(e) => setSifre(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="••••••••"
            />
          </div>

          {hata && (
            <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-3 font-body-sm text-body-sm">
              {hata}
            </div>
          )}

          <button
            type="submit"
            disabled={yukleniyor}
            className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-2"
          >
            {yukleniyor ? "…" : "Giriş Yap"}
          </button>
          <p className="font-label-mono text-[10px] text-on-surface-variant text-center">
            Demo hesap: <code>python manage.py bootstrap_kurum</code> ile oluşturulur.
          </p>
        </form>
      </div>
    </div>
  );
}
