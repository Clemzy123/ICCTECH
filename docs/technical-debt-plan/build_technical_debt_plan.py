#!/usr/bin/env python3
"""
Build a submission-ready Technical Debt Plan PDF for ICCTECH.

Typography: Times New Roman (Liberation Serif, metric-compatible), 12 pt body,
single spacing, justified; 14 pt bold chapter headings on new pages; 1.5 in
left / 1.0 in other margins. Tables rebuilt with wrapping cells. Architecture
and process diagrams rendered as PDF-native vectors.
"""

from __future__ import annotations

import os
import sys
from collections import OrderedDict

from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
import reportlab.rl_config as rl_config
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon, Group
from reportlab.platypus.flowables import Flowable

# ---------------------------------------------------------------------------
# Fonts — Liberation Serif is metric-compatible with Times New Roman
# ---------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/liberation"
pdfmetrics.registerFont(TTFont("TimesNewRoman", os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", os.path.join(FONT_DIR, "LiberationSerif-BoldItalic.ttf")))
pdfmetrics.registerFontFamily(
    "TimesNewRoman",
    normal="TimesNewRoman",
    bold="TimesNewRoman-Bold",
    italic="TimesNewRoman-Italic",
    boldItalic="TimesNewRoman-BoldItalic",
)
rl_config.canvas_basefontname = "TimesNewRoman"

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter  # 612 x 792 pt
LEFT_MARGIN = 1.5 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 1.0 * inch
BOTTOM_MARGIN = 1.0 * inch
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN  # 432 pt
CONTENT_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN  # 648 pt

# Palette (conservative academic)
NAVY = HexColor("#1B365D")
NAVY_MID = HexColor("#2C4A7C")
STEEL = HexColor("#4A6FA5")
RULE = HexColor("#2A2A2A")
LINE_GRAY = HexColor("#B8B8B8")
ROW_ALT = HexColor("#F4F6F8")
HEADER_BG = HexColor("#1B365D")
CRIT_BG = HexColor("#F6D9D9")
CRIT_FG = HexColor("#7A1515")
HIGH_BG = HexColor("#F8E6CC")
HIGH_FG = HexColor("#8A4B00")
MED_BG = HexColor("#DCE8DC")
MED_FG = HexColor("#1F4D2C")
NOTE_BG = HexColor("#F3F5F8")
NOTE_BAR = HexColor("#1B365D")
BOX_FILL = HexColor("#EEF2F7")
BOX_STROKE = HexColor("#1B365D")
APP_FILL = HexColor("#D9E6F5")
DB_FILL = HexColor("#E8E0D4")
WARN_FILL = HexColor("#F7E4E4")
OK_FILL = HexColor("#DCEBDD")
LIGHT_LINE = HexColor("#6A7A8A")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def _styles():
    base = getSampleStyleSheet()
    s = {}
    s["body"] = ParagraphStyle(
        "Body",
        fontName="TimesNewRoman",
        fontSize=12,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceBefore=0,
        spaceAfter=8,
        textColor=black,
        hyphenationLang="en_GB",
        splitLongWords=True,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter",
        fontName="TimesNewRoman-Bold",
        fontSize=14,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=12,
        textColor=black,
        keepWithNext=True,
    )
    s["section"] = ParagraphStyle(
        "Section",
        fontName="TimesNewRoman-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6,
        textColor=black,
        keepWithNext=True,
    )
    s["title_univ"] = ParagraphStyle(
        "TitleUniv",
        fontName="TimesNewRoman-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceAfter=4,
    )
    s["title_dept"] = ParagraphStyle(
        "TitleDept",
        fontName="TimesNewRoman-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=black,
        spaceAfter=2,
    )
    s["title_doc"] = ParagraphStyle(
        "TitleDoc",
        fontName="TimesNewRoman-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=NAVY,
        spaceBefore=18,
        spaceAfter=8,
    )
    s["title_sub"] = ParagraphStyle(
        "TitleSub",
        fontName="TimesNewRoman-Bold",
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=black,
        spaceAfter=16,
    )
    s["title_note"] = ParagraphStyle(
        "TitleNote",
        fontName="TimesNewRoman-Italic",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=HexColor("#444444"),
        spaceBefore=16,
    )
    s["front_h"] = ParagraphStyle(
        "FrontH",
        fontName="TimesNewRoman-Bold",
        fontSize=14,
        leading=18,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=10,
        textColor=black,
        keepWithNext=True,
    )
    s["caption"] = ParagraphStyle(
        "Caption",
        fontName="TimesNewRoman-Italic",
        fontSize=10,
        leading=12,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=10,
        textColor=black,
    )
    s["table_caption"] = ParagraphStyle(
        "TableCaption",
        fontName="TimesNewRoman-Italic",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=4,
        textColor=black,
        keepWithNext=True,
    )
    s["th"] = ParagraphStyle(
        "TH",
        fontName="TimesNewRoman-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD",
        fontName="TimesNewRoman",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["td_c"] = ParagraphStyle(
        "TDc",
        fontName="TimesNewRoman",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb",
        fontName="TimesNewRoman-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["td_crit"] = ParagraphStyle(
        "TDcrit",
        fontName="TimesNewRoman-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=CRIT_FG,
    )
    s["td_high"] = ParagraphStyle(
        "TDhigh",
        fontName="TimesNewRoman-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=HIGH_FG,
    )
    s["td_med"] = ParagraphStyle(
        "TDmed",
        fontName="TimesNewRoman-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=MED_FG,
    )
    s["label"] = ParagraphStyle(
        "Label",
        fontName="TimesNewRoman-Bold",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["cell"] = ParagraphStyle(
        "Cell",
        fontName="TimesNewRoman",
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["meta_label"] = ParagraphStyle(
        "MetaLabel",
        fontName="TimesNewRoman-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["meta_value"] = ParagraphStyle(
        "MetaValue",
        fontName="TimesNewRoman",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["toc_item"] = ParagraphStyle(
        "TOCItem",
        fontName="TimesNewRoman",
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        textColor=black,
    )
    s["toc_sub"] = ParagraphStyle(
        "TOCSub",
        fontName="TimesNewRoman",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        leftIndent=18,
        textColor=black,
    )
    s["bullet"] = ParagraphStyle(
        "Bullet",
        fontName="TimesNewRoman",
        fontSize=12,
        leading=14,
        alignment=TA_JUSTIFY,
        leftIndent=18,
        bulletIndent=6,
        spaceBefore=1,
        spaceAfter=3,
        textColor=black,
    )
    s["note"] = ParagraphStyle(
        "Note",
        fontName="TimesNewRoman-Italic",
        fontSize=11,
        leading=13,
        alignment=TA_JUSTIFY,
        textColor=black,
    )
    s["fig_label"] = ParagraphStyle(
        "FigLabel",
        fontName="TimesNewRoman",
        fontSize=7.5,
        leading=9,
        alignment=TA_CENTER,
        textColor=black,
    )
    s["header"] = ParagraphStyle(
        "Header",
        fontName="TimesNewRoman-Italic",
        fontSize=9,
        leading=11,
        textColor=HexColor("#333333"),
    )
    s["footer"] = ParagraphStyle(
        "Footer",
        fontName="TimesNewRoman",
        fontSize=9,
        leading=11,
        textColor=HexColor("#333333"),
    )
    s["list_of"] = ParagraphStyle(
        "ListOf",
        fontName="TimesNewRoman",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT,
        textColor=black,
    )
    return s


S = _styles()


class BookmarkPara(Paragraph):
    """Paragraph that records a TOC/outline bookmark during build."""

    def __init__(self, text, style, bookmark, level=0):
        Paragraph.__init__(self, text, style)
        self.bookmark = bookmark
        self.level = level


class PageMarker(Flowable):
    """Zero-height marker used to record a table/figure page number."""

    def __init__(self, bookmark, level=2):
        Flowable.__init__(self)
        self.bookmark = bookmark
        self.level = level
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        pass


class TNRCanvas(pdfcanvas.Canvas):
    """Force every canvas font request onto Times New Roman (no Helvetica fallback)."""

    _MAP = {
        "Helvetica": "TimesNewRoman",
        "Helvetica-Bold": "TimesNewRoman-Bold",
        "Helvetica-Oblique": "TimesNewRoman-Italic",
        "Helvetica-BoldOblique": "TimesNewRoman-BoldItalic",
        "Times-Roman": "TimesNewRoman",
        "Times-Bold": "TimesNewRoman-Bold",
        "Times-Italic": "TimesNewRoman-Italic",
        "Times-BoldItalic": "TimesNewRoman-BoldItalic",
        "Courier": "TimesNewRoman",
        "Courier-Bold": "TimesNewRoman-Bold",
    }

    def setFont(self, psfontname, size, leading=None, **kwargs):
        psfontname = self._MAP.get(psfontname, psfontname)
        return pdfcanvas.Canvas.setFont(self, psfontname, size, leading, **kwargs)


# ---------------------------------------------------------------------------
# Header / footer
# ---------------------------------------------------------------------------
def _draw_header_footer(canv: pdfcanvas.Canvas, doc):
    canv.saveState()
    header_y = PAGE_H - 0.52 * inch
    footer_y = 0.45 * inch

    canv.setStrokeColor(NAVY)
    canv.setLineWidth(0.8)
    canv.line(LEFT_MARGIN, header_y - 4, PAGE_W - RIGHT_MARGIN, header_y - 4)

    canv.setFont("TimesNewRoman-Italic", 9)
    canv.setFillColor(HexColor("#333333"))
    canv.drawString(LEFT_MARGIN, header_y, "ICCTECH — Technical Debt Plan")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, header_y, "CSCD602 | University of Ghana")

    canv.setStrokeColor(NAVY)
    canv.line(LEFT_MARGIN, footer_y + 12, PAGE_W - RIGHT_MARGIN, footer_y + 12)

    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, footer_y, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, footer_y, f"Page {doc.page}")
    canv.restoreState()


def _draw_title_header_footer(canv: pdfcanvas.Canvas, doc):
    """Same running header/footer on the title page for numbering consistency."""
    _draw_header_footer(canv, doc)


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------
def _table(data, col_widths, header=True, extra=None):
    style_cmds = [
        ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#6E7A88")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
    ]
    if header:
        style_cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    if extra:
        style_cmds.extend(extra)
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(style_cmds))
    t.hAlign = "LEFT"
    t.keepWithNext = False
    return t


def _p(text, style="td"):
    return Paragraph(str(text), S[style])


def _note_block(text):
    inner = Paragraph(text, S["note"])
    bar = Table(
        [[inner]],
        colWidths=[CONTENT_W - 10],
    )
    bar.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBEFORE", (0, 0), (0, -1), 3, NOTE_BAR),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    bar.hAlign = "LEFT"
    return bar


def _bullets(items):
    flow = []
    for item in items:
        flow.append(Paragraph("•  " + item, S["bullet"]))
    return flow


def _caption_table(n, title):
    return Paragraph(f"<i>Table {n}. {title}</i>", S["table_caption"])


def _caption_fig(n, title):
    return Paragraph(f"<i>Figure {n}. {title}</i>", S["caption"])


def _center_drawing(drawing):
    wrap = Table([[drawing]], colWidths=[CONTENT_W])
    wrap.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    wrap.hAlign = "LEFT"
    return wrap


def _section_block(heading, style_key, bookmark, level, *flowables, min_space=110):
    """Keep a heading with following content so it never sits alone at a page bottom."""
    head = BookmarkPara(heading, S[style_key], bookmark, level)
    if not flowables:
        return [CondPageBreak(min_space), head]
    keep = [head]
    rest = []
    for i, fl in enumerate(flowables):
        if i < 3:
            keep.append(fl)
        else:
            rest.append(fl)
    return [CondPageBreak(min_space), KeepTogether(keep), *rest]


# ---------------------------------------------------------------------------
# Vector diagrams
# ---------------------------------------------------------------------------
def _box(d, x, y, w, h, lines, fill, stroke, fs=8, text_color=black, lw=0.9):
    d.add(Rect(x, y, w, h, rx=3.5, ry=3.5, fillColor=fill, strokeColor=stroke, strokeWidth=lw))
    n = len(lines)
    line_h = fs + 2
    total = n * line_h
    start = y + (h + total) / 2.0 - line_h + 1
    for i, line in enumerate(lines):
        d.add(
            String(
                x + w / 2.0,
                start - i * line_h,
                line,
                fontName="TimesNewRoman",
                fontSize=fs,
                fillColor=text_color,
                textAnchor="middle",
            )
        )


def _arrow(d, x1, y1, x2, y2, color=NAVY, head=6):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.1))
    # arrow head pointing toward (x2, y2)
    import math

    ang = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2, y2)
    p2 = (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4))
    p3 = (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4))
    d.add(Polygon([p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]], fillColor=color, strokeColor=color, strokeWidth=0.2))


