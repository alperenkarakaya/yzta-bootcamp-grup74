import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, PERSONA_ETIKET, HEDEF_PERSONALAR, type SkorSonuc } from "../api";
import { Icon } from "../components/Icon";
import { durumBelirle, kapasiteYuzdesi, skorDeltaYuzde, type Durum } from "../lib/skor";

interface Satir extends SkorSonuc {
  id: number;
}

const ADET_PER_PERSONA = 6;

type Filtre = "hepsi" | "kurtarildi" | "reddedildi" | "hedef";

// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_m_teri_listesi
// ("AKS Terminal" — data-dense tablo, zebra-row, sticky header). Stitch
// mockup'ı uydurma isimler ve "PROFİL" etiketleri (Ahmet Yılmaz, Kurumsal,
// vb.) gösteriyordu — hiçbiri gerçek değil (proje isim/kişisel veri
// TOPLAMIYOR, bkz. execution.md §3b Phase 7 "minimum kişisel veri" kararı;
// uydurma isim göstermek hem yanlış hem tutarsız olurdu). Görsel dil
// (tablo/zebra/pill/sticky header) korunuyor, veri GERÇEK: risk bandı pill'i
// gerçek `risk_seviyesi` alanından, isim yerine persona etiketi.
function riskRenk(riskSeviyesi: string): { metin: string; nokta: string; sinir: string; zemin: string } {
  if (riskSeviyesi.includes("yüksek")) {
    return { metin: "text-error", nokta: "bg-error", sinir: "border-error/30", zemin: "bg-error-container/20" };
  }
  if (riskSeviyesi.includes("düşük")) {
    return { metin: "text-secondary", nokta: "bg-secondary", sinir: "border-secondary/20", zemin: "bg-secondary/10" };
  }
  return { metin: "text-caveat", nokta: "bg-caveat", sinir: "border-caveat/30", zemin: "bg-caveat/10" };
}

