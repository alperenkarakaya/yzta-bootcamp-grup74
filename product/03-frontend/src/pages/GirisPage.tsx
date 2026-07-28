import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "../components/Icon";

// Giriş sonrası doğru yüzey: yönetici → banka içi araştırma arayüzü (TÜM demo
// popülasyonunu görür), kurum personeli → kurum paneli (yalnızca rıza verilen
// müşteriler), sıradan kullanıcı → kendi portalı (yalnızca kendi yüklemeleri).
function varisYolu(k: KullaniciBilgisi): string {
  if (k.yonetici) return "/panel";
  if (k.kurum_uyesi) return "/kurum/musteriler";
  return "/portal";
}

// Site geneli giriş — küçük bir landing page: üstte kısa bir tanıtım, altında
// iki kutucuk (Kullanıcı / Kurum) — giren kişi giriş şeklini KENDİSİ seçer.
// Her kutucuğun altında doğrudan giriş alanları var (ayrı bir sayfaya
// geçmeye gerek yok). İkisi de AYNI oturum sistemini (`/api/auth/*`)
// kullanır — Kurum tarafı `kurumBen()` ile üyeliğini doğrular (KurumLoginPage
// ile birebir aynı mantık). Giriş sonrası varış `varisYolu()` ile role göre
// belirlenir. Herkese açık ana sayfa ayrı bir sayfadır (`/`, AnaSayfaPage).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_giri
// ("AKS Terminal" — tek kart, gradient üst şerit, ikon+etiket alanlı input,
// sekme geçişli giriş/kayıt) — burada aynı kart deseni YAN YANA iki kez
// (Kullanıcı / Kurum) kullanılıyor.
export default function GirisPage() {
  const navigate = useNavigate();
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);

  // Kullanıcı kutucuğu
  const [kMod, setKMod] = useState<"giris" | "kayit">("giris");
  const [kEmail, setKEmail] = useState("");
  const [kSifre, setKSifre] = useState("");
  const [kSifreGoster, setKSifreGoster] = useState(false);
  const [kHata, setKHata] = useState("");
  const [kYukleniyor, setKYukleniyor] = useState(false);

  // Kurum kutucuğu — öz-kayıt yok (kurum üyeliği kasıtlı provizyonlanır,
  // bkz. KurumLoginPage.tsx), yalnızca giriş.
  const [uEmail, setUEmail] = useState("");
  const [uSifre, setUSifre] = useState("");
  const [uSifreGoster, setUSifreGoster] = useState(false);
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
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Yükleniyor…</p>
      </div>
    );
  }

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col items-center justify-center p-gutter selection:bg-primary-container selection:text-on-primary-container">
      {/* Hero */}
      <div className="text-center max-w-lg mb-8">
        <Icon name="insights" className="text-primary text-[48px] mb-2" filled />
        <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tighter">
          AKS — Alternatif Kapasite Skoru
        </h1>
        <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-2">
          Devam etmek için giriş türünüzü seçin
        </p>
      </div>

      {/* İki kutucuk: Kullanıcı / Kurum */}
      <div className="w-full max-w-3xl grid grid-cols-1 md:grid-cols-2 gap-gutter">
        {/* Kullanıcı kutucuğu */}
        <main className="bg-surface-container-high rounded-lg border border-outline-variant p-grid-margin flex flex-col gap-stack-default relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary opacity-80" />

          <div className="flex flex-col items-center mb-2 mt-2">
            <Icon name="account_circle" className="text-primary text-[40px] mb-2" filled />
            <h2 className="font-headline-md text-headline-md text-on-surface">Kullanıcı</h2>
            <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-1 text-center">
              Kendi ekstrenizi yükleyip analizinizi görün
            </p>
          </div>

          <div className="flex border-b border-outline-variant mb-2">
            <button
              type="button"
              onClick={() => setKMod("giris")}
              className={`flex-1 pb-2 border-b-2 font-mono-label-sm text-mono-label-sm transition-colors uppercase ${
                kMod === "giris" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
              }`}
            >
              Giriş Yap
            </button>
            <button
              type="button"
              onClick={() => setKMod("kayit")}
              className={`flex-1 pb-2 border-b-2 font-mono-label-sm text-mono-label-sm transition-colors uppercase ${
                kMod === "kayit" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
              }`}
            >
              Kayıt Ol
            </button>
          </div>

          <form onSubmit={kullaniciGonder} className="flex flex-col gap-stack-default">
            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="k-email">
                E-Posta Adresi
              </label>
              <div className="relative">
                <Icon
                  name="mail"
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]"
                />
                <input
                  id="k-email"
                  type="email"
                  required
                  value={kEmail}
                  onChange={(e) => setKEmail(e.target.value)}
                  className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-outline-variant"
                  placeholder="ornek@eposta.com"
                />
              </div>
            </div>

            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="k-sifre">
                Şifre
              </label>
              <div className="relative">
                <Icon
                  name="key"
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]"
                />
                <input
                  id="k-sifre"
                  type={kSifreGoster ? "text" : "password"}
                  required
                  minLength={8}
                  value={kSifre}
                  onChange={(e) => setKSifre(e.target.value)}
                  className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-10 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-outline-variant"
                  placeholder="En az 8 karakter"
                />
                <button
                  type="button"
                  aria-label="Şifreyi göster"
                  onClick={() => setKSifreGoster((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary transition-colors"
                >
                  <Icon name={kSifreGoster ? "visibility_off" : "visibility"} className="text-[18px]" />
                </button>
              </div>
            </div>

            {kHata && (
              <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-2.5 font-body-md text-body-md">
                {kHata}
              </div>
            )}

            <button
              type="submit"
              disabled={kYukleniyor}
              className="w-full bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold py-3 rounded-DEFAULT hover:bg-primary-fixed transition-colors flex items-center justify-center gap-2 uppercase tracking-wide group mt-1 disabled:opacity-50"
            >
              {kYukleniyor ? "…" : kMod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
              {!kYukleniyor && (
                <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />
              )}
            </button>
          </form>

          <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant/70 mt-1 text-center leading-relaxed text-[11px]">
            Örnek kullanıcı: ornek@aks.com / OrnekSifre123
            <br />
            Yönetici: admin@aks.com / AdminSifre123
          </p>
        </main>

        {/* Kurum kutucuğu */}
        <main className="bg-surface-container-high rounded-lg border border-outline-variant p-grid-margin flex flex-col gap-stack-default relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-secondary to-primary opacity-80" />

          <div className="flex flex-col items-center mb-2 mt-2">
            <Icon name="account_balance" className="text-secondary text-[40px] mb-2" filled />
            <h2 className="font-headline-md text-headline-md text-on-surface">Kurum</h2>
            <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-1 text-center">
              Yalnızca rızalı erişimle müşteri verisi
            </p>
          </div>

          <div className="flex border-b border-outline-variant mb-2">
            <span className="flex-1 pb-2 border-b-2 border-secondary text-secondary font-mono-label-sm text-mono-label-sm uppercase text-center">
              Giriş Yap
            </span>
          </div>

          <form onSubmit={kurumGonder} className="flex flex-col gap-stack-default flex-1">
            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="u-email">
                E-Posta Adresi
              </label>
              <div className="relative">
                <Icon
                  name="mail"
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]"
                />
                <input
                  id="u-email"
                  type="email"
                  required
                  value={uEmail}
                  onChange={(e) => setUEmail(e.target.value)}
                  className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-4 py-3 focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-all placeholder:text-outline-variant"
                  placeholder="kurum@demo.aks"
                />
              </div>
            </div>

            <div className="flex flex-col gap-stack-compact">
              <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="u-sifre">
                Şifre
              </label>
              <div className="relative">
                <Icon
                  name="key"
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]"
                />
                <input
                  id="u-sifre"
                  type={uSifreGoster ? "text" : "password"}
                  required
                  value={uSifre}
                  onChange={(e) => setUSifre(e.target.value)}
                  className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-10 py-3 focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-all placeholder:text-outline-variant"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  aria-label="Şifreyi göster"
                  onClick={() => setUSifreGoster((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-secondary transition-colors"
                >
                  <Icon name={uSifreGoster ? "visibility_off" : "visibility"} className="text-[18px]" />
                </button>
              </div>
            </div>

            {uHata && (
              <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-2.5 font-body-md text-body-md">
                {uHata}
              </div>
            )}

            <div className="mt-auto flex flex-col gap-stack-default">
              <button
                type="submit"
                disabled={uYukleniyor}
                className="w-full bg-secondary-container text-on-secondary-container font-mono-label-sm text-mono-label-sm font-bold py-3 rounded-DEFAULT hover:bg-secondary transition-colors flex items-center justify-center gap-2 uppercase tracking-wide group disabled:opacity-50"
              >
                {uYukleniyor ? "…" : "Giriş Yap"}
                {!uYukleniyor && (
                  <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />
                )}
              </button>
              <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant/70 text-center text-[11px]">
                Örnek kurum: kurum@demo.aks / DemoKurum123!
              </p>
            </div>
          </form>
        </main>
      </div>

      <div className="mt-6 pt-4 flex items-center justify-center gap-2 text-on-surface-variant/70 max-w-lg">
        <Icon name="lock" className="text-[16px]" />
        <p className="font-mono-label-sm text-mono-label-sm text-[10px] text-center leading-relaxed">
          Her hesap yalnızca kendi verisini görür. Kurumlar bir müşterinin verisine ancak o
          müşteri portalinden onay verdikten sonra, onay süresi dolana kadar erişebilir.
        </p>
      </div>
    </div>
  );
}
