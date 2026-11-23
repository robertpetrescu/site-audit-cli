#!/usr/bin/env python3
"""
TradeCraft SiteAudit CLI (v1.0)
Audits any local service business website for mobile readiness, HTTPS, speed,
stale copyright years, SEO metadata, LocalBusiness schema, and click-to-call UX,
then generates a clean, client-ready HTML audit report (printable to PDF).

Zero external dependencies — runs on standard Python 3.

Usage:
  python3 tradecraft_audit.py https://example-plumber.com --out audit-report.html
"""

import argparse
import html as htmllib
import re
import ssl
import time
import urllib.request
from datetime import datetime
from pathlib import Path


def audit_url(url: str) -> dict:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start = time.perf_counter()
    final_url = url
    raw_html = ""
    status_code = 0
    error_msg = ""

    for candidate in ([url, url.replace("https://", "http://", 1)] if url.startswith("https://") else [url]):
        try:
            req = urllib.request.Request(
                candidate,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                status_code = resp.status
                final_url = resp.geturl()
                raw_html = resp.read(500000).decode("utf-8", errors="ignore")
                break
        except Exception as exc:
            error_msg = str(exc)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    if not raw_html:
        raise RuntimeError(f"Could not fetch {url}: {error_msg}")

    https_ok = final_url.startswith("https://")
    has_viewport = bool(re.search(r'<meta[^>]+name=["\']viewport["\']', raw_html, re.I))
    title_match = re.search(r"<title[^>]*>(.*?)</title>", raw_html, re.I | re.S)
    title_text = htmllib.unescape(re.sub(r"\s+", " ", title_match.group(1))).strip() if title_match else ""
    has_meta_desc = bool(re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'][^"\']{20,}', raw_html, re.I))
    has_tel_link = bool(re.search(r'href=["\']tel:', raw_html, re.I))
    has_schema = bool(re.search(r'application/ld\+json', raw_html, re.I))
    has_form = bool(re.search(r'<form\b', raw_html, re.I))
    broken_comment_leak = bool(re.search(r'(?:END\s*-->|-->\s*You are using an outdated browser)', raw_html, re.I))

    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)[^<\n]{0,45}?\b(20[0-2]\d)\b", raw_html, re.I)]
    latest_copyright = max(years) if years else None
    current_year = datetime.now().year
    stale_copyright = latest_copyright is not None and latest_copyright <= current_year - 3

    kb_size = round(len(raw_html.encode("utf-8")) / 1024, 1)

    checks = [
        ("HTTPS Security Padlock", https_ok, 20, "Site loads over encrypted HTTPS." if https_ok else "Site lacks HTTPS — browsers warn visitors 'Not Secure'."),
        ("Mobile Responsive Viewport", has_viewport, 20, "Mobile viewport meta tag is configured." if has_viewport else "Missing mobile viewport meta tag — renders tiny and hard to tap on phones."),
        ("Tap-to-Call Phone Link (tel:)", has_tel_link, 15, "Includes clickable tap-to-call phone links." if has_tel_link else "No clickable tel: link detected — mobile visitors must copy/paste your number."),
        ("Up-to-Date Site Copyright", not stale_copyright, 10, f"Copyright looks current ({latest_copyright or 'not dated old'})." if not stale_copyright else f"Footer copyright still reads {latest_copyright} — signals an outdated site to new leads."),
        ("SEO Meta Description", has_meta_desc, 10, "Meta description tag found for Google snippets." if has_meta_desc else "Missing or short meta description — hurting click-through rates in local Google results."),
        ("LocalBusiness Structured Schema", has_schema, 10, "JSON-LD structured data detected." if has_schema else "No JSON-LD schema found — missing rich local SEO signals."),
        ("Lead Capture / Quote Form", has_form, 10, "On-page contact/quote form detected." if has_form else "No quote/contact form detected on the homepage."),
        ("Clean Rendered HTML (No Leaks)", not broken_comment_leak, 5, "No broken HTML comment fragments detected." if not broken_comment_leak else "Visible broken HTML comment fragments appear on the rendered page."),
    ]

    score = sum(pts for _, passed, pts, _ in checks if passed)
    return {
        "input_url": url,
        "final_url": final_url,
        "status_code": status_code,
        "elapsed_ms": elapsed_ms,
        "kb_size": kb_size,
        "title": title_text or "(Untitled)",
        "score": score,
        "checks": checks,
        "audited_at": datetime.now().strftime("%Y-%m-%d"),
    }


