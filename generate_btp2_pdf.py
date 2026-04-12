"""Generate BTP2 report PDF with proper IIT Kharagpur thesis formatting."""
import markdown
from weasyprint import HTML, CSS
import os

PAPER_MD = "BTP2_REPORT.md"
FIGURES_DIR = "figures"
OUTPUT_PDF = "BTP2_REPORT.pdf"

with open(PAPER_MD) as f:
    md_text = f.read()

md_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
md_html = md_html.replace('src="figures/', f'src="{os.path.abspath(FIGURES_DIR)}/')

css = """
@page {
    size: A4;
    margin: 2.54cm 3.17cm 2.54cm 3.17cm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        font-family: 'Times New Roman', Times, serif;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #000;
    text-align: justify;
    hyphens: auto;
}

/* ===== TITLE PAGE ===== */
.titlepage {
    text-align: center;
    page-break-after: always;
    padding-top: 30pt;
}

.titlepage h1 {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 10pt;
    margin-bottom: 30pt;
    line-height: 1.4;
}

.titlepage p {
    text-align: center;
    font-size: 12pt;
    margin-top: 6pt;
    margin-bottom: 6pt;
    line-height: 1.6;
}

/* ===== H2 = Certificate / Acknowledgement / Contents / Summary headings ===== */
/* Each starts on its own page */
h2 {
    font-size: 14pt;
    font-weight: bold;
    text-align: center;
    margin-top: 60pt;
    margin-bottom: 24pt;
    text-transform: uppercase;
    letter-spacing: 1pt;
    page-break-before: always;
    page-break-after: avoid;
}

/* ===== H3 = Section headings (5.1, 5.2 etc.) ===== */
h3 {
    font-size: 12pt;
    font-weight: bold;
    text-align: left;
    margin-top: 16pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}

/* ===== H4 = Sub-section headings (e.g. 5.1, 5.2) ===== */
h4 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 16pt;
    margin-bottom: 8pt;
    page-break-after: avoid;
}

/* ===== H5 = Sub-sub-section headings ===== */
h5 {
    font-size: 12pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 12pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}

/* ===== BODY PARAGRAPHS ===== */
p {
    margin: 0 0 10pt 0;
    text-indent: 0;
}

hr {
    border: none;
    border-top: 1px solid #777;
    margin: 14pt 0;
}

/* ===== TABLES ===== */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 14pt 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background-color: #d0d0d0;
    border: 1pt solid #333;
    padding: 5pt 8pt;
    text-align: left;
    font-weight: bold;
}

td {
    border: 1pt solid #666;
    padding: 4pt 8pt;
    text-align: left;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f5f5f5;
}

/* ===== FIGURES ===== */
img {
    max-width: 90%;
    display: block;
    margin: 14pt auto;
    page-break-inside: avoid;
}

/* Figure caption: italic-only paragraph */
p > em:only-child {
    display: block;
    text-align: center;
    font-size: 10pt;
    margin-top: 4pt;
    margin-bottom: 18pt;
    font-style: italic;
    color: #111;
}

/* ===== LISTS ===== */
ul, ol {
    margin: 6pt 0 12pt 26pt;
    padding: 0;
}

li {
    margin-bottom: 5pt;
    line-height: 1.5;
}

/* ===== INLINE ===== */
strong {
    font-weight: bold;
}

code {
    font-family: 'Courier New', monospace;
    font-size: 9.5pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
}

/* ===== REFERENCES (hanging indent) ===== */
h2:last-of-type ~ p {
    text-indent: -24pt;
    padding-left: 24pt;
    font-size: 11pt;
    margin-bottom: 6pt;
}
"""

full_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
{md_html}
</body>
</html>"""

print("Generating BTP2 PDF...")
html = HTML(string=full_html, base_url=os.path.abspath('.'))
html.write_pdf(OUTPUT_PDF, stylesheets=[CSS(string=css)])

size = os.path.getsize(OUTPUT_PDF)
print(f"Generated: {OUTPUT_PDF} ({size/1024:.0f} KB)")

from weasyprint import HTML as WH
doc = WH(string=full_html, base_url=os.path.abspath('.')).render(stylesheets=[CSS(string=css)])
print(f"Pages: {len(doc.pages)}")
