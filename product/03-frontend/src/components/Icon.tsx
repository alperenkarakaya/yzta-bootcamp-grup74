// Material Symbols Outlined — index.html'de font olarak yüklü.
export function Icon({ name, className = "" }: { name: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{name}</span>;
}
