// AKS API istemcisi — Django backend (/api).
// Dev'de Vite proxy /api -> localhost:8000 yönlendirir.
// Bu istemcideki her alan product/04-backend/api/{views,services}.py ve
// aks_core/model/{adalet,aciklama}.py, aks_core/agents/danisman_agent.py'nin
// gerçek dönüş şekliyle birebir eşleşir — arayüzde uydurma veri yoktur.

const BASE = import.meta.env.VITE_API_BASE ?? "";

// §3b Phase 6 — kullanıcı portalı session çerezi (sessionid) + CSRF çerezi
// (csrftoken) kullanır. Vite dev proxy /api'yi aynı origin'den (localhost:5174)
// Django'ya yönlendirdiği için `credentials: "same-origin"` çerezlerin akmasına
// yeterli — cross-origin bir kuruluma geçilirse "include" + CORS_ALLOW_CREDENTIALS
// gerekir (bkz. architecture.md §11).
function csrfTokenAl(): string | null {
  const eslesme = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
  return eslesme ? decodeURIComponent(eslesme[1]) : null;
}

function _hataMesaji(govde: unknown, r: Response): string {
  const h = (govde as ApiHata)?.hata;
  if (h) return h;
  if (r.status === 401 || r.status === 403) return "Bu işlem için giriş yapmalısınız.";
  return `${r.status} ${r.statusText}`;
}

