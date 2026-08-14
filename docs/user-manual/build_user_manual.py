#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH User Manual PDF.

Typography: Times New Roman (Liberation Serif), 12 pt justified body, 14 pt
bold chapter headings on new pages, 1.5 in left / 1.0 in other margins.
Tables rebuilt with wrapping cells. Process and architecture diagrams rendered
as PDF-native vectors.
"""

from __future__ import annotations

import math
import os
import sys

from reportlab.lib.colors import HexColor, white, black
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
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.platypus.flowables import Flowable

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

PAGE_W, PAGE_H = letter
LEFT_MARGIN = 1.5 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 1.0 * inch
BOTTOM_MARGIN = 1.0 * inch
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
CONTENT_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN

NAVY = HexColor("#1B365D")
NAVY_MID = HexColor("#2C4A7C")
STEEL = HexColor("#4A6FA5")
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
USER_FILL = HexColor("#E4F0E6")
ADMIN_FILL = HexColor("#E8E0D4")
WARN_FILL = HexColor("#F7E4E4")
OK_FILL = HexColor("#DCEBDD")


def _styles():
    s = {}
    s["body"] = ParagraphStyle(
        "Body", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=8, textColor=black, splitLongWords=True,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter", fontName="TimesNewRoman-Bold", fontSize=14, leading=18,
        alignment=TA_LEFT, spaceAfter=12, textColor=black, keepWithNext=True,
    )
    s["section"] = ParagraphStyle(
        "Section", fontName="TimesNewRoman-Bold", fontSize=12, leading=16,
        alignment=TA_LEFT, spaceBefore=12, spaceAfter=6, textColor=black, keepWithNext=True,
    )
    s["title_univ"] = ParagraphStyle(
        "TitleUniv", fontName="TimesNewRoman-Bold", fontSize=16, leading=20,
        alignment=TA_CENTER, textColor=NAVY, spaceAfter=4,
    )
    s["title_dept"] = ParagraphStyle(
        "TitleDept", fontName="TimesNewRoman-Bold", fontSize=12, leading=16,
        alignment=TA_CENTER, textColor=black, spaceAfter=2,
    )
    s["title_doc"] = ParagraphStyle(
        "TitleDoc", fontName="TimesNewRoman-Bold", fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=NAVY, spaceBefore=18, spaceAfter=8,
    )
    s["title_sub"] = ParagraphStyle(
        "TitleSub", fontName="TimesNewRoman-Bold", fontSize=12, leading=16,
        alignment=TA_CENTER, textColor=black, spaceAfter=16,
    )
    s["title_note"] = ParagraphStyle(
        "TitleNote", fontName="TimesNewRoman-Italic", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=HexColor("#444444"), spaceBefore=16,
    )
    s["front_h"] = ParagraphStyle(
        "FrontH", fontName="TimesNewRoman-Bold", fontSize=14, leading=18,
        alignment=TA_LEFT, spaceAfter=10, textColor=black, keepWithNext=True,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=10, textColor=black,
    )
    s["table_caption"] = ParagraphStyle(
        "TableCaption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_LEFT, spaceBefore=8, spaceAfter=4, textColor=black, keepWithNext=True,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="TimesNewRoman-Bold", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="TimesNewRoman", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb", fontName="TimesNewRoman-Bold", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=black,
    )
    s["label"] = ParagraphStyle(
        "Label", fontName="TimesNewRoman-Bold", fontSize=10, leading=12,
        alignment=TA_LEFT, textColor=black,
    )
    s["cell"] = ParagraphStyle(
        "Cell", fontName="TimesNewRoman", fontSize=10, leading=12,
        alignment=TA_LEFT, textColor=black,
    )
    s["meta_label"] = ParagraphStyle(
        "MetaLabel", fontName="TimesNewRoman-Bold", fontSize=11, leading=14,
        alignment=TA_LEFT, textColor=black,
    )
    s["meta_value"] = ParagraphStyle(
        "MetaValue", fontName="TimesNewRoman", fontSize=11, leading=14,
        alignment=TA_LEFT, textColor=black,
    )
    s["bullet"] = ParagraphStyle(
        "Bullet", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, leftIndent=18, bulletIndent=6,
        spaceBefore=1, spaceAfter=3, textColor=black,
    )
    s["step"] = ParagraphStyle(
        "Step", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, leftIndent=22, firstLineIndent=-18,
        spaceBefore=1, spaceAfter=4, textColor=black,
    )
    s["note"] = ParagraphStyle(
        "Note", fontName="TimesNewRoman-Italic", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, textColor=black,
    )
    s["example"] = ParagraphStyle(
        "Example", fontName="TimesNewRoman", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, textColor=black,
    )
    return s


S = _styles()


class BookmarkPara(Paragraph):
    def __init__(self, text, style, bookmark, level=0):
        Paragraph.__init__(self, text, style)
        self.bookmark = bookmark
        self.level = level


class PageMarker(Flowable):
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


def _draw_header_footer(canv, doc):
    canv.saveState()
    header_y = PAGE_H - 0.52 * inch
    footer_y = 0.45 * inch
    canv.setStrokeColor(NAVY)
    canv.setLineWidth(0.8)
    canv.line(LEFT_MARGIN, header_y - 4, PAGE_W - RIGHT_MARGIN, header_y - 4)
    canv.setFont("TimesNewRoman-Italic", 9)
    canv.setFillColor(HexColor("#333333"))
    canv.drawString(LEFT_MARGIN, header_y, "ICCTECH — User Manual")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, header_y, "CSCD602 | University of Ghana")
    canv.setStrokeColor(NAVY)
    canv.line(LEFT_MARGIN, footer_y + 12, PAGE_W - RIGHT_MARGIN, footer_y + 12)
    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, footer_y, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, footer_y, f"Page {doc.page}")
    canv.restoreState()


def _p(text, style="td"):
    return Paragraph(str(text), S[style])


def _table(data, col_widths, header=True, extra=None):
    cmds = [
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
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    if extra:
        cmds.extend(extra)
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle(cmds))
    t.hAlign = "LEFT"
    return t


def _note_block(title, text, style="note"):
    inner = Paragraph(f"<b>{title}.</b> {text}" if title else text, S[style])
    bar = Table([[inner]], colWidths=[CONTENT_W - 10])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NOTE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NOTE_BAR),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    bar.hAlign = "LEFT"
    return bar


def _warn_block(title, text):
    inner = Paragraph(f"<b>{title}.</b> {text}", S["note"])
    bar = Table([[inner]], colWidths=[CONTENT_W - 10])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WARN_FILL),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBEFORE", (0, 0), (0, -1), 3, CRIT_FG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    bar.hAlign = "LEFT"
    return bar


def _bullets(items):
    return [Paragraph("•  " + item, S["bullet"]) for item in items]


def _steps(items):
    out = []
    for i, item in enumerate(items, 1):
        out.append(Paragraph(f"<b>{i}.</b>  {item}", S["step"]))
    return out


def _caption_table(n, title):
    return Paragraph(f"<i>Table {n}. {title}</i>", S["table_caption"])


def _caption_fig(n, title):
    return Paragraph(f"<i>Figure {n}. {title}</i>", S["caption"])


def _center_drawing(drawing):
    wrap = Table([[drawing]], colWidths=[CONTENT_W])
    wrap.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    wrap.hAlign = "LEFT"
    return wrap


def _section_block(heading, style_key, bookmark, level, *flowables, min_space=110):
    head = BookmarkPara(heading, S[style_key], bookmark, level)
    if not flowables:
        return [CondPageBreak(min_space), head]
    keep = [head]
    rest = []
    for i, fl in enumerate(flowables):
        (keep if i < 3 else rest).append(fl)
    return [CondPageBreak(min_space), KeepTogether(keep), *rest]


def _toc_line(title, page, indent=0, bold=False):
    st = ParagraphStyle(
        "tocline",
        fontName="TimesNewRoman-Bold" if bold else "TimesNewRoman",
        fontSize=12 if bold else 11,
        leading=16 if bold else 14,
        textColor=black,
        leftIndent=indent,
    )
    pg = ParagraphStyle("tocpg", parent=st, alignment=TA_RIGHT, leftIndent=0)
    t = Table([[Paragraph(title, st), Paragraph(str(page) if page else "—", pg)]],
              colWidths=[CONTENT_W - 36, 36])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, 0), (0, 0), 0.3, HexColor("#C8C8C8")),
    ]))
    t.hAlign = "LEFT"
    return t


def _box(d, x, y, w, h, lines, fill, stroke, fs=8, text_color=black, lw=0.9):
    d.add(Rect(x, y, w, h, rx=3.5, ry=3.5, fillColor=fill, strokeColor=stroke, strokeWidth=lw))
    n = len(lines)
    line_h = fs + 2
    total = n * line_h
    start = y + (h + total) / 2.0 - line_h + 1
    for i, line in enumerate(lines):
        d.add(String(
            x + w / 2.0, start - i * line_h, line,
            fontName="TimesNewRoman", fontSize=fs, fillColor=text_color, textAnchor="middle",
        ))


def _arrow(d, x1, y1, x2, y2, color=NAVY, head=6):
    d.add(Line(x1, y1, x2, y2, strokeColor=color, strokeWidth=1.1))
    ang = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2, y2)
    p2 = (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4))
    p3 = (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4))
    d.add(Polygon([p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]], fillColor=color, strokeColor=color, strokeWidth=0.2))


# ---------------------------------------------------------------------------
# Vector diagrams
# ---------------------------------------------------------------------------
def fig_roles_portals():
    W, H = CONTENT_W, 210
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    _box(d, 140, 176, 152, 28, ["ICCTECH live application"], APP_FILL, NAVY, fs=8.5)
    _arrow(d, 140, 190, 86, 150, STEEL)
    _arrow(d, 292, 190, 346, 150, STEEL)
    _box(d, 12, 118, 148, 44, ["Self-service portal", "/self-service/login.php"], USER_FILL, MED_FG, fs=8)
    _box(d, 272, 118, 148, 44, ["Staff / analyst / admin", "/login"], ADMIN_FILL, HexColor("#6B5428"), fs=8)
    _arrow(d, 86, 118, 86, 88, MED_FG)
    _arrow(d, 346, 118, 216, 88, NAVY)
    _arrow(d, 346, 118, 346, 88, HexColor("#6B5428"))
    _box(d, 12, 40, 148, 46, ["End User", "Submit, track, reply,", "search knowledge"], USER_FILL, MED_FG, fs=7.5)
    _box(d, 160, 40, 116, 46, ["IT Support Analyst", "Triage, update,", "resolve tickets"], APP_FILL, NAVY, fs=7.5)
    _box(d, 288, 40, 132, 46, ["System Administrator", "Users, roles, config,", "least privilege"], ADMIN_FILL, HexColor("#6B5428"), fs=7.5)
    d.add(String(W / 2, 14, "Examiner uses supplied test/admin credentials to verify the deployed workflow.",
                 fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle"))
    return d


def fig_signin_paths():
    W, H = CONTENT_W, 168
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    _box(d, 12, 118, 200, 42, ["End-user sign-in", "self-service/login.php"], USER_FILL, MED_FG, fs=8)
    _box(d, 220, 118, 200, 42, ["Staff / analyst / administrator", "http://.../login"], ADMIN_FILL, HexColor("#6B5428"), fs=8)
    steps_l = ["Email or user identifier", "Password  (+ MFA if enabled)", "Self-service dashboard"]
    steps_r = ["Staff username", "Password  (+ MFA if enabled)", "Module landing page"]
    for i, (a, b) in enumerate(zip(steps_l, steps_r)):
        y = 78 - i * 32
        _box(d, 28, y, 168, 26, [a], BOX_FILL, BOX_STROKE, fs=7.5)
        _box(d, 236, y, 168, 26, [b], BOX_FILL, BOX_STROKE, fs=7.5)
        if i == 0:
            _arrow(d, 112, 118, 112, y + 26, MED_FG, head=5)
            _arrow(d, 320, 118, 320, y + 26, NAVY, head=5)
        else:
            _arrow(d, 112, y + 32, 112, y + 26, MED_FG, head=5)
            _arrow(d, 320, y + 32, 320, y + 26, NAVY, head=5)
    return d


def fig_enduser_ticket():
    W, H = CONTENT_W, 118
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    steps = [
        "Dashboard",
        "New Ticket",
        "Subject &\ndescription",
        "Priority &\nattachments",
        "Submit",
        "Track &\nreply",
    ]
    n = len(steps)
    gap = 8
    side = 8
    bw = (W - 2 * side - (n - 1) * gap) / n
    for i, lab in enumerate(steps):
        x = side + i * (bw + gap)
        _box(d, x, 38, bw, 52, lab.split("\n"), USER_FILL if i in (0, 5) else APP_FILL, NAVY, fs=7.5)
        if i < n - 1:
            _arrow(d, x + bw, 64, x + bw + gap - 1, 64, NAVY, head=5)
    d.add(String(W / 2, 16, "Optional first: search Knowledge / Help Centre before opening a new ticket.",
                 fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle"))
    return d


def fig_analyst_triage():
    W, H = CONTENT_W, 150
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    steps = [
        (12, ["Open ticket", "read subject,", "files"]),
        (98, ["Classify", "category /", "queue"]),
        (184, ["Prioritise", "urgency and", "impact"]),
        (270, ["Assign", "analyst or", "team"]),
        (356, ["Update status", "next stage", "of work"]),
    ]
    bw = 76
    for x, lines in steps:
        _box(d, x, 70, bw, 56, lines, APP_FILL, NAVY, fs=7.5)
    for i in range(4):
        x = steps[i][0] + bw
        _arrow(d, x, 98, steps[i + 1][0], 98, NAVY, head=5)
    _box(d, 12, 12, 408, 40, [
        "Triage confirms that the request has enough information, an appropriate classification,",
        "established urgency and clear ownership before investigation proceeds.",
    ], NOTE_BG, STEEL, fs=7.5)
    return d


def fig_status_lifecycle():
    W, H = CONTENT_W, 168
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    top = [
        (10, APP_FILL, NAVY, ["Open /", "Awaiting Triage"]),
        (118, APP_FILL, NAVY, ["Assigned", "ownership set"]),
        (226, APP_FILL, NAVY, ["In Progress", "active work"]),
        (334, HIGH_BG, HIGH_FG, ["On Hold /", "Awaiting Response"]),
    ]
    bw, bh = 96, 46
    for x, fill, stroke, lines in top:
        _box(d, x, 104, bw, bh, lines, fill, stroke, fs=7.5)
    for i in range(3):
        _arrow(d, top[i][0] + bw, 127, top[i + 1][0], 127, NAVY, head=5)
    # hold returns to in progress
    d.add(Line(382, 104, 382, 92, strokeColor=STEEL, strokeWidth=1.0))
    d.add(Line(382, 92, 274, 92, strokeColor=STEEL, strokeWidth=1.0))
    _arrow(d, 274, 92, 274, 104, STEEL, head=5)
    _box(d, 118, 18, bw, bh, ["Resolved", "solution recorded"], OK_FILL, MED_FG, fs=8)
    _box(d, 258, 18, bw, bh, ["Closed", "process complete"], NAVY, NAVY, fs=8, text_color=white)
    _arrow(d, 274, 104, 166, 64, MED_FG, head=5)
    _arrow(d, 214, 41, 258, 41, NAVY, head=5)
    d.add(String(48, 38, "Reopen if further", fontName="TimesNewRoman", fontSize=7, fillColor=CRIT_FG))
    d.add(String(48, 26, "work is required", fontName="TimesNewRoman", fontSize=7, fillColor=CRIT_FG))
    _arrow(d, 118, 36, 70, 36, CRIT_FG, head=4)
    _arrow(d, 70, 36, 70, 127, CRIT_FG, head=4)
    _arrow(d, 70, 127, 118, 127, CRIT_FG, head=5)
    return d


def fig_rbac():
    W, H = CONTENT_W, 150
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    _box(d, 136, 108, 160, 34, ["Principle of least privilege"], NAVY, NAVY, fs=8.5, text_color=white)
    _arrow(d, 216, 108, 86, 86, NAVY, head=5)
    _arrow(d, 216, 108, 216, 86, NAVY, head=5)
    _arrow(d, 216, 108, 346, 86, NAVY, head=5)
    _box(d, 12, 36, 124, 50, ["End User", "No analyst or", "admin functions"], USER_FILL, MED_FG, fs=8)
    _box(d, 154, 36, 124, 50, ["Analyst", "Tickets and supporting", "functions for the role"], APP_FILL, NAVY, fs=8)
    _box(d, 296, 36, 124, 50, ["Administrator", "Trusted accounts only;", "verify with a test login"], ADMIN_FILL, HexColor("#6B5428"), fs=8)
    d.add(String(W / 2, 14, "After changing roles or permissions, verify the result using a test account.",
                 fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle"))
    return d


def fig_e2e_workflow():
    W, H = CONTENT_W, 228
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    items = [
        (USER_FILL, MED_FG, "1  End User", "Sign in to self-service"),
        (USER_FILL, MED_FG, "2  End User", "Create a support ticket"),
        (APP_FILL, NAVY, "3  Analyst", "Open the new ticket"),
        (APP_FILL, NAVY, "4  Analyst", "Categorise, prioritise, assign"),
        (APP_FILL, NAVY, "5  Analyst", "Add an update"),
        (USER_FILL, MED_FG, "6  End User", "Reply through self-service"),
        (APP_FILL, NAVY, "7  Analyst", "Record resolution"),
        (APP_FILL, NAVY, "8  Analyst", "Close the ticket"),
        (ADMIN_FILL, HexColor("#6B5428"), "9  Administrator", "Verify role restriction"),
    ]
    gap = 8
    side = 10
    row_gap = 22
    bw = (W - 2 * side - 2 * gap) / 3.0
    bh = 48
    coords = []
    for i, (fill, stroke, t1, t2) in enumerate(items):
        r, c = divmod(i, 3)
        x = side + c * (bw + gap)
        y = 168 - r * (bh + row_gap)
        coords.append((x, y))
        _box(d, x, y, bw, bh, [t1, t2], fill, stroke, fs=8)
        if c < 2:
            _arrow(d, x + bw, y + bh / 2, x + bw + gap - 1, y + bh / 2, NAVY, head=5)
    for start, end in ((2, 3), (5, 6)):
        x1, y1 = coords[start]
        x2, y2 = coords[end]
        mid_y = y1 - row_gap / 2.0
        d.add(Line(x1 + bw / 2, y1, x1 + bw / 2, mid_y, strokeColor=STEEL, strokeWidth=1.1))
        d.add(Line(x1 + bw / 2, mid_y, x2 + bw / 2, mid_y, strokeColor=STEEL, strokeWidth=1.1))
        _arrow(d, x2 + bw / 2, mid_y, x2 + bw / 2, y2 + bh, STEEL, head=5)
    d.add(String(
        W / 2, 12, "Recommended quick demonstration of the examination scope.",
        fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle",
    ))
    return d


def fig_examiner_verification():
    W, H = CONTENT_W, 200
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    left = [
        "1. Confirm site reachable",
        "2. End-user self-service sign-in",
        "3. Create demonstration ticket",
        "4. Sign out; analyst/admin sign-in",
        "5. Locate ticket; set priority; assign",
    ]
    right = [
        "6. Add analyst response; update status",
        "7. End-user sees response/status",
        "8. Record resolution and close",
        "9. Open Knowledge and Assets",
        "10. Confirm restricted admin action",
    ]
    _box(d, 12, 8, 198, 184, ["Verification sequence"] + left, BOX_FILL, BOX_STROKE, fs=8)
    _box(d, 222, 8, 198, 184, ["(continued)"] + right, BOX_FILL, BOX_STROKE, fs=8)
    _arrow(d, 210, 100, 222, 100, NAVY, head=6)
    return d


def fig_asset_flow():
    W, H = CONTENT_W, 112
    d = Drawing(W, H)
    d.add(Rect(0, 0, W, H, fillColor=white, strokeColor=None))
    steps = ["Open Asset\nManagement", "Search /\nselect asset", "View record\n(tag, status,\nlocation)", "Update\nauthorised fields", "Assign to user\n(+ return date)"]
    n = len(steps)
    gap = 8
    side = 8
    bw = (W - 2 * side - (n - 1) * gap) / n
    for i, lab in enumerate(steps):
        x = side + i * (bw + gap)
        _box(d, x, 28, bw, 64, lab.split("\n"), ADMIN_FILL if i >= 3 else APP_FILL, NAVY, fs=7.5)
        if i < n - 1:
            _arrow(d, x + bw, 60, x + bw + gap - 1, 60, NAVY, head=5)
    d.add(String(W / 2, 12, "Only authorised staff should modify ownership, status or custody information.",
                 fontName="TimesNewRoman", fontSize=7.5, fillColor=HexColor("#333333"), textAnchor="middle"))
    return d


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def table_roles():
    headers = ["Role", "Primary responsibilities"]
    rows = [
        ("End User", "Submit support tickets, monitor progress, reply to analysts and search self-service knowledge resources."),
        ("IT Support Analyst", "Review, categorise, prioritise, assign, investigate, update and resolve support tickets."),
        ("System Administrator", "Manage users, analysts, roles, permissions and essential configuration; access administrative functions."),
        ("Examiner", "Use the supplied test/admin credentials to verify the deployed application and core workflow."),
    ]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    fills = [USER_FILL, APP_FILL, ADMIN_FILL, NOTE_BG]
    for i, (a, b) in enumerate(rows, 1):
        data.append([_p(f"<b>{a}</b>", "td"), _p(b, "td")])
        extra.append(("BACKGROUND", (0, i), (0, i), fills[i - 1]))
    return _table(data, [130, CONTENT_W - 130], extra=extra)


def table_access():
    headers = ["Purpose", "Address / Source"]
    rows = [
        ("Live application", "http://45.79.223.146:8080/index.php"),
        ("Staff / analyst / administrator sign-in", "http://45.79.223.146:8080/login"),
        ("End-user self-service sign-in", "http://45.79.223.146:8080/self-service/login.php"),
        ("Source repository", "https://github.com/Clemzy123/ICCTECH"),
        ("Credentials", "Use the accounts listed in Deployment_and_Source_Links.txt supplied with the examination package."),
    ]
    data = [[_p(h, "th") for h in headers]]
    for a, b in rows:
        data.append([_p(f"<b>{a}</b>", "td"), _p(b, "td")])
    return _table(data, [170, CONTENT_W - 170])


def table_priorities():
    headers = ["Priority", "Typical use"]
    rows = [
        ("High", "Significant business impact, urgent support need or time-sensitive interruption."),
        ("Normal", "Standard support issue requiring normal service-desk attention."),
        ("Low", "Minor impact, informational request or issue that can reasonably wait."),
    ]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    fills = [CRIT_BG, HIGH_BG, MED_BG]
    for i, (a, b) in enumerate(rows, 1):
        data.append([_p(f"<b>{a}</b>", "td"), _p(b, "td")])
        extra.append(("BACKGROUND", (0, i), (0, i), fills[i - 1]))
    return _table(data, [80, CONTENT_W - 80], extra=extra)


def table_status():
    headers = ["Typical status", "Meaning"]
    rows = [
        ("Open / Awaiting Triage", "Ticket has been received and requires review."),
        ("Assigned", "Ownership has been established."),
        ("In Progress", "An analyst is actively investigating or working on the request."),
        ("On Hold / Awaiting Response", "Further action depends on information, an external dependency or the requester."),
        ("Resolved", "A solution has been recorded and the issue is considered fixed."),
        ("Closed", "The support process is complete."),
    ]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    fills = [APP_FILL, APP_FILL, APP_FILL, HIGH_BG, OK_FILL, NAVY]
    for i, (a, b) in enumerate(rows, 1):
        if a == "Closed":
            closed = ParagraphStyle("cl", parent=S["td"], textColor=white, fontName="TimesNewRoman-Bold")
            data.append([Paragraph(a, closed), _p(b, "td")])
        else:
            data.append([_p(f"<b>{a}</b>", "td"), _p(b, "td")])
        extra.append(("BACKGROUND", (0, i), (0, i), fills[i - 1]))
    return _table(data, [150, CONTENT_W - 150], extra=extra)


def table_e2e():
    headers = ["Step", "Role", "Action", "Expected outcome"]
    rows = [
        ("1", "End User", "Sign in to self-service portal", "Dashboard is displayed."),
        ("2", "End User", "Create a support ticket", "Ticket is stored with a unique reference."),
        ("3", "Analyst", "Open the new ticket", "Request details are available for review."),
        ("4", "Analyst", "Categorise, prioritise and assign", "Ticket gains classification, urgency and ownership."),
        ("5", "Analyst", "Add an update / request information", "Communication is stored in ticket history."),
        ("6", "End User", "Reply through self-service", "Requester response appears on the ticket."),
        ("7", "Analyst", "Record resolution and set Resolved", "Resolution is retained and status changes."),
        ("8", "Analyst", "Close the ticket", "Ticket lifecycle is completed."),
        ("9", "Administrator", "Verify role-restricted function", "Unauthorised role is prevented from accessing restricted action."),
    ]
    data = [[_p(h, "th") for h in headers]]
    extra = []
    role_fill = {"End User": USER_FILL, "Analyst": APP_FILL, "Administrator": ADMIN_FILL}
    for i, r in enumerate(rows, 1):
        data.append([_p(f"<b>{r[0]}</b>", "td"), _p(r[1], "td"), _p(r[2], "td"), _p(r[3], "td")])
        extra.append(("BACKGROUND", (1, i), (1, i), role_fill[r[1]]))
        extra.append(("ALIGN", (0, i), (0, i), "CENTER"))
    return _table(data, [36, 78, 150, CONTENT_W - 264], extra=extra)


def table_troubleshooting():
    headers = ["Problem", "Recommended action"]
    rows = [
        ("Live page does not open", "Confirm the URL and internet connection. Retry after a short period. If the application remains unavailable, verify Linode/server and Docker service status."),
        ("Login rejected", "Check the username/email and password in Deployment_and_Source_Links.txt. Confirm the correct portal is being used. Do not repeatedly guess passwords."),
        ("MFA prompt appears", "Enter the current verification code for the configured account. If the examiner account was not intended to use MFA, use the supplied alternative test account."),
        ("A module is missing", "Module visibility is role-based. Confirm that the signed-in account has permission for that module."),
        ("Cannot perform an administrative action", "The account may not have the required capability. Verify the assigned role rather than attempting to bypass access controls."),
        ("Ticket update does not appear", "Refresh/reopen the ticket and confirm that the save/send operation succeeded. Check for an error message before retrying."),
        ("Database-related error", "Confirm MySQL service availability and application database connectivity. Production database access should remain restricted to authorised administrators."),
        ("Uploaded file fails", "Confirm that the file type/size is accepted by the application and that storage permissions are available."),
        ("Slow response", "Retry the page and confirm server/network conditions. Persistent performance problems should be recorded for maintenance investigation."),
    ]
    data = [[_p(h, "th") for h in headers]]
    for a, b in rows:
        data.append([_p(f"<b>{a}</b>", "td"), _p(b, "td")])
    return _table(data, [140, CONTENT_W - 140])


def table_reference():
    headers = ["Item", "Value"]
    rows = [
        ("Project", "ICCTECH: A Web-Based IT Service Management and Helpdesk System"),
        ("Student", "Clement Asamoah"),
        ("Student ID", "22424193"),
        ("Course", "CSCD602 — Advanced Software Engineering"),
        ("Live application", "http://45.79.223.146:8080/index.php"),
        ("Staff login", "http://45.79.223.146:8080/login"),
        ("Self-service login", "http://45.79.223.146:8080/self-service/login.php"),
        ("Repository", "https://github.com/Clemzy123/ICCTECH"),
        ("Credentials file", "Deployment_and_Source_Links.txt in the final submission package"),
    ]
    white_label = ParagraphStyle("WL", parent=S["label"], textColor=white, fontSize=9, leading=11)
    data = []
    for a, b in rows:
        data.append([Paragraph(a, white_label), _p(b, "cell")])
    t = Table(data, colWidths=[120, CONTENT_W - 120])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.45, HexColor("#6E7A88")),
        ("BACKGROUND", (0, 0), (0, -1), HEADER_BG),
        ("BACKGROUND", (1, 0), (1, -1), white),
    ]))
    t.hAlign = "LEFT"
    return t


def _meta_table():
    rows = [
        ("Student Name", "Clement Asamoah"),
        ("Student ID", "22424193"),
        ("Course", "CSCD602 — Advanced Software Engineering"),
        ("Academic Period", "First Semester, 2025/2026"),
        ("Examination Duration", "48 Hours"),
        ("Document Version", "1.0 — Final User Manual"),
        ("Live Application", "http://45.79.223.146:8080/index.php"),
        ("Source Repository", "https://github.com/Clemzy123/ICCTECH"),
    ]
    data = [[_p(a, "meta_label"), _p(b, "meta_value")] for a, b in rows]
    t = Table(data, colWidths=[150, CONTENT_W - 150])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#6E7A88")),
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#EEF2F7")),
        ("BACKGROUND", (1, 0), (1, -1), white),
    ]))
    t.hAlign = "LEFT"
    return t


TOC_ENTRIES = [
    ("ch1", 0, "1. About This Manual"),
    ("ch1.1", 1, "1.1 User Roles"),
    ("ch1.2", 1, "1.2 Access Information"),
    ("ch2", 0, "2. Getting Started"),
    ("ch2.1", 1, "2.1 Browser Requirements"),
    ("ch2.2", 1, "2.2 Staff / Analyst / Administrator Sign-In"),
    ("ch2.3", 1, "2.3 End-User Sign-In"),
    ("ch2.4", 1, "2.4 Signing Out"),
    ("ch3", 0, "3. End-User Self-Service Guide"),
    ("ch3.1", 1, "3.1 Self-Service Dashboard"),
    ("ch3.2", 1, "3.2 Create a New Support Ticket"),
    ("ch3.3", 1, "3.3 View and Track Tickets"),
    ("ch3.4", 1, "3.4 Reply to a Ticket"),
    ("ch3.5", 1, "3.5 Knowledge-Base Self-Service"),
    ("ch4", 0, "4. IT Support Analyst Guide"),
    ("ch4.1", 1, "4.1 Open the Tickets Module"),
    ("ch4.2", 1, "4.2 Review and Triage Incoming Tickets"),
    ("ch4.3", 1, "4.3 Ticket Priorities"),
    ("ch4.4", 1, "4.4 Add Notes and Communicate with the Requester"),
    ("ch4.5", 1, "4.5 Update Ticket Status"),
    ("ch4.6", 1, "4.6 Resolve and Close a Ticket"),
    ("ch4.7", 1, "4.7 Reopen a Ticket"),
    ("ch5", 0, "5. System Administrator Guide"),
    ("ch5.1", 1, "5.1 User and Analyst Management"),
    ("ch5.2", 1, "5.2 Role-Based Access Control"),
    ("ch5.3", 1, "5.3 Account Security"),
    ("ch6", 0, "6. Knowledge Base"),
    ("ch6.1", 1, "6.1 Search and Read Knowledge Articles"),
    ("ch6.2", 1, "6.2 Knowledge Management for Authorised Staff"),
    ("ch7", 0, "7. Asset Management"),
    ("ch7.1", 1, "7.1 View Assets"),
    ("ch7.2", 1, "7.2 Update an Asset"),
    ("ch7.3", 1, "7.3 Assign an Asset to a User"),
    ("ch8", 0, "8. Core End-to-End Workflow"),
    ("ch9", 0, "9. Troubleshooting"),
    ("ch9.1", 1, "9.1 Reporting a Problem During Evaluation"),
    ("ch10", 0, "10. Security and Responsible Use"),
    ("ch11", 0, "11. Examiner Quick Verification"),
    ("ch12", 0, "12. Reference Information"),
]

TABLE_LIST = [
    ("t1", "Table 1. User roles and primary responsibilities"),
    ("t2", "Table 2. Access information"),
    ("t3", "Table 3. Ticket priorities"),
    ("t4", "Table 4. Typical ticket status meanings"),
    ("t5", "Table 5. Core end-to-end examination workflow"),
    ("t6", "Table 6. Troubleshooting"),
    ("t7", "Table 7. Reference information"),
]

FIGURE_LIST = [
    ("f1", "Figure 1. ICCTECH user roles and access portals"),
    ("f2", "Figure 2. Staff and end-user sign-in paths"),
    ("f3", "Figure 3. End-user support-ticket process"),
    ("f4", "Figure 4. Analyst triage sequence"),
    ("f5", "Figure 5. Typical ticket status lifecycle"),
    ("f6", "Figure 6. Role-based access and least privilege"),
    ("f7", "Figure 7. Asset view, update and assignment flow"),
    ("f8", "Figure 8. Core end-to-end demonstration workflow"),
    ("f9", "Figure 9. Examiner quick-verification sequence"),
]


def build_story(pages: dict) -> list:
    story = []

    # Title
    story.append(Spacer(1, 0.45 * inch))
    story.append(Paragraph("UNIVERSITY OF GHANA", S["title_univ"]))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE", S["title_dept"]))
    story.append(Paragraph("CSCD602 — ADVANCED SOFTWARE ENGINEERING", S["title_dept"]))
    story.append(Paragraph("USER MANUAL", S["title_doc"]))
    story.append(Paragraph(
        "ICCTECH: A Web-Based IT Service Management and Helpdesk System", S["title_sub"],
    ))
    story.append(_meta_table())
    story.append(Paragraph(
        "Prepared for the Individual Software Engineering Capstone Examination", S["title_note"],
    ))

    # TOC
    story.append(PageBreak())
    story.append(Paragraph("Table of Contents", S["front_h"]))
    story.append(Spacer(1, 4))
    for key, level, title in TOC_ENTRIES:
        story.append(_toc_line(title, pages.get(key, ""), indent=18 if level else 0, bold=(level == 0)))
    story.append(Spacer(1, 12))
    story.append(Paragraph("List of Tables", S["section"]))
    for key, title in TABLE_LIST:
        story.append(_toc_line(title, pages.get(key, ""), indent=0, bold=False))
    story.append(Spacer(1, 8))
    story.append(Paragraph("List of Figures", S["section"]))
    for key, title in FIGURE_LIST:
        story.append(_toc_line(title, pages.get(key, ""), indent=0, bold=False))

    # Ch 1
    story.append(PageBreak())
    story.extend(_section_block(
        "1. About This Manual", "chapter", "ch1", 0,
        Paragraph(
            "This manual explains how to use the ICCTECH web-based IT Service Management and helpdesk system within the functionality defined for the CSCD602 examination project. It is intended for end users, IT support analysts, system administrators and the course examiner.",
            S["body"],
        ),
    ))
    story.append(_note_block(
        "Scope note",
        "The repository contains additional modules beyond the examination scope. This manual focuses on the core functions demonstrated for the project: authentication, ticket management, role-based access, knowledge-base use, asset management and essential administration.",
    ))
    story.extend(_section_block(
        "1.1 User Roles", "section", "ch1.1", 1,
        PageMarker("t1", 2),
        _caption_table(1, "User roles and primary responsibilities"),
        table_roles(),
        min_space=160,
    ))
    story.append(KeepTogether([
        PageMarker("f1", 2),
        _center_drawing(fig_roles_portals()),
        _caption_fig(1, "ICCTECH user roles and access portals"),
    ]))
    story.extend(_section_block(
        "1.2 Access Information", "section", "ch1.2", 1,
        PageMarker("t2", 2),
        _caption_table(2, "Access information"),
        table_access(),
        min_space=160,
    ))
    story.append(_warn_block(
        "Security note",
        "Do not place examiner passwords or production credentials in the public GitHub repository. The submission package contains the credentials separately in Deployment_and_Source_Links.txt.",
    ))

    # Ch 2
    story.append(PageBreak())
    story.extend(_section_block(
        "2. Getting Started", "chapter", "ch2", 0,
        BookmarkPara("2.1 Browser Requirements", S["section"], "ch2.1", 1),
        Paragraph(
            "Use a current desktop or mobile web browser with JavaScript and cookies enabled. The application is designed to remain usable on desktop and mobile-sized screens.",
            S["body"],
        ),
    ))
    story.append(KeepTogether([
        PageMarker("f2", 2),
        _center_drawing(fig_signin_paths()),
        _caption_fig(2, "Staff and end-user sign-in paths"),
    ]))
    story.extend(_section_block("2.2 Staff / Analyst / Administrator Sign-In", "section", "ch2.2", 1))
    story.extend(_steps([
        "Open http://45.79.223.146:8080/login in a web browser.",
        "Enter the staff username supplied for the account.",
        "Enter the password.",
        "Select Sign In.",
        "If multi-factor authentication is enabled for the account, enter the requested verification code.",
        "After successful authentication, the ICCTECH module landing page is displayed. The modules shown depend on the permissions assigned to the account.",
    ]))
    story.extend(_section_block("2.3 End-User Sign-In", "section", "ch2.3", 1))
    story.extend(_steps([
        "Open http://45.79.223.146:8080/self-service/login.php.",
        "Enter the email address or configured user identifier.",
        "Enter the password and select Sign In.",
        "If MFA is enabled, enter the six-digit verification code when prompted.",
        "The self-service dashboard opens after successful authentication.",
    ]))
    story.extend(_section_block(
        "2.4 Signing Out", "section", "ch2.4", 1,
        Paragraph(
            "Use the user/account menu and select the available sign-out/log-out option. Always sign out when using a shared computer.",
            S["body"],
        ),
    ))

    # Ch 3
    story.append(PageBreak())
    story.extend(_section_block(
        "3. End-User Self-Service Guide", "chapter", "ch3", 0,
        BookmarkPara("3.1 Self-Service Dashboard", S["section"], "ch3.1", 1),
        Paragraph(
            "The self-service dashboard gives the requester a summary of their support activity. Depending on configuration, it can display recent tickets, ticket status summaries, current service status, service requests and popular knowledge articles.",
            S["body"],
        ),
    ))
    story.extend(_bullets([
        "<b>New Ticket</b> — opens the support-ticket submission form.",
        "<b>Your Tickets / Recent Tickets</b> — shows tickets the user is authorised to view.",
        "<b>Status and Priority</b> — indicate the current state and urgency of each ticket.",
        "<b>Knowledge / Popular Articles</b> — provides access to self-service troubleshooting information.",
    ]))
    story.append(KeepTogether([
        PageMarker("f3", 2),
        _center_drawing(fig_enduser_ticket()),
        _caption_fig(3, "End-user support-ticket process"),
    ]))
    story.extend(_section_block("3.2 Create a New Support Ticket", "section", "ch3.2", 1))
    story.extend(_steps([
        "From the self-service dashboard, select New Ticket.",
        "Enter a clear Subject that summarises the issue.",
        "Describe the problem in the Description field. Include useful details such as what happened, when it started and any error message shown.",
        "Select the relevant support mailbox or queue when the option is presented.",
        "Choose an appropriate priority from the available list.",
        "Attach supporting files when useful. The interface also supports screen-recording functionality when the browser and configuration permit it.",
        "Review the information and select Submit.",
        "After successful submission, the system records the ticket and provides a ticket reference that can be used for tracking.",
    ]))
    story.append(_note_block(
        "Good ticket example",
        'Subject: Cannot connect to office Wi-Fi. Description: Laptop connects to the network but reports “No Internet” from 09:15. Restarted Wi-Fi and the laptop; issue continues.',
        style="example",
    ))
    story.extend(_section_block("3.3 View and Track Tickets", "section", "ch3.3", 1))
    story.extend(_steps([
        "Open the Tickets area from the self-service portal.",
        "Use the status filter if you need to display tickets in a particular state.",
        "Select a ticket to open its details.",
        "Review the ticket reference, subject, status, priority and communication history.",
        "Return to the ticket list to select another request.",
    ]))
    story.extend(_section_block("3.4 Reply to a Ticket", "section", "ch3.4", 1))
    story.extend(_steps([
        "Open the required ticket.",
        "Locate the reply area.",
        "Enter the information or response requested by the analyst.",
        "Add an attachment when supporting evidence is required.",
        "Select Send/Reply. The message becomes part of the ticket history.",
    ]))
    story.extend(_section_block(
        "3.5 Knowledge-Base Self-Service", "section", "ch3.5", 1,
        Paragraph(
            "Before opening a new ticket, users should check the available knowledge articles when appropriate. Reusable troubleshooting instructions may resolve common issues without analyst intervention.",
            S["body"],
        ),
    ))
    story.extend(_steps([
        "Open the Help Centre / Knowledge area.",
        "Search using keywords that describe the problem.",
        "Open the most relevant article.",
        "Follow the documented troubleshooting steps.",
        "If the issue remains unresolved, create a ticket and mention the troubleshooting already attempted.",
    ]))

    # Ch 4
    story.append(PageBreak())
    story.extend(_section_block(
        "4. IT Support Analyst Guide", "chapter", "ch4", 0,
        BookmarkPara("4.1 Open the Tickets Module", S["section"], "ch4.1", 1),
    ))
    story.extend(_steps([
        "Sign in using an analyst account.",
        "From the module landing page, select Tickets.",
        "The ticket workspace displays tickets available to the analyst according to assigned permissions.",
    ]))
    story.extend(_section_block(
        "4.2 Review and Triage Incoming Tickets", "section", "ch4.2", 1,
        Paragraph(
            "Triage determines how a new request should be handled. The analyst should confirm that the ticket contains enough information, choose an appropriate classification and establish urgency and ownership.",
            S["body"],
        ),
    ))
    story.append(KeepTogether([
        PageMarker("f4", 2),
        _center_drawing(fig_analyst_triage()),
        _caption_fig(4, "Analyst triage sequence"),
    ]))
    story.extend(_steps([
        "Open an incoming or untriaged ticket.",
        "Read the subject, description and any attachments.",
        "Confirm or select the appropriate category/queue.",
        "Set the ticket priority based on urgency and impact.",
        "Assign the ticket to the appropriate analyst or team.",
        "Update the ticket status to reflect the next stage of work.",
    ]))
    story.extend(_section_block(
        "4.3 Ticket Priorities", "section", "ch4.3", 1,
        PageMarker("t3", 2),
        _caption_table(3, "Ticket priorities"),
        table_priorities(),
        min_space=160,
    ))
    story.append(Paragraph(
        "Priority choices are configurable; analysts should follow the organisation’s service rules where these have been defined.",
        S["body"],
    ))
    story.extend(_section_block("4.4 Add Notes and Communicate with the Requester", "section", "ch4.4", 1))
    story.extend(_steps([
        "Open the ticket.",
        "Record investigation notes or the message that should be communicated.",
        "Use the appropriate note/reply control so that the communication is stored against the ticket.",
        "Include meaningful technical details, actions already completed and any next step required from the requester.",
        "Save/send the update and confirm that it appears in the ticket history.",
    ]))
    story.extend(_section_block(
        "4.5 Update Ticket Status", "section", "ch4.5", 1,
        Paragraph(
            "Update status whenever the state of work changes. The exact status names are configurable, but a typical workflow is shown below.",
            S["body"],
        ),
    ))
    story.append(KeepTogether([
        PageMarker("t4", 2),
        _caption_table(4, "Typical ticket status meanings"),
        table_status(),
    ]))
    story.append(KeepTogether([
        PageMarker("f5", 2),
        _center_drawing(fig_status_lifecycle()),
        _caption_fig(5, "Typical ticket status lifecycle"),
    ]))
    story.extend(_section_block("4.6 Resolve and Close a Ticket", "section", "ch4.6", 1))
    story.extend(_steps([
        "Confirm that the reported issue has been addressed.",
        "Record a clear resolution explaining what was done.",
        "Set the ticket status to Resolved.",
        "Where required, verify the outcome with the requester.",
        "Close the ticket once the support process is complete.",
    ]))
    story.extend(_section_block(
        "4.7 Reopen a Ticket", "section", "ch4.7", 1,
        Paragraph(
            "If a resolved or closed issue requires additional work and the account has the necessary permission, reopen or restore the ticket, record why further work is required, and continue the normal workflow.",
            S["body"],
        ),
    ))

    # Ch 5
    story.append(PageBreak())
    story.extend(_section_block(
        "5. System Administrator Guide", "chapter", "ch5", 0,
        Paragraph(
            "Administrator access is permission-controlled. The exact modules shown depend on the roles and capabilities assigned to the administrator account.",
            S["body"],
        ),
        BookmarkPara("5.1 User and Analyst Management", S["section"], "ch5.1", 1),
    ))
    story.extend(_steps([
        "Sign in using the administrator credentials supplied in the submission package.",
        "Open the relevant System / Administration area from the module landing page.",
        "Locate the user, analyst or access-management function.",
        "Create or update the required account details.",
        "Assign the appropriate role, team, module access or capabilities.",
        "Save the change.",
        "Verify the account with the intended role to confirm that access is neither excessive nor insufficient.",
    ]))
    story.extend(_section_block(
        "5.2 Role-Based Access Control", "section", "ch5.2", 1,
        Paragraph(
            "ICCTECH applies role and capability checks to control which modules and actions are available. Administrators should follow the principle of least privilege: grant only the permissions needed for the user’s responsibilities.",
            S["body"],
        ),
    ))
    story.append(KeepTogether([
        PageMarker("f6", 2),
        _center_drawing(fig_rbac()),
        _caption_fig(6, "Role-based access and least privilege"),
    ]))
    story.extend(_bullets([
        "End users should not receive analyst or administrative functions.",
        "Analysts should receive the ticket and supporting functions needed for their assigned role.",
        "Administrative capabilities should be limited to trusted accounts.",
        "After changing roles or permissions, verify the result using a test account before relying on it in production.",
    ]))
    story.extend(_section_block("5.3 Account Security", "section", "ch5.3", 1))
    story.extend(_bullets([
        "Use unique passwords for test and administrative accounts.",
        "Do not reuse database or server credentials as application passwords.",
        "Enable MFA where configured and appropriate.",
        "Remove or disable test accounts when they are no longer needed.",
        "Review access periodically and remove unnecessary privileges.",
    ]))

    # Ch 6
    story.append(PageBreak())
    story.extend(_section_block(
        "6. Knowledge Base", "chapter", "ch6", 0,
        Paragraph(
            "The Knowledge module provides reusable troubleshooting information. It is intended to reduce repeated support work and improve consistency when common problems occur.",
            S["body"],
        ),
        BookmarkPara("6.1 Search and Read Knowledge Articles", S["section"], "ch6.1", 1),
    ))
    story.extend(_steps([
        "Open the Knowledge module or Help Centre available to the account.",
        "Search using the problem, product or symptom as keywords.",
        "Select an article from the results.",
        "Read the article and follow any documented resolution steps.",
        "Return to the results or create a ticket if the article does not resolve the issue.",
    ]))
    story.extend(_section_block(
        "6.2 Knowledge Management for Authorised Staff", "section", "ch6.2", 1,
        Paragraph(
            "Authorised knowledge managers or administrators can maintain knowledge content according to their assigned capabilities. The wider codebase supports article management, review/versioning and tagging; only functions exposed to the configured examination accounts should be used during grading.",
            S["body"],
        ),
    ))

    # Ch 7
    story.append(PageBreak())
    story.extend(_section_block(
        "7. Asset Management", "chapter", "ch7", 0,
        Paragraph(
            "The Asset Management module stores information about IT equipment and supports linking assets to operational support activities.",
            S["body"],
        ),
        BookmarkPara("7.1 View Assets", S["section"], "ch7.1", 1),
    ))
    story.extend(_steps([
        "Sign in with an account that has access to Asset Management.",
        "Select Asset Management from the module landing page.",
        "Use the asset list/search controls to locate a device.",
        "Open the asset to view identifying and operational information such as hostname, asset tag, type, status, location, purchase information and assigned user when present.",
    ]))
    story.append(KeepTogether([
        PageMarker("f7", 2),
        _center_drawing(fig_asset_flow()),
        _caption_fig(7, "Asset view, update and assignment flow"),
    ]))
    story.extend(_section_block("7.2 Update an Asset", "section", "ch7.2", 1))
    story.extend(_steps([
        "Open the required asset record.",
        "Edit an authorised field such as asset tag, status, location or purchasing information.",
        "Save or leave the field as required by the interface so that the update is committed.",
        "Confirm that the updated value is displayed correctly.",
    ]))
    story.extend(_section_block("7.3 Assign an Asset to a User", "section", "ch7.3", 1))
    story.extend(_steps([
        "Open the asset record.",
        "Select the Assign function.",
        "Search for the user who will receive the asset.",
        "Select the user and, where required, specify an expected return date.",
        "Confirm the assignment.",
        "Verify that the assigned user is displayed on the asset record.",
    ]))
    story.append(_note_block(
        "Asset handling note",
        "Only authorised staff should modify asset ownership, status or custody information. Changes should reflect the physical state of the equipment.",
    ))

    # Ch 8
    story.append(PageBreak())
    story.extend(_section_block(
        "8. Core End-to-End Workflow", "chapter", "ch8", 0,
        Paragraph(
            "The following sequence is the recommended quick demonstration of the examination scope.",
            S["body"],
        ),
        PageMarker("t5", 2),
        min_space=140,
    ))
    story.append(_caption_table(5, "Core end-to-end examination workflow"))
    story.append(table_e2e())
    story.append(KeepTogether([
        PageMarker("f8", 2),
        _center_drawing(fig_e2e_workflow()),
        _caption_fig(8, "Core end-to-end demonstration workflow"),
    ]))

    # Ch 9
    story.append(PageBreak())
    story.extend(_section_block(
        "9. Troubleshooting", "chapter", "ch9", 0,
        PageMarker("t6", 2),
        _caption_table(6, "Troubleshooting"),
        table_troubleshooting(),
        min_space=180,
    ))
    story.extend(_section_block(
        "9.1 Reporting a Problem During Evaluation", "section", "ch9.1", 1,
        Paragraph(
            "If a problem occurs during grading, record the exact page, action performed, time, visible error message and account role. This information makes it easier to distinguish a user-access issue from an application, database or hosting issue.",
            S["body"],
        ),
    ))

    # Ch 10
    story.append(PageBreak())
    story.extend(_section_block("10. Security and Responsible Use", "chapter", "ch10", 0))
    story.extend(_bullets([
        "Use only the accounts and permissions provided for evaluation.",
        "Do not publish credentials from Deployment_and_Source_Links.txt.",
        "Use role-based access rather than sharing administrator accounts.",
        "Do not attempt to access database or server services unless this forms part of authorised administration.",
        "Sign out after testing, particularly on shared devices.",
        "Treat user, ticket and asset information as operational data and avoid entering unnecessary sensitive information into demonstration records.",
    ]))
    story.append(Spacer(1, 6))
    story.append(_warn_block(
        "Current deployment hardening",
        "The examination deployment is currently accessed over HTTP and the technical-debt plan identifies HTTPS, production secret management, database exposure, backups and monitoring as priority hardening work before long-term production use.",
    ))

    # Ch 11
    story.append(PageBreak())
    story.extend(_section_block(
        "11. Examiner Quick Verification", "chapter", "ch11", 0,
        Paragraph(
            "For a short verification of the implemented examination scope, the following workflow provides the fastest route through the principal functions.",
            S["body"],
        ),
    ))
    story.append(KeepTogether([
        PageMarker("f9", 2),
        _center_drawing(fig_examiner_verification()),
        _caption_fig(9, "Examiner quick-verification sequence"),
    ]))
    story.extend(_steps([
        "Open the live application URL and confirm that the site is reachable.",
        "Use the end-user credentials from Deployment_and_Source_Links.txt to sign in to the self-service portal.",
        "Create a demonstration ticket and record the ticket reference.",
        "Sign out and sign in using the analyst/admin account.",
        "Open the Tickets module, locate the demonstration ticket, set its priority and assign it.",
        "Add an analyst response and update the ticket status.",
        "Return to the end-user portal and verify that the response/status are visible.",
        "Return to the analyst account, record a resolution and close the ticket.",
        "Open Knowledge and Asset Management to verify the supporting modules within scope.",
        "Verify that an account without administrative permission cannot access a restricted administrative action.",
    ]))

    # Ch 12
    story.append(PageBreak())
    story.extend(_section_block(
        "12. Reference Information", "chapter", "ch12", 0,
        PageMarker("t7", 2),
        _caption_table(7, "Reference information"),
        table_reference(),
        min_space=160,
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "This manual documents the defined ICCTECH examination scope. Detailed requirements, testing results, technical debt and deployment information are provided in the accompanying SRS, Testing Report, Technical Debt Plan and Project Documentation.",
        S["body"],
    ))
    return story


def _make_doc(path: str) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        path,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH User Manual",
        author="Clement Asamoah (Student ID: 22424193)",
        subject="CSCD602 Advanced Software Engineering — User Manual",
        creator="ICCTECH User Manual generator",
        keywords="ICCTECH, user manual, CSCD602, University of Ghana",
    )
    frame = Frame(
        LEFT_MARGIN, BOTTOM_MARGIN, CONTENT_W, CONTENT_H, id="normal",
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="title", frames=frame, onPage=_draw_header_footer),
        PageTemplate(id="body", frames=frame, onPage=_draw_header_footer),
    ])
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
                    doc.canv.addOutlineEntry(text[:80], bm, level=min(flowable.level, 2), closed=False)
            except Exception:
                pass

    tmp = output_path + ".pass1.pdf"
    doc = _make_doc(tmp)
    doc.afterFlowable = after_flowable
    story = [NextPageTemplate("body")] + build_story({})
    doc.build(story, canvasmaker=TNRCanvas)
    pages = dict(collected)

    collected.clear()
    doc = _make_doc(output_path)
    doc.afterFlowable = after_flowable
    story = [NextPageTemplate("body")] + build_story(pages)
    doc.build(story, canvasmaker=TNRCanvas)
    if os.path.exists(tmp):
        os.remove(tmp)
    return pages


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/workspace/docs/User_Manual.pdf"
    pages = build(out)
    print(f"Wrote {out}")
    print("Bookmark pages:", sorted(pages.items(), key=lambda kv: (kv[1], kv[0])))


if __name__ == "__main__":
    main()
