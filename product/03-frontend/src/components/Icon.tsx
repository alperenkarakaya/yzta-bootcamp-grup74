// Material Symbols Outlined — index.html'de font olarak yüklü.
// `filled`: bazı ekranlarda (marka ikonu, aktif nav öğesi, durum noktası)
// dolu varyant kullanılıyor — varsayılan her zaman outline (bkz. index.css).
export function Icon({
  name,
  className = "",
  filled = false,
}: {
  name: string;
  className?: string;
  filled?: boolean;
}) {
  return <span className={`material-symbols-outlined ${filled ? "fill-icon" : ""} ${className}`}>{name}</span>;
}
