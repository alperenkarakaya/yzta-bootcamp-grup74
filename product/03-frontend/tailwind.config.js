/** @type {import('tailwindcss').Config} */
// Design tokens ported 1:1 from planning/stitch_aks_finansal_kapasite_platformu
// (the "AKS Terminal" Google Stitch design system, aks_terminal/DESIGN.md) —
// verified byte-identical (after key-order normalization) across all 15
// exported screens, so this is the single canonical source, not a per-page
// guess. Fully replaces the previous ("AKS Intelligence") Stitch generation's
// tokens — every page is being re-skinned, so no old token names survive.
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "surface-tint": "#c3c0ff",
        "secondary-fixed-dim": "#45dfa4",
        "on-tertiary-fixed-variant": "#881d24",
        "secondary-container": "#00bd85",
        "on-error-container": "#ffdad6",
        outline: "#928f9a",
        "surface-container-highest": "#353438",
        surface: "#131317",
        "surface-bright": "#3a393d",
        "on-primary": "#2c2a5e",
        error: "#ffb4ab",
        "on-primary-fixed-variant": "#434176",
        "primary-fixed": "#e3dfff",
        "inverse-surface": "#e5e1e7",
        tertiary: "#ffdad8",
        "surface-container-lowest": "#0e0e11",
        "primary-container": "#c3c0ff",
        secondary: "#45dfa4",
        "inverse-on-surface": "#313034",
        "on-surface": "#e5e1e7",
        "on-tertiary-fixed": "#410006",
        "on-secondary-container": "#00452e",
        "tertiary-fixed": "#ffdad8",
        "outline-variant": "#47464f",
        "on-tertiary": "#670211",
        "secondary-fixed": "#68fcbf",
        background: "#131317",
        "inverse-primary": "#5a5890",
        "on-surface-variant": "#c8c5d0",
        "on-primary-container": "#4e4c83",
        "surface-container-high": "#2a292d",
        "on-background": "#e5e1e7",
        "on-secondary-fixed": "#002114",
        "on-secondary": "#003825",
        "surface-container": "#201f23",
        "on-tertiary-container": "#982a2f",
        "surface-container-low": "#1c1b1f",
        "on-secondary-fixed-variant": "#005137",
        "on-error": "#690005",
        "error-container": "#93000a",
        "surface-dim": "#131317",
        primary: "#e2dfff",
        "tertiary-container": "#ffb3b0",
        "surface-variant": "#353438",
        "tertiary-fixed-dim": "#ffb3b0",
        "on-primary-fixed": "#161349",
        "primary-fixed-dim": "#c3c0ff",
        // Semantic-only tokens, not part of the M3 role system above but used
        // consistently across the SHAP bars / caveat banners in every
        // multi-page screen (aks_m_teri_detay_1/2, aks_portf_y_analizi,
        // aks_portal_r_za_defterim, ...). Kept as real Tailwind colors
        // (not raw hex in index.css) so `text-shap-positive` etc. work.
        "shap-positive": "#34d399",
        "shap-negative": "#f87171",
        caveat: "#fbbf24",
      },
      borderRadius: {
        DEFAULT: "0.125rem",
        lg: "0.25rem",
        xl: "0.5rem",
        // Stitch'in 15 ekran export'u burada `0.75rem` yazıyor ama bu, kendi
        // tasarım belgesiyle ÇELİŞİYOR: aks_terminal/DESIGN.md hem token
        // listesinde (`full: 9999px`) hem de düzyazıda ("Global Navigation
        // (Pills): Full pill (999px) radius") tam-yuvarlak diyor. 0.75rem ile
        // `rounded-full` semantiği bozuluyordu — canlı denetimde müşteri
        // detayındaki twin-score daireleri KARE çıktı. DESIGN.md kanonik
        // kabul edildi.
        full: "9999px",
      },
      spacing: {
        gutter: "16px",
        "stack-default": "12px",
        "stack-compact": "4px",
        "container-padding": "16px",
        "grid-margin": "24px",
      },
      fontFamily: {
        "mono-label-sm": ["JetBrains Mono", "monospace"],
        "body-md": ["Geist", "sans-serif"],
        "headline-md": ["Geist", "sans-serif"],
        "mono-score-lg": ["JetBrains Mono", "monospace"],
        "headline-lg": ["Geist", "sans-serif"],
        "mono-data-md": ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "mono-label-sm": ["12px", { lineHeight: "16px", letterSpacing: "0.02em", fontWeight: "500" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "mono-score-lg": ["40px", { lineHeight: "40px", letterSpacing: "-0.04em", fontWeight: "700" }],
        "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "-0.02em", fontWeight: "600" }],
        "mono-data-md": ["14px", { lineHeight: "18px", fontWeight: "500" }],
        // Extra tier ABOVE headline-lg, for Ana Sayfa's marketing hero only —
        // no Stitch screen for that page exists (PO decision: match the
        // system, invent this one screen). Not used anywhere else.
        "display-hero": ["56px", { lineHeight: "1.05", letterSpacing: "-0.03em", fontWeight: "700" }],
      },
    },
  },
  plugins: [],
};