def fig_identification_process():
    """Figure 1 — identification sources feeding the debt record structure."""
    W, H = CONTENT_W, 232
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    sources = [
        "Source code and\nconfiguration",
        "Deployment\narchitecture",
        "Testing and\ntraceability",
        "Security\nhardening",
        "Maintainability\nand naming",
        "Operations and\nresilience",
    ]
    gap = 10
    side = 14
    bw = (W - 2 * side - 2 * gap) / 3.0
    xs = [side + i * (bw + gap) for i in range(3)]
    for i, label in enumerate(sources):
        x = xs[i % 3]
        y = 176 if i < 3 else 126
        _box(d, x, y, bw, 42, label.split("\n"), BOX_FILL, BOX_STROKE, fs=8)

    _arrow(d, W / 2.0, 124, W / 2.0, 108, NAVY, head=6)

    steps = ["Debt", "Cause", "Impact", "Priority", "Resolution"]
    sg = 8
    sw = (W - 2 * side - 4 * sg) / 5.0
    sy = 64
    for i, st in enumerate(steps):
        x = side + i * (sw + sg)
        _box(d, x, sy, sw, 36, [st], HexColor("#D9E4F2"), NAVY, fs=8.5)
        if i < 4:
            _arrow(d, x + sw, sy + 18, x + sw + sg - 1, sy + 18, NAVY, head=5)

    _arrow(d, W / 2.0, 64, W / 2.0, 46, NAVY, head=6)
    _box(
        d,
        side,
        8,
        W - 2 * side,
        34,
        [
            "Technical Debt Register  (TD-01 to TD-09)",
            "Classification, target timeframe and source evidence recorded so repayment is tracked",
        ],
        NAVY,
        NAVY,
        fs=8,
        text_color=white,
    )
    return d


def fig_classification_model():
    """Figure 2 — three-tier classification."""
    W, H = CONTENT_W, 168
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    rows = [
        (118, CRIT_BG, CRIT_FG, "CRITICAL  /  IMMEDIATE", "Unacceptable security or release risk  →  resolve before long-term production use"),
        (70, HIGH_BG, HIGH_FG, "HIGH  /  SCHEDULED", "Does not block demonstration; affects security, reliability or regression confidence"),
        (22, MED_BG, MED_FG, "MEDIUM  /  MANAGED", "Acceptable under examination scope; review each release and repay as needed"),
    ]
    # pyramid-like widening bars, centred
    cy = 18
    heights = [42, 42, 42]
    # draw from bottom
    specs = [
        (22, MED_BG, MED_FG, BOX_STROKE, "MEDIUM / MANAGED", "Temporarily acceptable; maintainability, resilience, scalability"),
        (70, HIGH_BG, HIGH_FG, HexColor("#C47A1A"), "HIGH / SCHEDULED", "Schedule into production hardening or first maintenance release"),
        (118, CRIT_BG, CRIT_FG, CRIT_FG, "CRITICAL / IMMEDIATE", "Resolve before long-term public / production operation"),
    ]
    y = 18
    for x0, fill, tcol, stroke, title, sub in specs:
        w = W - 2 * x0
        _box(d, x0, y, w, 42, [title, sub], fill, stroke, fs=8, text_color=tcol, lw=1.0)
        y += 48
    return d


