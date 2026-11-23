# SiteAudit CLI — Zero-Dependency Local Business Website Conversion Auditor

Audit any local service business website in 2 seconds and generate a clean, printable **0–100 HTML/PDF Conversion & Mobile UX Audit Report** — built with pure Python 3 standard library (zero `pip install`, zero external dependencies).

- **Interactive Web Grader & Live Templates:** https://tradecraft-kit.netlify.app/
- **Free MIT Local Business HTML Template:** https://github.com/robertpetrescu/tradecraft-lite

## What It Checks (100-Point Score)

1. **HTTPS Security Padlock (20 pts)** — Flags unencrypted HTTP sites showing browser "Not Secure" warnings.
2. **Mobile Responsive Viewport (20 pts)** — Checks `<meta name="viewport">` so phones don't render tiny zoomed-out desktop pages.
3. **Tap-to-Call Phone Links (15 pts)** — Verifies clickable `tel:` links for urgent mobile callers.
4. **Up-to-Date Copyright Year (10 pts)** — Flags stale 2011–2023 footers that erode visitor trust.
5. **SEO Meta Description (10 pts)** — Checks local search snippet metadata.
6. **LocalBusiness JSON-LD Schema (10 pts)** — Checks structured data for Google local packs.
7. **On-Page Lead / Quote Form (10 pts)** — Verifies whether visitors can request an estimate directly.
8. **Clean Rendered HTML (5 pts)** — Catches broken leaked HTML comments (`END -->`, outdated browser banners).

## Quick Start

```bash
python3 site_audit.py https://example-local-business.com --out audit-report.html
```

Open `audit-report.html` in any browser and press **Print → Save as PDF** to attach a clean visual audit to client proposals or redesign pitches.

## Example Before / After

- Outdated local contractor site: **35 / 100** (missing mobile viewport, no `tel:` link, 2011 copyright, no JSON-LD schema, no quote form)
- Upgraded TradeCraft single-file HTML site: **100 / 100** (~32KB payload, sticky mobile Call + Quote bar, LocalBusiness schema, $0/mo static hosting)

## Need Ready-to-Deploy Local Business Website Templates?

Preview all **8 mobile-first local trade themes** (Electrician, Plumbing, Tree & Lawn, HVAC, Roofing, Auto Detailing, Cleaning, Handyman) live in your browser + try the free interactive customizer:

👉 **https://tradecraft-kit.netlify.app/playground/**

## License

MIT License.
