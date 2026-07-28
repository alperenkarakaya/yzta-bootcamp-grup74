import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "../components/Icon";

// Giriş sonrası doğru yüzey: yönetici → banka içi araştırma arayüzü (TÜM demo
// popülasyonunu görür), kurum personeli → kurum paneli (yalnızca rıza verilen
// müşteriler), sıradan kullanıcı → kendi portalı (yalnızca kendi yüklemeleri).
function varisYolu(k: KullaniciBilgisi): string {
  if (k.yonetici) return "/";
  if (k.kurum_uyesi) return "/kurum/musteriler";
  return "/portal";
}

// Site geneli giriş — küçük bir landing page: üstte kısa bir tanıtım, altında
// iki kutucuk (Kullanıcı / Kurum) — giren kişi giriş şeklini KENDİSİ seçer.
// Her kutucuğun altında doğrudan giriş alanları var (ayrı bir sayfaya
// geçmeye gerek yok). İkisi de AYNI oturum sistemini (`/api/auth/*`)
// kullanır — Kurum tarafı `kurumBen()` ile üyeliğini doğrular (KurumLoginPage
// ile birebir aynı mantık), Kullanıcı tarafı banka içi arayüze (`/`) gider.
export default function GirisPage() {
  const navigate = useNavigate();
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);

  // Kullanıcı kutucuğu
  const [kMod, setKMod] = useState<"giris" | "kayit">("giris");
  const [kEmail, setKEmail] = useState("");
  const [kSifre, setKSifre] = useState("");
  const [kHata, setKHata] = useState("");
  const [kYukleniyor, setKYukleniyor] = useState(false);

  // Kurum kutucuğu — öz-kayıt yok (kurum üyeliği kasıtlı provizyonlanır,
  // bkz. KurumLoginPage.tsx), yalnızca giriş.
  const [uEmail, setUEmail] = useState("");
  const [uSifre, setUSifre] = useState("");
  const [uHata, setUHata] = useState("");
  const [uYukleniyor, setUYukleniyor] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const k = await api.ben();
        navigate(varisYolu(k), { replace: true });
        return;
      } catch {
        /* oturum yok — landing page gösterilecek */
      }
      setKontrolEdiliyor(false);
    })();
  }, [navigate]);

  async function kullaniciGonder(e: React.FormEvent) {
    e.preventDefault();
    setKHata("");
    setKYukleniyor(true);
    try {
      const k = kMod === "giris" ? await api.girisYap(kEmail, kSifre) : await api.kayitOl(kEmail, kSifre);
      navigate(varisYolu(k));
    } catch (err) {
      setKHata(String(err instanceof Error ? err.message : err));
    } finally {
      setKYukleniyor(false);
    }
  }

  async function kurumGonder(e: React.FormEvent) {
    e.preventDefault();
    setUHata("");
    setUYukleniyor(true);
    try {
      await api.girisYap(uEmail, uSifre);
      await api.kurumBen(); // bu hesap gerçekten bir kuruma üye mi?
      navigate("/kurum/musteriler");
    } catch (err) {
      setUHata(
        String(err instanceof Error ? err.message : err) +
          " (bu hesabın bir kuruma üyeliği yoksa kurum girişi kullanılamaz)"
      );
      await api.cikisYap().catch(() => {});
    } finally {
      setUYukleniyor(false);
    }
  }

  if (kontrolEdiliyor) {
    return <p className="p-8 text-center font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-4 py-16">
      {/* Hero */}
      <div className="text-center max-w-lg mb-10">
        <Icon name="insights" className="text-5xl text-primary" />
        <h1 className="font-display-sm text-display-sm text-on-background mt-3">AKS — Alternatif Kapasite Skoru</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2">
          Banka skorunu tamamlayan davranışsal kredi kapasitesi platformu. Devam etmek için giriş türünüzü seçin.
        </p>
      </div>

      {/* İki kutucuk: Kullanıcı / Kurum */}
      <div className="w-full max-w-3xl grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Kullanıcı kutucuğu */}
        <div className="bg-surface-container-low hairline-border rounded-xl p-6 flex flex-col">
          <div className="text-center mb-4">
            <Icon name="account_circle" className="text-3xl text-primary" />
            <h2 className="font-headline-md text-headline-md text-on-background mt-1">Kullanıcı</h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
              Kendi ekstrenizi yükleyip kapasite analizinizi görün. Yalnızca kendi verinize erişirsiniz.
            </p>
          </div>

          <div className="flex mb-4 rounded-DEFAULT border border-outline-variant/30 overflow-hidden">
            <button
              type="button"
              onClick={() => setKMod("giris")}
              className={`flex-1 py-1.5 font-label-mono text-label-mono transition-colors ${
                kMod === "giris" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Giriş Yap
            </button>
            <button
              type="button"
              onClick={() => setKMod("kayit")}
              className={`flex-1 py-1.5 font-label-mono text-label-mono transition-colors ${
                kMod === "kayit" ? "bg-primary-container text-white" : "text-on-surface-variant hover:bg-surface-container"
              }`}
            >
              Kayıt Ol
            </button>
          </div>

          <form onSubmit={kullaniciGonder} className="flex flex-col gap-3">
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
              <input
                type="email"
                required
                value={kEmail}
                onChange={(e) => setKEmail(e.target.value)}
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
                value={kSifre}
                onChange={(e) => setKSifre(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="En az 8 karakter"
              />
            </div>

            {kHata && (
              <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-2.5 font-body-sm text-body-sm">
                {kHata}
              </div>
            )}

            <button
              type="submit"
              disabled={kYukleniyor}
              className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-1"
            >
              {kYukleniyor ? "…" : kMod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
            </button>
          </form>

          <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-3 text-center leading-relaxed">
            Örnek kullanıcı: <span className="text-on-surface-variant">ornek@aks.com</span> /{" "}
            <span className="text-on-surface-variant">OrnekSifre123</span>
            <br />
            Yönetici (araştırma paneli):{" "}
            <span className="text-on-surface-variant">admin@aks.com</span> /{" "}
            <span className="text-on-surface-variant">AdminSifre123</span>
          </p>
        </div>

        {/* Kurum kutucuğu */}
        <div className="bg-surface-container-low hairline-border rounded-xl p-6 flex flex-col">
          <div className="text-center mb-4">
            <Icon name="account_balance" className="text-3xl text-primary" />
            <h2 className="font-headline-md text-headline-md text-on-background mt-1">Kurum</h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
              Banka/kurum personeli oturumu — müşteri verisine yalnızca rızalı erişimle ulaşılır.
            </p>
          </div>

          <form onSubmit={kurumGonder} className="flex flex-col gap-3 mt-auto">
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">E-posta</label>
              <input
                type="email"
                required
                value={uEmail}
                onChange={(e) => setUEmail(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="kurum@demo.aks"
              />
            </div>
            <div>
              <label className="font-label-mono text-[11px] text-on-surface-variant block mb-1">Şifre</label>
              <input
                type="password"
                required
                value={uSifre}
                onChange={(e) => setUSifre(e.target.value)}
                className="w-full bg-surface-container-lowest border border-outline-variant/30 rounded px-3 py-2 font-body-sm text-body-sm text-on-surface focus:outline-none focus:border-primary"
                placeholder="••••••••"
              />
            </div>

            {uHata && (
              <div className="bg-error-container/20 border border-error/40 text-error rounded-DEFAULT p-2.5 font-body-sm text-body-sm">
                {uHata}
              </div>
            )}

            <button
              type="submit"
              disabled={uYukleniyor}
              className="w-full py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors disabled:opacity-50 mt-1"
            >
              {uYukleniyor ? "…" : "Giriş Yap"}
            </button>
          </form>

          <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-3 text-center">
            Örnek kurum: <span className="text-on-surface-variant">kurum@demo.aks</span> /{" "}
            <span className="text-on-surface-variant">DemoKurum123!</span>
          </p>
        </div>
      </div>

      <p className="font-label-mono text-[11px] text-on-surface-variant/70 mt-8 text-center max-w-lg">
        Her hesap yalnızca kendi verisini görür. Kurumlar bir müşterinin verisine ancak o müşteri
        portalinden erişim talebini onayladıktan sonra, onayın süresi dolana kadar erişebilir.
      </p>
    </div>
  );
}
