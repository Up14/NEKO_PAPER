"""Generate a research paper PDF from markdown with academic styling."""
import markdown
from weasyprint import HTML, CSS
import os

PAPER_MD = "NEKO_2_PAPER_CONCISE.md"
FIGURES_DIR = "figures"
OUTPUT_PDF = "NEKO_2_PAPER.pdf"

# Read markdown
with open(PAPER_MD) as f:
    md_text = f.read()

# Convert markdown to HTML
md_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

# Fix image paths to absolute
md_html = md_html.replace('src="figures/', f'src="{os.path.abspath(FIGURES_DIR)}/')

# Academic paper CSS
css = """
@page {
    size: letter;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @bottom-center {
        content: counter(page);
        font-size: 10pt;
        font-family: 'Times New Roman', Times, serif;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #000;
    text-align: justify;
    hyphens: auto;
}

h1 {
    font-size: 16pt;
    text-align: center;
    margin-bottom: 5pt;
    line-height: 1.3;
    page-break-after: avoid;
}

/* Author info right after h1 */
h1 + p {
    text-align: center;
    font-size: 11pt;
    margin-bottom: 3pt;
}

h1 + p + p {
    text-align: center;
    font-size: 10pt;
    font-style: italic;
    margin-bottom: 3pt;
}

h1 + p + p + p {
    text-align: center;
    font-size: 10pt;
    margin-bottom: 15pt;
}

h2 {
    font-size: 13pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 12pt;
    margin-bottom: 4pt;
    page-break-after: avoid;
}

p {
    margin: 0 0 8pt 0;
    text-indent: 0;
}

hr {
    border: none;
    margin: 10pt 0;
}

/* Abstract styling */
h2:first-of-type {
    text-align: center;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 9pt;
    page-break-inside: avoid;
}

th {
    background-color: #f0f0f0;
    border: 1px solid #999;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
}

td {
    border: 1px solid #ccc;
    padding: 3pt 6pt;
    text-align: left;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

/* Figures */
img {
    max-width: 100%;
    display: block;
    margin: 8pt auto;
    page-break-inside: avoid;
}

/* Figure captions */
em {
    display: block;
    text-align: center;
    font-size: 9pt;
    margin-bottom: 12pt;
    color: #333;
}

/* Lists */
ul, ol {
    margin: 4pt 0 8pt 20pt;
    padding: 0;
}

li {
    margin-bottom: 3pt;
}

/* Strong/bold */
strong {
    font-weight: bold;
}

/* Code */
code {
    font-family: 'Courier New', monospace;
    font-size: 9pt;
    background: #f5f5f5;
    padding: 1pt 3pt;
}

/* Keywords line */
p strong:first-child {
    font-size: 10pt;
}

/* References section */
h2:last-of-type ~ p {
    text-indent: -20pt;
    padding-left: 20pt;
    font-size: 10pt;
    margin-bottom: 4pt;
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

print("Generating PDF...")
html = HTML(string=full_html, base_url=os.path.abspath('.'))
html.write_pdf(OUTPUT_PDF, stylesheets=[CSS(string=css)])

size = os.path.getsize(OUTPUT_PDF)
print(f"Generated: {OUTPUT_PDF} ({size/1024:.0f} KB)")

# Count pages approximately
from weasyprint import HTML as WH
doc = WH(string=full_html, base_url=os.path.abspath('.')).render(stylesheets=[CSS(string=css)])
print(f"Pages: {len(doc.pages)}")
