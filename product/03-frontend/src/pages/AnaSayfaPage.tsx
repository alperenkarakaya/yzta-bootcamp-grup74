import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type KullaniciBilgisi } from "../api";
import { Icon } from "../components/Icon";

// Site kökü (`/`) — herkese açık ana sayfa. Bilinçli olarak İNCE tutuldu:
// ürünün ne olduğunu bir ekranda anlatır ve doğru kapıya yönlendirir, başka
// hiçbir iş yapmaz. Veri gösteren her yüzey (banka paneli, portal, kurum)
// kendi oturum kapısının ARKASINDA — bkz. execution.md §3b Phase 7/7.11.
//
// Buradan yönlendirme YAPILMAZ (giriş yapmış kullanıcı da ana sayfayı
// görebilmeli); yalnızca oturum varsa üstteki buton "Panelime git"e dönüşür.
// Zorunlu yönlendirme `/giris`'in işi.
//
// Tasarım: planning/stitch_aks_finansal_kapasite_platformu klasöründe bu
// sayfanın Stitch karşılığı YOK (PO kararı: aynı "AKS Terminal" tasarım
// sistemiyle — aks_terminal/DESIGN.md — burada üretilsin). Hero için
// paylaşılan token setinin ötesinde tek bir ek boyut (`display-hero`,
// tailwind.config.js) kullanılıyor; geri kalan her şey (renk, mono/sans
// ayrımı, hairline-border, buton stili) diğer 15 ekranla birebir aynı.

const OZELLIKLER = [
  {
    ikon: "receipt_long",
    baslik: "Ekstre → kapasite skoru",
    metin: "PDF, Excel veya CSV hesap ekstresi yüklenir; 9 davranışsal özellik çıkarılıp 300–850 aralığında bir AKS skoru üretilir.",
  },
  {
    ikon: "compare_arrows",
    baslik: "Bankanın skorunu ezmez",
    metin: "AKS tamamlayıcıdır. Klasik skor her değerlendirmede olduğu gibi, değiştirilmeden değiştirilemez denetim izine yazılır.",
  },
  {
    ikon: "verified_user",
    baslik: "Erişim müşterinin onayıyla",
    metin: "Kurum, AKS numarasıyla erişim talebi açar; müşteri portalinden onaylar. Onay sürelidir, her an iptal edilebilir.",
  },
  {
    ikon: "insights",
    baslik: "Neden bu skor",
    metin: "Her sonuç SHAP gerekçe kodlarıyla gelir — hangi faktör skoru ne yönde etkiledi, açıkça gösterilir.",
  },
];

export default function AnaSayfaPage() {
  const [kullanici, setKullanici] = useState<KullaniciBilgisi | null>(null);

  useEffect(() => {
    // Sessizce dener — oturum yoksa 401 normaldir, hata gösterilmez.
    api.ben().then(setKullanici).catch(() => setKullanici(null));
  }, []);

  const panelYolu = kullanici?.yonetici
    ? "/panel"
    : kullanici?.kurum_uyesi
      ? "/kurum/musteriler"
      : "/portal";

  return (
    <div className="min-h-screen bg-background text-on-background font-body-md text-body-md">
      <header className="border-b border-outline-variant">
        <div className="max-w-5xl mx-auto px-gutter h-16 flex items-center justify-between">
          <span className="font-headline-md text-headline-md font-bold text-primary tracking-tighter">AKS</span>
          {kullanici ? (
            <Link
              to={panelYolu}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold hover:bg-primary-fixed transition-colors"
            >
              Panelime git
            </Link>
          ) : (
            <Link
              to="/giris"
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold hover:bg-primary-fixed transition-colors"
            >
              Giriş / Kayıt
            </Link>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-gutter">
        <section className="py-24 text-center">
          <p className="font-mono-label-sm text-mono-label-sm text-secondary uppercase tracking-wide mb-4">
            Alternatif Kapasite Skoru
          </p>
          <h1 className="font-headline-lg text-display-hero tracking-tight max-w-2xl mx-auto text-on-surface">
            Klasik skorun göremediğini görür.
          </h1>
          <p className="font-body-md text-body-md text-on-surface-variant mt-6 max-w-xl mx-auto leading-relaxed">
            Klasik kredi skoru ince dosyalı kişileri görmez: düzenli geliri ve sağlam ödeme
            davranışı olan biri, yalnızca kredi geçmişi kısa diye reddedilebilir. AKS, hesap
            hareketlerinden okunan davranışsal kapasiteyi bankanın kendi skorunun{" "}
            <span className="text-on-surface">yanına</span> koyar — yerine değil.
          </p>
          <div className="flex flex-wrap gap-3 justify-center mt-10">
            <Link
              to="/giris"
              className="px-6 py-3 rounded-DEFAULT bg-primary-container text-on-primary-container font-mono-label-sm text-mono-label-sm font-bold uppercase tracking-wide hover:bg-primary-fixed transition-colors flex items-center gap-2 group"
            >
              Başla
              <Icon name="arrow_forward" className="text-[18px] group-hover:translate-x-1 transition-transform" />
            </Link>
            <a
              href="https://github.com/alperenkarakaya/yzta-bootcamp-grup74"
              target="_blank"
              rel="noreferrer"
              className="px-6 py-3 rounded-DEFAULT border border-outline-variant font-mono-label-sm text-mono-label-sm hover:border-primary hover:text-primary transition-colors"
            >
              Projeyi incele
            </a>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-gutter pb-24">
          {OZELLIKLER.map((o) => (
            <div
              key={o.baslik}
              className="bg-surface-container-low border border-outline-variant rounded-lg p-6 hover:border-primary transition-colors"
            >
              <Icon name={o.ikon} className="text-2xl text-primary" />
              <h2 className="font-headline-md text-headline-md mt-3 text-on-surface">{o.baslik}</h2>
              <p className="font-body-md text-body-md text-on-surface-variant mt-2 leading-relaxed">{o.metin}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="border-t border-outline-variant">
        <div className="max-w-5xl mx-auto px-gutter py-8 font-mono-label-sm text-mono-label-sm text-on-surface-variant/70 text-center leading-relaxed">
          AKS bir araştırma/bootcamp projesidir; gerçek bir kredi kararı vermez ve yatırım ya da
          finansal tavsiye içermez. Model sentetik veri üzerinde eğitilmiştir.
        </div>
      </footer>
    </div>
  );
}
