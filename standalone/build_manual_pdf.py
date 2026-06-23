"""
Render TECHNICAL_MANUAL.md into a print-ready, vibrant PDF at
TECHNICAL_MANUAL.pdf (A4) using WeasyPrint.

Usage:  python build_manual_pdf.py
Requires: pip install markdown weasyprint  (+ system pango/cairo)
"""
import pathlib
import markdown
from weasyprint import HTML

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "TECHNICAL_MANUAL.md"
OUT = ROOT / "TECHNICAL_MANUAL.pdf"

body = markdown.markdown(
    SRC.read_text(encoding="utf-8"),
    extensions=["tables", "fenced_code", "toc", "sane_lists"],
)

CSS = """
@page{size:A4;margin:16mm 14mm 18mm 14mm;
  @bottom-center{content:"Astro Adviser - Technical Manual   |   page " counter(page) " of " counter(pages);
    font-size:8pt;color:#8a8fb0;}}
*{box-sizing:border-box;}
body{font-family:"DejaVu Sans","Helvetica","Arial",sans-serif;font-size:9.5pt;line-height:1.5;color:#15182b;}
h1{font-size:20pt;color:#5b2fd0;margin:0 0 4pt;}
h1+p{color:#666;}
h2{font-size:12.5pt;color:#fff;background:linear-gradient(90deg,#6a2cf5,#9a5cff);
  padding:6pt 10pt;border-radius:6pt;margin:16pt 0 7pt;page-break-after:avoid;}
h3{font-size:10.5pt;color:#7c3aed;border-bottom:2pt solid #ffc24d;display:inline-block;
  padding-bottom:1pt;margin:12pt 0 4pt;page-break-after:avoid;}
h4{font-size:9.5pt;color:#c01f8a;margin:9pt 0 3pt;}
p,li{margin:4pt 0;}
a{color:#6a2cf5;text-decoration:none;}
code{background:#f1eefb;border:1pt solid #e3dffb;border-radius:3pt;padding:0 3pt;
  font-family:"DejaVu Sans Mono",monospace;font-size:8.5pt;color:#5b2fd0;}
pre{background:#f6f4fc;border:1pt solid #e3dffb;border-radius:6pt;padding:8pt 10pt;
  page-break-inside:avoid;}
pre code{border:none;background:none;color:#3a2b6e;font-size:8pt;}
table{width:100%;border-collapse:collapse;margin:7pt 0;font-size:8pt;page-break-inside:avoid;}
th,td{border:0.6pt solid #d7d3ee;padding:4pt 6pt;text-align:left;vertical-align:top;}
th{background:#ede9fe;color:#5b2fd0;font-weight:bold;}
tr:nth-child(even) td{background:#faf8ff;}
blockquote{border-left:3pt solid #f4b740;background:#fff8e8;margin:7pt 0;padding:5pt 10pt;color:#665; border-radius:4pt;}
hr{border:none;border-top:0.6pt solid #d7d3ee;margin:14pt 0;}
"""

html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"
HTML(string=html, base_url=str(ROOT)).write_pdf(str(OUT))
print("Wrote", OUT, f"({OUT.stat().st_size // 1024} KB)")
