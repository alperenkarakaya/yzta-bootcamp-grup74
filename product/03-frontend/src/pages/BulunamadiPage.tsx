import { Link } from "react-router-dom";

export default function BulunamadiPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <p className="font-display-lg text-display-lg text-primary">404</p>
        <h1 className="font-headline-md text-headline-md text-on-background mt-2">Sayfa bulunamadı</h1>
        <p className="font-body-sm text-body-sm text-on-surface-variant mt-2">
          Aradığınız adres mevcut değil ya da taşınmış olabilir.
        </p>
        <div className="flex flex-wrap gap-3 justify-center mt-6">
          <Link
            to="/"
            className="px-4 py-2 rounded-DEFAULT bg-primary-container text-white font-label-mono text-label-mono hover:bg-inverse-primary transition-colors"
          >
            Banka Paneli
          </Link>
          <Link
            to="/portal"
            className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 text-on-surface font-label-mono text-label-mono hover:bg-surface-container transition-colors"
          >
            Kullanıcı Portalı
          </Link>
          <Link
            to="/kurum/musteriler"
            className="px-4 py-2 rounded-DEFAULT border border-outline-variant/50 text-on-surface font-label-mono text-label-mono hover:bg-surface-container transition-colors"
          >
            Kurum Girişi
          </Link>
        </div>
      </div>
    </div>
  );
}
