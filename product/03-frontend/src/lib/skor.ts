// Paylaşılan skor sınıflandırma yardımcıları.
// Eşikler backend'in gerçek varsayılanlarıyla birebir aynı (services.py::portfoy/adalet
// varsayılan parametreleri klasik_esik=680, aks_esik=650) — arayüz kendi eşiğini icat etmez.
export const KLASIK_ESIK = 680;
export const AKS_ESIK = 650;

export type Durum = "kurtarildi" | "onaylandi" | "reddedildi";

export function durumBelirle(klasikSkor: number | null, aksSkor: number): Durum {
  const klasikRed = klasikSkor != null && klasikSkor < KLASIK_ESIK;
  const aksOnay = aksSkor >= AKS_ESIK;
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