export default function CustomersPage() {
  const [satirlar, setSatirlar] = useState<Satir[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [evrenBuyuklugu, setEvrenBuyuklugu] = useState<number | null>(null);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [hata, setHata] = useState("");
  const [filtre, setFiltre] = useState<Filtre>("hepsi");
  const [arama, setArama] = useState("");

  useEffect(() => {
    let iptal = false;
    setYukleniyor(true);
    setSatirlar([]);
    setLog([]);
    api
      .bilgi()
      .then((b) => !iptal && setEvrenBuyuklugu(b.demo_musteri_sayisi))
      .catch(() => {});
    api
      .demoMusteriler(ADET_PER_PERSONA)
      .then(async (grup) => {
        const ids = Object.values(grup).flat();
        setLog((l) => [...l, `[INFO] ${ids.length} demo müşteri kimliği alındı`]);
        await Promise.all(
          ids.map(async (id) => {
            try {
              const s = await api.skorlaDemo(id);
              if (iptal) return;
              setSatirlar((prev) => [...prev, { ...s, id }].sort((a, b) => a.id - b.id));
              setLog((l) => [...l.slice(-30), `[OK] #${id} skorlandı → AKS ${s.aks_skor}`]);
            } catch {
              setLog((l) => [...l.slice(-30), `[ERR] #${id} skorlanamadı`]);
            }
          })
        );
      })
      .catch((e) => setHata(String(e)))
      .finally(() => !iptal && setYukleniyor(false));
    return () => {
      iptal = true;
    };
  }, []);

  const filtreli = useMemo(() => {
    return satirlar.filter((s) => {
      const durum: Durum = durumBelirle(s.klasik_skor, s.aks_skor);
      if (filtre === "kurtarildi" && durum !== "kurtarildi") return false;
      if (filtre === "reddedildi" && durum !== "reddedildi") return false;
      if (filtre === "hedef" && !HEDEF_PERSONALAR.includes(s.persona)) return false;
      if (arama) {
        const q = arama.toLowerCase();
        const hit = String(s.id).includes(q) || (PERSONA_ETIKET[s.persona] ?? s.persona).toLowerCase().includes(q);
        if (!hit) return false;
      }
      return true;
    });
  }, [satirlar, filtre, arama]);

  const kurtarilanSayisi = satirlar.filter((s) => durumBelirle(s.klasik_skor, s.aks_skor) === "kurtarildi").length;

  return (
    <div className="flex flex-col gap-stack-default">
      {/* Header Actions & Search */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 w-full">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`w-2 h-2 rounded-full ${yukleniyor ? "bg-secondary pulse-dot" : "bg-secondary"}`} />
            <span className="font-mono-label-sm text-mono-label-sm text-secondary uppercase tracking-widest">
              {yukleniyor ? "Skorlanıyor…" : "Canlı Değerlendirme Kuyruğu"}
            </span>
          </div>
          <h1 className="text-headline-lg font-headline-lg text-on-background">Müşteri Listesi</h1>
          <p className="text-mono-label-sm font-mono-label-sm text-outline mt-1">
            {evrenBuyuklugu != null ? `Demo popülasyon · ${evrenBuyuklugu} kayıt` : "Demo popülasyon"} · Kurtarılan {kurtarilanSayisi}
          </p>
        </div>
        <div className="flex items-center gap-3 w-full md:w-auto flex-wrap">
          {([
            ["hepsi", "Tümü"],
            ["kurtarildi", "Kurtarılan"],
            ["reddedildi", "Reddedilen"],
            ["hedef", "Hedef Segment"],
          ] as [Filtre, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setFiltre(key)}
              className={`px-3 py-1.5 rounded-full font-mono-label-sm text-mono-label-sm transition-colors ${
                filtre === key ? "bg-primary-container text-on-primary-container" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {label}
            </button>
          ))}
          <div className="relative w-full md:w-56">
            <Icon name="search" className="absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]" />
            <input
              value={arama}
              onChange={(e) => setArama(e.target.value)}
              placeholder="ID veya persona ara…"
              className="w-full bg-surface-container-lowest border border-outline-variant rounded-DEFAULT pl-9 pr-3 py-2 text-mono-data-md font-mono-data-md text-on-background focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            />
          </div>
        </div>
      </div>

      {hata && (
        <div className="border border-error/40 bg-error-container/20 text-error p-3 font-mono-label-sm text-mono-label-sm">
          Backend hatası: {hata}
        </div>
      )}

      {/* Data Dense Table */}
      <div className="bg-surface-container-low border border-outline-variant flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-surface-dim border-b border-outline-variant sticky top-0 z-10">
              <tr>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline">MÜŞTERİ ID</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline">PERSONA</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline">KAPASİTE SİNYALİ</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline text-right">SKOR DEĞİŞİMİ</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline text-right">KLASİK SKOR</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-primary text-right">AKS SKORU</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline">RİSK BANDI</th>
                <th className="px-4 py-3 text-mono-label-sm font-mono-label-sm text-outline text-right">AKSİYON</th>
              </tr>
            </thead>
            <tbody className="text-mono-data-md font-mono-data-md">
              {filtreli.map((s) => {
                const durum = durumBelirle(s.klasik_skor, s.aks_skor);
                const delta = skorDeltaYuzde(s.klasik_skor, s.aks_skor);
                const kapasite = kapasiteYuzdesi(s.aks_skor);
                const risk = riskRenk(s.risk_seviyesi);
                const renk = durum === "kurtarildi" ? "text-secondary" : durum === "reddedildi" ? "text-error" : "text-primary";
                return (
                  <tr className="border-b border-outline-variant/30 zebra-row hover:bg-surface-container-high/50 transition-colors" key={s.id}>
                    <td className="px-4 py-3 text-outline-variant">#CST-{String(s.id).padStart(4, "0")}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="bg-surface-container px-2 py-0.5 rounded-DEFAULT text-mono-label-sm border border-outline-variant/50">
                          {PERSONA_ETIKET[s.persona] ?? s.persona}
                        </span>
                        {durum === "kurtarildi" && (
                          <span className="bg-secondary-container/30 text-secondary px-2 py-0.5 rounded-DEFAULT text-[10px] uppercase font-bold border border-secondary-container/50">
                            Kurtarıldı
                          </span>
                        )}
                        {s.anomali_bayrak && (
                          <span title="Atipik profil — anomali tespit edildi">
                            <Icon name="warning" className="text-caveat text-[16px]" />
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-1 bg-surface-container-highest overflow-hidden min-w-[60px]">
                          <div className={`h-full ${renk.replace("text-", "bg-")}`} style={{ width: `${kapasite}%` }} />
                        </div>
                        <span className={`font-mono-label-sm text-mono-label-sm ${renk}`}>{kapasite}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className={`font-bold ${delta != null && delta >= 0 ? "text-secondary" : "text-error"}`}>
                        {delta != null ? `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}%` : "—"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-on-surface-variant">{s.klasik_skor ?? "—"}</td>
                    <td className={`px-4 py-3 text-right font-bold border-l border-primary/30 ${renk}`}>{s.aks_skor}</td>
                    <td className="px-4 py-3">
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border ${risk.zemin} ${risk.sinir} ${risk.metin}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${risk.nokta}`} />
                        {s.risk_seviyesi}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/customers/${s.id}`}
                        className="font-bold text-mono-label-sm bg-primary-container text-on-primary-container px-3 py-1 rounded-DEFAULT hover:bg-primary-fixed transition-colors"
                      >
                        Detay
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className="border-t border-outline-variant bg-surface-dim px-4 py-3 flex items-center justify-between text-mono-label-sm font-mono-label-sm text-outline flex-wrap gap-2">
          <span>
            Gösterilen {filtreli.length} / yüklenen {satirlar.length}
            {evrenBuyuklugu != null && ` · demo evreni ${evrenBuyuklugu}`}
          </span>
        </div>
      </div>

      {/* Skorlama telemetrisi. Önceden `fixed` (sağ altta yüzen panel) idi ve
          `pointer-events-none` ile tıklamaların altına geçmesi sağlanmıştı —
          ama canlı tarayıcı denetiminde görüldü ki tablonun RİSK BANDI/AKSİYON
          kolonlarını GÖRSEL olarak kapatıyordu (tıklama geçse de içerik
          okunamıyordu). Normal akışa, tablonun altına alındı. */}
      <div className="bg-surface-container-high border border-outline-variant overflow-hidden">
        <div className="bg-surface-container-highest px-4 py-2 border-b border-outline-variant flex items-center justify-between">
          <span className="font-mono-label-sm text-mono-label-sm text-on-surface">Etkinlik Günlüğü</span>
          <span className="font-mono-label-sm text-mono-label-sm text-outline">
            {yukleniyor ? "skorlanıyor…" : "hazır"}
          </span>
        </div>
        <div className="p-4 font-mono-label-sm text-[11px] space-y-1.5 leading-relaxed max-h-40 overflow-y-auto">
          {log.slice(-12).map((l, i) => (
            <p key={i} className={l.startsWith("[ERR]") ? "text-error" : l.startsWith("[OK]") ? "text-on-surface-variant" : "text-primary"}>
              {l}
            </p>
          ))}
          {!yukleniyor && <p className="text-on-surface-variant opacity-40">&gt; hazır</p>}
        </div>
      </div>
    </div>
  );
}
