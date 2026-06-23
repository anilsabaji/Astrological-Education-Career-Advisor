"""
Render TECHNICAL_MANUAL.md into a styled, self-contained, printable HTML page
at docs/manual.html (the app's vibrant theme + an A4 print stylesheet).

Usage:  python build_manual.py
"""
import pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "TECHNICAL_MANUAL.md"
OUT = ROOT / "docs" / "manual.html"

body = markdown.markdown(
    SRC.read_text(encoding="utf-8"),
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Technical Manual - Astro Adviser (KP + Parashara)</title>
<style>
:root{--bg:#0f1020;--bg2:#15172b;--card:#1c1f3a;--ink:#e9e9f3;--muted:#a7abc9;
  --accent:#f4b740;--accent2:#8b7bf0;--line:#2e3252;}
*{box-sizing:border-box;}
body{margin:0;font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;line-height:1.6;
  background:radial-gradient(1200px 600px at 80% -10%,#25264a 0%,var(--bg) 55%);color:var(--ink);}
.bar{background:rgba(15,16,32,.9);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5;
  backdrop-filter:blur(8px);}
.bar .in{max-width:920px;margin:0 auto;padding:13px 22px;display:flex;justify-content:space-between;
  align-items:center;gap:10px;flex-wrap:wrap;}
.bar a{color:var(--accent2);text-decoration:none;font-weight:600;}
.bar .logo{color:var(--accent);}
.pdf-btn{background:linear-gradient(90deg,#7c3aed,#ff7ac3);color:#fff;border:none;border-radius:10px;
  padding:9px 18px;font-weight:800;cursor:pointer;}
.wrap{max-width:920px;margin:0 auto;padding:26px 22px 60px;}
h1{font-size:2rem;margin:.2em 0 .1em;}
h2{font-size:1.4rem;margin:1.6em 0 .5em;color:#fff;background:linear-gradient(90deg,#6a2cf5,#9a5cff);
  padding:8px 14px;border-radius:8px;}
h3{color:var(--accent);margin:1.3em 0 .4em;}
h4{color:var(--accent2);margin:1.1em 0 .3em;}
a{color:var(--accent2);}
p,li{color:#d6d8ea;}
code{background:#0c0d18;border:1px solid var(--line);border-radius:5px;padding:1px 5px;font-size:.92em;color:#ffd479;}
pre{background:#0c0d18;border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow:auto;}
pre code{border:none;background:none;color:#cfe3ff;}
table{width:100%;border-collapse:collapse;margin:12px 0;font-size:.92rem;}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top;}
th{background:linear-gradient(90deg,#241f47,#2c2350);color:var(--accent2);}
tr:nth-child(even) td{background:rgba(255,255,255,.02);}
blockquote{border-left:3px solid var(--accent);margin:10px 0;padding:6px 14px;color:var(--muted);background:rgba(244,183,64,.06);border-radius:6px;}
hr{border:none;border-top:1px solid var(--line);margin:26px 0;}
.foot{color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);margin-top:30px;padding-top:14px;}

@media print{
  @page{size:A4;margin:14mm 12mm;}
  html,body{background:#fff !important;color:#15182b !important;font-size:9.5pt !important;
    -webkit-print-color-adjust:exact !important;print-color-adjust:exact !important;}
  .bar,.pdf-btn,.no-print{display:none !important;}
  .wrap{max-width:100% !important;padding:0 !important;}
  h2{background:linear-gradient(90deg,#6a2cf5,#9a5cff) !important;color:#fff !important;font-size:1rem;
    page-break-after:avoid;}
  h3{color:#7c3aed !important;}h4{color:#c01f8a !important;}
  p,li,td{color:#222 !important;}
  table,tr,pre,blockquote{page-break-inside:avoid;}
  th{background:#ede9fe !important;color:#6a2cf5 !important;}
  tr:nth-child(even) td{background:#faf8ff !important;}
  code,pre{background:#f4f3fb !important;color:#5b3fd0 !important;border-color:#e3e0f5 !important;}
  a{color:#6a2cf5 !important;}
}
</style>
</head>
<body>
<div class="bar"><div class="in">
  <span><span class="logo">&#9789;</span> <a href="index.html">&larr; Astro Adviser</a></span>
  <span>
    <a class="pdf-btn" href="TECHNICAL_MANUAL.pdf" download style="text-decoration:none;margin-right:8px;">&#11015; Download PDF</a>
    <button class="pdf-btn" onclick="window.print()">&#128424; Save / Print as PDF</button>
  </span>
</div></div>
<div class="wrap">
__BODY__
<p class="foot">Developed by Dr. Anil Sabaji &middot; email: anilsabaji@gmail.com</p>
</div>
</body>
</html>
"""

OUT.write_text(HTML.replace("__BODY__", body), encoding="utf-8")
print("Wrote", OUT, f"({OUT.stat().st_size//1024} KB)")
