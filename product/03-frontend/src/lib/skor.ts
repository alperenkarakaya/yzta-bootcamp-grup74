// Paylaşılan skor sınıflandırma yardımcıları.
//
// §3b/U21: eşikler artık backend'den (/api/politika -> portfoy_esikleri) çekiliyor,
// burada ikinci kez ELLE YAZILMIYOR — önceki hardcoded 680/650 kopyası, backend'in
// varsayılanı değişirse fark etmeden kayabilirdi (drift riski, recon'da bulundu).
// `durumBelirle` senkron kalmalı (birçok sayfada render içinde inline çağrılıyor),
// bu yüzden değerler modül-seviyesi bir değişkende tutulup uygulama açılışında bir kez
// arka planda güncelleniyor; fetch tamamlanana kadar (veya başarısız olursa) backend'in
// BİLİNEN gerçek varsayılanı (680/650) fallback olarak kalıyor — davranış değişmiyor,
// yalnızca artık tek kaynaktan besleniyor.
import { api } from "../api";

let _esikler = { klasik_esik: 680, aks_esik: 650 };
let _yuklendi = false;

export function politikaEsikleriniYukle(): void {
  if (_yuklendi) return;
  _yuklendi = true;
  api
    .politika()
    .then((p) => {
      if (p.portfoy_esikleri) _esikler = p.portfoy_esikleri;
    })
    .catch(() => {
      /* fallback değerlerle devam — arayüz backend'e bağımlı kalmamalı */
    });
}

export type Durum = "kurtarildi" | "onaylandi" | "reddedildi";

export function durumBelirle(klasikSkor: number | null, aksSkor: number): Durum {
  const klasikRed = klasikSkor != null && klasikSkor < _esikler.klasik_esik;
  const aksOnay = aksSkor >= _esikler.aks_esik;
  if (klasikRed && aksOnay) return "kurtarildi";
  if (aksOnay) return "onaylandi";
  return "reddedildi";
}

export const DURUM_ETIKET: Record<Durum, string> = {
  kurtarildi: "Kurtarıldı",
  onaylandi: "Onaylandı",
  reddedildi: "Reddedildi",
};

export function skorDeltaYuzde(klasikSkor: number | null, aksSkor: number): number | null {
  if (klasikSkor == null || klasikSkor === 0) return null;
  return ((aksSkor - klasikSkor) / klasikSkor) * 100;
}

// AKS skoru 300-850 aralığında; 0-100 arası normalize kapasite göstergesi
// ("model confidence" DEĞİL — Stitch tasarımındaki uydurma "confidence" yerine
// gerçek, hesaplanmış bir büyüklük).
export function kapasiteYuzdesi(aksSkor: number): number {
  return Math.round(((aksSkor - 300) / (850 - 300)) * 100);
}

export function paraFormat(deger: number | null | undefined): string {
  if (deger == null) return "—";
  return `${deger.toLocaleString("tr-TR")} TL`;
}
