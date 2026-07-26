import { useEffect, useState } from "react";
import { api, type ProfilBilgisi } from "../../api";
import { Icon } from "../../components/Icon";

// §3b Phase 7/7.2 — kullanıcının kimlik-katmanı görünümü: AKS numarası
// (kimlik numarası gibi davranan ama hiçbir resmi kimlikten türetilmemiş
// pseudonim tanımlayıcı) + opsiyonel telefon doğrulama (OTP).
export default function PortalProfilPage() {
  const [profil, setProfil] = useState<ProfilBilgisi | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [kopyalandi, setKopyalandi] = useState(false);

  const [telefon, setTelefon] = useState("");
  const [dogrulamaId, setDogrulamaId] = useState<number | null>(null);
  const [debugKod, setDebugKod] = useState<string | null>(null);
  const [kod, setKod] = useState("");
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
      setDebugKod(r.debug_kod ?? null);
      setMesaj(`Doğrulama kodu gönderildi (${r.gecerlilik_dakika} dakika geçerli).`);
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  async function kodDogrula() {
    if (dogrulamaId === null) return;
    setHata("");
    setIsleniyor(true);
    try {
      await api.telefonDogrula(dogrulamaId, kod);
      setMesaj("Telefon doğrulandı.");
      setDogrulamaId(null);
      yenile();
    } catch (e) {
      setHata(String(e instanceof Error ? e.message : e));
    } finally {
      setIsleniyor(false);
    }
  }

  if (yukleniyor) return <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>;
  if (!profil) return <p className="font-body-sm text-body-sm text-error">{hata || "Profil bulunamadı"}</p>;

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Profilim</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Kimlik bilgisi (isim/soyisim/TCKN) tutmuyoruz — yalnızca bu numara ile tanımlanıyorsunuz. Bir kuruma
          hesap açtırırken bu numarayı verebilirsiniz.
        </p>
      </header>

      <section className="card-surface rounded-lg p-6 flex flex-col items-center text-center gap-3">
        <span className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider">
          AKS Numaranız
        </span>
        <span className="font-display-md text-display-md text-primary tracking-wider">{profil.aks_no}</span>
        <button
          onClick={kopyala}
          className="flex items-center gap-2 px-4 py-2 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono text-on-surface hover:bg-surface-container transition-colors"
        >
          <Icon name={kopyalandi ? "check" : "content_copy"} className="text-[16px]" />
          {kopyalandi ? "Kopyalandı" : "Kopyala"}
        </button>
      </section>

      <section className="bg-surface-container hairline-border rounded-xl p-6">
        <h2 className="font-label-mono text-label-mono text-on-surface-variant uppercase tracking-wider mb-4 flex items-center gap-2">
          Telefon Doğrulama
          {profil.telefon_dogrulandi_mi && (
            <span className="text-emerald-400 flex items-center gap-1">
              <Icon name="verified" className="text-[16px]" /> Doğrulandı
            </span>
          )}
        </h2>

        {!profil.telefon_dogrulandi_mi && (
          <div className="flex flex-col gap-4 max-w-sm">
            <p className="font-body-sm text-body-sm text-on-surface-variant">
              Aynı telefon numarası yalnızca bir hesaba bağlanabilir — bu, birinin sizin adınıza ikinci bir hesap
              açmasını zorlaştırır (SMS sağlayıcısı henüz demo modda; kod aşağıda görünür).
            </p>
            {!dogrulamaId ? (
              <div className="flex gap-2">
                <input
                  value={telefon}
                  onChange={(e) => setTelefon(e.target.value)}
                  placeholder="+905551112233"
                  className="flex-1 bg-surface-container-low border border-outline-variant/40 rounded-DEFAULT px-3 py-2 font-body-sm text-body-sm text-on-surface"
                />
                <button
                  onClick={kodGonder}
                  disabled={!telefon || isleniyor}
                  className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                >
                  Kod Gönder
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  value={kod}
                  onChange={(e) => setKod(e.target.value)}
                  placeholder="6 haneli kod"
                  className="flex-1 bg-surface-container-low border border-outline-variant/40 rounded-DEFAULT px-3 py-2 font-body-sm text-body-sm text-on-surface"
                />
                <button
                  onClick={kodDogrula}
                  disabled={!kod || isleniyor}
                  className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono disabled:opacity-40"
                >
                  Doğrula
                </button>
              </div>
            )}
            {debugKod && (
              <p className="font-label-mono text-[11px] text-amber-400">
                DEBUG modu: kod = {debugKod} (SMS sağlayıcısı kurulana kadar geçici)
              </p>
            )}
            {mesaj && <p className="font-label-mono text-[11px] text-emerald-400">{mesaj}</p>}
            {hata && <p className="font-label-mono text-[11px] text-error">{hata}</p>}
          </div>
        )}
      </section>
    </div>
  );
}