def fig_current_architecture():
    """Figure 3 — current 48-hour deployment, with debt call-outs."""
    W, H = CONTENT_W, 268
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    # Outer host
    d.add(Rect(18, 28, 396, 188, rx=5, ry=5, fillColor=HexColor("#F7F9FC"), strokeColor=NAVY, strokeWidth=1.2))
    d.add(String(26, 198, "Linode VPS  —  single host  (TD-07: single point of failure)", fontName="TimesNewRoman-Bold", fontSize=8, fillColor=NAVY))

    # Docker compose envelope
    d.add(Rect(32, 48, 250, 140, rx=4, ry=4, fillColor=white, strokeColor=STEEL, strokeWidth=0.9))
    d.add(String(40, 172, "Docker Compose", fontName="TimesNewRoman-Bold", fontSize=8, fillColor=STEEL))

    _box(d, 48, 100, 100, 56, ["PHP application", "ICCTECH / FreeITSM", "port 8080"], APP_FILL, NAVY_MID, fs=7.5)
    _box(d, 168, 100, 100, 56, ["MySQL 8", "container :3306", "volume persist"], DB_FILL, HexColor("#6B5428"), fs=7.5)
    _arrow(d, 148, 128, 166, 128, NAVY)

    _box(d, 48, 58, 220, 32, ["Default / development credentials declared in Compose  (TD-01)"], WARN_FILL, CRIT_FG, fs=7)

    # Published port callout
    _box(d, 298, 108, 104, 52, ["Host port 3307", "published  (TD-03)", "attack surface"], WARN_FILL, CRIT_FG, fs=7.5)
    _arrow(d, 268, 128, 296, 128, CRIT_FG)

    # Internet
    _box(d, 140, 232, 150, 28, ["Internet / examiner clients"], HexColor("#E8EEF6"), NAVY, fs=8)
    _arrow(d, 215, 232, 215, 218, CRIT_FG)
    d.add(String(222, 220, "HTTP :8080  (TD-02 — no TLS)", fontName="TimesNewRoman-Bold", fontSize=7.5, fillColor=CRIT_FG))

    d.add(String(26, 12, "No independent off-host backup (TD-05)  ·  Limited monitoring/alerting (TD-06)  ·  No CI workflow (TD-04)", fontName="TimesNewRoman", fontSize=7, fillColor=HexColor("#333333")))
    return d


def fig_target_architecture():
    """Figure 4 — intended production-hardened architecture after repayment."""
    W, H = CONTENT_W, 250
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    _box(d, 140, 216, 150, 26, ["Internet / clients"], HexColor("#E8EEF6"), NAVY, fs=8)
    _arrow(d, 215, 216, 215, 198, HexColor("#1F4D2C"))
    d.add(String(222, 202, "HTTPS :443  (TD-02 repaid)", fontName="TimesNewRoman-Bold", fontSize=7.5, fillColor=MED_FG))

    d.add(Rect(18, 28, 396, 168, rx=5, ry=5, fillColor=HexColor("#F3F8F4"), strokeColor=MED_FG, strokeWidth=1.2))
    d.add(String(26, 178, "Hardened production host  —  secrets externalised, TLS terminated, DB internal", fontName="TimesNewRoman-Bold", fontSize=7.5, fillColor=MED_FG))

    _box(d, 36, 118, 110, 48, ["Reverse proxy", "TLS certificate", "HTTP → HTTPS"], OK_FILL, MED_FG, fs=7.5)
    _arrow(d, 146, 142, 164, 142, NAVY)
    _box(d, 166, 118, 110, 48, ["PHP application", "internal network", "no public secrets"], APP_FILL, NAVY_MID, fs=7.5)
    _arrow(d, 276, 142, 294, 142, NAVY)
    _box(d, 296, 118, 102, 48, ["MySQL", "internal only", "no host :3307"], DB_FILL, HexColor("#6B5428"), fs=7.5)

    _box(d, 36, 44, 118, 56, ["Secrets", "env / Docker secrets", "not in source control", "(TD-01)"], OK_FILL, MED_FG, fs=7)
    _box(d, 166, 44, 118, 56, ["Off-host backups", "scheduled + restore test", "independent of VPS", "(TD-05)"], OK_FILL, MED_FG, fs=7)
    _box(d, 296, 44, 102, 56, ["Monitoring", "uptime, host, DB", "TLS expiry alerts", "(TD-06)"], OK_FILL, MED_FG, fs=7)
    return d


def fig_repayment_roadmap():
    """Figure 5 — three-phase repayment sequence."""
    W, H = CONTENT_W, 200
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    phases = [
        (12, CRIT_BG, CRIT_FG, "Phase 1", "Immediate /", "pre-production", ["TD-01  credentials", "TD-02  HTTPS", "TD-03  DB port", "TD-09  freeze release"]),
        (152, HIGH_BG, HIGH_FG, "Phase 2", "First", "maintenance", ["TD-04  tests + CI", "TD-05  off-host backup", "TD-06  monitoring", ""]),
        (292, MED_BG, MED_FG, "Phase 3", "Future", "evolution", ["TD-07  split / HA", "TD-08  naming", "", ""]),
    ]
    for x, fill, tcol, phase, l1, l2, items in phases:
        d.add(Rect(x, 48, 128, 140, rx=4, ry=4, fillColor=fill, strokeColor=tcol, strokeWidth=1.0))
        d.add(String(x + 64, 168, phase, fontName="TimesNewRoman-Bold", fontSize=9, fillColor=tcol, textAnchor="middle"))
        d.add(String(x + 64, 154, l1, fontName="TimesNewRoman-Bold", fontSize=8, fillColor=black, textAnchor="middle"))
        d.add(String(x + 64, 142, l2, fontName="TimesNewRoman-Bold", fontSize=8, fillColor=black, textAnchor="middle"))
        d.add(Line(x + 14, 136, x + 114, 136, strokeColor=tcol, strokeWidth=0.6))
        yy = 118
        for it in items:
            if it:
                d.add(String(x + 12, yy, "•  " + it, fontName="TimesNewRoman", fontSize=7.5, fillColor=black))
            yy -= 16

    _arrow(d, 140, 118, 152, 118, NAVY)
    _arrow(d, 280, 118, 292, 118, NAVY)

    d.add(String(W / 2, 18, "Exit: secrets + TLS + restricted DB + frozen release   →   CI + backup/restore + alerts   →   HA + naming", fontName="TimesNewRoman", fontSize=7, fillColor=HexColor("#333333"), textAnchor="middle"))
    return d


def fig_governance_cycle():
    """Figure 6 — review, governance and change-control cycle."""
    W, H = CONTENT_W, 188
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    # six boxes around a centre
    items = [
        (156, 148, "1. Review open items", "confirm impact & priority"),
        (300, 100, "2. Record new debt", "from impl. / test / deploy"),
        (300, 36, "3. Identify repaid debt", "retain resolution evidence"),
        (156, 8, "4. Re-prioritise", "security, reliability, delay"),
        (14, 36, "5. Protect critical debt", "do not defer security"),
        (14, 100, "6. Update artefacts", "roadmap, notes, docs"),
    ]
    for x, y, t1, t2 in items:
        _box(d, x, y, 116, 36, [t1, t2], BOX_FILL, BOX_STROKE, fs=7)
    _box(d, 156, 78, 116, 44, ["Debt register", "reviewed each release", "and on major change"], NAVY, NAVY, fs=7.5, text_color=white)
    # light connecting lines
    d.add(Line(214, 148, 214, 122, strokeColor=STEEL, strokeWidth=0.8))
    d.add(Line(214, 78, 214, 44, strokeColor=STEEL, strokeWidth=0.8))
    d.add(Line(156, 100, 130, 118, strokeColor=STEEL, strokeWidth=0.8))
    d.add(Line(272, 100, 300, 118, strokeColor=STEEL, strokeWidth=0.8))
    d.add(Line(156, 88, 130, 54, strokeColor=STEEL, strokeWidth=0.8))
    d.add(Line(272, 88, 300, 54, strokeColor=STEEL, strokeWidth=0.8))
    return d


