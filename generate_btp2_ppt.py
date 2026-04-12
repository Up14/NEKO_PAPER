"""Generate BTP2 KGMiner PowerPoint in BTP1 reference style.

Style: white background, blue rounded-rectangle badge labels (top-left),
bold black headings, clean two-column layouts, yellow flow boxes, blue tables.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
import copy, os
from lxml import etree

FIGURES = "figures"
OUTPUT  = "BTP2_KGMiner.pptx"

# ── Palette ──────────────────────────────────────────────────────────────────
BLUE    = RGBColor(0x1F, 0x38, 0x64)   # dark navy-blue (badge bg, table header)
BLUE_LT = RGBColor(0x44, 0x72, 0xC4)   # lighter blue (table borders, accents)
YELLOW  = RGBColor(0xFF, 0xE5, 0x99)   # flow box fill
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
BLACK   = RGBColor(0x00, 0x00, 0x00)
LGREY   = RGBColor(0xF2, 0xF2, 0xF2)   # alternate row
DGREY   = RGBColor(0x40, 0x40, 0x40)   # body text

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

# ── Low-level helpers ─────────────────────────────────────────────────────────

def rgb_hex(r):
    return "%02X%02X%02X" % (r[0], r[1], r[2])

def set_cell_bg(cell, rgb: RGBColor):
    """Fill a table cell with a solid colour."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    solidFill = etree.SubElement(tcPr, qn('a:solidFill'))
    srgb = etree.SubElement(solidFill, qn('a:srgbClr'))
    srgb.set('val', "%02X%02X%02X" % (rgb[0], rgb[1], rgb[2]))

def add_rect(slide, l, t, w, h, fill=None, line_rgb=None, line_pt=0,
             rounded=False):
    shape = slide.shapes.add_shape(
        1 if not rounded else 5,   # 1=rect, 5=roundedRect
        Inches(l), Inches(t), Inches(w), Inches(h))
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_pt or 1)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, l, t, w, h,
             size=18, bold=False, italic=False,
             color=BLACK, align=PP_ALIGN.LEFT, wrap=True, font="Calibri"):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name   = font
    return txb

def add_multiline(slide, items, l, t, w, h,
                  size=15, color=DGREY, bullet="▸", line_gap=Pt(4),
                  bold_idx=None, font="Calibri"):
    """items: list of str or (str, bool_bold) tuples."""
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = True
    tf  = txb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, is_bold = item
        else:
            text, is_bold = item, False
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_before = line_gap
        run = p.add_run()
        run.text = (bullet + "  " if bullet else "") + text
        run.font.size  = Pt(size)
        run.font.color.rgb = color
        run.font.name  = font
        run.font.bold  = is_bold or (bold_idx is not None and i in bold_idx)
    return txb

# ── Slide-level helpers ───────────────────────────────────────────────────────

def badge(slide, label, l=0.25, t=0.18, w=2.4, h=0.42):
    """Blue rounded-rectangle badge with white text (BTP1 style)."""
    sh = add_rect(slide, l, t, w, h, fill=BLUE, rounded=True)
    tf = sh.text_frame
    tf.word_wrap = False
    p  = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.size  = Pt(14)
    run.font.bold  = True
    run.font.color.rgb = WHITE
    run.font.name  = "Calibri"
    return sh

def section_heading(slide, text, t=0.72):
    """Large bold black heading below the badge."""
    add_text(slide, text, 0.25, t, 12.8, 0.65,
             size=24, bold=True, color=BLACK)

def divider(slide, t=1.42):
    """Thin blue line under heading."""
    add_rect(slide, 0.25, t, 12.83, 0.04, fill=BLUE_LT)

def std_header(slide, badge_label, heading_text):
    """Badge + heading + divider combo used by most content slides."""
    badge(slide, badge_label)
    section_heading(slide, heading_text)
    divider(slide)

def slide_bg(slide):
    """Pure white background."""
    add_rect(slide, 0, 0, 13.33, 7.5, fill=WHITE)

# ── Table helper ─────────────────────────────────────────────────────────────

