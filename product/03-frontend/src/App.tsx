import { useEffect, useState } from "react";
import { api, type Bilgi, type SkorSonuc, type Portfoy } from "./api";

// NOT: Bu, frontend<->backend döngüsünü kanıtlayan geçici bir yüzeydir.
// Google Stitch tasarımı geldiğinde bileşenler burada değiştirilecek;
// api.ts istemcisi ve Django uçları aynı kalır.

export default function App() {
  const [bilgi, setBilgi] = useState<Bilgi | null>(null);
  const [id, setId] = useState(1);
  const [skor, setSkor] = useState<SkorSonuc | null>(null);
  const [portfoy, setPortfoy] = useState<Portfoy | null>(null);
  const [hata, setHata] = useState<string>("");

  useEffect(() => {
    api.bilgi().then(setBilgi).catch((e) => setHata(String(e)));
    api.portfoy().then(setPortfoy).catch(() => {});
  }, []);

  async function skorla() {
    setHata("");
    try {
      setSkor(await api.skorlaDemo(id));
    } catch (e) {
      setHata(String(e));
    }
  }

  return (
    <main className="wrap">
      <header>
        <h1>AKS — Alternatif Kapasite Skoru</h1>
        <p className="alt">
          {bilgi ? `${bilgi.servis} · ${bilgi.surum} · model: ${bilgi.model} · ${bilgi.demo_musteri_sayisi} demo müşteri` : "backend'e bağlanılıyor…"}
        </p>
        <p className="rozet">Sınır: AKS bankanın segmentini <b>ezmez</b>, yalnızca tamamlar.</p>
      </header>

      {hata && <div className="hata">Backend hatası: {hata} — Django çalışıyor mu? (uvicorn değil: <code>python manage.py runserver</code>)</div>}

      <section className="kart">
        <h2>Müşteri Değerlendirme</h2>
        <div className="satir">
          <label>Demo müşteri ID: <input type="number" value={id} min={1} onChange={(e) => setId(Number(e.target.value))} /></label>
          <button onClick={skorla}>Skorla</button>
        </div>
        {skor && (
          <div className="sonuc">
            <div className="skorlar">
              <div className="skorkutu klasik"><span>Klasik (banka)</span><b>{skor.klasik_skor ?? "—"}</b></div>
              <div className="ok">→ tamamlanır →</div>
              <div className="skorkutu aks"><span>AKS</span><b>{skor.aks_skor}</b></div>
            </div>
            <ul>
              <li>Persona: <b>{skor.persona}</b></li>
              <li>Risk: <b>{skor.risk_seviyesi}</b></li>
              <li>Karar: <b>{skor.karar}</b></li>
              <li>Önerilen limit: <b>{skor.onerilen_limit != null ? `${skor.onerilen_limit.toLocaleString("tr-TR")} ₺` : "—"}</b></li>
            </ul>
          </div>
        )}
      </section>

      {portfoy && (
        <section className="kart">
          <h2>Banka Portföyü (illüstratif)</h2>
          <p>
            Klasik skorun reddettiği kredibl <b>{portfoy.kredibl_red}</b> kişiden{" "}
            <b>{portfoy.kurtarilan}</b> tanesi ({Math.round(portfoy.kurtarma_orani * 100)}%) AKS ile kurtarılıyor.
            Net illüstratif getiri: <b>{portfoy.illustratif_getiri.net.toLocaleString("tr-TR")} ₺</b>.
          </p>
        </section>
      )}

      <footer className="alt">Placeholder arayüz — Google Stitch tasarımı entegre edilecek (03-frontend).</footer>
    </main>
  );
}