def render_report(data: dict) -> str:
    score = data["score"]
    grade_color = "#16A34A" if score >= 80 else ("#D97706" if score >= 55 else "#DC2626")
    grade_label = "Strong" if score >= 80 else ("Needs Refresh" if score >= 55 else "High Opportunity — Losing Mobile Leads")

    rows = []
    for name, passed, pts, note in data["checks"]:
        badge = '<span class="pill pass">PASS</span>' if passed else f'<span class="pill fail">MISSING (-{pts})</span>'
        rows.append(
            f'<tr><td><strong>{htmllib.escape(name)}</strong></td><td>{badge}</td><td>{htmllib.escape(note)}</td></tr>'
        )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Website Conversion Audit — {htmllib.escape(data["final_url"])}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #F8FAFC; color: #0F172A; margin: 0; padding: 36px 20px; line-height: 1.55; }}
    .sheet {{ max-width: 860px; margin: 0 auto; background: #FFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 36px; box-shadow: 0 12px 32px rgba(15,23,42,0.06); }}
    .top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 20px; border-bottom: 1px solid #E2E8F0; padding-bottom: 24px; margin-bottom: 24px; }}
    .eyebrow {{ font-size: 0.78rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: #0284C7; margin-bottom: 6px; }}
    h1 {{ font-size: 1.55rem; margin: 0 0 6px; }}
    .meta {{ color: #64748B; font-size: 0.9rem; }}
    .score-box {{ text-align: center; background: #0F172A; color: #FFF; padding: 18px 26px; border-radius: 14px; min-width: 160px; }}
    .score-num {{ font-size: 2.3rem; font-weight: 900; color: {grade_color}; line-height: 1; }}
    .score-lbl {{ font-size: 0.78rem; color: #CBD5E1; margin-top: 6px; font-weight: 600; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 26px; }}
    .stat {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px; }}
    .stat span {{ display: block; font-size: 0.76rem; color: #64748B; font-weight: 700; text-transform: uppercase; }}
    .stat strong {{ font-size: 1.05rem; color: #0F172A; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid #E2E8F0; vertical-align: top; }}
    th {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; }}
    .pill {{ display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 800; white-space: nowrap; }}
    .pill.pass {{ background: #DCFCE7; color: #166534; }}
    .pill.fail {{ background: #FEE2E2; color: #991B1B; }}
    .summary {{ margin-top: 26px; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 18px 20px; font-size: 0.92rem; }}
    .foot {{ margin-top: 22px; font-size: 0.8rem; color: #64748B; display: flex; justify-content: space-between; }}
    @media print {{ body {{ background: #FFF; padding: 0; }} .sheet {{ box-shadow: none; border: none; }} }}
  </style>
</head>
<body>
  <div class="sheet">
    <div class="top">
      <div>
        <div class="eyebrow">Local Website Mobile &amp; Conversion Audit</div>
        <h1>{htmllib.escape(data["title"])}</h1>
        <div class="meta">{htmllib.escape(data["final_url"])} &middot; Audited {data["audited_at"]}</div>
      </div>
      <div class="score-box">
        <div class="score-num">{score}/100</div>
        <div class="score-lbl">{grade_label}</div>
      </div>
    </div>

    <div class="stats">
      <div class="stat"><span>HTTP Status</span><strong>{data["status_code"]} OK</strong></div>
      <div class="stat"><span>Response Time</span><strong>{data["elapsed_ms"]} ms</strong></div>
      <div class="stat"><span>HTML Payload</span><strong>{data["kb_size"]} KB</strong></div>
    </div>

    <table>
      <thead><tr><th>Check</th><th>Status</th><th>Finding</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>

    <div class="summary">
      <strong>Recommended Next Step:</strong> Upgrading to a fast (~32KB) mobile-first single-page site with HTTPS, sticky tap-to-call button, above-the-fold estimate form, and LocalBusiness schema immediately resolves every flagged item above with $0/month static hosting.
    </div>

    <div class="foot">
      <span>Generated by TradeCraft SiteAudit CLI</span>
      <span>Print &rarr; Save as PDF to share with clients</span>
    </div>
  </div>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description="Audit a local business website and generate a client-ready HTML report.")
    parser.add_argument("url", help="Target website URL (e.g. https://example.com)")
    parser.add_argument("--out", default="audit-report.html", help="Output HTML report path")
    args = parser.parse_args()

    result = audit_url(args.url)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_report(result), encoding="utf-8")
    print(f"Audited {result['final_url']} -> Score: {result['score']}/100 | Report saved to {out}")
    for name, passed, pts, note in result["checks"]:
        mark = "PASS" if passed else f"FAIL (-{pts})"
        print(f"  [{mark}] {name}: {note}")


if __name__ == "__main__":
    main()
