"""Generate BTP2 report PDF with IIT Kharagpur academic styling."""
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
    size: letter;
    margin: 2.5cm 2.5cm 2.5cm 2.5cm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        font-family: 'Times New Roman', Times, serif;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #000;
    text-align: justify;
    hyphens: auto;
}

/* Title page */
h1 {
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 30pt;
    margin-bottom: 12pt;
    line-height: 1.4;
    page-break-after: avoid;
}

/* Title page wrapper */
.titlepage {
    text-align: center;
    margin-bottom: 10pt;
}

.titlepage h1 {
    font-size: 18pt;
    font-weight: bold;
    margin-top: 30pt;
    margin-bottom: 18pt;
    line-height: 1.4;
}

.titlepage p {
    text-align: center;
    font-size: 11pt;
    margin-bottom: 8pt;
    margin-top: 0;
}


/* CERTIFICATE / ACKNOWLEDGEMENT headings */
h2 {
    font-size: 13pt;
    font-weight: bold;
    text-align: center;
    margin-top: 24pt;
    margin-bottom: 10pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
    page-break-after: avoid;
}

/* Chapter headings */
h3 {
    font-size: 12pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
    text-transform: uppercase;
}

/* Sub-section headings */
h4 {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

/* Sub-sub-section headings */
h5 {
    font-size: 11pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 10pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

p {
    margin: 0 0 8pt 0;
    text-indent: 0;
}

hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 16pt 0;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background-color: #e8e8e8;
    border: 1px solid #666;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
}

td {
    border: 1px solid #999;
    padding: 3pt 6pt;
    text-align: left;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8f8f8;
}

/* Figures */
img {
    max-width: 90%;
    display: block;
    margin: 10pt auto;
    page-break-inside: avoid;
}

/* Figure captions = italic paragraphs after images */
p > em:only-child {
    display: block;
    text-align: center;
    font-size: 9.5pt;
    margin-bottom: 14pt;
    color: #333;
    font-style: italic;
}

/* Lists */
ul, ol {
    margin: 4pt 0 8pt 22pt;
    padding: 0;
}

li {
    margin-bottom: 4pt;
    line-height: 1.5;
}

/* Bold */
strong {
    font-weight: bold;
}

/* Code */
code {
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    background: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
}

/* References - hanging indent */
h2:last-of-type ~ p {
    text-indent: -20pt;
    padding-left: 20pt;
    font-size: 10pt;
    margin-bottom: 5pt;
}

/* CONTENTS table spacing */
p + p {
    margin-top: 0;
}
"""

full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
{md_html}
</body>
</html>
"""

print("Generating BTP2 Report PDF...")
html = HTML(string=full_html, base_url=os.path.abspath('.'))
html.write_pdf(OUTPUT_PDF, stylesheets=[CSS(string=css)])

size = os.path.getsize(OUTPUT_PDF)
print(f"Generated: {OUTPUT_PDF} ({size/1024:.0f} KB)")

from weasyprint import HTML as WH
doc = WH(string=full_html, base_url=os.path.abspath('.')).render(stylesheets=[CSS(string=css)])
print(f"Pages: {len(doc.pages)}")