def fig_testing_vs_debt():
    """Figure 7 — testing/acceptance versus technical-debt management."""
    W, H = CONTENT_W, 168
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))

    _box(d, 16, 70, 186, 86, ["Functional testing", "Do the defined requirements", "behave as expected?", "Example: login tests pass"], APP_FILL, NAVY_MID, fs=8)
    _box(d, 230, 70, 186, 86, ["Technical-debt management", "Is the solution hardened,", "maintainable, recoverable?", "Example: HTTPS still required"], WARN_FILL, CRIT_FG, fs=8)
    d.add(String(W / 2, 48, "A 100% pass rate for selected functional tests can coexist with open debt items.", fontName="TimesNewRoman-Bold", fontSize=8, fillColor=NAVY, textAnchor="middle"))
    d.add(String(W / 2, 28, "Ticket persistence may survive container restart while independent disaster-recovery backup remains future work (TD-05).", fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle"))
    d.add(String(W / 2, 12, "Acceptance testing  ≠  elimination of engineering risk.", fontName="TimesNewRoman-Italic", fontSize=8, fillColor=black, textAnchor="middle"))
    return d


# ---------------------------------------------------------------------------
# Document content
# ---------------------------------------------------------------------------
def _meta_table():
    rows = [
        ("Student Name", "Clement Asamoah"),
        ("Student ID", "22424193"),
        ("Project", "ICCTECH"),
        ("Academic Year", "First Semester, 2025/2026"),
        ("Examination Duration", "48 Hours"),
        ("Live Application", "http://45.79.223.146:8080/index.php"),
        ("Report Version", "1.0 — Final"),
    ]
    data = [[_p(a, "meta_label"), _p(b, "meta_value")] for a, b in rows]
    t = Table(data, colWidths=[150, CONTENT_W - 150])
    t.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "TimesNewRoman"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#6E7A88")),
                ("BACKGROUND", (0, 0), (0, -1), HexColor("#EEF2F7")),
                ("BACKGROUND", (1, 0), (1, -1), white),
            ]
        )
    )
    t.hAlign = "LEFT"
    return t


def _doc_control_table():
    rows = [
        ("Document", "Technical_Debt_Plan.pdf"),
        (
            "Purpose",
            "Identification, prioritisation, management and repayment plan for significant ICCTECH technical debt.",
        ),
        (
            "Primary Basis",
            "Defined 48-hour project scope, deployed Linode/Docker architecture and submitted source-code configuration.",
        ),
        ("Debt Items", "9 significant technical-debt items."),
        ("Highest Priority", "Credential management and HTTPS hardening."),
        (
            "Review Status",
            "Prepared for final examination submission; release traceability must be verified during final packaging.",
        ),
    ]
    data = [[_p(a, "label"), _p(b, "cell")] for a, b in rows]
    t = Table(data, colWidths=[120, CONTENT_W - 120])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.45, HexColor("#6E7A88")),
                ("BACKGROUND", (0, 0), (0, -1), HexColor("#EEF2F7")),
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ]
        )
    )
    # first column header look: actually all labels on left. Colour first col only.
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), HexColor("#1B365D")),
                ("TEXTCOLOR", (0, 0), (0, -1), white),
            ]
        )
    )
    # labels are Paragraphs with black - need white label style
    white_label = ParagraphStyle("WL", parent=S["label"], textColor=white, fontSize=10, leading=12)
    data = [[Paragraph(a, white_label), _p(b, "cell")] for a, b in rows]
    t = Table(data, colWidths=[120, CONTENT_W - 120])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, -1), 0.45, HexColor("#6E7A88")),
                ("BACKGROUND", (0, 0), (0, -1), HEADER_BG),
                ("BACKGROUND", (1, 0), (1, -1), white),
            ]
        )
    )
    t.hAlign = "LEFT"
    return t


def _priority_style(level):
    return {"Critical": "td_crit", "High": "td_high", "Medium": "td_med"}[level]


def _priority_bg(level):
    return {"Critical": CRIT_BG, "High": HIGH_BG, "Medium": MED_BG}[level]


def _register_table():
    headers = ["ID", "Technical Debt", "Priority", "Classification", "Target", "Status"]
    items = [
        ("TD-01", "Development/default credentials remain in Docker configuration", "Critical", "Immediate resolution", "Before continued public/production use", "Outstanding / managed"),
        ("TD-02", "Live deployment currently uses HTTP rather than HTTPS", "Critical", "Immediate resolution", "Before long-term production use", "Outstanding / managed"),
        ("TD-03", "MySQL host port is published in the Docker Compose deployment", "High", "Production hardening", "Before hardened production use", "Outstanding / managed"),
        ("TD-04", "Project-specific automated regression coverage and CI are limited", "High", "Scheduled for next release", "First maintenance release", "Outstanding / managed"),
        ("TD-05", "No demonstrated automated off-host backup and restore process", "High", "Scheduled for next release", "First maintenance release", "Outstanding / managed"),
        ("TD-06", "Production monitoring and automated alerting are limited", "Medium", "Scheduled", "Subsequent maintenance release", "Outstanding / managed"),
        ("TD-07", "Application and database share a single Linode host", "Medium", "Temporarily acceptable / future evolution", "Future production evolution", "Outstanding / managed"),
        ("TD-08", "Legacy/upstream naming remains in internal configuration and resources", "Medium", "Temporarily acceptable / scheduled refactoring", "Future refactoring releases", "Outstanding / managed"),
        ("TD-09", "Documentation and evidence can drift from the exact deployed release", "Medium", "Resolve before submission", "Before final Sakai submission", "Outstanding / managed"),
    ]
    # 432 total
    widths = [38, 118, 48, 78, 80, 70]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    for i, row in enumerate(items, start=1):
        pri = row[2]
        data.append(
            [
                _p(f"<b>{row[0]}</b>", "td"),
                _p(row[1], "td"),
                _p(pri, _priority_style(pri)),
                _p(row[3], "td"),
                _p(row[4], "td"),
                _p(row[5], "td"),
            ]
        )
        extra.append(("BACKGROUND", (2, i), (2, i), _priority_bg(pri)))
        extra.append(("VALIGN", (0, i), (-1, i), "TOP"))
        extra.append(("ALIGN", (2, i), (2, i), "CENTER"))
    return _table(data, widths, header=True, extra=extra)


def _classification_table():
    headers = ["Classification", "Meaning", "Treatment"]
    rows = [
        (
            "Critical / Immediate",
            "Creates unacceptable security or release risk for continued production use.",
            "Resolve before long-term public/production operation.",
        ),
        (
            "High / Scheduled",
            "Does not prevent examination demonstration but materially affects security, reliability or regression confidence.",
            "Schedule into production hardening or first maintenance release.",
        ),
        (
            "Medium / Managed",
            "Acceptable temporarily under the examination scope but affects maintainability, resilience or future scalability.",
            "Document, review each release and repay according to operational need.",
        ),
    ]
    widths = [110, 161, 161]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    bgs = [CRIT_BG, HIGH_BG, MED_BG]
    for i, r in enumerate(rows, start=1):
        data.append([_p(f"<b>{r[0]}</b>", "td"), _p(r[1], "td"), _p(r[2], "td")])
        extra.append(("BACKGROUND", (0, i), (0, i), bgs[i - 1]))
    return _table(data, widths, header=True, extra=extra)


def _debt_detail_table(fields: OrderedDict):
    white_label = ParagraphStyle("DL", parent=S["label"], textColor=white, fontSize=9, leading=11)
    data = []
    for k, v in fields.items():
        data.append([Paragraph(k, white_label), Paragraph(v, S["cell"])])
    t = Table(data, colWidths=[118, CONTENT_W - 118])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.4, HexColor("#6E7A88")),
                ("BACKGROUND", (0, 0), (0, -1), HEADER_BG),
                ("BACKGROUND", (1, 0), (1, -1), white),
            ]
        )
    )
    t.hAlign = "LEFT"
    return t


