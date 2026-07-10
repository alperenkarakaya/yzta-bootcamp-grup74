---
name: Synthetic Intelligence Interface
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1c1b1d'
  surface-container: '#201f22'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#c7c4d8'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#313032'
  outline: '#918fa1'
  outline-variant: '#464555'
  surface-tint: '#c3c0ff'
  primary: '#c3c0ff'
  on-primary: '#1d00a5'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#4d44e3'
  secondary: '#89ceff'
  on-secondary: '#00344d'
  secondary-container: '#00a2e6'
  on-secondary-container: '#00344e'
  tertiary: '#d0bcff'
  on-tertiary: '#3c0091'
  tertiary-container: '#6f3dd9'
  on-tertiary-container: '#e3d5ff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#c9e6ff'
  secondary-fixed-dim: '#89ceff'
  on-secondary-fixed: '#001e2f'
  on-secondary-fixed-variant: '#004c6e'
  tertiary-fixed: '#e9ddff'
  tertiary-fixed-dim: '#d0bcff'
  on-tertiary-fixed: '#23005c'
  on-tertiary-fixed-variant: '#5516be'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  display-sm:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.03em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: -0.01em
  body-sm:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: 0em
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.02em
  display-sm-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.2'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 24px
  gutter: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered for an elite fintech environment where speed and predictive accuracy are paramount. The brand personality is hyper-professional, high-performance, and technically sophisticated. It balances the cold precision of automated credit scoring with the immersive quality of modern developer tools.

The visual style is a fusion of **Modern Corporate** and **Minimalist Tech-Forward**. It utilizes deep midnight foundations to create a focused "command center" atmosphere. Key design markers include:
- **High-Performance Aesthetic:** Borrowing from Vercel’s efficiency and Linear’s spatial precision.
- **AI-Immersive:** Subtle glows and micro-interactions indicate active machine learning processes without cluttering the interface.
- **Precision Engineering:** Hairline borders and tight whitespace suggest a platform that is calibrated to the decimal point.

## Colors

The palette is optimized for long-session focus and high-contrast data visualization. 

- **Foundation:** The system uses `Deep Midnight` (#020617) for the primary background to reduce eye strain and provide a canvas for vibrant accents.
- **Accents:** `Indigo-Electric` serves as the primary action color, signifying utility and trust. `Electric Blue` and `Vivid Violet` are reserved for secondary AI-driven insights and progress indicators.
- **Grayscale:** A sophisticated range of cool grays is used for text and structural elements. Text levels follow a strict hierarchy from White (100% opacity) for headers to Slate-400 (60%) for metadata.
- **Borders:** Borders use a low-opacity Slate-800 to ensure they remain functional but secondary to the content.

## Typography

This design system utilizes **Geist** for its technical, minimalist character and superior legibility at small sizes. 

- **Tight Tracking:** Headlines use negative letter spacing (-0.02em to -0.04em) to create a compact, high-end editorial feel.
- **Technical Monospace:** **JetBrains Mono** is introduced for data points, credit scores, and API-related labels to reinforce the "AI-Powered" narrative.
- **Weight Contrast:** Strong contrast between Bold (700) headers and Regular (400) body text ensures immediate scannability of complex financial data.

## Layout & Spacing

The layout philosophy is built on a **Fluid Grid** with fixed-width constraints for readability.

- **Modular System:** Content is housed in a modular 12-column system.
- **Navigation:** Eschewing the standard sidebar, this design system uses a **Floating Command-Center** or a sleek Top-Bar. This maximizes horizontal real estate for data tables and charts.
- **Density:** Spacing is intentional and tight. A 4px base unit is used, favoring 8px and 16px gaps to maintain a high information density without feeling cramped.
- **Responsiveness:** On mobile, containers collapse to a single column, and padding reduces to 16px. Large display typography scales down significantly to maintain visual balance.

## Elevation & Depth

Visual hierarchy is established through **Tonal Layering** and **Subtle Glows** rather than traditional heavy shadows.

- **Surface Tiers:** Background is #020617. Cards and containers use #0F172A. Elevated modals or hover states use #1E293B.
- **Hairline Borders:** All containers feature a 0.5px or 1px border. In "Active" AI states, these borders may transition to a subtle Indigo glow.
- **Inner Shadows:** Buttons and inputs use a very subtle inner shadow (1px) to provide a "pressed into the surface" tactile feel, reminiscent of high-end hardware interfaces.
- **Backdrop Blurs:** Modals and dropdowns use a 12px blur (Glassmorphism) to maintain context while isolating the user's focus.

## Shapes

The shape language is precise and consistent.

- **Main Containers:** Use a 10px to 12px radius. This provides a modern, approachable feel while maintaining the structural integrity of a professional tool.
- **Action Elements:** Buttons and input fields follow the `rounded-lg` (10px) standard.
- **Status Indicators:** Small elements like tags or "AI-Active" pips use a full pill-shape (9999px) to distinguish them from structural components.

## Components

- **Buttons:** High-contrast Indigo fills for primary actions. Ghost buttons with 0.5px borders for secondary actions. Text is strictly semi-bold.
- **Modular Cards:** Containers for credit metrics should have a "Glass" header—a slightly lighter top-section (1px) to separate the title from the data.
- **Floating Command-Center:** A centered, floating navigation bar at the top or bottom of the screen with a heavy backdrop blur.
- **Input Fields:** Darker than the card surface, with a 1px border that glows Indigo on focus. No labels inside the box; labels are always "Label-Mono" style above the field.
- **AI Glows:** Use a `box-shadow: 0 0 15px -5px rgba(79, 70, 229, 0.4)` on cards where AI is currently calculating or highlighting an anomaly.
- **Data Visuals:** Charts should use vibrant gradients (Indigo to Cyan) with zero-area-shading to keep the look clean and technical.