"""Generate BTP2 PowerPoint presentation from the KGMiner report."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import os

FIGURES = "figures"
OUTPUT = "BTP2_REPORT.ppt.pptx"

# IIT KGP colors
NAVY   = RGBColor(0x1A, 0x35, 0x6E)   # deep blue
GOLD   = RGBColor(0xC5, 0x9B, 0x00)   # gold accent
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF0, 0xF4, 0xFA)   # slide bg
DARK   = RGBColor(0x1A, 0x1A, 0x2E)   # body text
GREY   = RGBColor(0x5A, 0x5A, 0x6E)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]   # completely blank layout

# ── helpers ─────────────────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill=None, line=None):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.line.fill.background()
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

def add_text(slide, text, l, t, w, h,
             font_size=18, bold=False, color=DARK, align=PP_ALIGN.LEFT,
             italic=False, wrap=True):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txb

def add_multiline(slide, lines, l, t, w, h,
                  font_size=16, color=DARK, bullet=True,
                  bold_first=False, line_space=1.1):
    """lines = list of strings; if bullet=True prepend bullet char."""
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    first = True
    for i, line in enumerate(lines):
        p = tf.add_paragraph() if not first else tf.paragraphs[0]
        first = False
        p.alignment = PP_ALIGN.LEFT
        p.space_before = Pt(2)
        if bullet:
            p.level = 0
        run = p.add_run()
        prefix = "▸  " if bullet else ""
        run.text = prefix + line
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.name = "Calibri"
        run.font.bold = (bold_first and i == 0)
    return txb

def slide_header(slide, title, subtitle=None):
    """Navy top bar with title."""
    add_rect(slide, 0, 0, 13.33, 1.1, fill=NAVY)
    add_text(slide, title, 0.3, 0.08, 12.4, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, 0.3, 0.72, 12.4, 0.35,
                 font_size=14, bold=False, color=GOLD, align=PP_ALIGN.LEFT)
    # gold accent line
    add_rect(slide, 0, 1.1, 13.33, 0.05, fill=GOLD)
    # light bg
    add_rect(slide, 0, 1.15, 13.33, 6.35, fill=LIGHT)
    # slide number strip
    add_rect(slide, 0, 7.2, 13.33, 0.3, fill=NAVY)

def add_figure(slide, path, l, t, w, h):
    if os.path.exists(path):
        slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))

def two_col(slide, left_items, right_items,
            font_size=15, l_title=None, r_title=None):
    """Two-column bullet layout under the header."""
    lx, rx = 0.35, 6.9
    ty = 1.3
    col_w = 6.2
    if l_title:
        add_rect(slide, lx, ty, col_w, 0.38, fill=NAVY)
        add_text(slide, l_title, lx+0.1, ty+0.02, col_w-0.2, 0.34,
                 font_size=13, bold=True, color=WHITE)
        ty2 = ty + 0.42
    else:
        ty2 = ty
    if r_title:
        add_rect(slide, rx, ty, col_w, 0.38, fill=NAVY)
        add_text(slide, r_title, rx+0.1, ty+0.02, col_w-0.2, 0.34,
                 font_size=13, bold=True, color=WHITE)
    add_multiline(slide, left_items,  lx, ty2, col_w, 5.8, font_size=font_size)
    add_multiline(slide, right_items, rx, ty2, col_w, 5.8, font_size=font_size)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)

# Full navy bg
add_rect(sl, 0, 0, 13.33, 7.5, fill=NAVY)
# Gold accent bars
add_rect(sl, 0, 2.4, 13.33, 0.06, fill=GOLD)
add_rect(sl, 0, 5.4, 13.33, 0.06, fill=GOLD)

# IIT logo
add_figure(sl, f"{FIGURES}/iit_logo.png", 0.35, 0.2, 1.1, 1.1)

# Institute
add_text(sl, "Indian Institute of Technology Kharagpur",
         1.6, 0.25, 11.0, 0.55, font_size=18, bold=True, color=GOLD,
         align=PP_ALIGN.LEFT)
add_text(sl, "Department of Energy Science and Engineering  |  BTP2 — Spring Semester 2025-26",
         1.6, 0.72, 11.0, 0.4, font_size=13, color=RGBColor(0xCC,0xCC,0xFF),
         align=PP_ALIGN.LEFT)

# Main title
add_text(sl, "KGMiner",
         0.5, 1.55, 12.3, 0.95, font_size=52, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER)
add_text(sl,
         "Enhanced Knowledge Graph Mining with\n"
         "Ontology-Constrained Multi-Pass Extraction\n"
         "and Graph-RAG for Scientific Literature",
         0.5, 2.55, 12.3, 1.8, font_size=22, color=LIGHT,
         align=PP_ALIGN.CENTER)

# Student / supervisor
add_text(sl, "Upanshu Jain  |  Roll No: 22BT10035",
         0.5, 4.55, 6.0, 0.5, font_size=16, bold=True, color=WHITE)
add_text(sl, "Supervisor: Prof. Amit Ghosh",
         0.5, 5.05, 6.0, 0.4, font_size=14, color=GOLD)
add_text(sl, "Mentor: Mr. Sayan Saha Roy (PhD Scholar)",
         0.5, 5.42, 6.0, 0.4, font_size=13, color=RGBColor(0xCC,0xCC,0xFF))

# Key numbers on right
stats = [("4,722", "Typed Triples"),
         ("2,996", "Unique Entities"),
         ("226",   "PubMed Articles"),
         ("+170.6%","Recall Gain")]
for i, (num, label) in enumerate(stats):
    bx = 8.4 + (i % 2) * 2.4
    by = 4.5 + (i // 2) * 1.0
    add_rect(sl, bx, by, 2.1, 0.85, fill=RGBColor(0x2A, 0x50, 0x9E))
    add_text(sl, num,   bx+0.05, by+0.00, 2.0, 0.45,
             font_size=22, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, label, bx+0.05, by+0.44, 2.0, 0.35,
             font_size=11, color=WHITE, align=PP_ALIGN.CENTER)

add_text(sl, "Biotechnology and Biochemical Engineering",
         0.5, 6.95, 12.33, 0.4, font_size=12,
         color=RGBColor(0xAA,0xAA,0xCC), align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 2 — OUTLINE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Presentation Outline")

sections = [
    ("1", "Background & Motivation",    "BTP1 achievements and identified gaps"),
    ("2", "Objectives of BTP2",          "Four core limitations to address"),
    ("3", "KGMiner Pipeline",            "6-stage automated architecture"),
    ("4", "Key Results",                 "4,722 triples, 170.6% recall gain, Graph-RAG"),
    ("5", "Query Output Comparison",     "BTP1 vs KGMiner verbatim response"),
    ("6", "Conclusion & Future Work",    "Contributions and next steps"),
]
for i, (num, title, desc) in enumerate(sections):
    row = i
    bx, by = 0.4, 1.3 + row * 0.97
    add_rect(sl, bx, by, 0.55, 0.75, fill=NAVY)
    add_text(sl, num, bx, by, 0.55, 0.75,
             font_size=22, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_rect(sl, bx+0.6, by, 11.9, 0.75, fill=WHITE,
             line=RGBColor(0xCC,0xCC,0xDD))
    add_text(sl, title, bx+0.75, by+0.04, 4.5, 0.4,
             font_size=17, bold=True, color=NAVY)
    add_text(sl, desc, bx+0.75, by+0.40, 8.5, 0.3,
             font_size=13, color=GREY)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 3 — BTP1 BACKGROUND & GAPS
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Background: BTP1 (NEKO Implementation)",
             subtitle="What we achieved — and what remained unsolved")

add_rect(sl, 0.35, 1.3, 6.1, 0.4, fill=NAVY)
add_text(sl, "✓  BTP1 Achievements", 0.45, 1.32, 6.0, 0.36,
         font_size=14, bold=True, color=WHITE)
btp1_ok = [
    "Implemented NEKO workflow locally (free-tier LLMs)",
    "Processed 1,088 Rhodococcus abstracts from PubMed",
    "Built knowledge graph with 180+ unique nodes",
    "Demonstrated advantage over zero-shot GPT-4 queries",
    "Validated data provenance and traceability",
]
add_multiline(sl, btp1_ok, 0.35, 1.75, 6.1, 4.0, font_size=15,
              color=RGBColor(0x11,0x44,0x11))

add_rect(sl, 6.85, 1.3, 6.1, 0.4, fill=RGBColor(0x99,0x11,0x11))
add_text(sl, "✗  Critical Gaps Identified", 6.95, 1.32, 6.0, 0.36,
         font_size=14, bold=True, color=WHITE)
btp1_gaps = [
    "Untyped relationships — no activation vs inhibition",
    "Single-pass extraction missed secondary details",
    "Keyword-only queries — required exact entity names",
    "Hallucination risk in answer synthesis",
    "No quantitative metric capture",
]
add_multiline(sl, btp1_gaps, 6.85, 1.75, 6.1, 4.0, font_size=15,
              color=RGBColor(0x77,0x11,0x11))

add_rect(sl, 0.35, 6.55, 12.63, 0.5, fill=RGBColor(0xFF,0xF3,0xCD))
add_text(sl,
         "BTP2 Goal: Directly address each of these 4 limitations through the KGMiner architecture.",
         0.5, 6.57, 12.3, 0.42, font_size=14, bold=True,
         color=RGBColor(0x66,0x44,0x00))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 4 — OBJECTIVES
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Objectives of BTP2",
             subtitle="Four targeted architectural improvements")

objs = [
    ("01", "Ontology-Constrained\nTriple Extraction",
     "Replace untyped associations with (Subject, Relation, Object)\ntriples using a 13-relation controlled biological vocabulary",
     RGBColor(0x1A,0x5C,0x8A)),
    ("02", "Multi-Pass Extraction\nwith Refinement",
     "Apply 3 sequential extraction passes + 1 independent\nvalidation pass per abstract to improve recall",
     RGBColor(0x1A,0x6B,0x3A)),
    ("03", "Graph-RAG Querying\nwith Semantic Search",
     "Enable full natural-language queries via embedding-based\nsemantic search over 4,722 typed triple embeddings",
     RGBColor(0x7A,0x3A,0x8A)),
    ("04", "Anti-Hallucination\nAnswer Generation",
     "Trace every claim in generated answers to specific extracted\ntriples and source PMIDs — no ungrounded synthesis",
     RGBColor(0x8A,0x3A,0x1A)),
]
for i, (num, title, desc, col) in enumerate(objs):
    bx = 0.35 + (i % 2) * 6.5
    by = 1.3  + (i // 2) * 2.8
    add_rect(sl, bx, by, 6.2, 2.6, fill=col)
    add_text(sl, num,   bx+0.15, by+0.10, 1.0, 0.7,
             font_size=30, bold=True, color=GOLD)
    add_text(sl, title, bx+0.15, by+0.70, 5.9, 0.9,
             font_size=17, bold=True, color=WHITE)
    add_text(sl, desc,  bx+0.15, by+1.55, 5.9, 1.0,
             font_size=13, color=RGBColor(0xDD,0xDD,0xFF))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 5 — KGMINER PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "KGMiner: 6-Stage Pipeline Architecture")

stages = [
    ("1", "Automated\nQuery Gen",    "LLM decomposes research\ngoal → 3 PubMed queries",
     RGBColor(0x1A,0x5C,0x8A)),
    ("2", "Literature\nRetrieval",   "PubMed Entrez API\nwith relevance filtering",
     RGBColor(0x1A,0x6B,0x3A)),
    ("3", "Ontology\nExtraction",    "3-pass LLM extraction\n13-relation vocabulary",
     RGBColor(0x7A,0x3A,0x8A)),
    ("4", "Normaliz-\nation",        "Embedding-based entity\ndeduplication + chains",
     RGBColor(0x8A,0x6A,0x0A)),
    ("5", "Graph\nConstruction",     "NetworkX directed\nmultigraph with typed edges",
     RGBColor(0x8A,0x3A,0x1A)),
    ("6", "Graph-RAG\nQuerying",     "Semantic search + anti-\nhallucination synthesis",
     RGBColor(0x2A,0x5A,0x6A)),
]
box_w = 1.95
for i, (num, title, desc, col) in enumerate(stages):
    bx = 0.25 + i * (box_w + 0.12)
    add_rect(sl, bx, 1.3, box_w, 0.55, fill=col)
    add_text(sl, f"Stage {num}", bx+0.05, 1.32, box_w-0.1, 0.5,
             font_size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(sl, bx, 1.88, box_w, 1.4, fill=RGBColor(0xE8,0xF0,0xF8))
    add_text(sl, title, bx+0.05, 1.9, box_w-0.1, 0.7,
             font_size=13, bold=True, color=col, align=PP_ALIGN.CENTER)
    add_text(sl, desc, bx+0.05, 2.55, box_w-0.1, 0.75,
             font_size=11, color=DARK, align=PP_ALIGN.CENTER)
    if i < 5:
        add_text(sl, "→", bx+box_w+0.01, 1.85, 0.12, 0.5,
                 font_size=22, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# Pipeline figure
add_figure(sl, f"{FIGURES}/fig1_pipeline_comparison.png",
           0.3, 3.45, 12.6, 3.6)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 6 — ONTOLOGY (13 RELATIONS)
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Controlled Ontology: 13-Relation Biological Vocabulary",
             subtitle="Replaces untyped associations with semantically typed predicates")

relations = [
    ("activates",      "A → promotes activity of B"),
    ("inhibits",       "A → suppresses activity of B"),
    ("produces",       "A → synthesizes compound B"),
    ("encodes",        "Gene A → encodes protein B"),
    ("is_a",           "A → is a subtype/class of B"),
    ("has_capability", "Organism A → can perform B"),
    ("increases",      "A → upregulates quantity of B"),
    ("decreases",      "A → downregulates quantity of B"),
    ("has_metric",     "Entity A → has measured value B"),
    ("integrated_in",  "Gene/pathway A → embedded in B"),
    ("is_host_for",    "Organism A → hosts pathway/gene B"),
    ("is_variant_of",  "Strain A → variant of organism B"),
    ("depends_on",     "Process A → requires factor B"),
]
cols = 2
rows = 7
for i, (rel, desc) in enumerate(relations):
    col_i = i % cols
    row_i = i // cols
    bx = 0.35 + col_i * 6.5
    by = 1.3  + row_i * 0.78
    add_rect(sl, bx, by, 2.3, 0.62, fill=NAVY)
    add_text(sl, rel, bx+0.08, by+0.08, 2.1, 0.48,
             font_size=13, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_rect(sl, bx+2.35, by, 4.1, 0.62,
             fill=WHITE, line=RGBColor(0xCC,0xCC,0xDD))
    add_text(sl, desc, bx+2.5, by+0.1, 3.9, 0.45,
             font_size=13, color=DARK)

add_rect(sl, 0.35, 6.62, 12.63, 0.55, fill=RGBColor(0xE8,0xF4,0xE8))
add_text(sl,
         "Result: 73.5% of 4,722 triples use canonical vocabulary  •  "
         "41 raw relation synonyms → 13 canonical types  •  "
         "26.5% non-canonical captured as extended triples",
         0.5, 6.65, 12.3, 0.45, font_size=13,
         color=RGBColor(0x11,0x55,0x11), bold=True)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 7 — MULTI-PASS EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Multi-Pass Extraction: Closing the Recall Gap",
             subtitle="3 sequential passes + 1 independent validation pass per abstract")

add_text(sl, "Pass Design", 0.35, 1.25, 5.8, 0.4,
         font_size=16, bold=True, color=NAVY)
passes = [
    ("Pass 1 — Exhaustive",   "Extract ALL entity-relation triples from the full abstract"),
    ("Pass 2 — Overlooked Scan", "Re-read abstract focusing on secondary/implied relationships missed in Pass 1"),
    ("Pass 3 — Gap-Filling",  "Extract implied relationships and supporting context not yet captured"),
    ("Validation Pass",       "Independent single-pass extraction; used to compute Jaccard stability score"),
]
for i, (pname, pdesc) in enumerate(passes):
    by = 1.65 + i * 1.05
    col = NAVY if i < 3 else RGBColor(0x55,0x55,0x55)
    add_rect(sl, 0.35, by, 2.5, 0.85, fill=col)
    add_text(sl, pname, 0.45, by+0.08, 2.3, 0.7,
             font_size=12, bold=True, color=WHITE)
    add_text(sl, pdesc, 2.95, by+0.1, 3.3, 0.7,
             font_size=13, color=DARK)

# Ablation results figure
add_figure(sl, f"{FIGURES}/fig10_ablation_results.png",
           6.5, 1.2, 6.6, 4.5)

# Result callout
add_rect(sl, 0.35, 6.52, 6.0, 0.72, fill=RGBColor(0xE8,0xF8,0xE8))
add_text(sl,
         "316 triples (single-pass)  →  855 triples (multi-pass)\n"
         "+170.6% recall on 15-article ablation study",
         0.5, 6.54, 5.7, 0.65, font_size=14,
         color=RGBColor(0x11,0x55,0x11), bold=True)

add_rect(sl, 6.5, 6.52, 6.6, 0.72, fill=RGBColor(0xE8,0xF0,0xF8))
add_text(sl,
         "Pass 1: 45.7%  •  Pass 2: 35.3%  •  Pass 3: 18.9%\n"
         "Each pass contributes meaningfully — diminishing returns",
         6.65, 6.54, 6.3, 0.65, font_size=13, color=NAVY, bold=False)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 8 — RESULTS: EXTRACTION OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Results: Beta-Carotene Biosynthesis Case Study",
             subtitle="226 PubMed articles processed — beta-carotene production in microorganisms")

metrics = [
    ("4,722",   "Typed Triples\nExtracted"),
    ("2,996",   "Normalized\nEntities"),
    ("226",     "PubMed Articles\nProcessed"),
    ("598",     "has_metric Triples\n(Quantitative Data)"),
    ("73.5%",   "Canonical Ontology\nCoverage"),
    ("+170.6%", "Recall Gain\n(Multi-Pass vs Single)"),
]
for i, (val, label) in enumerate(metrics):
    bx = 0.3 + (i % 3) * 4.3
    by = 1.3 + (i // 3) * 2.0
    col = NAVY if i % 2 == 0 else RGBColor(0x1A,0x6B,0x3A)
    add_rect(sl, bx, by, 4.0, 1.75, fill=col)
    add_text(sl, val,   bx+0.1, by+0.15, 3.8, 0.9,
             font_size=34, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, label, bx+0.1, by+1.0,  3.8, 0.7,
             font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

add_figure(sl, f"{FIGURES}/fig2_results_summary.png",
           0.3, 5.4, 12.6, 1.9)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 9 — KNOWLEDGE GRAPH STRUCTURE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Knowledge Graph: Structure and Relation Distribution",
             subtitle="Directed multigraph with 13 typed edge types across 2,996 entities")

add_figure(sl, f"{FIGURES}/fig3_graph_structure.png",
           0.3, 1.25, 7.8, 5.9)

top_rels = [
    ("has_metric",     "598", "12.7%", "Quantitative benchmarks"),
    ("is_a",           "543", "11.5%", "Classification relationships"),
    ("has_capability", "525", "11.1%", "Organism capability profiling"),
    ("produces",       "523", "11.1%", "Core production relationships"),
    ("activates",      "487", "10.3%", "Regulatory activation events"),
    ("increases",      "402",  "8.5%", "Upregulation relationships"),
    ("encodes",        "378",  "8.0%", "Gene-protein relationships"),
    ("inhibits",       "294",  "6.2%", "Negative regulatory events"),
]
add_rect(sl, 8.3, 1.25, 4.7, 0.42, fill=NAVY)
add_text(sl, "Top Canonical Relations", 8.4, 1.27, 4.5, 0.38,
         font_size=13, bold=True, color=WHITE)
for i, (rel, cnt, pct, interp) in enumerate(top_rels):
    by = 1.72 + i * 0.65
    bg = LIGHT if i % 2 == 0 else WHITE
    add_rect(sl, 8.3, by, 4.7, 0.60, fill=bg)
    add_text(sl, rel,  8.4,  by+0.06, 1.55, 0.48, font_size=12, bold=True, color=NAVY)
    add_text(sl, cnt,  9.95, by+0.06, 0.65, 0.48, font_size=12, color=DARK, align=PP_ALIGN.CENTER)
    add_text(sl, pct, 10.55, by+0.06, 0.65, 0.48, font_size=12, color=GREY, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 10 — STABILITY SCORE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Jaccard Stability Score: Article Quality Filter",
             subtitle="Measures consistency between extraction passes and independent validation")

add_text(sl,
         "Stability = |Extraction ∩ Validation| / |Extraction ∪ Validation|",
         0.35, 1.22, 12.63, 0.52,
         font_size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

add_figure(sl, f"{FIGURES}/fig5_stability_histogram.png",
           0.3, 1.8, 7.2, 4.9)

add_rect(sl, 7.7, 1.85, 5.3, 2.3, fill=RGBColor(0xE8,0xF4,0xE8))
add_text(sl, "Peak at 0.0 — 95 articles (42.0%)",
         7.85, 1.9, 5.0, 0.38, font_size=14, bold=True,
         color=RGBColor(0x11,0x55,0x11))
add_multiline(sl, [
    "Extraction and validation found complementary, non-overlapping triples",
    "Low Jaccard does NOT mean failure — indicates extra coverage",
    "Both triple sets are preserved via set union",
], 7.85, 2.3, 5.0, 1.7, font_size=12, color=DARK)

add_rect(sl, 7.7, 4.3, 5.3, 2.3, fill=RGBColor(0xF4,0xE8,0xE8))
add_text(sl, "Peak at 1.0 — 123 articles (54.4%)",
         7.85, 4.35, 5.0, 0.38, font_size=14, bold=True,
         color=RGBColor(0x77,0x11,0x11))
add_multiline(sl, [
    "Both extraction and validation found ZERO relationships",
    "Articles retrieved by broad PubMed query but irrelevant to beta-carotene production",
    "Reliably filtered from productive article pool",
], 7.85, 4.75, 5.0, 1.7, font_size=12, color=DARK)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 11 — GRAPH-RAG QUERY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Graph-RAG: Semantic Querying with Anti-Hallucination Protocol",
             subtitle="Natural language → embedding search → evidence-grounded answer")

steps = [
    ("①", "Natural Language\nQuery Input",
     "User enters full question:\n\"How can we increase\nbeta-carotene production?\""),
    ("②", "Triple\nEmbedding Search",
     "all-MiniLM-L6-v2 encodes query;\ncosine similarity over 4,722\nembedded triples; top-k=50 retrieved"),
    ("③", "Evidence-Grounded\nSynthesis",
     "LLM synthesizes answer ONLY\nfrom retrieved triples; each claim\ntraced to triple ID + PMID"),
    ("④", "Structured\nReport Output",
     "Sections, tables, quantitative\nmetrics — all with source citations;\n'NOT FOUND' for missing data"),
]
for i, (num, title, desc) in enumerate(steps):
    bx = 0.35 + i * 3.2
    add_rect(sl, bx, 1.3, 3.0, 0.55, fill=NAVY)
    add_text(sl, f"{num} {title}", bx+0.1, 1.32, 2.8, 0.52,
             font_size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(sl, bx, 1.9, 3.0, 2.5, fill=LIGHT, line=RGBColor(0xAA,0xBB,0xCC))
    add_text(sl, desc, bx+0.15, 2.0, 2.75, 2.3,
             font_size=13, color=DARK)
    if i < 3:
        add_text(sl, "→", bx+3.05, 2.5, 0.15, 0.5,
                 font_size=24, bold=True, color=NAVY)

add_figure(sl, f"{FIGURES}/fig6_query_capabilities.png",
           0.3, 4.55, 12.7, 2.7)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 12 — QUERY OUTPUT COMPARISON
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Query Output Comparison: BTP1 vs KGMiner",
             subtitle='Query: "How we can increase beta carotene production"')

# BTP1 column
add_rect(sl, 0.3, 1.25, 6.2, 0.5, fill=RGBColor(0x99,0x33,0x11))
add_text(sl, "BTP1 / NEKO-Style Output",
         0.4, 1.27, 6.0, 0.46, font_size=14, bold=True, color=WHITE)
add_rect(sl, 0.3, 1.78, 6.2, 4.8, fill=RGBColor(0xFF,0xF5,0xF0),
         line=RGBColor(0xCC,0x88,0x77))
btp1_out = [
    'Keyword: "beta-carotene"',
    "Entities in graph: Yarrowia lipolytica,",
    "E. coli, crtYB gene, lycopene, IPP,",
    "MVA pathway, glucose...",
    "",
    "Summary: Beta-carotene production involves",
    "carotenoid pathway engineering. Metabolic",
    "engineering including pathway overexpression",
    "and carbon source optimization reported.",
    "Further studies needed.",
    "",
    "❌  No relation types",
    "❌  No yield values",
    "❌  No citations",
    "❌  Generic, untraced",
]
add_multiline(sl, btp1_out, 0.4, 1.85, 6.0, 4.65,
              font_size=12, bullet=False, color=RGBColor(0x44,0x11,0x00))

# KGMiner column
add_rect(sl, 6.85, 1.25, 6.2, 0.5, fill=RGBColor(0x1A,0x5C,0x1A))
add_text(sl, "KGMiner — Verbatim System Response",
         6.95, 1.27, 6.0, 0.46, font_size=14, bold=True, color=WHITE)
add_rect(sl, 6.85, 1.78, 6.2, 4.8, fill=RGBColor(0xF0,0xFF,0xF0),
         line=RGBColor(0x77,0xAA,0x77))
kg_out = [
    "Metabolic Engineering: Overexpression of",
    "all-trans-beta-carotene hydroxylase →",
    "11.3-fold increase (PMID: 31193511).",
    "Gene deletions → 107.3% increase.",
    "",
    "Culture Medium: Glucose/peptone →",
    "107.22 mg/L yield (PMID: 18633963).",
    "pH 30°C → 78.9% decrease in H2O2.",
    "",
    "Host Strategies: Yarrowia lipolytica",
    "142 mg/L highest yield (PMID: 34983533).",
    "",
    "✓  13 typed relations",
    "✓  Specific yield metrics + PMIDs",
    "✓  23 papers synthesized, 50 triples",
]
add_multiline(sl, kg_out, 6.95, 1.85, 6.0, 4.65,
              font_size=12, bullet=False, color=RGBColor(0x00,0x44,0x11))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 13 — BTP1 vs BTP2 COMPARISON TABLE
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "BTP1 vs BTP2: System-Level Comparison",
             subtitle="KGMiner directly addresses each structural limitation of BTP1")

rows_data = [
    ("Feature",               "BTP1: NEKO",                    "BTP2: KGMiner"),
    ("Query Input",           "Manual keyword",                 "Natural language (auto-decomposed)"),
    ("Relation Types",        "Untyped (any string)",           "13-relation controlled vocabulary"),
    ("Extraction Passes",     "Single pass",                    "3 extraction + 1 validation pass"),
    ("Recall (15 articles)",  "~316 triples",                   "855 triples (+170.6%)"),
    ("Entity Deduplication",  "Cosine sim > 0.80, first-seen", "Cosine sim > 0.85, longest name"),
    ("Query Interface",       "Keyword graph traversal",        "Semantic search over triple embeddings"),
    ("Hallucination Guard",   "None",                           "Anti-hallucination + PMID tracing"),
    ("Metric Capture",        "Embedded in entity names",       "Structured has_metric triples (598)"),
    ("Deployment",            "Local Python scripts",           "FastAPI web application"),
]
header_cols = [2.3, 4.0, 5.6]
col_starts  = [0.3, 2.65, 6.7]
for r, row in enumerate(rows_data):
    by = 1.25 + r * 0.57
    for c, (cell, cx, cw) in enumerate(zip(row, col_starts, header_cols)):
        if r == 0:
            add_rect(sl, cx, by, cw, 0.52, fill=NAVY)
            add_text(sl, cell, cx+0.08, by+0.06, cw-0.15, 0.42,
                     font_size=13, bold=True, color=WHITE)
        else:
            bg = LIGHT if r % 2 == 0 else WHITE
            add_rect(sl, cx, by, cw, 0.52, fill=bg, line=RGBColor(0xCC,0xCC,0xDD))
            color = RGBColor(0x77,0x11,0x11) if c == 1 else (
                    RGBColor(0x11,0x55,0x11) if c == 2 else DARK)
            add_text(sl, cell, cx+0.08, by+0.06, cw-0.15, 0.42,
                     font_size=12, color=color)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 14 — CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Conclusion",
             subtitle="KGMiner: A complete solution to all four BTP1 limitations")

conclusions = [
    "Ontology-constrained extraction: 73.5% of 4,722 triples use the 13-relation canonical vocabulary, enabling mechanistic reasoning (activation vs inhibition, production vs encoding)",
    "Multi-pass extraction: +170.6% recall on 15-article ablation (855 vs 316 triples); Pass 2 alone contributes 35.3% — nearly equal to Pass 1",
    "Graph-RAG with semantic search: Full natural-language queries over 2,996-entity graph; top-50 triple retrieval with cosine similarity ranking",
    "Anti-hallucination protocol: Every quantitative claim (11.3-fold, 107.22 mg/L, 142 mg/L) traceable to a specific triple and source PMID",
    "Deployed as FastAPI web application using free-tier LLMs (Groq + Cerebras) — accessible without GPU infrastructure",
]
add_multiline(sl, conclusions, 0.35, 1.3, 12.63, 5.0,
              font_size=15, color=DARK)

add_rect(sl, 0.35, 6.5, 12.63, 0.75, fill=NAVY)
add_text(sl,
         "BTP2 transforms a static knowledge graph visualizer into an active scientific research assistant "
         "that synthesizes multi-paper evidence into structured, citation-backed answers.",
         0.5, 6.54, 12.3, 0.65,
         font_size=14, bold=True, color=GOLD, align=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 15 — FUTURE WORK
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
slide_header(sl, "Future Work",
             subtitle="Five priority extensions to KGMiner")

fw = [
    ("01", "Ontology Expansion",
     "Analyze 512 non-canonical relation strings; add 5-7 types\n(is_substrate_of, competes_with, is_precursor_to) → >85% coverage",
     RGBColor(0x1A,0x5C,0x8A)),
    ("02", "Full-Text Processing",
     "Extend from abstracts to full-text via PubMed Central Open Access;\nsubstantially increase triple density and metric capture",
     RGBColor(0x1A,0x6B,0x3A)),
    ("03", "Neo4j Graph Database",
     "Replace in-memory NetworkX with Neo4j; enable Cypher queries,\nmulti-hop path finding, and real-time literature updates",
     RGBColor(0x7A,0x3A,0x8A)),
    ("04", "Hypothesis Generation",
     "Use typed graph to suggest unexplored combinations:\nif Organism A has_capability lipid accumulation and B produces\nbeta-carotene → test A as host for B's pathway",
     RGBColor(0x8A,0x6A,0x0A)),
    ("05", "Cross-Domain Validation",
     "Benchmark against BRENDA / MetaCyc / ChEMBL curated databases;\nrigorously measure precision and recall at scale",
     RGBColor(0x8A,0x3A,0x1A)),
]
for i, (num, title, desc, col) in enumerate(fw):
    bx = 0.3  + (i % 3) * 4.35
    by = 1.28 + (i // 3) * 3.05
    add_rect(sl, bx, by, 4.1, 2.8, fill=col)
    add_text(sl, num,   bx+0.12, by+0.10, 0.8, 0.6,
             font_size=22, bold=True, color=GOLD)
    add_text(sl, title, bx+0.12, by+0.65, 3.85, 0.55,
             font_size=15, bold=True, color=WHITE)
    add_text(sl, desc,  bx+0.12, by+1.2,  3.85, 1.5,
             font_size=12, color=RGBColor(0xDD,0xDD,0xFF))

# ═══════════════════════════════════════════════════════════════════════════
# SLIDE 16 — THANK YOU
# ═══════════════════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, 13.33, 7.5, fill=NAVY)
add_rect(sl, 0, 3.2, 13.33, 0.06, fill=GOLD)
add_rect(sl, 0, 4.6, 13.33, 0.06, fill=GOLD)

add_figure(sl, f"{FIGURES}/iit_logo.png", 6.0, 0.3, 1.3, 1.3)

add_text(sl, "Thank You",
         0.5, 1.7, 12.33, 1.2, font_size=60, bold=True,
         color=WHITE, align=PP_ALIGN.CENTER)

add_text(sl, "Questions & Discussion",
         0.5, 2.7, 12.33, 0.55, font_size=22,
         color=GOLD, align=PP_ALIGN.CENTER)

add_text(sl, "Upanshu Jain  |  Roll No: 22BT10035",
         0.5, 3.45, 12.33, 0.5, font_size=18, bold=True,
         color=WHITE, align=PP_ALIGN.CENTER)

add_text(sl, "Supervisor: Prof. Amit Ghosh  •  Mentor: Mr. Sayan Saha Roy",
         0.5, 3.92, 12.33, 0.4, font_size=14,
         color=GOLD, align=PP_ALIGN.CENTER)

add_text(sl, "BTP2 — Spring Semester 2025-26\n"
             "Energy Science and Engineering, IIT Kharagpur",
         0.5, 4.75, 12.33, 0.7, font_size=15,
         color=RGBColor(0xCC,0xCC,0xFF), align=PP_ALIGN.CENTER)

# Key repo links
add_text(sl,
         "Code: github.com/Up14/Knowledge   •   Report: github.com/Up14/NEKO_PAPER",
         0.5, 5.6, 12.33, 0.45, font_size=13,
         color=RGBColor(0xAA,0xCC,0xFF), align=PP_ALIGN.CENTER)

# Summary stats bar
stats2 = [("4,722", "Typed Triples"), ("2,996", "Entities"),
          ("226", "Articles"), ("+170.6%", "Recall Gain"), ("42", "Report Pages")]
bw = 13.33 / len(stats2)
for i, (val, lbl) in enumerate(stats2):
    bx = i * bw
    add_rect(sl, bx, 6.6, bw, 0.9, fill=RGBColor(0x2A,0x50,0x9E))
    add_text(sl, val, bx+0.05, 6.62, bw-0.1, 0.45,
             font_size=18, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, lbl, bx+0.05, 7.03, bw-0.1, 0.35,
             font_size=10, color=WHITE, align=PP_ALIGN.CENTER)

# ─── save ───────────────────────────────────────────────────────────────────
prs.save(OUTPUT)
print(f"Saved: {OUTPUT}  ({os.path.getsize(OUTPUT)//1024} KB)  —  {len(prs.slides)} slides")