def _roadmap_table():
    headers = ["Phase", "Debt Items", "Objective", "Exit Condition"]
    rows = [
        (
            "Immediate / pre-production",
            "TD-01, TD-02, TD-03, TD-09",
            "Reduce security and submission-traceability risk.",
            "Secrets externalised; HTTPS plan/implementation complete for production; database exposure restricted; final release frozen and identified.",
        ),
        (
            "First maintenance release",
            "TD-04, TD-05, TD-06",
            "Improve regression confidence, recoverability and observability.",
            "CI regression suite running; off-host backup + restore test documented; monitoring alerts operational.",
        ),
        (
            "Future evolution",
            "TD-07, TD-08",
            "Improve resilience, scalability and maintainability.",
            "Architecture changes justified by scale; naming refactoring completed incrementally without breaking required attribution.",
        ),
    ]
    widths = [90, 88, 112, 142]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    bgs = [CRIT_BG, HIGH_BG, MED_BG]
    for i, r in enumerate(rows, start=1):
        data.append([_p(f"<b>{r[0]}</b>", "td"), _p(r[1], "td"), _p(r[2], "td"), _p(r[3], "td")])
        extra.append(("BACKGROUND", (0, i), (0, i), bgs[i - 1]))
    return _table(data, widths, header=True, extra=extra)


def _toc_line(title, page, indent=0, bold=False):
    """Dotted-leader TOC row as a two-column table."""
    st = ParagraphStyle(
        "tocline",
        fontName="TimesNewRoman-Bold" if bold else "TimesNewRoman",
        fontSize=12 if bold else 11,
        leading=16 if bold else 14,
        textColor=black,
        leftIndent=indent,
    )
    pg = ParagraphStyle("tocpg", parent=st, alignment=TA_RIGHT, leftIndent=0)
    left = Paragraph(title, st)
    right = Paragraph(str(page) if page else "—", pg)
    t = Table([[left, right]], colWidths=[CONTENT_W - 36, 36])
    t.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LINEBELOW", (0, 0), (0, 0), 0.3, HexColor("#C8C8C8")),
            ]
        )
    )
    t.hAlign = "LEFT"
    return t


# Debt item data (verbatim from source)
DEBT_ITEMS = [
    (
        "4.1 TD-01 — Development/default credentials remain in Docker configuration",
        "ch4.1",
        OrderedDict(
            [
                ("Debt", "Development/default credentials remain in Docker configuration."),
                (
                    "Cause",
                    "The timeboxed Docker environment used directly declared development/default database credentials for rapid setup and reproducibility.",
                ),
                (
                    "Impact",
                    "If development credentials are reused in an internet-accessible environment, exposure of the repository or configuration could increase the risk of unauthorised database access.",
                ),
                ("Priority", "Critical"),
                ("Classification", "Immediate resolution"),
                (
                    "Proposed Resolution",
                    "Create unique production credentials, rotate any reused credentials, move secrets to protected environment variables or Docker secrets, and keep secret files outside source control.",
                ),
                ("Target", "Before continued public/production use"),
                (
                    "Source Evidence",
                    "docker-compose.yml declares database credential variables directly.",
                ),
            ]
        ),
        "Security note: the plan intentionally does not reproduce actual credential values. The correct action is to rotate and externalise production secrets rather than copy them into documentation.",
    ),
    (
        "4.2 TD-02 — Live deployment currently uses HTTP rather than HTTPS",
        "ch4.2",
        OrderedDict(
            [
                ("Debt", "Live deployment currently uses HTTP rather than HTTPS."),
                (
                    "Cause",
                    "The application was deployed rapidly to the Linode server by IP address and port 8080 without TLS termination during the 48-hour project period.",
                ),
                (
                    "Impact",
                    "Authentication and application traffic are not encrypted in transit, making the deployment unsuitable for long-term production use on untrusted networks.",
                ),
                ("Priority", "Critical"),
                ("Classification", "Immediate resolution"),
                (
                    "Proposed Resolution",
                    "Assign a domain name, configure a reverse proxy or web-server virtual host, install a trusted TLS certificate, and redirect all HTTP requests to HTTPS.",
                ),
                ("Target", "Before long-term production use"),
                (
                    "Source Evidence",
                    "The verified live application URL uses http://45.79.223.146:8080/index.php.",
                ),
            ]
        ),
        None,
    ),
    (
        "4.3 TD-03 — MySQL host port is published in the Docker Compose deployment",
        "ch4.3",
        OrderedDict(
            [
                ("Debt", "MySQL host port is published in the Docker Compose deployment."),
                (
                    "Cause",
                    "Publishing the database port simplified development, troubleshooting and direct database administration.",
                ),
                (
                    "Impact",
                    "If host or cloud firewall controls allow remote access, unnecessary database exposure increases the attack surface.",
                ),
                ("Priority", "High"),
                ("Classification", "Production hardening"),
                (
                    "Proposed Resolution",
                    "Remove the public database port mapping in the production Compose profile and use the internal Docker network. Where administrator access is needed, use SSH tunnelling or tightly restricted firewall rules.",
                ),
                ("Target", "Before hardened production use"),
                (
                    "Source Evidence",
                    "docker-compose.yml maps host port 3307 to MySQL container port 3306.",
                ),
            ]
        ),
        None,
    ),
    (
        "4.4 TD-04 — Project-specific automated regression coverage and CI are limited",
        "ch4.4",
        OrderedDict(
            [
                ("Debt", "Project-specific automated regression coverage and CI are limited."),
                (
                    "Cause",
                    "The 48-hour project prioritised completion and validation of the core ticket lifecycle. The repository contains automated test scripts, but there is no demonstrated CI workflow executing a requirements-mapped regression suite on every change.",
                ),
                (
                    "Impact",
                    "Future modifications may introduce regressions that are discovered late or only during manual testing.",
                ),
                ("Priority", "High"),
                ("Classification", "Scheduled for next release"),
                (
                    "Proposed Resolution",
                    "Expand automated tests for authentication, RBAC, ticket creation, assignment, status transitions, resolution and persistence; map tests to FR/NFR identifiers; add a GitHub Actions or equivalent CI pipeline.",
                ),
                ("Target", "First maintenance release"),
                (
                    "Source Evidence",
                    "The repository contains tests/, while .github contains no workflow configuration.",
                ),
            ]
        ),
        None,
    ),
    (
        "4.5 TD-05 — No demonstrated automated off-host backup and restore process",
        "ch4.5",
        OrderedDict(
            [
                ("Debt", "No demonstrated automated off-host backup and restore process."),
                (
                    "Cause",
                    "The examination focused on functional deployment and Docker volume persistence rather than disaster-recovery automation.",
                ),
                (
                    "Impact",
                    "Container volumes protect against normal container recreation but do not by themselves protect against server loss, corruption or accidental destructive changes.",
                ),
                ("Priority", "High"),
                ("Classification", "Scheduled for next release"),
                (
                    "Proposed Resolution",
                    "Implement scheduled MySQL backups, store copies independently of the Linode host, define retention rules, protect backup access, and perform documented restoration tests.",
                ),
                ("Target", "First maintenance release"),
                (
                    "Source Evidence",
                    "Docker volumes provide persistence, but the submitted deployment does not demonstrate an independent backup/restore workflow.",
                ),
            ]
        ),
        "Engineering distinction: persistent Docker volumes reduce data loss during normal container restart or recreation, but persistence is not equivalent to an independent backup and disaster-recovery capability.",
    ),
    (
        "4.6 TD-06 — Production monitoring and automated alerting are limited",
        "ch4.6",
        OrderedDict(
            [
                ("Debt", "Production monitoring and automated alerting are limited."),
                (
                    "Cause",
                    "Implementation effort was concentrated on application functionality, testing and deployment rather than operational observability.",
                ),
                (
                    "Impact",
                    "Application, database, container, disk or host failures may not be detected until a user reports a problem.",
                ),
                ("Priority", "Medium"),
                ("Classification", "Scheduled"),
                (
                    "Proposed Resolution",
                    "Add uptime checks, container health monitoring, CPU/memory/disk metrics, database availability monitoring and threshold-based alerts. Include TLS certificate expiry monitoring once HTTPS is implemented.",
                ),
                ("Target", "Subsequent maintenance release"),
                (
                    "Source Evidence",
                    "No project-specific production monitoring or alerting configuration is demonstrated in the submitted deployment assets.",
                ),
            ]
        ),
        None,
    ),
    (
        "4.7 TD-07 — Application and database share a single Linode host",
        "ch4.7",
        OrderedDict(
            [
                ("Debt", "Application and database share a single Linode host."),
                (
                    "Cause",
                    "A single-server Docker deployment was the simplest, fastest and most economical architecture for the 48-hour examination.",
                ),
                (
                    "Impact",
                    "The server is a single point of failure and limits high availability and horizontal scalability. A host outage affects both the web application and database.",
                ),
                ("Priority", "Medium"),
                ("Classification", "Temporarily acceptable / future evolution"),
                (
                    "Proposed Resolution",
                    "For higher availability, separate application and database workloads, consider a managed or replicated database, implement health checks and backups, and introduce load balancing when scale justifies it.",
                ),
                ("Target", "Future production evolution"),
                (
                    "Source Evidence",
                    "The current deployment runs the application and MySQL services through Docker Compose on one Linode server.",
                ),
            ]
        ),
        None,
    ),
    (
        "4.8 TD-08 — Legacy/upstream naming remains in internal configuration and resources",
        "ch4.8",
        OrderedDict(
            [
                ("Debt", "Legacy/upstream naming remains in internal configuration and resources."),
                (
                    "Cause",
                    "Renaming every inherited internal identifier during the 48-hour period would create unnecessary regression risk and consume time better spent validating the core workflow.",
                ),
                (
                    "Impact",
                    "Legacy names can confuse maintainers and reduce consistency between the ICCTECH project identity and internal configuration, database names, paths or documentation.",
                ),
                ("Priority", "Medium"),
                ("Classification", "Temporarily acceptable / scheduled refactoring"),
                (
                    "Proposed Resolution",
                    "Refactor legacy identifiers incrementally, beginning with project-facing configuration and documentation. Run regression tests after each naming change and preserve required third-party attribution and licence notices.",
                ),
                ("Target", "Future refactoring releases"),
                (
                    "Source Evidence",
                    "Examples of legacy FreeITSM identifiers remain in docker-compose.yml, database paths and application configuration.",
                ),
            ]
        ),
        "Refactoring must preserve any required upstream attribution, copyright and licence notices. The objective is naming consistency and maintainability, not removal of legitimate third-party acknowledgement.",
    ),
    (
        "4.9 TD-09 — Documentation and evidence can drift from the exact deployed release",
        "ch4.9",
        OrderedDict(
            [
                ("Debt", "Documentation and evidence can drift from the exact deployed release."),
                (
                    "Cause",
                    "Source code, documentation, screenshots and testing evidence were prepared rapidly during the same examination window.",
                ),
                (
                    "Impact",
                    "If artifacts refer to different revisions, traceability is weakened and the examiner may see discrepancies between documentation, repository and live system.",
                ),
                ("Priority", "Medium"),
                ("Classification", "Resolve before submission"),
                (
                    "Proposed Resolution",
                    "Freeze the final application version, commit and tag it, record the final Git commit hash, verify screenshots and documentation against that build, and avoid untracked changes after evidence capture.",
                ),
                ("Target", "Before final Sakai submission"),
                (
                    "Source Evidence",
                    "Release traceability depends on final repository state and should be confirmed as part of submission packaging.",
                ),
            ]
        ),
        None,
    ),
]


