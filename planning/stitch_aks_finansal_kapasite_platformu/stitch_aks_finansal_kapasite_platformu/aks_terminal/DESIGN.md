---
name: AKS Terminal
colors:
  surface: '#131317'
  surface-dim: '#131317'
  surface-bright: '#3a393d'
  surface-container-lowest: '#0e0e11'
  surface-container-low: '#1c1b1f'
  surface-container: '#201f23'
  surface-container-high: '#2a292d'
  surface-container-highest: '#353438'
  on-surface: '#e5e1e7'
  on-surface-variant: '#c8c5d0'
  inverse-surface: '#e5e1e7'
  inverse-on-surface: '#313034'
  outline: '#928f9a'
  outline-variant: '#47464f'
  surface-tint: '#c3c0ff'
  primary: '#e2dfff'
  on-primary: '#2c2a5e'
  primary-container: '#c3c0ff'
  on-primary-container: '#4e4c83'
  inverse-primary: '#5a5890'
  secondary: '#45dfa4'
  on-secondary: '#003825'
  secondary-container: '#00bd85'
  on-secondary-container: '#00452e'
  tertiary: '#ffdad8'
  on-tertiary: '#670211'
  tertiary-container: '#ffb3b0'
  on-tertiary-container: '#982a2f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e3dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#161349'
  on-primary-fixed-variant: '#434176'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffdad8'
  tertiary-fixed-dim: '#ffb3b0'
  on-tertiary-fixed: '#410006'
  on-tertiary-fixed-variant: '#881d24'
  background: '#131317'
  on-background: '#e5e1e7'
  surface-variant: '#353438'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  mono-label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  mono-score-lg:
    fontFamily: JetBrains Mono
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.04em
  mono-data-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  grid-margin: 24px
  gutter: 16px
  stack-compact: 4px
  stack-default: 12px
  container-padding: 16px
---

## Brand & Style
The design system is engineered for high-stakes financial decision-making, where data density and precision are paramount. The brand personality is authoritative, technical, and clinical, evoking the feeling of a modern trading desk or a high-performance developer environment. 

The aesthetic is a hybrid of **Minimalism** and **Technical Brutalism**. It prioritizes information architecture over decorative elements, using high-contrast typography and structured layouts to instill confidence. The UI operates on a "dark-mode-first" principle, reducing eye strain for long-duration analysis while emphasizing critical status indicators through saturated accent colors.

## Colors
This system utilizes a deep, layered palette to define hierarchy without the use of elevation shadows. 

- **Background & Surfaces:** The foundation is a near-black (#020617). Intermediate layers use Slate shades to create visual containment. 
- **Accents:** Saturated Indigo (#c3c0ff) is the singular signal for interactivity. 
- **Semantic Logic:** Success (Emerald) and Error (Red) are used exclusively for status results and SHAP (Shapley Additive Explanations) values. 
- **Borders:** All surfaces are defined by 1px hairline borders (#334155) to maintain a crisp, grid-based appearance.

## Typography
Typography is the primary driver of the system's technical feel. 

- **Geist (Sans):** Used for all qualitative data, headings, and instructional text. It provides a modern, neutral foundation.
- **JetBrains Mono (Monospace):** Reserved for quantitative data, unique IDs, status badges, buttons, and scores. The monospaced nature ensures that numeric values remain vertically aligned in tables and data-dense views, aiding in rapid comparison.

All numeric data must use tabular lining to ensure columns of figures remain perfectly aligned.

## Layout & Spacing
The layout follows a **Fluid Grid** model optimized for high-density information displays. 

- **Desktop:** 12-column grid with 16px gutters.
- **Tablets:** 8-column grid with 16px gutters.
- **Mobile:** 4-column grid with 12px gutters.

Spacing is tight and systematic, utilizing a 4px base unit. Data tables should minimize vertical padding to maximize the number of visible rows. Information groups are separated by 1px Slate-700 dividers rather than expansive whitespace to maintain the "terminal" feel.

## Elevation & Depth
This design system rejects ambient shadows in favor of **Tonal Layers** and **1px Outlines**. 

Depth is communicated through brightness: the further "forward" an element is, the lighter its background hex code. 
- Level 0 (Base): #020617
- Level 1 (Cards/Tables): #0f172a
- Level 2 (Modals/Popovers): #1e293b

All interactive elements and containers must have a consistent 1px hairline border. Active states are indicated by changing the border color to the Primary Accent (#c3c0ff) rather than increasing shadow or glow.

## Shapes
The shape language is "Soft" yet disciplined. While the majority of the UI uses a subtle 0.25rem (4px) radius to maintain a professional edge, specific navigational elements like the mobile floating pill-nav use a fully rounded radius to distinguish them as high-level UI controls. 

- **Standard Elements (Inputs, Cards, Buttons):** 4px radius.
- **Status Badges:** 2px radius or sharp.
- **Global Navigation (Pills):** Full pill (999px) radius.

## Components

### Data-Dense Tables
Tables are the core of the experience. Headers use `mono-label-sm` in muted slate. All numeric columns and ID strings must use `mono-data-md`. Use alternating row highlights (zebra striping) at very low opacity (2% white) for legibility.

### Twin-Score Cards
These cards present 'Klasik Skor' and 'AKS Skoru' as side-by-side equals. They use `mono-score-lg` for the numeric value. The 'AKS Skoru' side should feature a subtle border-left highlight in the Primary Accent to denote its status as the advanced metric.

### SHAP Factor Bars
Visual representations of impact. These are horizontal stacked bars. Positive factors extend right in Emerald (#34d399); negative factors extend left in Red (#f87171). Labels for factors should be in `mono-label-sm`.

### Caveat Banners
Permanent, non-dismissible banners located at the top of content blocks. Use the Amber (#fbbf24) color for the border and a low-opacity Amber fill. These must always be visible to ensure regulatory transparency.

### Buttons & Inputs
- **Primary Button:** Indigo (#c3c0ff) background with black text, `mono-label-sm` weight 700.
- **Inputs:** 1px Slate border, JetBrains Mono text. On focus, the border transitions to Indigo.

### Consent Ledger
Items in the audit trail use a vertical timeline thread. Each entry includes a `mono-label-sm` timestamp and a hexadecimal signature string to emphasize the immutability of the record.