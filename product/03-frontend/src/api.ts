// AKS API istemcisi — Django backend (/api).
// Dev'de Vite proxy /api -> localhost:8000 yönlendirir.

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

export interface SkorSonuc {
  musteri_id: number;
  persona: string;
  klasik_skor: number | null;
  aks_skor: number;
  onerilen_limit: number | null;
  risk_seviyesi: string;
  karar: string;
  ozellikler: Record<string, number>;
  aciklama: unknown;
  danisman: unknown;
}

export interface Portfoy {
  toplam_musteri: number;
  kredibl_red: number;
  kurtarilan: number;
  kurtarma_orani: number;
  illustratif_getiri: { net: number; potansiyel_kazanc: number; beklenen_kayip: number };
  persona_kirilimi: Record<string, number>;
}

export const api = {
  bilgi: () => get<Bilgi>("/bilgi"),
  demoMusteriler: () => get<Record<string, number[]>>("/demo-musteriler"),
  skorlaDemo: (id: number) => get<SkorSonuc>(`/skorla/${id}`),
  portfoy: () => get<Portfoy>("/portfoy"),
  asistan: (soru: string, baglam: unknown = {}) =>
    post<Record<string, unknown>>("/asistan", { soru, baglam }),
};