TOC_ENTRIES = [
    ("front-dc", 0, "Document Control"),
    ("front-exec", 0, "Executive Summary"),
    ("ch1", 0, "1. Purpose and Context"),
    ("ch1.1", 1, "1.1 Purpose"),
    ("ch1.2", 1, "1.2 Definition of Technical Debt"),
    ("ch1.3", 1, "1.3 Project Context"),
    ("ch2", 0, "2. Technical Debt Management Approach"),
    ("ch2.1", 1, "2.1 Identification Sources"),
    ("ch2.2", 1, "2.2 Required Debt Record Structure"),
    ("ch2.3", 1, "2.3 Priority and Classification"),
    ("ch3", 0, "3. Technical Debt Register"),
    ("ch4", 0, "4. Detailed Debt Analysis"),
    ("ch4.1", 1, "4.1 TD-01 — Credentials in Docker configuration"),
    ("ch4.2", 1, "4.2 TD-02 — HTTP rather than HTTPS"),
    ("ch4.3", 1, "4.3 TD-03 — Published MySQL host port"),
    ("ch4.4", 1, "4.4 TD-04 — Limited automated regression and CI"),
    ("ch4.5", 1, "4.5 TD-05 — No off-host backup and restore"),
    ("ch4.6", 1, "4.6 TD-06 — Limited monitoring and alerting"),
    ("ch4.7", 1, "4.7 TD-07 — Single-host application and database"),
    ("ch4.8", 1, "4.8 TD-08 — Legacy/upstream naming"),
    ("ch4.9", 1, "4.9 TD-09 — Documentation and evidence drift"),
    ("ch5", 0, "5. Repayment Plan and Roadmap"),
    ("ch5.1", 1, "5.1 Immediate Security and Submission Actions"),
    ("ch5.2", 1, "5.2 First Maintenance Release"),
    ("ch5.3", 1, "5.3 Future Evolution"),
    ("ch5.4", 1, "5.4 Repayment Sequence"),
    ("ch6", 0, "6. Review, Governance and Change Control"),
    ("ch6.1", 1, "6.1 Proposed Review Procedure"),
    ("ch6.2", 1, "6.2 Definition of Debt Repaid"),
    ("ch7", 0, "7. Relationship to Testing and Acceptance"),
    ("ch8", 0, "8. Residual Risk and Project Limitations"),
    ("ch9", 0, "9. Conclusion"),
    ("ch10", 0, "10. References and Acknowledgements"),
]

TABLE_LIST = [
    ("t1", "Table 1. Technical debt classification model"),
    ("t2", "Table 2. ICCTECH technical debt register"),
    ("t3", "Table 3. Technical debt repayment roadmap"),
]

FIGURE_LIST = [
    ("f1", "Figure 1. Technical debt identification and recording process"),
    ("f2", "Figure 2. Technical debt classification model"),
    ("f3", "Figure 3. Current ICCTECH deployment architecture and associated debt"),
    ("f4", "Figure 4. Target production-hardened architecture after debt repayment"),
    ("f5", "Figure 5. Technical debt repayment roadmap"),
    ("f6", "Figure 6. Review, governance and change-control cycle"),
    ("f7", "Figure 7. Functional testing versus technical-debt management"),
]