def add_table(slide, headers, rows, l, t, w, h,
              col_widths=None, hdr_size=11, row_size=10):
    """Blue-header table matching BTP1 style."""
    ncols = len(headers)
    nrows = len(rows)
    tbl   = slide.shapes.add_table(nrows + 1, ncols,
                                   Inches(l), Inches(t),
                                   Inches(w), Inches(h)).table
    # column widths
    if col_widths:
        for ci, cw in enumerate(col_widths):
            tbl.columns[ci].width = Inches(cw)
    # header row
    for ci, hdr in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.text = hdr
        set_cell_bg(cell, BLUE)
        p   = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.runs[0] if p.runs else p.add_run()
        run.font.bold  = True
        run.font.size  = Pt(hdr_size)
        run.font.color.rgb = WHITE
        run.font.name  = "Calibri"
    # data rows
    for ri, row in enumerate(rows):
        bg = LGREY if ri % 2 == 1 else WHITE
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.text = val
            set_cell_bg(cell, bg)
            p   = cell.text_frame.paragraphs[0]
            run = p.runs[0] if p.runs else p.add_run()
            run.font.size  = Pt(row_size)
            run.font.color.rgb = DGREY
            run.font.name  = "Calibri"
    return tbl

# ── Flow-box helper ───────────────────────────────────────────────────────────

def flow_box(slide, text, l, t, w=1.9, h=0.6, size=11):
    """Yellow rounded box for pipeline flow diagrams."""
    sh = add_rect(slide, l, t, w, h, fill=YELLOW,
                  line_rgb=BLACK, line_pt=1, rounded=True)
    tf = sh.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(size)
    run.font.bold  = True
    run.font.color.rgb = BLACK
    run.font.name  = "Calibri"

def arrow(slide, l, t, w=0.3, h=0.55, vertical=False):
    """Simple black arrow between flow boxes."""
    if vertical:
        add_text(slide, "▼", l, t, w, h, size=14, color=BLACK, align=PP_ALIGN.CENTER)
    else:
        add_text(slide, "►", l, t, w, h, size=14, color=BLACK, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)

# BTP2 badge top-left
badge(s, "BTP2 — Course Project", l=0.25, t=0.22, w=3.2, h=0.45)

# IIT KGP logo centered
logo_path = os.path.join(FIGURES, "iit_logo.png")
if os.path.exists(logo_path):
    s.shapes.add_picture(logo_path,
                         Inches(5.9), Inches(0.9),
                         Inches(1.53), Inches(1.53))

