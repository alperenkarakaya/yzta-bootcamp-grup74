import { useEffect, useState } from "react";
import { api, type RizaDefteriKaydi } from "../../api";
import { Icon } from "../../components/Icon";

const OLAY_META: Record<string, { etiket: string; ikon: string; renk: string; nokta: string }> = {
  talep_olusturuldu: {
    etiket: "Talep Oluşturuldu",
    ikon: "add_circle",
    renk: "bg-surface-container-highest border-outline text-on-surface-variant",
    nokta: "border-outline group-hover:bg-outline",
  },
  onaylandi: {
    etiket: "Onaylandı",
    ikon: "check_circle",
    renk: "bg-secondary/10 border-secondary/30 text-secondary",
    nokta: "border-secondary group-hover:bg-secondary",
  },
  reddedildi: {
    etiket: "Reddedildi",
    ikon: "cancel",
    renk: "bg-error/10 border-error/30 text-error",
    nokta: "border-error group-hover:bg-error",
  },
  iptal_edildi: {
    etiket: "İptal Edildi",
    ikon: "block",
    renk: "bg-surface-variant border-outline-variant text-on-surface-variant",
    nokta: "border-outline-variant group-hover:bg-outline-variant",
  },
  erisim_kullanildi: {
    etiket: "Erişim Kullanıldı",
    ikon: "visibility",
    renk: "bg-primary-container/20 border-primary-container/30 text-primary-fixed",
    nokta: "border-primary group-hover:bg-primary",
  },
};

// §3b Phase 7/7.2 — değiştirilemez rıza defterinin (kimlik.RizaKaydi,
// append-only) doğrudan okunabilir hâli: kim, ne zaman, ne için erişti/
// erişmeye çalıştı. "Engelleme değil, hesap verebilirlik" iddiasının kanıtı.
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu/aks_portal_r_za_defterim
// ("AKS Terminal" — dikey zaman çizelgesi, olay bazlı rozet). Mockup'ın "blokzincir
// altyapısı" iddiası ve sahte "0x7a2b9f4e..." imza dizeleri KULLANILMADI —
// gerçek güvence Django'nun append-only DB kısıtı (RizaKaydi.save/delete
// engeli), blokzincir değil; yanlış bir teknik iddia göstermek proje etiğine
// aykırı olurdu. Banner bu yüzden gerçek mekanizmayı anlatıyor.
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
    <div className="flex flex-col gap-stack-default">
      <header className="flex flex-col gap-2 border-b border-outline-variant pb-4">
        <h1 className="font-headline-lg text-headline-lg text-on-surface">Rıza Defterim</h1>
        <p className="font-body-md text-body-md text-on-surface-variant max-w-2xl">
          Kişisel verilerinize erişim sağlayan kurumların onay ve işlem geçmişini içeren, değiştirilemez denetim
          kaydı.
        </p>
      </header>

      <div className="caveat-banner border rounded-DEFAULT p-4 flex gap-3 items-start">
        <Icon name="policy" className="text-caveat text-[20px] shrink-0 mt-0.5" />
        <div className="flex flex-col gap-1">
          <span className="font-mono-label-sm text-mono-label-sm text-caveat font-bold uppercase tracking-wider">
            Salt-Okunur Denetim İzi
          </span>
          <span className="font-body-md text-body-md text-on-surface-variant">
            Bu defterdeki kayıtlar veritabanı düzeyinde değiştirilemez/silinemez şekilde korunur (append-only) — bir
            kayıt yazıldıktan sonra hiçbir kullanıcı, kurum ya da yönetici onu geriye dönük düzenleyemez.
          </span>
        </div>
      </div>

      {yukleniyor ? (
        <p className="font-body-md text-body-md text-on-surface-variant">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <p className="font-body-md text-body-md text-on-surface-variant">Henüz bir kayıt yok.</p>
      ) : (
        <div className="flex flex-col w-full relative">
          <div className="absolute left-[11px] top-4 bottom-4 w-px bg-outline-variant z-0 hidden sm:block" />
          <ol className="space-y-stack-default z-10 w-full">
            {kayitlar.map((k) => {
              const meta = OLAY_META[k.olay] ?? OLAY_META.talep_olusturuldu;
              return (
                <li
                  key={k.id}
                  className="group relative flex flex-col sm:flex-row bg-surface-container-low border border-outline-variant rounded-DEFAULT p-4 hover:border-primary-fixed transition-colors duration-300 w-full ml-0 sm:ml-8 sm:w-[calc(100%-2rem)]"
                >
                  <div
                    className={`hidden sm:block absolute -left-6 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-surface border-2 transition-colors ${meta.nokta}`}
                  />
                  <div className="flex-grow flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex flex-col gap-1.5">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-headline-md text-headline-md text-on-surface text-lg">{k.kurum}</span>
                        <span className={`px-2 py-0.5 rounded-DEFAULT border font-mono-label-sm text-mono-label-sm flex items-center gap-1 ${meta.renk}`}>
                          <Icon name={meta.ikon} className="text-[14px]" />
                          {meta.etiket}
                        </span>
                      </div>
                      <span className="font-body-md text-body-md text-on-surface-variant">{k.amac}</span>
                    </div>
                    <div className="flex flex-col md:items-end gap-1 border-t border-outline-variant md:border-t-0 pt-3 md:pt-0 mt-2 md:mt-0">
                      <div className="flex items-center gap-1 text-on-surface-variant">
                        <Icon name="schedule" className="text-[14px]" />
                        <span className="font-mono-label-sm text-mono-label-sm">{k.created_at.replace("T", " ")}</span>
                      </div>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </div>
      )}
    </div>
  );
}