def build_story(pages: dict) -> list:
    story = []

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 0.55 * inch))
    story.append(Paragraph("UNIVERSITY OF GHANA", S["title_univ"]))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE", S["title_dept"]))
    story.append(Paragraph("CSCD602 — ADVANCED SOFTWARE ENGINEERING", S["title_dept"]))
    story.append(Paragraph("TECHNICAL DEBT PLAN", S["title_doc"]))
    story.append(
        Paragraph(
            "ICCTECH: A Web-Based IT Service Management and Helpdesk System",
            S["title_sub"],
        )
    )
    story.append(_meta_table())
    story.append(
        Paragraph(
            "Prepared for the Individual Software Engineering Capstone Examination",
            S["title_note"],
        )
    )

    # ===== DOCUMENT CONTROL =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "Document Control",
            "front_h",
            "front-dc",
            0,
            _doc_control_table(),
        )
    )

    # ===== EXECUTIVE SUMMARY =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "Executive Summary",
            "front_h",
            "front-exec",
            0,
            Paragraph(
                "This Technical Debt Plan documents significant technical debt identified during the ICCTECH 48-hour software-engineering project. Technical debt is treated as a managed engineering trade-off rather than simply as unfinished functionality. The plan identifies the cause and impact of each debt item, assigns a priority and classification, and defines a practical resolution path.",
                S["body"],
            ),
        )
    )
    story.append(
        Paragraph(
            "Nine significant debt items are recorded. Two are classified as critical security-hardening concerns requiring immediate attention before long-term production use, several high-priority items are scheduled for the first maintenance release, and medium-priority architecture and maintainability items are accepted temporarily or scheduled for later evolution. The plan also explains how debt will be reviewed, repaid and prevented from accumulating without visibility.",
            S["body"],
        )
    )
    story.append(
        Paragraph(
            "The presence of technical debt does not imply that the core examination workflow failed testing. Functional acceptance and technical debt address different questions: testing verifies whether the defined requirements behave as expected, while technical-debt management identifies design, security, operational and maintainability improvements that remain desirable after the timeboxed implementation.",
            S["body"],
        )
    )

    # ===== TABLE OF CONTENTS =====
    story.append(PageBreak())
    story.append(Paragraph("Table of Contents", S["front_h"]))
    story.append(Spacer(1, 6))
    for key, level, title in TOC_ENTRIES:
        pg = pages.get(key, "")
        story.append(_toc_line(title, pg, indent=18 if level else 0, bold=(level == 0)))

    story.append(Spacer(1, 14))
    story.append(Paragraph("List of Tables", S["section"]))
    for key, title in TABLE_LIST:
        story.append(_toc_line(title, pages.get(key, ""), indent=0, bold=False))

    story.append(Spacer(1, 10))
    story.append(Paragraph("List of Figures", S["section"]))
    for key, title in FIGURE_LIST:
        story.append(_toc_line(title, pages.get(key, ""), indent=0, bold=False))

    # ===== CHAPTER 1 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "1. Purpose and Context",
            "chapter",
            "ch1",
            0,
            BookmarkPara("1.1 Purpose", S["section"], "ch1.1", 1),
            Paragraph(
                "The purpose of this plan is to provide a formal record of technical debt identified in ICCTECH and to show how that debt will be prioritised, monitored and repaid after the 48-hour examination period. It complements the SRS, Testing Report, Deployment section and Maintenance Strategy by documenting engineering compromises that are acceptable temporarily but should not remain invisible.",
                S["body"],
            ),
        )
    )
    story.extend(
        _section_block(
            "1.2 Definition of Technical Debt",
            "section",
            "ch1.2",
            1,
            Paragraph(
                "For this project, technical debt is any implementation, architecture, security, testing, deployment or maintainability compromise that reduces short-term effort but creates future cost, risk or rework. Technical debt may be deliberate, such as accepting a single-server architecture for a short examination, or incidental, such as retaining legacy internal naming because broad refactoring would create unnecessary regression risk.",
                S["body"],
            ),
        )
    )
    story.extend(
        _section_block(
            "1.3 Project Context",
            "section",
            "ch1.3",
            1,
            Paragraph(
                "ICCTECH was completed under a strict 48-hour capstone examination. The project therefore prioritised a demonstrable IT Service Management workflow, requirements traceability, testing, deployment and documentation. This time constraint made it necessary to defer some production-hardening, automation and operational-resilience work to later releases.",
                S["body"],
            ),
        )
    )

    # ===== CHAPTER 2 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "2. Technical Debt Management Approach",
            "chapter",
            "ch2",
            0,
            BookmarkPara("2.1 Identification Sources", S["section"], "ch2.1", 1),
            Paragraph(
                "Significant technical debt was identified from the following complementary reviews of the delivered system:",
                S["body"],
            ),
        )
    )
    story.extend(
        _bullets(
            [
                "Source-code and configuration review, including Docker and database configuration.",
                "Deployment architecture review of the Linode-hosted environment.",
                "Testing and requirements traceability review.",
                "Security-hardening review of authentication, transport and network exposure.",
                "Maintainability review of internal naming, automation and release traceability.",
                "Operational review of backup, monitoring, resilience and future scaling needs.",
            ]
        )
    )
    story.append(Spacer(1, 8))
    story.append(KeepTogether([
        PageMarker("f1", 2),
        _center_drawing(fig_identification_process()),
        _caption_fig(1, "Technical debt identification and recording process"),
    ]))

    story.extend(
        _section_block(
            "2.2 Required Debt Record Structure",
            "section",
            "ch2.2",
            1,
            Paragraph(
                "Each significant technical-debt item is recorded using the examination structure: Debt → Cause → Impact → Priority → Proposed Resolution. The plan additionally records a classification, target timeframe and source evidence so that repayment can be tracked rather than treated as an informal intention.",
                S["body"],
            ),
        )
    )

    story.extend(
        _section_block(
            "2.3 Priority and Classification",
            "section",
            "ch2.3",
            1,
            PageMarker("t1", 2),
            _caption_table(1, "Technical debt classification model"),
            _classification_table(),
            min_space=220,
        )
    )
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        PageMarker("f2", 2),
        _center_drawing(fig_classification_model()),
        _caption_fig(2, "Technical debt classification model"),
    ]))

    # ===== CHAPTER 3 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "3. Technical Debt Register",
            "chapter",
            "ch3",
            0,
            Paragraph(
                "Table 2 summarises the significant debt items identified for the current ICCTECH release. The detailed analysis in Section 4 expands each item using the required debt-management structure.",
                S["body"],
            ),
        )
    )
    story.append(KeepTogether([
        PageMarker("t2", 2),
        _caption_table(2, "ICCTECH technical debt register"),
        _register_table(),
    ]))
    story.append(Spacer(1, 8))
    story.append(KeepTogether([
        PageMarker("f3", 2),
        _center_drawing(fig_current_architecture()),
        _caption_fig(
            3,
            "Current ICCTECH deployment architecture and associated debt (TD-01, TD-02, TD-03, TD-07; TD-04/05/06 noted)",
        ),
        Paragraph(
            "Figure 3 locates the register items on the deployed architecture. TD-01, TD-02, TD-03 and TD-07 appear as structural call-outs on the single Linode host; TD-04, TD-05 and TD-06 are operational gaps noted beneath the host boundary. Section 4 records each item in the required Debt, Cause, Impact, Priority and Proposed Resolution structure.",
            S["body"],
        ),
    ]))

    # ===== CHAPTER 4 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "4. Detailed Debt Analysis",
            "chapter",
            "ch4",
            0,
            Paragraph(
                "Each item below follows the required record structure. Priority and classification are repeated from the register so that the analysis can be read independently of Table 2.",
                S["body"],
            ),
        )
    )

    for i, (heading, bm, fields, note) in enumerate(DEBT_ITEMS):
        block = [
            BookmarkPara(heading, S["section"], bm, 1),
            _debt_detail_table(fields),
        ]
        if note:
            block.append(Spacer(1, 6))
            block.append(_note_block(note))
        # After TD-02 (index 1), show target architecture once we have described HTTP debt
        story.append(CondPageBreak(100))
        story.append(KeepTogether(block[:2]))
        if note:
            story.append(Spacer(1, 6))
            story.append(_note_block(note))
        if i == 1:
            story.append(Spacer(1, 10))
            story.append(KeepTogether([
                PageMarker("f4", 2),
                _center_drawing(fig_target_architecture()),
                _caption_fig(
                    4,
                    "Target production-hardened architecture after repayment of TD-01, TD-02, TD-03, TD-05 and TD-06",
                ),
            ]))

    # ===== CHAPTER 5 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "5. Repayment Plan and Roadmap",
            "chapter",
            "ch5",
            0,
            BookmarkPara("5.1 Immediate Security and Submission Actions", S["section"], "ch5.1", 1),
        )
    )
    story.extend(
        _bullets(
            [
                "TD-01: rotate/externalise production credentials and ensure secrets are not committed to the public repository.",
                "TD-02: introduce HTTPS before long-term production use.",
                "TD-03: remove or strictly restrict direct database host-port exposure.",
                "TD-09: freeze the final build, record the repository commit/tag, and verify all submitted evidence against that release.",
            ]
        )
    )
    story.extend(
        _section_block(
            "5.2 First Maintenance Release",
            "section",
            "ch5.2",
            1,
        )
    )
    story.extend(
        _bullets(
            [
                "TD-04: expand requirements-mapped automated regression tests and add CI execution.",
                "TD-05: implement automated off-host database backups and perform a documented restore test.",
                "TD-06: add baseline uptime, host, container and database monitoring with alerts.",
            ]
        )
    )
    story.extend(
        _section_block(
            "5.3 Future Evolution",
            "section",
            "ch5.3",
            1,
        )
    )
    story.extend(
        _bullets(
            [
                "TD-07: improve resilience when operational scale justifies separating or replicating application/database workloads.",
                "TD-08: refactor legacy internal naming incrementally while protecting upstream attribution and regression stability.",
            ]
        )
    )
    story.extend(
        _section_block(
            "5.4 Repayment Sequence",
            "section",
            "ch5.4",
            1,
            PageMarker( "t3", 2),
            _caption_table(3, "Technical debt repayment roadmap"),
            _roadmap_table(),
        )
    )
    story.append(Spacer(1, 10))
    story.append(KeepTogether([
        Paragraph(
            "Figure 5 presents the same sequence as a visual roadmap. Each phase must meet its exit condition before the next phase is treated as complete.",
            S["body"],
        ),
        PageMarker("f5", 2),
        _center_drawing(fig_repayment_roadmap()),
        _caption_fig(5, "Technical debt repayment roadmap"),
    ]))

    # ===== CHAPTER 6 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "6. Review, Governance and Change Control",
            "chapter",
            "ch6",
            0,
            Paragraph(
                "The technical debt register should be reviewed at each maintenance release and whenever a significant architecture, security or deployment change is proposed. Critical security debt takes precedence over new features. High-priority reliability and test-automation debt is planned into the next release cycle. Medium-priority debt is ranked using user impact, operational risk, implementation effort and the likelihood that the debt will become more expensive to repay later.",
                S["body"],
            ),
        )
    )
    story.append(KeepTogether([
        PageMarker("f6", 2),
        _center_drawing(fig_governance_cycle()),
        _caption_fig(6, "Review, governance and change-control cycle"),
    ]))

    story.extend(
        _section_block(
            "6.1 Proposed Review Procedure",
            "section",
            "ch6.1",
            1,
        )
    )
    story.extend(
        _bullets(
            [
                "Review open debt items and confirm whether the original impact and priority remain valid.",
                "Record newly introduced debt during implementation, testing or deployment.",
                "Identify debt that has been repaid and retain evidence of the resolution.",
                "Re-prioritise remaining items based on security, reliability, user impact and cost of delay.",
                "Ensure new feature work does not repeatedly defer critical security or data-protection debt.",
                "Update the roadmap, release notes and relevant project documentation.",
            ]
        )
    )
    story.extend(
        _section_block(
            "6.2 Definition of Debt Repaid",
            "section",
            "ch6.2",
            1,
            Paragraph(
                "A debt item is considered repaid only when the proposed resolution has been implemented and verified. For example, TD-05 is not closed merely because a backup script exists; it should remain open until a backup is created, stored independently and successfully restored in a controlled test.",
                S["body"],
            ),
        )
    )

    # ===== CHAPTER 7 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "7. Relationship to Testing and Acceptance",
            "chapter",
            "ch7",
            0,
            Paragraph(
                "The final ICCTECH testing cycle verifies whether the prioritised requirements behave as expected within the defined examination scope. Technical debt addresses a different dimension of software quality: whether the solution is sufficiently hardened, maintainable, observable, recoverable and scalable for future use. Therefore, a 100% pass rate for the selected functional test cases can coexist with open technical-debt items.",
                S["body"],
            ),
        )
    )
    story.append(
        Paragraph(
            "For example, a login function may pass all authentication tests while the deployment still requires HTTPS before long-term production use. Similarly, ticket persistence may pass service-restart testing even though an independent disaster-recovery backup process remains future work. The plan makes these distinctions explicit so that successful acceptance testing is not confused with complete elimination of engineering risk.",
            S["body"],
        )
    )
    story.append(KeepTogether([
        PageMarker("f7", 2),
        _center_drawing(fig_testing_vs_debt()),
        _caption_fig(7, "Functional testing versus technical-debt management"),
    ]))

    # ===== CHAPTER 8 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "8. Residual Risk and Project Limitations",
            "chapter",
            "ch8",
            0,
            Paragraph(
                "Until the critical and high-priority debt items are repaid, the current deployment should be regarded as suitable for examination demonstration and controlled evaluation rather than as a fully hardened enterprise production environment. The most important residual risks relate to transport security, secret management, database exposure, disaster recovery, operational monitoring and single-host availability.",
                S["body"],
            ),
        )
    )
    story.append(
        Paragraph(
            "The 48-hour project constraint also limits the amount of automated regression coverage and large-scale operational validation that can reasonably be completed. These limitations are intentionally documented rather than hidden, and they are connected to specific repayment actions in the roadmap.",
            S["body"],
        )
    )

    # ===== CHAPTER 9 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "9. Conclusion",
            "chapter",
            "ch9",
            0,
            Paragraph(
                "ICCTECH demonstrates deliberate technical-debt management by identifying significant compromises, explaining why they exist, evaluating their impact, assigning priorities and defining practical repayment actions. The highest-priority debt concerns production security hardening, followed by regression automation, backup/recovery and monitoring. Architecture resilience and internal naming consistency are longer-term evolution items.",
                S["body"],
            ),
        )
    )
    story.append(
        Paragraph(
            "This approach ensures that the timeboxed examination solution remains understandable and maintainable after deployment. Technical debt is therefore treated as a controlled engineering obligation that is visible, prioritised and scheduled rather than as hidden unfinished work.",
            S["body"],
        )
    )

    # ===== CHAPTER 10 =====
    story.append(PageBreak())
    story.extend(
        _section_block(
            "10. References and Acknowledgements",
            "chapter",
            "ch10",
            0,
        )
    )
    story.extend(
        _bullets(
            [
                "University of Ghana, Department of Computer Science. CSCD602 Advanced Software Engineering Individual Project-Based Examination, First Semester 2025/2026.",
                "ICCTECH source repository and submitted project source code, including Docker deployment configuration and test assets.",
                "ICCTECH live deployment: http://45.79.223.146:8080/index.php.",
                "Docker documentation — containerisation, Compose networking, secrets and persistent storage concepts.",
                "MySQL 8.0 documentation — database security, backup and recovery concepts.",
                "PHP documentation — application runtime and security guidance.",
                "Linode/Akamai cloud hosting documentation — server networking, firewalls, backups and monitoring concepts.",
                "Upstream/third-party components used by the project are acknowledged in the main Project Documentation and repository licensing/attribution materials.",
            ]
        )
    )

    return story