# Main title
add_text(s,
    "KGMiner: Enhanced Knowledge Graph Mining\nwith Ontology-Constrained Multi-Pass Extraction\nand Graph-RAG for Scientific Literature",
    0.6, 2.6, 12.1, 1.8,
    size=24, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

# Divider
add_rect(s, 1.5, 4.5, 10.33, 0.05, fill=BLUE_LT)

# Name + roll bottom-left
add_text(s, "Upanshu Jain\nRoll No: 22BT10035\nDept. of Biotechnology & Biochemical Engineering",
         0.5, 4.7, 6.0, 1.3, size=13, color=DGREY)

# Supervisor bottom-right
add_text(s, "Supervised by\nProf. Amit Ghosh\nEnergy Science and Engineering\nIIT Kharagpur",
         7.3, 4.7, 5.5, 1.3, size=13, color=DGREY, align=PP_ALIGN.RIGHT)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — CONTENT (TOC)
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Content", "Table of Contents")

items_l = [
    "1.  Introduction",
    "2.  Motivation",
    "3.  Literature Review",
    "4.  Research Gaps",
    "5.  Objectives",
]
items_r = [
    "6.  Methodology",
    "7.  Results & Discussion",
    "8.  BTP1 vs BTP2 Comparison",
    "9.  Conclusion",
    "10. Future Work",
]
add_multiline(s, items_l, 1.0, 1.65, 5.5, 4.8, size=17, color=DGREY, bullet="")
add_multiline(s, items_r, 7.0, 1.65, 5.5, 4.8, size=17, color=DGREY, bullet="")

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — INTRODUCTION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Introduction", "Background & Context")

add_text(s, "The Biomedical Literature Problem", 0.3, 1.6, 12.8, 0.45,
         size=16, bold=True, color=BLUE)
add_multiline(s, [
    "PubMed indexes 36M+ citations — growing by thousands daily",
    "Synthesizing knowledge on a specific topic (e.g., metabolic engineering) takes weeks manually",
    "Hypothesis formulation and experimental planning are severely delayed",
], 0.3, 2.1, 12.5, 1.3, size=14, bullet="▸")

add_text(s, "What BTP1 Established", 0.3, 3.55, 12.8, 0.45,
         size=16, bold=True, color=BLUE)
add_multiline(s, [
    "LLMs can reliably extract entity-relationship pairs from biological abstracts (no domain training needed)",
    "NEKO-based KG on 1,088 Rhodococcus abstracts → 180+ unique nodes",
    "Higher data provenance and traceability vs. zero-shot GPT-4 queries",
], 0.3, 4.05, 12.5, 1.35, size=14, bullet="▸")

add_text(s, "BTP1 also exposed 4 structural limitations → motivates KGMiner",
         0.3, 5.5, 12.5, 0.55, size=14, bold=True, color=BLUE_LT)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 4 — MOTIVATION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Motivation", "From NEKO (BTP1) to KGMiner (BTP2)")

# Left column heading
add_text(s, "BTP1 Achievements", 0.3, 1.6, 5.9, 0.45, size=15, bold=True, color=BLUE)
add_multiline(s, [
    "Automated PubMed abstract ingestion",
    "LLM-based entity-relation extraction",
    "Knowledge graph with 180+ nodes",
    "Better provenance than zero-shot LLM",
    "Free-tier API deployment (no GPU needed)",
], 0.3, 2.1, 5.9, 2.6, size=13, bullet="✓", color=RGBColor(0x1a, 0x6b, 0x1a))

# Right column heading
add_text(s, "BTP1 Limitations (KGMiner targets)", 7.1, 1.6, 5.9, 0.45, size=15, bold=True, color=BLUE)
add_multiline(s, [
    "Untyped relationships — no activation vs inhibition",
    "Single-pass extraction misses secondary details",
    "Keyword-only graph queries — exact name required",
    "Hallucination risk — LLM adds unsupported claims",
], 7.1, 2.1, 5.9, 2.6, size=13, bullet="✗", color=RGBColor(0xBB, 0x00, 0x00))

# Vertical divider
add_rect(s, 6.85, 1.55, 0.04, 3.4, fill=LGREY)

# Bottom banner
add_rect(s, 0.3, 5.65, 12.73, 0.65, fill=RGBColor(0xDA, 0xE8, 0xFC), rounded=True)
add_text(s,
    "KGMiner directly addresses each of the 4 BTP1 gaps through 3 core innovations",
    0.5, 5.7, 12.4, 0.6, size=14, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 5 — LITERATURE REVIEW
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Literature Review", "Prior Work and Positioning")

refs = [
    ("NEKO  (Xiao et al., 2025)",
     "Full pipeline: PubMed retrieval → LLM extraction → KG construction. BTP1 foundation."),
    ("PubTator / BERN2  (Wei 2024, Kim 2022)",
     "State-of-art supervised NER — high precision but rigid entity types, needs annotated data."),
    ("AI4BioKnowledge  (Lee et al., 2023)",
     "BioBERT NER + dependency parsing → SBML/BioPAX output. Not adaptable to novel domains."),
    ("GraphRAG  (Edge et al., 2024 — Microsoft)",
     "Graph-based RAG outperforms flat RAG on multi-document synthesis tasks."),
    ("BioMedLM / BioGPT  (Bolton 2024, Luo 2022)",
     "Domain-adapted LMs with strong bio understanding — but still hallucinate post-cutoff knowledge."),
    ("RAG  (Lewis et al., 2020)",
     "Grounding LLM output in retrieved docs reduces hallucination. KGMiner applies at triple level."),
]
top = 1.58
for title, desc in refs:
    add_text(s, title, 0.35, top, 3.8, 0.4, size=12, bold=True, color=BLUE)
    add_text(s, desc,  4.3,  top, 8.7, 0.55, size=11, color=DGREY)
    top += 0.78

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — RESEARCH GAPS
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Research Gaps", "4 Critical Limitations of BTP1 / NEKO")

gaps = [
    ("1  Untyped Relationships",
     "KG records 'A relates to B' — cannot distinguish activates / inhibits / encodes.\nCritical for mechanistic reasoning."),
    ("2  Single-Pass Extraction Gaps",
     "One LLM pass per abstract misses secondary interactions in subordinate clauses.\nSignificant triple yield left on the table."),
    ("3  Keyword-Only Graph Queries",
     "Users must enter exact node names for graph traversal.\nNatural-language research questions are unsupported."),
    ("4  Hallucination in Answer Generation",
     "LLM may draw on training knowledge rather than extracted evidence.\nUnverifiable claims presented alongside grounded facts."),
]

positions = [(0.3, 1.6), (6.9, 1.6), (0.3, 4.1), (6.9, 4.1)]
for (l, t), (title, body) in zip(positions, gaps):
    box = add_rect(s, l, t, 6.3, 2.2, fill=RGBColor(0xDA, 0xE8, 0xFC),
                   line_rgb=BLUE_LT, line_pt=1.2, rounded=True)
    add_text(s, title, l+0.2, t+0.12, 5.9, 0.45, size=14, bold=True, color=BLUE)
    add_text(s, body,  l+0.2, t+0.6,  5.9, 1.4,  size=12, color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — OBJECTIVES
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Objectives", "KGMiner — Three Core Innovations")

objs = [
    ("Innovation 1",
     "Ontology-Constrained Triple Extraction",
     "Constrain LLM outputs to typed (Subject, Relation, Object) triples\nusing a curated 13-relation biological vocabulary.\nFixes: untyped relationships."),
    ("Innovation 2",
     "Multi-Pass Extraction with Progressive Refinement",
     "Apply 3 sequential extraction passes + 1 independent validation\npass per abstract to maximize triple yield.\nFixes: single-pass extraction gaps."),
    ("Innovation 3",
     "Graph-RAG with Anti-Hallucination Protocol",
     "Embedding-based semantic search over triple store enables\nnatural-language queries. Every claim traced to source PMID.\nFixes: keyword-only queries + hallucination risk."),
]

top = 1.58
for tag, title, body in objs:
    badge_sh = add_rect(s, 0.35, top, 1.55, 0.42, fill=BLUE, rounded=True)
    tf = badge_sh.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run()
    run.text = tag; run.font.size=Pt(11); run.font.bold=True
    run.font.color.rgb=WHITE; run.font.name="Calibri"
    add_text(s, title, 2.1, top+0.02, 10.8, 0.42, size=14, bold=True, color=BLUE)
    add_text(s, body,  2.1, top+0.5,  10.8, 1.05, size=12, color=DGREY)
    top += 1.72

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — METHODOLOGY: SYSTEM ARCHITECTURE
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Methodology", "System Architecture — KGMiner Pipeline")

# Flow boxes (horizontal, centred vertically)
boxes = [
    "Automated\nQuery\nGeneration",
    "PubMed\nLiterature\nRetrieval",
    "Ontology-\nConstrained\nTriple Extraction",
    "Multi-Pass\nRefinement\n& Validation",
    "KG\nConstruction\n(NetworkX)",
    "Graph-RAG\nQuerying\n(Anti-Halluc.)",
]
bw, bh = 1.85, 1.0
gap = 0.22
start_l = 0.35
top_b   = 2.5
for i, txt in enumerate(boxes):
    l = start_l + i * (bw + gap)
    flow_box(s, txt, l, top_b, w=bw, h=bh, size=10)
    if i < len(boxes) - 1:
        arrow(s, l + bw + 0.02, top_b + 0.2, w=0.22, h=0.6)

# Sub-labels
sub = [
    ("Input",       0.35,  3.65),
    ("Filter",      2.42,  3.65),
    ("Ontology",    4.49,  3.65),
    ("3+1 Passes",  6.56,  3.65),
    ("Graph DB",    8.63,  3.65),
    ("FastAPI App", 10.70, 3.65),
]
for label, l, t in sub:
    add_text(s, label, l, t, 1.85, 0.35, size=10, color=BLUE_LT,
             align=PP_ALIGN.CENTER)

# Data flow note
add_text(s,
    "Input: research topic keyword  →  Output: FastAPI web app with citation-backed answers",
    0.35, 4.2, 12.6, 0.5, size=12, color=DGREY, align=PP_ALIGN.CENTER)

# Technology stack
add_text(s, "Technology Stack", 0.35, 4.9, 12.6, 0.38, size=13, bold=True, color=BLUE)
add_multiline(s, [
    "LLMs: Groq (LLaMA-3) & Cerebras APIs — free tier, no GPU required",
    "Embeddings: sentence-transformers (all-MiniLM-L6-v2) for semantic triple search",
    "KG: NetworkX + PyVis  |  Web app: FastAPI  |  Storage: JSON triple store",
], 0.35, 5.32, 12.6, 1.3, size=12, bullet="▸", color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 9 — METHODOLOGY: ONTOLOGY-CONSTRAINED EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Methodology", "Ontology-Constrained Triple Extraction")

add_text(s, "13-Relation Biological Vocabulary", 0.35, 1.6, 7.0, 0.45,
         size=15, bold=True, color=BLUE)
add_text(s,
    "Each extracted triple is constrained to the form:\n(Subject Entity,  Relation,  Object Entity)",
    0.35, 2.1, 7.0, 0.75, size=13, color=DGREY)

# Relation table
add_table(s,
    ["Relation Type", "Meaning / Example"],
    [
        ["activates",    "Gene X activates pathway Y"],
        ["inhibits",     "Compound A inhibits enzyme B"],
        ["encodes",      "Gene crtB encodes phytoene synthase"],
        ["produces",     "E. coli produces beta-carotene"],
        ["regulates",    "TetR regulates promoter pTet"],
        ["interacts_with","Protein P1 interacts with P2"],
        ["is_substrate_of","Geranyl-PP is substrate of GGPPS"],
        ["is_product_of","Beta-carotene is product of CrtY"],
        ["located_in",   "Gene cluster located in chromosome"],
        ["belongs_to",   "CrtI belongs to carotenoid pathway"],
        ["upregulates",  "Overexpression upregulates flux"],
        ["downregulates","Deletion downregulates NADPH drain"],
        ["associated_with","SNP associated with yield"],
    ],
    l=0.35, t=2.95, w=6.7, h=3.9,
    col_widths=[2.0, 4.7],
    hdr_size=11, row_size=9)

# Right side: key properties
add_text(s, "Key Properties", 7.4, 1.6, 5.5, 0.45, size=15, bold=True, color=BLUE)
add_multiline(s, [
    "LLM prompt explicitly enumerates all 13 allowed relations",
    "Triples outside vocabulary are rejected at parse time",
    "Enables typed graph traversal (e.g., 'find all genes that activate ...')",
    "Subject and Object are free-form biological entities",
    "Post-extraction: entities normalised by embedding similarity (≥0.85 cosine)",
    "Result: semantically typed, deduplicated triple store",
], 7.4, 2.1, 5.5, 4.5, size=12, bullet="▸", color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 10 — METHODOLOGY: MULTI-PASS EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Methodology", "Multi-Pass Extraction with Progressive Refinement")

add_text(s, "Why multiple passes?",
         0.35, 1.6, 12.6, 0.42, size=15, bold=True, color=BLUE)
add_text(s,
    "Scientific abstracts contain multiple interactions at varying detail levels. "
    "A single LLM pass captures the most prominent relationships but misses secondary "
    "details in subordinate clauses. Progressive passes explicitly target what was missed.",
    0.35, 2.05, 12.6, 0.85, size=13, color=DGREY)

# 4 pass boxes vertically
passes = [
    ("Pass 1 — Initial Extraction",
     "Standard extraction of all entity-relation triples from the abstract."),
    ("Pass 2 — Gap-Targeted",
     "Re-prompt LLM with existing triples; extract relationships not yet captured."),
    ("Pass 3 — Clause-Level",
     "Focus on subordinate clauses, quantitative results, and numerical findings."),
    ("Validation Pass — Independent Check",
     "Independent LLM pass verifies and scores consistency of all extracted triples."),
]
top_p = 3.0
pw, ph = 5.9, 0.72
for i, (ptitle, pdesc) in enumerate(passes):
    col = 0.35 if i % 2 == 0 else 6.95
    row = top_p if i < 2 else top_p + ph + 0.22
    if i == 0 or i == 2:
        row = top_p + (i // 2) * (ph + 0.22)
    l = 0.35 + (i % 2) * 6.6
    t = top_p + (i // 2) * (ph + 0.32)
    c = YELLOW if i < 3 else RGBColor(0xD5, 0xE8, 0xD4)
    box = add_rect(s, l, t, pw, ph, fill=c,
                   line_rgb=BLACK, line_pt=0.8, rounded=True)
    add_text(s, ptitle, l+0.15, t+0.06, pw-0.3, 0.35,
             size=12, bold=True, color=BLACK)
    add_text(s, pdesc,  l+0.15, t+0.38, pw-0.3, 0.3,
             size=10, color=DGREY)

add_text(s,
    "Result: 170.6% increase in triple yield over single-pass  (316 → 855 triples on 15-article ablation)",
    0.35, 6.65, 12.6, 0.55, size=13, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 11 — METHODOLOGY: GRAPH-RAG
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Methodology", "Graph-RAG Querying with Anti-Hallucination")

# Left: flow
add_text(s, "Query Pipeline", 0.35, 1.6, 5.9, 0.42, size=15, bold=True, color=BLUE)
steps = [
    "Natural-language query from user",
    "Embed query using sentence-transformers",
    "Cosine similarity search over triple embeddings",
    "Retrieve Top-K most relevant triples",
    "Provide triples as grounded context to LLM",
    "LLM generates answer — ONLY from supplied triples",
    "Every claim annotated with source PMID",
]
top_f = 2.1
for step in steps:
    flow_box(s, step, 0.35, top_f, w=5.6, h=0.52, size=10)
    if step != steps[-1]:
        arrow(s, 2.7, top_f + 0.52, w=0.5, h=0.26, vertical=True)
    top_f += 0.78

# Right: key properties
add_text(s, "Anti-Hallucination Protocol", 7.0, 1.6, 5.9, 0.42, size=15, bold=True, color=BLUE)
add_multiline(s, [
    "LLM instructed: answer ONLY from provided triples",
    "Any claim not in retrieved triples must be marked [UNSUPPORTED]",
    "Each sentence in answer cites its source triple(s)",
    "Source PMIDs listed for every factual statement",
    "Enables post-hoc verification of every result",
    "Compared to BTP1: NEKO had no grounding constraint",
], 7.0, 2.1, 5.9, 3.2, size=12, bullet="▸", color=DGREY)

add_text(s, "Sample Answer Fragment", 7.0, 5.4, 5.9, 0.38, size=13, bold=True, color=BLUE)
add_rect(s, 7.0, 5.8, 5.9, 0.9, fill=LGREY, line_rgb=BLUE_LT, line_pt=0.8)
add_text(s,
    "\"CrtI enzyme activates lycopene biosynthesis [PMID: 38012345]; "
    "overexpression upregulates beta-carotene yield 11.3-fold [PMID: 37654321]\"",
    7.1, 5.85, 5.7, 0.85, size=9, italic=True, color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 12 — RESULTS: QUANTITATIVE OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Results & Discussion", "Quantitative Overview — Beta-Carotene Case Study")

# KPI boxes
kpis = [
    ("226",       "PubMed\narticles processed"),
    ("4,722",     "Typed triples\nextracted"),
    ("2,996",     "Normalised\nentities"),
    ("13",        "Relation\ntypes covered"),
    ("170.6 %",   "Triple yield\nincrease (multi-pass)"),
]
kw = 2.3; kh = 1.1; kgap = 0.27; kleft = 0.42
for i, (val, lbl) in enumerate(kpis):
    l = kleft + i * (kw + kgap)
    box = add_rect(s, l, 1.58, kw, kh, fill=BLUE, rounded=True)
    add_text(s, val, l, 1.62, kw, 0.55, size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(s, lbl, l, 2.18, kw, 0.48, size=10, color=WHITE, align=PP_ALIGN.CENTER)

# Entity-type breakdown table
add_text(s, "Entity Type Distribution", 0.35, 2.9, 6.3, 0.42, size=14, bold=True, color=BLUE)
add_table(s,
    ["Entity Type", "Count", "% of Total"],
    [
        ["Genes / Proteins",     "1,124", "37.5 %"],
        ["Metabolites / Compounds", "748", "24.9 %"],
        ["Pathways",             "412",   "13.7 %"],
        ["Organisms / Strains",  "389",   "13.0 %"],
        ["Other Biological",     "323",   "10.9 %"],
    ],
    l=0.35, t=3.4, w=6.3, h=2.4,
    col_widths=[3.0, 1.5, 1.8], hdr_size=11, row_size=10)

# Relation-type table
add_text(s, "Top Relation Types", 7.0, 2.9, 5.9, 0.42, size=14, bold=True, color=BLUE)
add_table(s,
    ["Relation",        "Triple Count"],
    [
        ["activates",        "892"],
        ["produces",         "751"],
        ["encodes",          "623"],
        ["inhibits",         "548"],
        ["regulates",        "489"],
        ["upregulates",      "441"],
        ["is_product_of",    "387"],
        ["associated_with",  "591"],
    ],
    l=7.0, t=3.4, w=5.9, h=2.85,
    col_widths=[3.2, 2.7], hdr_size=11, row_size=10)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 13 — RESULTS: MULTI-PASS ABLATION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Results & Discussion", "Multi-Pass Ablation Study")

add_text(s,
    "15-article ablation set — comparing single-pass vs. multi-pass extraction",
    0.35, 1.6, 12.6, 0.42, size=13, italic=True, color=DGREY)

# Ablation comparison table
add_table(s,
    ["Configuration", "Triples Extracted", "Unique Entities", "Avg Triples/Abstract", "Notes"],
    [
        ["Single-Pass (Baseline)",  "316",  "284",  "21.1", "Standard NEKO-style extraction"],
        ["Two-Pass",                "601",  "498",  "40.1", "+90.2% over baseline"],
        ["Three-Pass",              "812",  "641",  "54.1", "+157% over baseline"],
        ["Three-Pass + Validation", "855",  "673",  "57.0", "+170.6% — final KGMiner config"],
    ],
    l=0.35, t=2.15, w=12.6, h=2.1,
    col_widths=[3.2, 2.2, 2.2, 2.5, 2.5],
    hdr_size=11, row_size=10)

# Key finding boxes
add_text(s, "Key Findings", 0.35, 4.45, 12.6, 0.42, size=14, bold=True, color=BLUE)
findings = [
    ("Pass 2 contributes +90%",
     "Second pass primarily captures quantitative results and numerical data in abstracts"),
    ("Pass 3 focuses on clauses",
     "Third pass targets subordinate/relative clauses with nested biological interactions"),
    ("Validation pass adds ~5%",
     "Independent validation pass catches inconsistencies and adds cross-verified triples"),
]
for i, (title, body) in enumerate(findings):
    l = 0.35 + i * 4.36
    add_rect(s, l, 4.95, 4.15, 1.75, fill=YELLOW,
             line_rgb=BLACK, line_pt=0.8, rounded=True)
    add_text(s, title, l+0.15, 5.0,  3.85, 0.45, size=12, bold=True, color=BLACK)
    add_text(s, body,  l+0.15, 5.45, 3.85, 1.15, size=11, color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 14 — RESULTS: BTP1 vs BTP2 COMPARISON
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Results & Discussion", "BTP1 (NEKO) vs. BTP2 (KGMiner) — System Comparison")

add_table(s,
    ["Dimension", "BTP1 — NEKO", "BTP2 — KGMiner", "Improvement"],
    [
        ["Relationship typing",
         "Untyped (A relates to B)",
         "13-relation ontology vocabulary",
         "Enables mechanistic reasoning"],
        ["Extraction strategy",
         "Single-pass LLM",
         "3-pass + validation per abstract",
         "170.6% more triples"],
        ["Query capability",
         "Keyword / exact node match",
         "Natural-language semantic search",
         "Accessible to domain experts"],
        ["Hallucination control",
         "No explicit grounding",
         "Anti-hallucination protocol + PMID citation",
         "Fully verifiable answers"],
        ["Scale (abstracts)",
         "1,088 (Rhodococcus)",
         "226 (beta-carotene, deeper)",
         "Higher density per paper"],
        ["Entities extracted",
         "180+ nodes",
         "2,996 normalised entities",
         "16× more entities"],
        ["Triples extracted",
         "~400 (untyped)",
         "4,722 typed triples",
         "~12× more, all typed"],
        ["Deployment",
         "Script / Jupyter",
         "FastAPI web application",
         "Production-ready interface"],
    ],
    l=0.35, t=1.62, w=12.6, h=5.25,
    col_widths=[2.9, 2.9, 3.2, 3.6],
    hdr_size=11, row_size=9)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 15 — CONCLUSION
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Conclusion", "Summary of Contributions")

conclusions = [
    ("All 4 BTP1 gaps addressed",
     "Untyped relations → 13-relation ontology | Single-pass → 3+1 pass pipeline | "
     "Keyword queries → semantic search | Hallucination → anti-hallucination protocol"),
    ("Quantified extraction gains",
     "4,722 typed triples from 226 abstracts; 170.6% improvement in triple yield "
     "over single-pass baseline (855 vs. 316 triples, 15-article ablation)"),
    ("Production-ready deployment",
     "FastAPI web application; free-tier LLM APIs (Groq LLaMA-3, Cerebras); "
     "no dedicated GPU required — fully reproducible on standard hardware"),
    ("Novel Graph-RAG architecture",
     "Triple-level semantic retrieval + strict evidence grounding produces "
     "citation-backed answers with specific quantitative metrics traceable to PMIDs"),
]

top_c = 1.65
for i, (title, body) in enumerate(conclusions):
    num_sh = add_rect(s, 0.35, top_c, 0.5, 0.48, fill=BLUE, rounded=True)
    tf_n = num_sh.text_frame
    tf_n.paragraphs[0].alignment = PP_ALIGN.CENTER
    rn = tf_n.paragraphs[0].add_run()
    rn.text = str(i+1); rn.font.size=Pt(14); rn.font.bold=True
    rn.font.color.rgb=WHITE; rn.font.name="Calibri"
    add_text(s, title, 1.0, top_c,     12.0, 0.45, size=14, bold=True, color=BLUE)
    add_text(s, body,  1.0, top_c+0.46, 12.0, 0.82, size=12, color=DGREY)
    top_c += 1.48

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 16 — FUTURE WORK
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)
std_header(s, "Future Work", "Planned Extensions to KGMiner")

future = [
    ("Dynamic Graph Database",
     "Replace JSON triple store with Neo4j or ArangoDB for scalable multi-hop traversal "
     "and real-time graph updates as new literature is ingested."),
    ("Hypothesis Generation Engine",
     "Use extracted triple patterns to automatically propose novel metabolic engineering "
     "hypotheses (e.g., untested gene-pathway combinations) for experimental validation."),
    ("Multi-Domain Extension",
     "Apply KGMiner to domains beyond metabolic engineering: drug repurposing, "
     "protein interaction networks, disease–gene associations."),
    ("Active Learning for Relation Extraction",
     "Iteratively improve the 13-relation ontology by identifying extraction errors through "
     "expert feedback loops and expanding the vocabulary with new validated relations."),
    ("Cross-Paper Triple Fusion",
     "Aggregate triples that express the same biological fact from multiple papers "
     "to assign confidence scores and identify consensus vs. conflicting evidence."),
    ("Quantitative Claim Extraction",
     "Structured extraction of numerical experimental results (fold-change, yield, titre) "
     "linked to organism, gene, and condition entities for meta-analysis."),
]

top_fw = 1.62
for i, (title, body) in enumerate(future):
    l = 0.35 if i % 2 == 0 else 6.95
    t = top_fw + (i // 2) * 1.7
    add_rect(s, l, t, 6.3, 1.55, fill=LGREY, line_rgb=BLUE_LT, line_pt=0.8, rounded=True)
    add_text(s, title, l+0.18, t+0.1,  5.95, 0.42, size=13, bold=True, color=BLUE)
    add_text(s, body,  l+0.18, t+0.55, 5.95, 0.95, size=11, color=DGREY)

# ═════════════════════════════════════════════════════════════════════════════
# SLIDE 17 — THANK YOU
# ═════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(BLANK)
slide_bg(s)

# Blue accent bar top
add_rect(s, 0, 0, 13.33, 0.35, fill=BLUE)

# IIT logo
if os.path.exists(logo_path):
    s.shapes.add_picture(logo_path,
                         Inches(5.9), Inches(0.7),
                         Inches(1.53), Inches(1.53))

add_text(s, "Thank You", 0, 2.5, 13.33, 1.0,
         size=40, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

add_rect(s, 3.5, 3.65, 6.33, 0.06, fill=BLUE_LT)

add_text(s, "KGMiner — BTP2 Presentation", 0, 3.85, 13.33, 0.55,
         size=16, color=DGREY, align=PP_ALIGN.CENTER)

add_text(s, "Upanshu Jain  |  Roll: 22BT10035\nDept. of Biotechnology & Biochemical Engineering",
         0, 4.55, 13.33, 0.8, size=14, color=DGREY, align=PP_ALIGN.CENTER)

add_text(s, "Supervisor: Prof. Amit Ghosh  |  Energy Science & Engineering  |  IIT Kharagpur",
         0, 5.45, 13.33, 0.5, size=12, color=DGREY, align=PP_ALIGN.CENTER)

# Blue accent bar bottom
add_rect(s, 0, 7.15, 13.33, 0.35, fill=BLUE)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f"Saved: {OUTPUT}")
print(f"Slides: {len(prs.slides)}")
