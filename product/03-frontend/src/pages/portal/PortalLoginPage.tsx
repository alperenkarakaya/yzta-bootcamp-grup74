import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

export default function PortalLoginPage() {
  const [mod, setMod] = useState<"giris" | "kayit">("giris");
  const [email, setEmail] = useState("");
  const [sifre, setSifre] = useState("");
  const [ad, setAd] = useState("");
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Zaten oturumu açık bir kullanıcı giriş ekranına gelirse doğrudan portala geç.
    api
      .ben()
      .then(() => navigate("/portal", { replace: true }))
      .catch(() => {})
      .finally(() => setKontrolEdiliyor(false));
  }, [navigate]);

  async function gonder(e: React.FormEvent) {
    e.preventDefault();
    setHata("");
    setYukleniyor(true);
    try {
      if (mod === "giris") {
        await api.girisYap(email, sifre);
      } else {
        await api.kayitOl(email, sifre, ad);
      }
      navigate("/portal");
    } catch (err) {
      setHata(String(err instanceof Error ? err.message : err));
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
          <Icon name="account_circle" className="text-5xl text-primary" />
          <h1 className="font-headline-md text-headline-md text-on-background mt-2">AKS Portal</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
            Kendi ekstrenizi yükleyip davranışsal kapasite analizinizi görün.
          </p>
        </div>

        <div className="flex mb-6 rounded-DEFAULT border border-outline-variant/30 overflow-hidden">
          <button
            type="button"
            onClick={() => setMod("giris")}
            className={`flex-1 py-2 font-label-mono text-label-mono transition-colors ${
              mod === "giris" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            Giriş Yap
          </button>
          <button
            type="button"
            onClick={() => setMod("kayit")}
            className={`flex-1 py-2 font-label-mono text-label-mono transition-colors ${
              mod === "kayit" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            Kayıt Ol
          </button>
        </div>

        <form onSubmit={gonder} className="flex flex-col gap-4">
          {mod === "kayit" && (
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Ad Soyad</label>
              <input
                value={ad}
                onChange={(e) => setAd(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="Ayşe Yılmaz"
              />
            </div>
          )}
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="ornek@eposta.com"
            />
          </div>
          <div>
            <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
            <input
              type="password"
              required
              minLength={8}
              value={sifre}
              onChange={(e) => setSifre(e.target.value)}
              className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
              placeholder="En az 8 karakter"
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
            {yukleniyor ? "…" : mod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
          </button>
        </form>
      </div>
    </div>
  );
}
