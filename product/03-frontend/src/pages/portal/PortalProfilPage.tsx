import { useEffect, useRef, useState } from "react";
import { api, type ProfilBilgisi } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kullanıcının kimlik-katmanı görünümü: AKS numarası
// (kimlik numarası gibi davranan ama hiçbir resmi kimlikten türetilmemiş
// pseudonim tanımlayıcı) + opsiyonel telefon doğrulama (OTP).
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_profilim
// ("AKS Terminal" — geniş AKS-ID kartı + 6 kutulu OTP girişi). OTP kutuları
// gerçek: 6 ayrı input, otomatik odak ilerletme/backspace, birleştirilip TEK
// bir `kod` string'i olarak `api.telefonDogrula()`'ya gönderiliyor — mockup'ın
// sahte "02:59" geri sayımı ve maskeli "555 *** ** 99" telefon göstergesi
// KULLANILMADI (elimizde gerçek bir maskeli numara/canlı geri sayım yok,
// yalnızca `gecerlilik_dakika` var — onu metinle gösteriyoruz).
export default function PortalProfilPage() {
  const [profil, setProfil] = useState<ProfilBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [kopyalandi, setKopyalandi] = useState(false);

  const [telefon, setTelefon] = useState("");
  const [dogrulamaId, setDogrulamaId] = useState<number | null>(null);
  const [gecerlilikDk, setGecerlilikDk] = useState<number | null>(null);
  const [debugKod, setDebugKod] = useState<string | null>(null);
  const [otpHaneler, setOtpHaneler] = useState<string[]>(["", "", "", "", "", ""]);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [hata, setHata] = useState("");
  const [mesaj, setMesaj] = useState("");
  const [isleniyor, setIsleniyor] = useState(false);

  function yenile() {
    setYukleniyor(true);
    api
      .profilim()
      .then(setProfil)
      .catch(() => setHata("Profil yüklenemedi"))
      .finally(() => setYukleniyor(false));
  }

  useEffect(yenile, []);

  async function kopyala() {
    if (!profil) return;
    await navigator.clipboard.writeText(profil.aks_no);
    setKopyalandi(true);
    setTimeout(() => setKopyalandi(false), 1500);
  }

  async function kodGonder() {
    setHata("");
    setMesaj("");
    setIsleniyor(true);
    try {
      const r = await api.telefonGonder(telefon);
      setDogrulamaId(r.dogrulama_id);
      setGecerlilikDk(r.gecerlilik_dakika);
      setDebugKod(r.demo_kod ?? r.debug_kod ?? null);
      setOtpHaneler(["", "", "", "", "", ""]);
      setMesaj(`Doğrulama kodu gönderildi (${r.gecerlilik_dakika} dakika geçerli).`);
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  function otpDegisti(i: number, deger: string) {
    const hane = deger.replace(/\D/g, "").slice(-1);
    setOtpHaneler((prev) => {
      const yeni = [...prev];
      yeni[i] = hane;
      return yeni;
    });
    if (hane && i < 5) otpRefs.current[i + 1]?.focus();
  }

  function otpTusVuruldu(i: number, e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Backspace" && !otpHaneler[i] && i > 0) otpRefs.current[i - 1]?.focus();
  }

  async function kodDogrula() {
    if (dogrulamaId === null) return;
    setHata("");
    setIsleniyor(true);
    try {
      await api.telefonDogrula(dogrulamaId, otpHaneler.join(""));
      setMesaj("Telefon doğrulandı.");
      setDogrulamaId(null);
      yenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  const kodTam = otpHaneler.every((h) => h !== "");

  if (yukleniyor) {
    return <p className="font-body-md text-body-md text-on-surface-variant">Yükleniyor…</p>;
  }
  if (!profil) {
    return <p className="font-body-md text-body-md text-error">{hata || "Profil bulunamadı"}</p>;
  }

  return (
    <div className="flex flex-col gap-stack-default">
      <header>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Güvenlik &amp; Kimlik</h2>
        <p className="font-mono-data-md text-mono-data-md text-on-surface-variant mt-2">
          Kimlik bilgisi (isim/soyisim/TCKN) tutmuyoruz — yalnızca AKS numaranızla tanımlanıyorsunuz.
        </p>
      </header>

      {/* AKS ID Card */}
      <div className="bg-surface-container border border-outline-variant rounded-lg p-6 relative overflow-hidden hover:border-primary-container transition-colors duration-300">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-primary">
              <Icon name="badge" className="text-sm" />
              <span className="font-mono-label-sm text-mono-label-sm uppercase tracking-widest text-primary-fixed-dim">
                AKS Kimlik Numarası
              </span>
            </div>
            <div className="font-mono-score-lg text-mono-score-lg text-on-surface tracking-tight mt-2">{profil.aks_no}</div>
            <p className="font-mono-label-sm text-mono-label-sm text-on-surface-variant opacity-70 mt-1">
              Bir kuruma hesap açtırırken bu numarayı verebilirsiniz.
            </p>
          </div>
          <button
            onClick={kopyala}
            className="flex items-center gap-2 bg-surface-container-high hover:bg-surface-bright border border-outline-variant hover:border-primary text-on-surface font-mono-label-sm text-mono-label-sm px-4 py-3 rounded-DEFAULT transition-all active:scale-95"
          >
            <Icon name={kopyalandi ? "check" : "content_copy"} className="text-base" />
            {kopyalandi ? "Kopyalandı" : "Kopyala"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-gutter">
        {/* Phone Verification */}
        <div className="bg-surface-container-low border border-outline-variant rounded-lg p-6 flex flex-col">
          <div className="flex items-center gap-3 border-b border-outline-variant pb-4 mb-6">
            <Icon name="phonelink_lock" className="text-secondary" />
            <h3 className="font-headline-md text-headline-md text-on-surface">Telefon Doğrulama</h3>
            {profil.telefon_dogrulandi_mi && (
              <span className="text-secondary flex items-center gap-1 ml-auto">
                <Icon name="verified" className="text-[16px]" filled /> Doğrulandı
              </span>
            )}
          </div>

          {!profil.telefon_dogrulandi_mi && (
            <div className="flex flex-col gap-stack-default flex-grow">
              <p className="font-body-md text-body-md text-on-surface-variant">
                Aynı telefon numarası yalnızca bir hesaba bağlanabilir — bu, birinin sizin adınıza ikinci bir hesap
                açmasını zorlaştırır.
              </p>

              <div className="flex flex-col gap-2">
                <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Kayıtlı GSM Numarası</label>
                <div className="flex gap-2">
                  <input
                    value={telefon}
                    onChange={(e) => setTelefon(e.target.value)}
                    placeholder="+905551112233"
                    disabled={!!dogrulamaId}
                    className="flex-grow bg-surface-container-lowest border border-outline-variant rounded-DEFAULT px-4 py-3 font-mono-data-md text-mono-data-md text-on-surface focus:outline-none focus:border-primary disabled:opacity-60"
                  />
                  <button
                    onClick={kodGonder}
                    disabled={!telefon || isleniyor}
                    className="bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold px-6 rounded-DEFAULT hover:opacity-90 transition-opacity whitespace-nowrap disabled:opacity-40"
                  >
                    Kod Gönder
                  </button>
                </div>
              </div>

              {dogrulamaId && (
                <>
                  <div className="flex items-center justify-center py-2">
                    <div className="h-[1px] w-full bg-outline-variant opacity-30" />
                    <Icon name="arrow_downward" className="text-outline-variant mx-4 text-sm opacity-50" />
                    <div className="h-[1px] w-full bg-outline-variant opacity-30" />
                  </div>
                  <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-end">
                      <label className="font-mono-label-sm text-mono-label-sm text-on-surface-variant">Doğrulama Kodu (OTP)</label>
                      {gecerlilikDk != null && (
                        <span className="font-mono-label-sm text-mono-label-sm text-tertiary flex items-center gap-1">
                          <Icon name="timer" className="text-[14px]" />
                          {gecerlilikDk} dk geçerli
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2 justify-between">
                      {otpHaneler.map((h, i) => (
                        <input
                          key={i}
                          ref={(el) => {
                            otpRefs.current[i] = el;
                          }}
                          value={h}
                          onChange={(e) => otpDegisti(i, e.target.value)}
                          onKeyDown={(e) => otpTusVuruldu(i, e)}
                          maxLength={1}
                          type="number"
                          placeholder="·"
                          className="w-full max-w-[48px] h-14 bg-surface-container-lowest border border-outline-variant rounded-DEFAULT text-center font-mono-score-lg text-mono-score-lg text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
                        />
                      ))}
                    </div>
                    <button
                      onClick={kodDogrula}
                      disabled={!kodTam || isleniyor}
                      className="w-full bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold py-3 rounded-DEFAULT disabled:opacity-40"
                    >
                      {isleniyor ? "…" : "Doğrula"}
                    </button>
                  </div>
                </>
              )}

              {debugKod && (
                <p className="font-mono-label-sm text-[11px] text-caveat">Demo modu — doğrulama kodunuz: {debugKod}</p>
              )}
              {mesaj && <p className="font-mono-label-sm text-[11px] text-secondary">{mesaj}</p>}
              {hata && <p className="font-mono-label-sm text-[11px] text-error">{hata}</p>}
            </div>
          )}
        </div>

        {/* Security note */}
        <div className="bg-surface border-l-2 border-caveat p-4 flex items-start gap-3 h-fit">
          <Icon name="warning" className="text-caveat text-xl mt-0.5" filled />
          <div>
            <h4 className="font-mono-data-md text-mono-data-md text-on-surface mb-1">Güvenlik Uyarısı</h4>
            <p className="font-body-md text-body-md text-on-surface-variant">
              Doğrulama kodunuzu personel dahil hiç kimseyle paylaşmayınız.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