async function get<T>(yol: string): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`, { credentials: "same-origin" });
  const govde = await r.json().catch(() => null);
  if (!r.ok) throw new Error(_hataMesaji(govde, r));
  return govde as T;
}
async function post<T>(yol: string, govde: unknown): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(csrfTokenAl() ? { "X-CSRFToken": csrfTokenAl()! } : {}),
    },
    body: JSON.stringify(govde),
  });
  const yanit = await r.json().catch(() => null);
  if (!r.ok) throw new Error(_hataMesaji(yanit, r));
  return yanit as T;
}

// multipart/form-data — Content-Type header'ı elle KONMAZ, tarayıcı boundary'yi
// kendi ekler; elle "multipart/form-data" yazmak boundary'siz bırakır ve backend
// isteği parse edemez.
async function postDosya<T>(yol: string, form: FormData): Promise<T> {
  const r = await fetch(`${BASE}/api${yol}`, {
    method: "POST",
    credentials: "same-origin",
    headers: csrfTokenAl() ? { "X-CSRFToken": csrfTokenAl()! } : undefined,
    body: form,
  });
  const govde = await r.json();
  if (!r.ok) throw new Error(_hataMesaji(govde, r));
  return govde as T;
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
  // §3b/U25 — anomali.py (İzolasyon Ormanı, denetimsiz). Anomali modeli artifact'ı
  // yoksa (eski/yeniden eğitilmemiş kurulum) her ikisi de null — karar mekanizmasını
  // ASLA etkilemez, yalnızca ek bir şeffaflık sinyalidir.
  anomali_bayrak: boolean | null;
  anomali_skoru: number | null;
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
  // §3b/U17 (OQ-44 bulgusu): bu toplu istatistikler hâlâ döngüsel etiketli demo
  // verisinden geliyor — tekil skorlamadan (dekuple/LR) farklı bir kaynak.
  veri_kaynagi: "dongusel" | "dekuple";
  uyari: string;
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
  veri_kaynagi: "dongusel" | "dekuple";
  uyari: string;
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

// POST /api/csv-skorla (U24) — belge/ekstre yükleme (§3b Phase 7/7.1: artık
// CSV/XLSX/PDF üçünü de kabul eder). Persona bilinmediği için backend
// klasik_skor/Formülasyon B alanlarını hesaplamıyor (services.degerlendir
// yalnızca persona verilirse bunları doldurur) — SkorSonuc'tan kasıtlı olarak dar.
export interface BelgeMeta {
  kaynak_format: "csv" | "xlsx" | "pdf";
  kategori_guveni: number;
  islem_sayisi: number;
  tarih_araligi?: { baslangic: string; bitis: string };
  pencere_gun?: number;
  beklenen_pencere_gun?: number;
  pencere_uyumlu?: boolean;
  atlanan_satir_orani?: number | null;
  bayraklar: string[];
  parmak_izi?: string;
  // §3b Phase 7/7.5 — belge_agent.py'nin çok-stratejili karar izini (insan-okur
  // cümleler) taşır; jüriye "gerçek agent" davranışını GÖSTEREN alan.
  iz?: string[];
}

export interface CsvSkorSonuc {
  islem_sayisi: number;
  aks_skor: number;
  risk_seviyesi: string;
  karar: string;
  onerilen_limit: number | null;
  aciklama: Aciklama;
  danisman: Danisman;
  anomali_bayrak: boolean | null;
  anomali_skoru: number | null;
  // §3b Phase 7/7.3 — yalnızca portal (giriş yapmış) yüklemelerinde dolu;
  // anonim /api/csv-skorla'da her zaman boş dizi. "coklu_sahiplik_supheli" /
  // "profil_tutarsiz" olabilir — KARARI DEĞİŞTİRMEZ, yalnızca şeffaflık sinyali.
  sahiplik_bayraklari?: string[];
  belge_meta?: BelgeMeta;
}

export interface ApiHata {
  hata: string;
}

// §3b Phase 6/7 — kullanıcı portalı (auth + kendi ekstresini yükleme/geçmiş).
export interface KullaniciBilgisi {
  id: number;
  email: string;
  ad: string;
  // §3b Phase 7/7.2 — kayıtta otomatik üretilir, isim/TCKN YERİNE kullanılır.
  aks_no?: string;
}

export interface PortalGecmisKayit {
  id: number;
  zaman: string;
  aks_skor: number;
  risk_seviyesi: string;
  karar: string;
  onerilen_limit: number | null;
}

// POST /api/simulasyon (U23) — what-if senaryo simülatörü. `degisiklikler`
// yalnızca DEĞİŞEN özellikleri taşır; backend geri kalanını mevcut müşterinin
// özellikleriyle doldurur (views.py::simulasyon, ozellikler.update(degisiklikler)).
export interface SimulasyonSonuc {
  musteri_id: number;
  mevcut_skor: number;
  senaryo_skor: number;
  skor_degisimi: number;
  uygulanan_degisiklikler: Record<string, number>;
  senaryo_karar: string;
}

// §3b/U26 — segmentasyon.py'nin (K-Means, denetimsiz keşif) persist ettiği rapor.
// Hiçbir skorlama/karar yoluna beslenmez — yalnızca araştırma/şeffaflık amaçlı.
export interface KumeProfili {
  n: number;
  persona_dagilimi: Record<string, number>;
  temerrut_orani: number;
  ozellik_ortalamalari: Record<string, number>;
}

export interface SegmentasyonRaporu {
  zaman: string;
  veri_kaynagi: "dekuple" | "dongusel";
  n_musteri: number;
  k: number;
  silhouette_skoru: number;
  bilinen_personalar: string[];
  kume_profilleri: Record<string, KumeProfili>;
  not: string;
}

// §4 R8/R10/R11 — genelleme_saglamlik.py'nin persist ettiği rapor.
export interface PersonaGenellemeSonuc {
  n_test: number;
  n_train?: number;
  auc: number | null;
  not?: string;
}

export interface InceDosyaSonuc {
  n: number;
  ort_mutlak_sapma: number;
  p90_mutlak_sapma: number;
  anomali_bayrak_orani: number | null;
}

export interface OyunlanabilirlikSonuc {
  ort_skor_kazanci: number;
  p90_skor_kazanci: number;
  degisim_orani: number;
}

export interface GenellemeSaglamlikRaporu {
  zaman: string;
  veri_kaynagi: string;
  n_musteri: number;
  model_adi_referans: string;
  sure_sn: number;
  persona_disi_genelleme: { aciklama: string; sonuc: Record<string, PersonaGenellemeSonuc> };
  out_of_time_split: { durum: string; gerekce: string };
  ince_dosya_stres_testi: { aciklama: string; sonuc: Record<string, InceDosyaSonuc> };
  oyunlanabilirlik_duyarliligi: { aciklama: string; sonuc: Record<string, OyunlanabilirlikSonuc> };
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

// §3b Phase 7/7.4 — risk_istahi.py'nin persist ettiği 3 profil (ihtiyatli/
// dengeli/atak). Sentetik/dekuple veri üzerinde, held-out ama sentetik bir
// benchmarkta üretildi — "doğrulanmış banka politikası" olarak alıntılanmamalı
// (bkz. rapor.uyari).
export interface RiskIstahiProfil {
  ad: string;
  hedef_kotu_oran: number;
  secilen_esik: number;
  gerceklesen_kotu_oran: number | null;
  gerceklesen_kotu_oran_ci95: [number, number] | null;
  onay_orani: number;
  onay_orani_ci95: [number, number] | null;
  n_onay: number;
  n_test: number;
  beklenen_net_kar: number;
  uyari: string | null;
}

export interface RiskIstahiRaporu {
  profiller: Record<"ihtiyatli" | "dengeli" | "atak", RiskIstahiProfil>;
  varsayimlar: { ort_kredi: number; getiri_orani: number; zarar_orani: number };
  n_test: number;
  model_adi_referans: string;
  zaman: string;
  veri_kaynagi: string;
  uyari: string;
}

// §3b Phase 7/7.2 — kimlik/rıza/kiracılık (müşteri + kurum taraflı).
export interface ProfilBilgisi {
  aks_no: string;
  telefon_dogrulandi_mi: boolean;
}

export interface TelefonGonderSonuc {
  gonderildi: boolean;
  gecerlilik_dakika: number;
  dogrulama_id: number;
  debug_kod?: string; // yalnızca DEBUG=true iken (SMS sağlayıcısı henüz yok)
}

export interface ErisimTalebiKaydi {
  id: number;
  kurum: string;
  kurum_kod: string;
  amac: string;
  durum: "bekliyor" | "onaylandi" | "reddedildi" | "iptal_edildi";
  gecerlilik_bitis: string | null;
  created_at: string;
  aktif_mi: boolean;
}

export interface RizaDefteriKaydi {
  id: number;
  olay: string;
  kurum: string;
  amac: string;
  created_at: string;
}

export interface KurumBilgisi {
  kurum: string;
  kurum_kod: string;
}

export interface KurumMusteriOzet {
  aks_no: string;
  amac: string;
  gecerlilik_bitis: string;
}

export interface MusteriRiskIstahiSonucu {
  ad: string;
  onaylanir_mi: boolean;
  esik: number;
}

export interface KurumMusteriDetay {
  aks_no: string;
  degerlendirme_var: boolean;
  aks_skor?: number;
  risk_seviyesi?: string;
  karar?: string;
  onerilen_limit?: number | null;
  kaynak_format?: string;
  sahiplik_bayraklari?: string[];
  created_at?: string;
  risk_istahi?: Record<"ihtiyatli" | "dengeli" | "atak", MusteriRiskIstahiSonucu> | null;
  aciklama?: Aciklama | null;
  not?: string;
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
  csvSkorla: (dosya: File) => {
    const form = new FormData();
    form.append("dosya", dosya);
    return postDosya<CsvSkorSonuc>("/csv-skorla", form);
  },
  simulasyon: (musteriId: number, degisiklikler: Record<string, number>) =>
    post<SimulasyonSonuc>("/simulasyon", { musteri_id: musteriId, degisiklikler }),
  segmentasyon: () => get<SegmentasyonRaporu>("/segmentasyon"),
  genellemeSaglamlik: () => get<GenellemeSaglamlikRaporu>("/genelleme-saglamlik"),
  riskIstahi: () => get<RiskIstahiRaporu>("/risk-istahi"),

  // §3b Phase 6 — kullanıcı portalı
  ben: () => get<KullaniciBilgisi>("/auth/ben"),
  kayitOl: (email: string, sifre: string) => post<KullaniciBilgisi>("/auth/kayit", { email, sifre }),
  girisYap: (email: string, sifre: string) => post<KullaniciBilgisi>("/auth/giris", { email, sifre }),
  cikisYap: () => post<{ cikis_yapildi: boolean }>("/auth/cikis", {}),
  // §3b Phase 7/7.3 — `beyan` ZORUNLU: "bu ekstre bana ait" onayı olmadan
  // backend 400 döner (bkz. portal_views.py::portal_yukle).
  portalYukle: (dosya: File, beyan: boolean) => {
    const form = new FormData();
    form.append("dosya", dosya);
    form.append("beyan", beyan ? "true" : "false");
    return postDosya<CsvSkorSonuc>("/portal/yukle", form);
  },
  portalGecmis: () => get<{ gecmis: PortalGecmisKayit[] }>("/portal/gecmis"),

  // §3b Phase 7/7.2 — kimlik: AKS no, telefon doğrulama, erişim talepleri, rıza defteri.
  profilim: () => get<ProfilBilgisi>("/kimlik/profilim"),
  telefonGonder: (telefon: string) => post<TelefonGonderSonuc>("/kimlik/telefon/gonder", { telefon }),
  telefonDogrula: (dogrulamaId: number, kod: string) =>
    post<{ dogrulandi: boolean }>("/kimlik/telefon/dogrula", { dogrulama_id: dogrulamaId, kod }),
  erisimTalepleri: () => get<{ talepler: ErisimTalebiKaydi[] }>("/kimlik/erisim-talepleri"),
  erisimTalebiOnayla: (id: number, gecerlilikGun = 30) =>
    post<{ onaylandi: boolean; gecerlilik_bitis: string }>(`/kimlik/erisim-talebi/${id}/onayla`, {
      gecerlilik_gun: gecerlilikGun,
    }),
  erisimTalebiReddet: (id: number) => post<{ reddedildi: boolean }>(`/kimlik/erisim-talebi/${id}/reddet`, {}),
  erisimTalebiIptal: (id: number) => post<{ iptal_edildi: boolean }>(`/kimlik/erisim-talebi/${id}/iptal`, {}),
  rizaDefterim: () => get<{ kayitlar: RizaDefteriKaydi[] }>("/kimlik/riza-defterim"),

  // §3b Phase 7/7.2 — kurum (banka) tarafı: yalnızca rızası olan müşteriyi görebilir.
  kurumBen: () => get<KurumBilgisi>("/kimlik/kurum/ben"),
  kurumErisimTalebiOlustur: (aksNo: string, amac: string) =>
    post<{ talep_id: number; durum: string }>("/kimlik/kurum/erisim-talebi", { aks_no: aksNo, amac }),
  kurumMusteriler: () => get<{ musteriler: KurumMusteriOzet[] }>("/kimlik/kurum/musteriler"),
  kurumMusteriDetay: (aksNo: string) => get<KurumMusteriDetay>(`/kimlik/kurum/musteri/${aksNo}`),
};
