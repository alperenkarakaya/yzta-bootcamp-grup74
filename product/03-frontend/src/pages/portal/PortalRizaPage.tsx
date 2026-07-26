import { useEffect, useState } from "react";
import { api, type RizaDefteriKaydi } from "../../api";

const OLAY_ETIKET: Record<string, string> = {
  talep_olusturuldu: "Talep oluşturuldu",
  onaylandi: "Onayladınız",
  reddedildi: "Reddettiniz",
  iptal_edildi: "İptal ettiniz",
  erisim_kullanildi: "Kurum verinize erişti",
};

// §3b Phase 7/7.2 — değiştirilemez rıza defterinin (kimlik.RizaKaydi,
// append-only) doğrudan okunabilir hâli: kim, ne zaman, ne için erişti/
// erişmeye çalıştı. "Engelleme değil, hesap verebilirlik" iddiasının kanıtı.
export default function PortalRizaPage() {
  const [kayitlar, setKayitlar] = useState<RizaDefteriKaydi[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  useEffect(() => {
    api
      .rizaDefterim()
      .then((r) => setKayitlar(r.kayitlar))
      .finally(() => setYukleniyor(false));
  }, []);

  return (
    <div className="flex flex-col gap-stack-lg pb-8">
      <header>
        <h1 className="font-headline-md text-headline-md text-on-background">Rıza Defterim</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-1">
          Verinize dair her olay (talep, onay, ret, iptal, erişim) buraya değiştirilemez şekilde yazılır.
        </p>
      </header>

      {yukleniyor ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <p className="font-body-sm text-body-sm text-on-surface-variant">Henüz bir kayıt yok.</p>
      ) : (
        <ol className="flex flex-col gap-2">
          {kayitlar.map((k) => (
            <li
              key={k.id}
              className="bg-surface-container hairline-border rounded-lg p-4 flex justify-between items-center flex-wrap gap-2"
            >
              <div>
                <div className="font-body-sm text-body-sm text-on-surface">
                  {OLAY_ETIKET[k.olay] ?? k.olay} — <span className="text-on-surface-variant">{k.kurum}</span>
                </div>
                <div className="font-label-mono text-[10px] text-on-surface-variant mt-1">{k.amac}</div>
              </div>
              <span className="font-label-mono text-[10px] text-on-surface-variant">
                {k.created_at.replace("T", " ")}
              </span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
