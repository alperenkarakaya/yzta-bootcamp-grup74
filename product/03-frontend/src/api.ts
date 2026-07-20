// AKS API istemcisi — Django backend (/api).
// Dev'de Vite proxy /api -> localhost:8000 yönlendirir.
// Bu istemcideki her alan product/04-backend/api/{views,services}.py ve
// aks_core/model/{adalet,aciklama}.py, aks_core/agents/danisman_agent.py'nin
// gerçek dönüş şekliyle birebir eşleşir — arayüzde uydurma veri yoktur.

const BASE = import.meta.env.VITE_API_BASE ?? "";

async function get<T>(yol: string): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}
async function post<T>(yol: string, govde: unknown): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(govde),
  });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export interface Bilgi {
  servis: string;
  surum: string;
  model: string;
  ozellikler: string[];
  demo_musteri_sayisi: number;
}

export interface FaktorEtki {
  faktor: string;
  kod: string;
  etki: number;
}

export interface Aciklama {
  riski_artiran: FaktorEtki[];
  riski_azaltan: FaktorEtki[];
}

export interface Danisman {
  ozet: string;
  oneriler: string[];
  dogal_dil?: string;
  dogal_dil_hatasi?: string;
}

export interface SkorSonuc {
  musteri_id: number;
  persona: string;
  klasik_skor: number | null;
  aks_skor: number;
  onerilen_limit: number | null;
  risk_seviyesi: string;
  karar: string;
  ozellikler: Record<string, number>;
  aciklama: Aciklama;
  danisman: Danisman;
  // Formülasyon B (architecture.md §5.3, §3b U10/U17) — klasik_skor bilinmiyorsa null.
  pd_geleneksel_bant: number | null;
  pd_fark: number | null;
  kapasite_sinyali: number | null;
}

export interface Portfoy {
  toplam_musteri: number;
  klasik_red: number;
  kredibl_red: number;
  kurtarilan: number;
  kurtarma_orani: number;
  yanlis_onay: number;
  yanlis_onay_orani: number;
  persona_kirilimi: Record<string, number>;
  illustratif_getiri: {
    varsayimlar: { ort_kredi: number; getiri_orani: number; zarar_orani: number };
    potansiyel_kazanc: number;
    beklenen_kayip: number;
    net: number;
  };
}

export interface GrupMetrik {
  n: number;
  onay_orani: number;
  kredibl_onay_orani_tpr: number;
  yanlis_onay_orani: number;
}

export interface AdaletAlan {
  gruplar: Record<string, GrupMetrik>;
  equal_opportunity_boslugu: number;
}

export interface Adalet {
  klasik_skor: AdaletAlan;
  aks_skor: AdaletAlan;
}

export interface GecmisKayit {
  zaman: string;
  aks_skor: number;
  risk_seviyesi: string;
}

export interface GecmisYanit {
  musteri_id: number;
  degerlendirme_sayisi: number;
  gecmis: GecmisKayit[];
}

export interface AsistanYanit {
  yanit: string;
  mod: "llm" | "kural";
}

// §3b/U15 — degerlendirme.py'nin (rigorous CV+CI+kalibrasyon harness'i) persist ettiği
// rapor. metrikler.json (egit()'in hızlı tek-split sağlık kontrolü) DEĞİL — bu "resmi"
// (raporlanabilir) kaynak.
export interface ModelMetrik {
  ad: string;
  roc_auc: { ortalama: number; std: number; ci95: [number, number] };
  pr_auc: { ortalama: number; std: number; ci95: [number, number] };
  brier_oof: number;
  ece_oof: number;
  reliability: { tahmin: number; gozlenen: number; n: number }[];
  persona_metrik: Record<string, { auc: number; brier: number; n: number }>;
}

export interface MetriklerRaporu {
  zaman: string;
  veri_kaynagi: "dekuple" | "dongusel";
  n_musteri: number;
  taban_temerrut_orani: number;
  yontem: string;
  modeller: ModelMetrik[];
}

// §3b/U16 — karar mekanizması politikası: tekil AKS bantları + toplu portföy eşikleri.
export interface PolitikaBant {
  esik: number;
  seviye: string;
  karar: string;
  carpan: number;
}

export interface Politika {
  surum: string;
  bantlar: PolitikaBant[];
  portfoy_esikleri: { klasik_esik: number; aks_esik: number };
}

// Bilinen 4 persona (aks_core/ozellik + model/etiketleme'de sabit) — tasarımdaki
// uydurma segment adları ("Digital Nomads" vb.) yerine gerçek etiketler.
export const PERSONA_ETIKET: Record<string, string> = {
  ogrenci_yuksek_hacim: "Öğrenci (Yüksek Hacim)",
  stajyer_degisken_gelir: "Stajyer / Değişken Gelir",
  klasik_maasli: "Klasik Maaşlı",
  dusuk_hacim_riskli: "Düşük Hacim (Riskli)",
};

export const HEDEF_PERSONALAR = ["ogrenci_yuksek_hacim", "stajyer_degisken_gelir"];

export const api = {
  bilgi: () => get<Bilgi>("/bilgi"),
  demoMusteriler: (adetPerPersona = 8) =>
    get<Record<string, number[]>>(`/demo-musteriler?adet_per_persona=${adetPerPersona}`),
  skorlaDemo: (id: number) => get<SkorSonuc>(`/skorla/${id}`),
  portfoy: () => get<Portfoy>("/portfoy"),
  adalet: () => get<Adalet>("/adalet"),
  gecmis: (id: number) => get<GecmisYanit>(`/gecmis/${id}`),
  asistan: (soru: string, baglam: unknown = {}) => post<AsistanYanit>("/asistan", { soru, baglam }),
  metrikler: () => get<MetriklerRaporu>("/metrikler"),
  politika: () => get<Politika>("/politika"),
};
