import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";
import { Icon } from "../../components/Icon";

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_giri
// ("AKS Terminal" — tek kart, gradient üst şerit, ikon+etiket alanlı input).
export default function PortalLoginPage() {
  const [mod, setMod] = useState<"giris" | "kayit">("giris");
  const [email, setEmail] = useState("");
  const [sifre, setSifre] = useState("");
  const [sifreGoster, setSifreGoster] = useState(false);
  const [hata, setHata] = useState("");
  const [yukleniyor, setYukleniyor] = useState(false);
  const [kontrolEdiliyor, setKontrolEdiliyor] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Zaten oturumu açık bir MÜŞTERİ giriş ekranına gelirse doğrudan portala
    // geç. `aks_no` kontrolü şart: kurum personelinin `Profil`'i yoktur, onu
    // portala göndermek PortalLayout ile sonsuz yönlendirme döngüsü yaratır.
    api
      .ben()
      .then((k) => {
        if (k.aks_no) navigate("/portal", { replace: true });
      })
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
        await api.kayitOl(email, sifre);
      }
      navigate("/portal");
    } catch (err) {
      setHata(String(err instanceof Error ? err.message : err));
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
    <div className="bg-background text-on-background min-h-screen flex items-center justify-center p-gutter selection:bg-primary-container selection:text-on-primary-container">
      <main className="w-full max-w-[420px] bg-surface-container-high rounded-lg border border-outline-variant p-grid-margin flex flex-col gap-stack-default relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-secondary opacity-80" />

        <div className="flex flex-col items-center mb-2 mt-2">
          <Icon name="account_circle" className="text-primary text-[48px] mb-2" filled />
          <h1 className="font-headline-lg text-headline-lg text-on-surface tracking-tighter">AKS Portal</h1>
          <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant mt-1 text-center">
            Kendi ekstrenizi yükleyip davranışsal kapasite analizinizi görün
          </p>
        </div>

        <div className="flex border-b border-outline-variant mb-2">
          <button
            type="button"
            onClick={() => setMod("giris")}
            className={`flex-1 pb-2 border-b-2 font-mono-label-sm text-mono-label-sm transition-colors uppercase ${
              mod === "giris" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
            }`}
          >
            Giriş Yap
          </button>
          <button
            type="button"
            onClick={() => setMod("kayit")}
            className={`flex-1 pb-2 border-b-2 font-mono-label-sm text-mono-label-sm transition-colors uppercase ${
              mod === "kayit" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
            }`}
          >
            Kayıt Ol
          </button>
        </div>

        <form onSubmit={gonder} className="flex flex-col gap-stack-default">
          {mod === "kayit" && (
            <p className="font-body-md text-body-md text-on-surface-variant bg-surface-container-lowest rounded-DEFAULT p-3 border border-outline-variant">
              Ad, soyad ve T.C. kimlik numarası <strong className="text-on-surface">istenmez</strong>. Hesabınız
              yalnızca e-postanıza ve size özel üretilen AKS numarasına bağlanır.
            </p>
          )}

          <div className="flex flex-col gap-stack-compact">
            <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="email">
              E-Posta Adresi
            </label>
            <div className="relative">
              <Icon name="mail" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]" />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-4 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-outline-variant"
                placeholder="ornek@eposta.com"
              />
            </div>
          </div>

          <div className="flex flex-col gap-stack-compact">
            <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant" htmlFor="sifre">
              Şifre
            </label>
            <div className="relative">
              <Icon name="key" className="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[18px]" />
              <input
                id="sifre"
                type={sifreGoster ? "text" : "password"}
                required
                minLength={8}
                value={sifre}
                onChange={(e) => setSifre(e.target.value)}
                className="w-full bg-surface text-on-surface font-mono-data-md text-mono-data-md border border-outline-variant rounded-DEFAULT pl-10 pr-10 py-3 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder:text-outline-variant"
                placeholder="En az 8 karakter"
              />
              <button
                type="button"
                aria-label="Şifreyi göster"
                onClick={() => setSifreGoster((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary transition-colors"
              >
                <Icon name={sifreGoster ? "visibility_off" : "visibility"} className="text-[18px]" />
              </button>
            </div>
          </div>

          {hata && (
            <div className="border border-error/40 bg-error-container/20 text-error rounded-DEFAULT p-2.5 font-body-md text-body-md">
              {hata}
            </div>
          )}

          <button
            type="submit"
            disabled={yukleniyor}
            className="w-full bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold py-3 rounded-DEFAULT hover:bg-primary-fixed transition-colors flex items-center justify-center gap-2 uppercase tracking-wide group mt-1 disabled:opacity-50"
          >
            {yukleniyor ? "…" : mod === "giris" ? "Giriş Yap" : "Hesap Oluştur"}
            {!yukleniyor && <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />}
          </button>
        </form>

        <div className="mt-2 pt-4 border-t border-outline-variant flex items-center justify-center gap-2 text-on-surface-variant opacity-70">
          <Icon name="lock" className="text-[16px]" />
          <span className="font-mono-label-sm text-mono-label-sm text-[10px]">Uçtan Uca Şifreli Bağlantı</span>
        </div>
      </main>
    </div>
  );
}
