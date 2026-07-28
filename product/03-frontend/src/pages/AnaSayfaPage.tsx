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
    <div className="min-h-screen bg-background text-on-background">
      <header className="border-b border-outline-variant/30">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <span className="font-display-sm text-display-sm font-bold tracking-tighter">AKS</span>
          {kullanici ? (
            <Link
              to={panelYolu}
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Panelime git
            </Link>
          ) : (
            <Link
              to="/giris"
              className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Giriş / Kayıt
            </Link>
          )}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4">
        <section className="py-20 text-center">
          <h1 className="font-display-lg text-display-lg tracking-tighter max-w-2xl mx-auto">
            Alternatif Kapasite Skoru
          </h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant mt-4 max-w-xl mx-auto leading-relaxed">
            Klasik kredi skoru ince dosyalı kişileri görmez: düzenli geliri ve sağlam ödeme
            davranışı olan biri, yalnızca kredi geçmişi kısa diye reddedilebilir. AKS, hesap
            hareketlerinden okunan davranışsal kapasiteyi bankanın kendi skorunun{" "}
            <em>yanına</em> koyar — yerine değil.
          </p>
          <div className="flex flex-wrap gap-3 justify-center mt-8">
            <Link
              to="/giris"
              className="px-5 py-2.5 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
            >
              Başla
            </Link>
            <a
              href="https://github.com/alperenkarakaya/yzta-bootcamp-grup74"
              target="_blank"
              rel="noreferrer"
              className="px-5 py-2.5 rounded-DEFAULT border border-outline-variant/50 font-label-mono text-label-mono hover:bg-surface-container transition-colors"
            >
              Projeyi incele
            </a>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4 pb-20">
          {OZELLIKLER.map((o) => (
            <div key={o.baslik} className="bg-surface-container-low hairline-border rounded-xl p-6">
              <Icon name={o.ikon} className="text-2xl text-primary" />
              <h2 className="font-headline-md text-headline-md mt-2">{o.baslik}</h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant mt-2 leading-relaxed">{o.metin}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="border-t border-outline-variant/30">
        <div className="max-w-5xl mx-auto px-4 py-8 font-label-mono text-[11px] text-on-surface-variant/70 text-center leading-relaxed">
          AKS bir araştırma/bootcamp projesidir; gerçek bir kredi kararı vermez ve yatırım ya da
          finansal tavsiye içermez. Model sentetik veri üzerinde eğitilmiştir.
        </div>
      </footer>
    </div>
  );
}
