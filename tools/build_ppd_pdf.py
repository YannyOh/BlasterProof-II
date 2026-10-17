"""docs/PPD.md -> docs/BLASTERPROOF-II_PPD.pdf (A4), with the 1:1 drawing appended.

Single source: edit PPD.md, re-run this. Needs: markdown, pypdf, playwright (Chromium).
"""
import os, re, sys, markdown
from pypdf import PdfReader, PdfWriter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
MD = os.path.join(DOCS, "PPD.md")
DRAWING = os.path.join(DOCS, "BLASTERPROOF-II_drawing_1to1_A4.pdf")
OUT = os.path.join(DOCS, "BLASTERPROOF-II_PPD.pdf")

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
html { font-family: 'Inter', 'DejaVu Sans', Arial, sans-serif; font-size: 9.6pt; color: #1a1a1a; line-height: 1.42; }
h1 { font-size: 20pt; margin: 0 0 4mm; padding-bottom: 2mm; border-bottom: 2.5px solid #2f6fb0; }
h2 { font-size: 13pt; margin: 7mm 0 2mm; color: #1d4f85; break-after: avoid; }
h3 { font-size: 10.5pt; margin: 4mm 0 1.5mm; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: 8.4pt; break-inside: avoid; }
th, td { border: 0.6px solid #c5ccd6; padding: 1.1mm 1.6mm; text-align: left; vertical-align: top; }
th { background: #eef3f9; }
tr:nth-child(even) td { background: #fafbfd; }
img { display: block; max-width: 82%; max-height: 82mm; margin: 2mm auto 3mm; break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.2pt; background: #f1f3f6; padding: 0 1mm; border-radius: 2px; }
hr { border: 0; border-top: 0.6px solid #ccc; margin: 4mm 0; }
a { color: #1d4f85; text-decoration: none; }
strong { color: #000; }
.footer-note { font-size: 7.5pt; color: #777; margin-top: 8mm; }
"""


def main():
    md = open(MD, encoding="utf-8").read()
    body = markdown.markdown(md, extensions=["tables", "sane_lists"])
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}" \
           f"<p class='footer-note'>Generated from docs/PPD.md. The 1:1 drawing follows as the last two pages; " \
           f"print those pages at 100 % / Actual size.</p></body></html>"
    tmp = os.path.join(DOCS, "_ppd_tmp.html")
    open(tmp, "w", encoding="utf-8").write(html)
    body_pdf = os.path.join(DOCS, "_ppd_body.pdf")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto("file://" + tmp)
        pg.wait_for_load_state("networkidle")
        pg.pdf(path=body_pdf, format="A4", print_background=True, display_header_footer=True,
               header_template="<div></div>",
               footer_template="<div style='font-size:7pt;color:#888;width:100%;padding:0 15mm;display:flex;justify-content:space-between'>"
                               "<span>BLASTERPROOF II · PPD-BP2-001 rev 2.2</span><span><span class='pageNumber'></span> / <span class='totalPages'></span></span></div>",
               margin=dict(top="16mm", bottom="18mm", left="15mm", right="15mm"))
        b.close()
    w = PdfWriter()
    for src in (body_pdf, DRAWING):
        for page in PdfReader(src).pages:
            w.add_page(page)
    w.add_metadata({"/Title": "BLASTERPROOF II - Production Procedure Document rev 2.2", "/Author": "BLASTERPROOF"})
    with open(OUT, "wb") as f:
        w.write(f)
    os.remove(tmp); os.remove(body_pdf)
    print(OUT, len(PdfReader(OUT).pages), "pages")


if __name__ == "__main__":
    main()