def _make_doc(path: str) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        path,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH Technical Debt Plan",
        author="Clement Asamoah (Student ID: 22424193)",
        subject="CSCD602 Advanced Software Engineering — Technical Debt Plan",
        creator="ICCTECH Technical Debt Plan generator",
        keywords="ICCTECH, technical debt, CSCD602, University of Ghana",
    )
    frame = Frame(
        LEFT_MARGIN,
        BOTTOM_MARGIN,
        CONTENT_W,
        CONTENT_H,
        id="normal",
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        showBoundary=0,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="title", frames=frame, onPage=_draw_title_header_footer),
            PageTemplate(id="body", frames=frame, onPage=_draw_header_footer),
        ]
    )
    return doc


def build(output_path: str) -> dict:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    collected = {}

    def after_flowable(flowable):
        bm = getattr(flowable, "bookmark", None)
        if not bm:
            return
        collected[bm] = doc.page
        if isinstance(flowable, BookmarkPara):
            try:
                text = flowable.getPlainText().strip()
                if text:
                    doc.canv.bookmarkPage(bm)
                    doc.canv.addOutlineEntry(
                        text[:80],
                        bm,
                        level=min(flowable.level, 2),
                        closed=False,
                    )
            except Exception:
                pass

    # Pass 1 — collect page numbers
    tmp = output_path + ".pass1.pdf"
    doc = _make_doc(tmp)
    doc.afterFlowable = after_flowable
    story = [NextPageTemplate("body")] + build_story({})
    doc.build(story, canvasmaker=TNRCanvas)

    pages = dict(collected)

    # Pass 2 — final with TOC page numbers
    collected.clear()
    doc = _make_doc(output_path)
    doc.afterFlowable = after_flowable
    story = [NextPageTemplate("body")] + build_story(pages)
    doc.build(story, canvasmaker=TNRCanvas)

    if os.path.exists(tmp):
        os.remove(tmp)
    return pages


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/workspace/docs/Technical_Debt_Plan.pdf"
    pages = build(out)
    print(f"Wrote {out}")
    print("Bookmark pages:", sorted(pages.items(), key=lambda kv: (kv[1], kv[0])))


if __name__ == "__main__":
    main()
