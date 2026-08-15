#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH Project Documentation PDF.

Typography: Times New Roman (Liberation Serif), 12 pt justified body with
1.0 single spacing, 14 pt bold chapter headings on new pages, 1.0 in margins
on all sides (left binding allowance). Tables wrap cleanly. Architecture,
use-case, activity, ER and sequence diagrams are PDF-native vectors.
Black and white only. Target: 18 pages (same as the source document).
"""

from __future__ import annotations

import os
import sys

from reportlab.lib.colors import Color, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.rl_config as rl_config
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable, HRFlowable

FONT_DIR = "/usr/share/fonts/truetype/liberation"
_FONT_CACHE = os.path.join(os.path.dirname(__file__), ".fontcache")


def _times_face(src_name, family, subfamily, ps_name, out_name):
    """Copy Liberation Serif and label it Times New Roman for PDF embedding."""
    from fontTools.ttLib import TTFont as _TT

    os.makedirs(_FONT_CACHE, exist_ok=True)
    dest = os.path.join(_FONT_CACHE, out_name)
    src = os.path.join(FONT_DIR, src_name)
    font = _TT(src)
    full = family if subfamily == "Regular" else f"{family} {subfamily}"
    for rec in font["name"].names:
        if rec.nameID in (1, 16):
            rec.string = family
        elif rec.nameID == 2:
            rec.string = subfamily
        elif rec.nameID == 4:
            rec.string = full
        elif rec.nameID == 6:
            rec.string = ps_name
    font.save(dest)
    return dest


_REG = _times_face("LiberationSerif-Regular.ttf", "Times New Roman", "Regular", "TimesNewRoman", "TimesNewRoman.ttf")
_BLD = _times_face("LiberationSerif-Bold.ttf", "Times New Roman", "Bold", "TimesNewRoman-Bold", "TimesNewRoman-Bold.ttf")
_ITA = _times_face("LiberationSerif-Italic.ttf", "Times New Roman", "Italic", "TimesNewRoman-Italic", "TimesNewRoman-Italic.ttf")
_BI = _times_face("LiberationSerif-BoldItalic.ttf", "Times New Roman", "Bold Italic", "TimesNewRoman-BoldItalic", "TimesNewRoman-BoldItalic.ttf")
pdfmetrics.registerFont(TTFont("TimesNewRoman", _REG))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Bold", _BLD))
pdfmetrics.registerFont(TTFont("TimesNewRoman-Italic", _ITA))
pdfmetrics.registerFont(TTFont("TimesNewRoman-BoldItalic", _BI))
pdfmetrics.registerFontFamily(
    "TimesNewRoman",
    normal="TimesNewRoman",
    bold="TimesNewRoman-Bold",
    italic="TimesNewRoman-Italic",
    boldItalic="TimesNewRoman-BoldItalic",
)
rl_config.canvas_basefontname = "TimesNewRoman"

PAGE_W, PAGE_H = letter
LEFT_MARGIN = 1.0 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 1.0 * inch
BOTTOM_MARGIN = 1.0 * inch
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
CONTENT_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN

GRAY_HEADER = Color(0.18, 0.18, 0.18)
GRAY_ROW = Color(0.94, 0.94, 0.94)
GRAY_LINE = Color(0.25, 0.25, 0.25)
GRAY_FILL = Color(0.96, 0.96, 0.96)
GRAY_BOX = Color(0.90, 0.90, 0.90)


def _styles():
    s = {}
    s["body"] = ParagraphStyle(
        "Body", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=7, textColor=black, splitLongWords=True,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter", fontName="TimesNewRoman-Bold", fontSize=14, leading=17,
        alignment=TA_LEFT, spaceAfter=10, textColor=black, keepWithNext=True,
    )
    s["section"] = ParagraphStyle(
        "Section", fontName="TimesNewRoman-Bold", fontSize=12, leading=14,
        alignment=TA_LEFT, spaceBefore=8, spaceAfter=4, textColor=black, keepWithNext=True,
    )
    s["title_univ"] = ParagraphStyle(
        "TitleUniv", fontName="TimesNewRoman-Bold", fontSize=16, leading=20,
        alignment=TA_CENTER, textColor=black, spaceAfter=3,
    )
    s["title_dept"] = ParagraphStyle(
        "TitleDept", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
        alignment=TA_CENTER, textColor=black, spaceAfter=2,
    )
    s["title_course"] = ParagraphStyle(
        "TitleCourse", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
        alignment=TA_CENTER, textColor=black, spaceAfter=2,
    )
    s["title_exam"] = ParagraphStyle(
        "TitleExam", fontName="TimesNewRoman", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=black, spaceAfter=1,
    )
    s["title_proj"] = ParagraphStyle(
        "TitleProj", fontName="TimesNewRoman-Bold", fontSize=22, leading=26,
        alignment=TA_CENTER, textColor=black, spaceBefore=10, spaceAfter=4,
    )
    s["title_sub"] = ParagraphStyle(
        "TitleSub", fontName="TimesNewRoman-Bold", fontSize=13, leading=16,
        alignment=TA_CENTER, textColor=black, spaceAfter=14,
    )
    s["front_h"] = ParagraphStyle(
        "FrontH", fontName="TimesNewRoman-Bold", fontSize=14, leading=18,
        alignment=TA_CENTER, spaceAfter=8, textColor=black,
    )
    s["toc_h"] = ParagraphStyle(
        "TOCH", fontName="TimesNewRoman-Bold", fontSize=12, leading=14,
        alignment=TA_LEFT, spaceAfter=8, textColor=black, keepWithNext=True,
    )
    s["toc"] = ParagraphStyle(
        "TOC", fontName="TimesNewRoman", fontSize=12, leading=18,
        alignment=TA_LEFT, textColor=black,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=3, spaceAfter=6, textColor=black,
    )
    s["table_caption"] = ParagraphStyle(
        "TableCaption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=3, textColor=black, keepWithNext=True,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="TimesNewRoman-Bold", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=white,
    )
    s["th_c"] = ParagraphStyle(
        "THc", fontName="TimesNewRoman-Bold", fontSize=9, leading=11,
        alignment=TA_CENTER, textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="TimesNewRoman", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_c"] = ParagraphStyle(
        "TDc", fontName="TimesNewRoman", fontSize=9, leading=11,
        alignment=TA_CENTER, textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb", fontName="TimesNewRoman-Bold", fontSize=9, leading=11,
        alignment=TA_LEFT, textColor=black,
    )
    s["bullet"] = ParagraphStyle(
        "Bullet", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, leftIndent=16, bulletIndent=4,
        spaceBefore=0, spaceAfter=2, textColor=black,
    )
    s["note"] = ParagraphStyle(
        "Note", fontName="TimesNewRoman", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, textColor=black,
    )
    s["note_h"] = ParagraphStyle(
        "NoteH", fontName="TimesNewRoman-Bold", fontSize=10, leading=12,
        alignment=TA_LEFT, textColor=white,
    )
    s["companion"] = ParagraphStyle(
        "Companion", fontName="TimesNewRoman-Italic", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, spaceBefore=14, textColor=black,
    )
    s["code"] = ParagraphStyle(
        "Code", fontName="TimesNewRoman-Italic", fontSize=11, leading=13,
        alignment=TA_LEFT, leftIndent=12, spaceBefore=2, spaceAfter=6, textColor=black,
    )
    s["lead"] = ParagraphStyle(
        "Lead", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=7, textColor=black,
    )
    return s


S = _styles()


def P(text, style="body"):
    return Paragraph(text, S[style] if isinstance(style, str) else style)


def i(text):
    return f"<i>{text}</i>"


def b(text):
    return f"<b>{text}</b>"


class Bookmark(Flowable):
    def __init__(self, key, title, level=0):
        Flowable.__init__(self)
        self.key = key
        self.title = title
        self.level = level
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        self.canv.bookmarkPage(self.key)
        self.canv.addOutlineEntry(self.title, self.key, self.level, closed=0)


class NoteBox(Flowable):
    """Black-and-white callout with a solid header bar."""

    def __init__(self, title, body, width=CONTENT_W):
        Flowable.__init__(self)
        self.title = title
        self.body = body
        self.box_width = width
        self._header_h = 16
        self._pad = 7

    def wrap(self, aw, ah):
        self.box_width = min(self.box_width, aw)
        inner = self.box_width - 2 * self._pad
        self._bp = Paragraph(self.body, S["note"])
        bw, bh = self._bp.wrap(inner, ah)
        self.width = self.box_width
        self.height = self._header_h + bh + 2 * self._pad
        self._bh = bh
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.setStrokeColor(black)
        c.setLineWidth(0.7)
        c.setFillColor(GRAY_HEADER)
        c.rect(0, self.height - self._header_h, self.width, self._header_h, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("TimesNewRoman-Bold", 10)
        c.drawString(self._pad, self.height - self._header_h + 4, self.title)
        c.setFillColor(GRAY_FILL)
        c.rect(0, 0, self.width, self.height - self._header_h, fill=1, stroke=1)
        self._bp.drawOn(c, self._pad, self._pad)


def make_table(headers, rows, col_widths, numeric=None, header_center=None):
    numeric = set(numeric or [])
    header_center = set(header_center or numeric)
    head = []
    for i, h in enumerate(headers):
        head.append(Paragraph(h, S["th_c"] if i in header_center else S["th"]))
    data = [head]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            style = S["td_c"] if i in numeric else S["td"]
            cells.append(Paragraph(str(cell), style))
        data.append(cells)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "TimesNewRoman-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0, r), (-1, r), GRAY_ROW))
    tbl.setStyle(TableStyle(commands))
    return tbl


def bullets(items):
    return [
        Paragraph(f"•  {item}", S["bullet"]) for item in items
    ]


# ---------------------------------------------------------------------------
# Vector diagrams
# ---------------------------------------------------------------------------

def _round_box(c, x, y, w, h, text_lines, font="TimesNewRoman", size=8, radius=4, fill=GRAY_FILL):
    c.setFillColor(fill)
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.setFillColor(black)
    n = len(text_lines)
    line_h = size + 2
    start = y + h / 2 + (n - 1) * line_h / 2 - 2
    for i, line in enumerate(text_lines):
        name, sz, txt = (font, size, line) if not isinstance(line, tuple) else line
        c.setFont(name, sz)
        c.drawCentredString(x + w / 2, start - i * line_h, txt)


def _arrow(c, x1, y1, x2, y2, label=None, label_side=6):
    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setLineWidth(0.9)
    c.line(x1, y1, x2, y2)
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    ah = 6
    a1 = ang + 2.6
    a2 = ang - 2.6
    c.line(x2, y2, x2 + ah * math.cos(a1), y2 + ah * math.sin(a1))
    c.line(x2, y2, x2 + ah * math.cos(a2), y2 + ah * math.sin(a2))
    if label:
        c.setFont("TimesNewRoman-Italic", 7)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        c.drawCentredString(mx + label_side, my + 3, label)


def _cylinder(c, x, y, w, h, lines):
    eh = 8
    c.setStrokeColor(black)
    c.setFillColor(GRAY_FILL)
    c.setLineWidth(0.8)
    path = c.beginPath()
    path.moveTo(x, y + eh)
    path.lineTo(x, y + h - eh)
    path.curveTo(x, y + h, x + w, y + h, x + w, y + h - eh)
    path.lineTo(x + w, y + eh)
    path.curveTo(x + w, y, x, y, x, y + eh)
    c.drawPath(path, fill=1, stroke=1)
    c.setFillColor(Color(0.88, 0.88, 0.88))
    c.ellipse(x, y + h - 2 * eh, x + w, y + h, fill=1, stroke=1)
    c.setFillColor(black)
    c.setFont("TimesNewRoman-Bold", 8)
    c.drawCentredString(x + w / 2, y + h / 2 + 2, lines[0])
    if len(lines) > 1:
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(x + w / 2, y + h / 2 - 10, lines[1])


class ArchitectureDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=430, caption_mode=False):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w = self.width
        cx = w / 2
        bw = 250
        x = cx - bw / 2
        y = self.height
        gap = 14
        h1, h2, h3, h4, happ, hdb = 22, 20, 28, 22, 40, 30

        y -= h1
        _round_box(c, x, y, bw, h1, [("TimesNewRoman-Bold", 8, "End User / Support Analyst / Administrator")], size=8)
        _arrow(c, cx, y, cx, y - gap + 1)
        y -= gap + h2
        _round_box(c, x + 40, y, bw - 80, h2, ["Web Browser"], size=8)
        _arrow(c, cx, y, cx, y - gap + 1)
        y -= gap + h3
        _round_box(c, x, y, bw, h3, [
            ("TimesNewRoman-Bold", 8, "Linode Linux Cloud Server"),
            ("TimesNewRoman", 8, "HTTP : 8080"),
        ], size=8)
        _arrow(c, cx, y, cx, y - gap + 1)
        y -= gap + h4
        _round_box(c, x, y, bw, h4, [("TimesNewRoman-Bold", 8, "Docker Compose Environment")], size=8)
        _arrow(c, cx, y, cx, y - gap + 1)
        y -= gap + happ
        _round_box(c, x, y, bw, happ, [
            ("TimesNewRoman-Bold", 8, "Application Container"),
            ("TimesNewRoman", 8, "Apache + PHP 8.4"),
            ("TimesNewRoman", 8, "ICCTECH Web Application"),
        ], size=8)

        app_bottom = y
        db_w, db_h = 150, hdb
        db_x = cx - 155
        vol_y = 8
        vol_h = 36
        db_y = vol_y + vol_h + 28
        _arrow(c, cx - 50, app_bottom, db_x + db_w / 2, db_y + db_h, "PDO / MySQL", label_side=-42)
        _arrow(c, cx + 50, app_bottom, cx + 90, vol_y + vol_h + 6, "attachments / key", label_side=36)
        _round_box(c, db_x, db_y, db_w, db_h, [
            ("TimesNewRoman-Bold", 8, "Database Container"),
            ("TimesNewRoman", 8, "MySQL 8.0"),
        ], size=8)
        _arrow(c, db_x + db_w / 2, db_y, cx - 40, vol_y + vol_h)
        _cylinder(c, cx - 175, vol_y, 350, vol_h, [
            "Persistent Docker Volumes",
            "Database  |  Ticket Attachments  |  Change Attachments  |  Encryption Keys",
        ])


class UseCaseDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=455):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def _actor(self, c, x, y, label):
        c.setStrokeColor(black)
        c.setFillColor(white)
        c.setLineWidth(0.9)
        c.circle(x, y + 22, 5, fill=0, stroke=1)
        c.line(x, y + 17, x, y + 6)
        c.line(x - 7, y + 13, x + 7, y + 13)
        c.line(x, y + 6, x - 6, y - 2)
        c.line(x, y + 6, x + 6, y - 2)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(x, y - 12, label)

    def _oval(self, c, x, y, w, h, text):
        c.setFillColor(GRAY_FILL)
        c.setStrokeColor(black)
        c.setLineWidth(0.7)
        c.ellipse(x, y, x + w, y + h, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(x + w / 2, y + h / 2 - 2.5, text)
        return x + w / 2, y + h / 2

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        box_x, box_y = 118, 8
        box_w, box_h = w - 126, h - 22
        c.setStrokeColor(black)
        c.setLineWidth(1.0)
        c.setFillColor(white)
        c.rect(box_x, box_y, box_w, box_h, fill=0, stroke=1)
        c.setFont("TimesNewRoman-Bold", 9)
        c.setFillColor(black)
        c.drawCentredString(box_x + box_w / 2, h - 14, "ICCTECH")

        cases = [
            "View Ticket Progress",
            "Create Support Ticket",
            "Search Knowledge Base",
            "Communicate on Ticket",
            "Update Status / Notes",
            "Categorise & Prioritise Ticket",
            "Assign Ticket",
            "Resolve / Close Ticket",
            "Authenticate",
            "View / Manage Asset Records",
            "Manage Service Settings",
            "View Audit / Operational Information",
            "Manage Users, Roles & Permissions",
        ]
        oval_w, oval_h = 200, 22
        ox = box_x + (box_w - oval_w) / 2
        top = box_y + box_h - 28
        centres = []
        for i, name in enumerate(cases):
            cy = top - i * (oval_h + 6)
            centres.append(self._oval(c, ox, cy, oval_w, oval_h, name))

        actors = [
            (48, h - 95, "End User", [0, 1, 2, 3, 8]),
            (48, h / 2 - 10, "Support Analyst", [0, 2, 3, 4, 5, 6, 7, 8]),
            (48, 70, "Administrator", [8, 9, 10, 11, 12]),
        ]
        for ax, ay, label, links in actors:
            self._actor(c, ax, ay, label)
            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            for idx in links:
                _cx, cy = centres[idx]
                # Stay in the left gutter so association lines never cut ovals.
                c.line(ax + 10, ay + 10, box_x, cy)
                c.line(box_x, cy, ox, cy)


class ActivityDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=470):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def _box(self, c, x, y, w, h, text):
        _round_box(c, x, y, w, h, text if isinstance(text, list) else [text], size=8, radius=8)

    def _diamond(self, c, cx, cy, w, h, text):
        path = c.beginPath()
        path.moveTo(cx, cy + h / 2)
        path.lineTo(cx + w / 2, cy)
        path.lineTo(cx, cy - h / 2)
        path.lineTo(cx - w / 2, cy)
        path.close()
        c.setFillColor(GRAY_FILL)
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.drawPath(path, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        for i, line in enumerate(text):
            c.drawCentredString(cx, cy + 4 - i * 9, line)

    def draw(self):
        import math
        c = self.canv
        w = self.width
        cx = w / 2
        bw = 230
        x = cx - bw / 2
        y = self.height - 6

        def down_arrow(y1, y2):
            _arrow(c, cx, y1, cx, y2)

        # start
        c.setFillColor(black)
        c.circle(cx, y, 4, fill=1, stroke=0)
        _arrow(c, cx, y - 4, cx, y - 12)
        y -= 34
        steps = [
            (22, ["End user submits ticket"]),
            (22, ["System creates unique ticket record"]),
            (22, ["Analyst triages, categorises and prioritises"]),
            (22, ["Ticket assigned to analyst / team"]),
            (22, ["In Progress"]),
        ]
        for h, txt in steps:
            self._box(c, x, y - h, bw, h, txt)
            down_arrow(y - h, y - h - 10)
            y = y - h - 12

        # decision 1
        dh = 44
        self._diamond(c, cx, y - dh / 2, 200, dh, ["Need user response", "or temporary hold?"])
        dec1 = y - dh / 2
        # No left
        c.setFont("TimesNewRoman-Bold", 7)
        c.drawString(x - 28, dec1 + 2, "No")
        _arrow(c, cx - 100, dec1, 70, dec1)
        inv_w, inv_h = 130, 28
        self._box(c, 18, dec1 - inv_h / 2, inv_w, inv_h, ["Investigate, add notes", "and communicate"])
        # Yes right
        c.drawString(cx + 104, dec1 + 2, "Yes")
        _arrow(c, cx + 100, dec1, w - 18 - 120, dec1)
        hold_w, hold_h = 120, 28
        self._box(c, w - 18 - hold_w, dec1 - hold_h / 2, hold_w, hold_h, ["On Hold /", "Awaiting Response"])
        # Resume back to In Progress (the 5th box)
        inprog_y = self.height - 6 - 4 - 12 - (22 + 12) * 4 - 22
        c.setStrokeColor(black)
        c.setDash(2, 2)
        c.line(w - 18 - hold_w / 2, dec1 + hold_h / 2, w - 18 - hold_w / 2, inprog_y + 11)
        c.setDash()
        _arrow(c, w - 18 - hold_w / 2, inprog_y + 11, x + bw, inprog_y + 11)
        c.setFont("TimesNewRoman-Italic", 7)
        c.drawString(w - 70, inprog_y + 14, "Resume")

        y = dec1 - dh / 2 - 12
        # from investigate down to resolution
        _arrow(c, 18 + inv_w / 2, dec1 - inv_h / 2, 18 + inv_w / 2, y - 8)
        c.line(18 + inv_w / 2, y - 8, cx, y - 8)
        _arrow(c, cx, y - 8, cx, y - 16)
        y -= 38
        self._box(c, x, y - 22, bw, 22, ["Resolution recorded"])
        down_arrow(y - 22, y - 32)
        y -= 54
        self._box(c, x, y - 22, bw, 22, ["Closed"])
        down_arrow(y - 22, y - 32)
        y -= 56
        self._diamond(c, cx, y - 22, 190, 44, ["Further work required?"])
        # Yes loops up right side to In Progress
        c.setFont("TimesNewRoman-Bold", 7)
        c.drawString(cx + 98, y - 20, "Yes")
        c.setStrokeColor(black)
        c.line(cx + 95, y - 22, w - 8, y - 22)
        c.line(w - 8, y - 22, w - 8, inprog_y + 22)
        _arrow(c, w - 8, inprog_y + 22, x + bw, inprog_y + 11)
        # No down to end
        c.drawCentredString(cx - 14, y - 48, "No")
        _arrow(c, cx, y - 44, cx, 16)
        c.setFillColor(white)
        c.setStrokeColor(black)
        c.setLineWidth(1.1)
        c.circle(cx, 10, 6, fill=1, stroke=1)
        c.setFillColor(black)
        c.circle(cx, 10, 3.2, fill=1, stroke=0)


class ERDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=455):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def _entity(self, c, x, y, w, h, title, attrs):
        hh = 13
        c.setFillColor(GRAY_HEADER)
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        c.rect(x, y + h - hh, w, hh, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("TimesNewRoman-Bold", 7)
        c.drawCentredString(x + w / 2, y + h - hh + 3, title)
        c.setFillColor(GRAY_FILL)
        c.rect(x, y, w, h - hh, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 6.5)
        for i, a in enumerate(attrs):
            c.drawString(x + 4, y + h - hh - 11 - i * 9, a)
        return (x + w / 2, y + h / 2, x, y, w, h)

    def _edge(self, ent, side):
        _cx, _cy, x, y, w, h = ent
        if side == "bottom":
            return (x + w / 2.0, y)
        if side == "top":
            return (x + w / 2.0, y + h)
        if side == "left":
            return (x, y + h / 2.0)
        if side == "right":
            return (x + w, y + h / 2.0)
        return (x + w / 2.0, y + h / 2.0)

    def _ortho(self, c, a, a_side, b, b_side, label=None, label_dx=0, label_dy=4):
        x1, y1 = self._edge(a, a_side)
        x2, y2 = self._edge(b, b_side)
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        if a_side in ("bottom", "top") and b_side in ("bottom", "top"):
            midy = (y1 + y2) / 2.0
            c.line(x1, y1, x1, midy)
            c.line(x1, midy, x2, midy)
            c.line(x2, midy, x2, y2)
            lx, ly = (x1 + x2) / 2.0, midy
        elif a_side in ("left", "right") and b_side in ("left", "right"):
            midx = (x1 + x2) / 2.0
            c.line(x1, y1, midx, y1)
            c.line(midx, y1, midx, y2)
            c.line(midx, y2, x2, y2)
            lx, ly = midx, (y1 + y2) / 2.0
        else:
            c.line(x1, y1, x1, y2)
            c.line(x1, y2, x2, y2)
            lx, ly = (x1 + x2) / 2.0, y2
        if label:
            c.setFont("TimesNewRoman-Italic", 6)
            c.setFillColor(black)
            c.drawCentredString(lx + label_dx, ly + label_dy, label)

    def draw(self):
        c = self.canv
        W, H = self.width, self.height
        ew, eh = 108, 50
        gap_x = 10
        # row 1
        r1y = H - 58
        xs = [4, 4 + ew + gap_x, 4 + 2 * (ew + gap_x), 4 + 3 * (ew + gap_x)]
        d = self._entity(c, xs[0], r1y, ew, eh, "departments", ["id PK", "name"])
        ts = self._entity(c, xs[1], r1y, ew, eh, "ticket_statuses", ["id PK", "name", "is_closed"])
        tp = self._entity(c, xs[2], r1y, ew, eh, "ticket_priorities", ["id PK", "name", "SLA targets"])
        us = self._entity(c, xs[3], r1y, ew, 58, "users", ["id PK", "email / username", "display_name"])

        # tickets + analysts
        tw, th = 168, 88
        tx = (W - tw) / 2 - 40
        ty = r1y - 118
        tk = self._entity(c, tx, ty, tw, th, "tickets", [
            "id PK    ticket_number",
            "user_id FK",
            "assigned_analyst_id FK",
            "status_id FK",
            "priority_id FK",
            "department_id FK",
        ])
        an = self._entity(c, tx + tw + 16, ty + 18, ew, 64, "analysts", [
            "id PK", "username", "is_admin", "totp_enabled",
        ])

        self._ortho(c, d, "bottom", tk, "top", "department", label_dx=-18, label_dy=2)
        self._ortho(c, ts, "bottom", tk, "top", "status", label_dx=-8, label_dy=2)
        self._ortho(c, tp, "bottom", tk, "top", "priority", label_dx=10, label_dy=2)
        self._ortho(c, us, "bottom", tk, "top", "requester", label_dx=28, label_dy=2)
        self._ortho(c, an, "left", tk, "right", "assigned analyst", label_dy=6)

        # row 3
        r3y = ty - 92
        ta = self._entity(c, 4, r3y, ew, 50, "ticket_audit", ["id PK", "ticket_id FK", "analyst_id FK"])
        tn = self._entity(c, 4 + ew + gap_x, r3y, ew, 50, "ticket_notes", ["id PK", "ticket_id FK", "analyst_id FK"])
        kn = self._entity(c, 4 + 2 * (ew + gap_x), r3y, ew, 58, "knowledge_articles", [
            "id PK", "title", "author_id FK", "is_published",
        ])
        ast = self._entity(c, 4 + 3 * (ew + gap_x), r3y, ew, 50, "assets", [
            "id PK", "hostname", "model / service_tag",
        ])
        self._ortho(c, tk, "bottom", ta, "top", "1 : many", label_dx=-10)
        self._ortho(c, tk, "bottom", tn, "top", "1 : many", label_dx=8)
        self._ortho(c, an, "bottom", kn, "top", "authors")

        # row 4
        r4y = 8
        rb = self._entity(c, 4 + 2 * (ew + gap_x), r4y, ew, 50, "RBAC", [
            "rbac_roles", "rbac_role_capabilities", "rbac_analyst_roles",
        ])
        ua = self._entity(c, 4 + 3 * (ew + gap_x), r4y, ew, 50, "users_assets", [
            "id PK", "user_id FK", "asset_id FK",
        ])
        self._ortho(c, an, "bottom", rb, "top", "assigned roles")
        self._ortho(c, ast, "bottom", ua, "top", "1 : many")
        # Route users → users_assets along the right margin so the line
        # does not pass through the assets entity.
        x1, y1 = self._edge(us, "right")
        x2, y2 = self._edge(ua, "right")
        x_edge = W - 3
        c.setStrokeColor(black)
        c.setLineWidth(0.6)
        c.line(x1, y1, x_edge, y1)
        c.line(x_edge, y1, x_edge, y2)
        c.line(x_edge, y2, x2, y2)
        c.setFont("TimesNewRoman-Italic", 6)
        c.setFillColor(black)
        c.drawCentredString(x_edge - 16, (y1 + y2) / 2.0, "1 : many")


class SequenceDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=470):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        actors = [
            "End User",
            "Web Browser",
            "Support Analyst",
            "ICCTECH\nPHP App",
            "Authentication\n/ RBAC",
            "MySQL",
        ]
        n = len(actors)
        left, right = 28, self.width - 8
        span = right - left
        xs = [left + span * (i + 0.5) / n for i in range(n)]
        head_y = self.height - 28
        foot_y = 10

        for i, (x, name) in enumerate(zip(xs, actors)):
            lines = name.split("\n")
            bw, bh = 76, 12 + 10 * len(lines)
            c.setFillColor(GRAY_FILL)
            c.setStrokeColor(black)
            c.setLineWidth(0.7)
            c.rect(x - bw / 2, head_y, bw, bh, fill=1, stroke=1)
            c.setFillColor(black)
            c.setFont("TimesNewRoman-Bold", 6.5)
            for j, line in enumerate(lines):
                c.drawCentredString(x, head_y + bh - 12 - j * 9, line)
            c.setDash(1.5, 1.5)
            c.setStrokeColor(GRAY_LINE)
            c.setLineWidth(0.6)
            c.line(x, head_y, x, foot_y)
            c.setDash()

        messages = [
            (0, 1, "1. Submit ticket form", False),
            (1, 3, "2. HTTP request (create ticket)", False),
            (3, 4, "3. Validate session / access", False),
            (4, 3, "4. Authorised", True),
            (3, 5, "5. INSERT ticket", False),
            (5, 3, "6. Ticket ID / reference", True),
            (3, 1, "7. Confirmation", True),
            (2, 1, "8. Open queue / ticket", False),
            (3, 5, "9. SELECT ticket", False),
            (5, 3, "10. Ticket data", True),
            (2, 1, "11. Assign / update / resolve", False),
            (3, 3, "12. Check capability", False),
            (3, 5, "13. UPDATE ticket + audit / note", False),
            (5, 3, "14. Persisted", True),
        ]
        top = head_y - 8
        step = (top - foot_y - 8) / (len(messages) + 0.4)
        c.setFont("TimesNewRoman", 6.5)
        for i, (src, dst, label, dashed) in enumerate(messages):
            y = top - i * step
            x1, x2 = xs[src], xs[dst]
            c.setStrokeColor(black)
            c.setFillColor(black)
            c.setLineWidth(0.7)
            if src == dst:
                c.setDash()
                c.line(x1, y, x1 + 28, y)
                c.line(x1 + 28, y, x1 + 28, y - 8)
                c.line(x1 + 28, y - 8, x1, y - 8)
                c.line(x1, y - 8, x1 + 5, y - 5)
                c.line(x1, y - 8, x1 + 5, y - 11)
                c.setFont("TimesNewRoman", 6.5)
                c.drawString(x1 + 32, y - 4, label)
                continue
            if dashed:
                c.setDash(2, 1.5)
            else:
                c.setDash()
            c.line(x1, y, x2, y)
            c.setDash()
            direction = 1 if x2 > x1 else -1
            c.line(x2, y, x2 - 6 * direction, y + 2.5)
            c.line(x2, y, x2 - 6 * direction, y - 2.5)
            c.setFont("TimesNewRoman", 6.5)
            mx = (x1 + x2) / 2
            c.drawCentredString(mx, y + 3, label)


# ---------------------------------------------------------------------------
# Page furniture
# ---------------------------------------------------------------------------

def draw_header_footer(canv, doc):
    canv.saveState()
    if doc.page == 1:
        canv.restoreState()
        return
    canv.setFillColor(black)
    canv.setStrokeColor(black)
    canv.setFont("TimesNewRoman-Italic", 8)
    left = "ICCTECH: A Web-Based IT Service Management and Helpdesk System"
    right = "Student ID: 22424193"
    canv.drawString(LEFT_MARGIN, PAGE_H - 0.62 * inch, left)
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 0.62 * inch, right)
    canv.setLineWidth(0.6)
    canv.line(LEFT_MARGIN, PAGE_H - 0.72 * inch, PAGE_W - RIGHT_MARGIN, PAGE_H - 0.72 * inch)
    canv.line(LEFT_MARGIN, 0.62 * inch, PAGE_W - RIGHT_MARGIN, 0.62 * inch)
    canv.setFont("TimesNewRoman", 10)
    canv.drawCentredString(PAGE_W / 2.0, 0.42 * inch, f"Page {doc.page}")
    canv.restoreState()


def chapter(title, key, level=0):
    return [
        PageBreak(),
        Bookmark(key, title, level),
        P(title, "chapter"),
    ]


# ---------------------------------------------------------------------------
# Document body
# ---------------------------------------------------------------------------

def build_story():
    story = []
    W = CONTENT_W

    # ===== PAGE 1: Cover =====
    story.append(Bookmark("cover", "Cover", 0))
    story.append(Spacer(1, 18))
    story.append(P("UNIVERSITY OF GHANA", "title_univ"))
    story.append(P("DEPARTMENT OF COMPUTER SCIENCE", "title_dept"))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1.0, color=black, spaceAfter=8))
    story.append(P("CSCD602 — ADVANCED SOFTWARE ENGINEERING", "title_course"))
    story.append(P("INDIVIDUAL PROJECT-BASED EXAMINATION", "title_exam"))
    story.append(P("PROJECT DOCUMENTATION", "title_exam"))
    story.append(HRFlowable(width="100%", thickness=1.0, color=black, spaceBefore=8, spaceAfter=18))
    story.append(P("ICCTECH", "title_proj"))
    story.append(P("A Web-Based IT Service Management<br/>and Helpdesk System", "title_sub"))
    story.append(Spacer(1, 10))

    cover_rows = [
        ["Student Name", "Clement Asamoah"],
        ["Student ID", "22424193"],
        ["Academic Year", "2025/2026"],
        ["Examination Duration", "48 Hours"],
        ["Live Application", "http://45.79.223.146:8080/index.php"],
        ["Source Repository", "https://github.com/Clemzy123/ICCTECH"],
    ]
    cover_data = [[
        Paragraph("Item", S["th"]),
        Paragraph("Details", S["th"]),
    ]]
    for a, b_ in cover_rows:
        cover_data.append([
            Paragraph(a, S["td_b"]),
            Paragraph(b_, S["td"]),
        ])
    cover_tbl = Table(cover_data, colWidths=[180, W - 180])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("BACKGROUND", (0, 1), (0, -1), GRAY_ROW),
        ("GRID", (0, 0), (-1, -1), 0.5, black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 36))
    bar = Table([[""]], colWidths=[W], rowHeights=[28])
    bar.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRAY_HEADER),
        ("LINEABOVE", (0, 0), (-1, 0), 3, black),
    ]))
    story.append(bar)

    # ===== PAGE 2: Contents =====
    story.append(PageBreak())
    story.append(Bookmark("contents", "Contents", 0))
    story.append(P("PROJECT DOCUMENTATION", "front_h"))
    story.append(P("Contents", "toc_h"))
    toc_items = [
        ("1.", "Introduction, Stakeholders and Requirements Summary", "3"),
        ("2.", "Software Effort Estimation", "4"),
        ("3.", "System Analysis", "6"),
        ("4.", "System Design", "8"),
        ("5.", "Implementation", "13"),
        ("6.", "Testing and Technical Debt Summary", "16"),
        ("7.", "Deployment and Accessibility", "17"),
        ("8.", "Maintenance, Future Evolution, Limitations and Conclusion", "18"),
        ("9.", "References and Acknowledgements", "18"),
    ]
    toc_data = []
    for num, title, page in toc_items:
        toc_data.append([
            Paragraph(num, S["toc"]),
            Paragraph(title, S["toc"]),
            Paragraph(page, ParagraphStyle("tocp", parent=S["toc"], alignment=TA_RIGHT)),
        ])
    toc_tbl = Table(toc_data, colWidths=[28, W - 68, 40])
    toc_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, Color(0.7, 0.7, 0.7)),
    ]))
    story.append(toc_tbl)
    story.append(P(
        "Dedicated companion files: <i>SRS.pdf</i>, <i>Testing_Report.pdf</i>, "
        "<i>Technical_Debt_Plan.pdf</i> and <i>User_Manual.pdf</i>.",
        "companion",
    ))

    # ===== PAGE 3: Chapter 1 =====
    story += chapter("1. Introduction, Stakeholders and Requirements Summary", "ch1")
    story.append(P(
        f"{b('Problem.')} Fragmented IT support through calls, email, messaging, "
        "spreadsheets and verbal reports causes lost or duplicated requests, unclear "
        "ownership, inconsistent priority/status, incomplete history and weak service visibility."
    ))
    story.append(P(
        f"{b('Aim.')} ICCTECH provides a centralised browser-based ITSM/helpdesk workflow "
        "for recording, assigning, tracking, communicating on and resolving support requests "
        "while demonstrating the required Advanced Software Engineering lifecycle."
    ))
    story.append(P("Stakeholders and roles", "section"))
    story += bullets([
        f"{b('End users:')} authenticate, submit and track permitted tickets, reply to support staff and use published knowledge.",
        f"{b('Support analysts:')} triage, categorise, prioritise, assign, investigate, communicate, update status and resolve tickets.",
        f"{b('Administrators:')} manage users, analysts, roles, permissions, teams, settings and permitted operational information.",
        f"{b('Managers/knowledge/asset stakeholders:')} use service information, reusable knowledge and equipment records; the examiner validates traceable engineering evidence.",
    ])
    story.append(P("Requirements and scope", "section"))
    story.append(P(
        "The formal baseline contains 16 functional requirements and 12 non-functional "
        "requirements. Must-Have scope covers authentication, RBAC, the complete ticket "
        "lifecycle and administration; knowledge and assets are Should-Have; basic "
        "audit/operational information is Could-Have. Quality requirements cover usability, "
        "representative performance, security, persistent MySQL storage, availability, "
        "compatibility, Docker deployability, maintainability and responsive use. Full FR/NFR "
        "definitions, use cases, acceptance criteria and traceability are in SRS.pdf."
    ))
    story.append(P(
        f"{b('Core workflow:')} Submit ticket → triage → categorise/prioritise → assign → "
        "investigate/communicate → resolve → close → reopen when further work is required."
    ))

    # ===== PAGES 4–5: Chapter 2 =====
    story += chapter("2. Software Effort Estimation", "ch2")
    story.append(P(
        "Effort is estimated with a bottom-up three-point (PERT) model. For each activity, "
        "optimistic (O), most-likely (M) and pessimistic (P) hours are recorded and the "
        "expected value is computed as (O + 4M + P) / 6. The estimate covers analysis, "
        "design, implementation, deployment, testing and documentation within the 48-hour examination."
    ))
    story.append(P("2.1 Effort Calculation", "section"))
    story.append(P(
        "Table 2.1. Bottom-up three-point (PERT) effort calculation by project activity",
        "table_caption",
    ))
    story.append(make_table(
        ["Project Activity", "O", "M", "P", "Expected Hours"],
        [
            ["Define problem, users and requirements", "1.0", "2.5", "4.0", "2.5"],
            ["Analyse application requirements and technical feasibility", "2.0", "3.0", "4.0", "3.0"],
            ["Review/design architecture, database and workflow", "2.0", "3.0", "4.0", "3.0"],
            ["Implement/validate core ticket workflow", "4.0", "6.0", "8.0", "6.0"],
            ["Implement/validate authentication and role access", "2.0", "3.0", "4.0", "3.0"],
            ["Configure/validate knowledge and asset functions", "1.0", "2.5", "4.0", "2.5"],
            ["Configure Docker and deploy to Linode", "2.0", "4.0", "6.0", "4.0"],
            ["Execute functional and security tests", "3.0", "5.0", "7.0", "5.0"],
            ["Correct defects and perform regression testing", "2.0", "3.0", "4.0", "3.0"],
            ["Prepare project/deployment documentation", "2.0", "3.0", "4.0", "3.0"],
            ["Final verification and submission checks", "0.5", "1.0", "1.5", "1.0"],
        ],
        [W - 196, 46, 46, 46, 58],
        numeric={1, 2, 3, 4},
    ))
    story.append(Spacer(1, 8))
    story.append(NoteBox(
        "Estimated effort",
        "Total planned work = 36 person-hours. A four-hour contingency reserve is added "
        "for unexpected technical issues, producing an estimated total of 40 person-hours.",
    ))
    story.append(P("2.2 Estimated Development Duration", "section"))
    story.append(P(
        "The examination provides 48 elapsed calendar hours. With one student developer, "
        "40 person-hours represent approximately 40 active working hours. The remaining "
        "eight hours provide allowance for rest, meals, short interruptions and unavoidable "
        "non-project activity."
    ))

    story.append(PageBreak())
    story.append(P(
        "Table 2.2. Planned distribution of the 48-hour examination period",
        "table_caption",
    ))
    story.append(make_table(
        ["Calendar Period", "Main Activity", "Active Hours", "Break / Other"],
        [
            ["Hours 1–6", "Problem definition, stakeholders, requirements and scope", "5", "1"],
            ["Hours 7–12", "Technical analysis, architecture and design", "5", "1"],
            ["Hours 13–24", "Core workflow and access-control work", "10", "2"],
            ["Hours 25–30", "Docker/Linode deployment", "4", "2"],
            ["Hours 31–38", "Testing and defect correction", "7", "1"],
            ["Hours 39–44", "Documentation and evidence", "5", "1"],
            ["Hours 45–48", "Contingency, verification and submission", "4", "0"],
        ],
        [110, W - 230, 70, 50],
        numeric={2, 3},
    ))
    story.append(P("2.3 Assumptions", "section"))
    story += bullets([
        "One student performs all project activities.",
        "The Linode server and internet connection remain available.",
        "PHP 8.4, Apache, MySQL 8.0, Docker and Docker Compose can be used in the target environment.",
        "The core ticket workflow is the main implementation and validation focus.",
        "Third-party integrations that require external credentials are outside the critical path.",
        "Testing and documentation are included in the person-hour estimate.",
        "The contingency reserve is used only for unexpected technical problems.",
    ])
    story.append(P("2.4 Constraints", "section"))
    story += bullets([
        "Fixed 48-hour examination duration.",
        "Single developer.",
        "Large codebase with functionality outside the examination scope.",
        "Limited time for exhaustive testing of every module.",
        "Deployment depends on cloud, network, container and database availability.",
        "Documentation, testing and implementation compete for the same limited time.",
    ])

    # ===== PAGES 6–7: Chapter 3 =====
    story += chapter("3. System Analysis", "ch3")
    story.append(P("3.1 Analysis of the Existing Problem", "section"))
    story.append(P(
        "The existing support-management problem is characterised by fragmented reporting "
        "channels and weak traceability. A phone call or instant message can communicate a "
        "problem quickly, but it does not necessarily create a persistent operational record. "
        "This makes status tracking, ownership, prioritisation, historical analysis and audit difficult."
    ))
    story.append(P(
        "Table 3.1. Observed problems, effects and the required system response",
        "table_caption",
    ))
    story.append(make_table(
        ["Observed Problem", "Effect", "Required System Response"],
        [
            ["Requests arrive through informal channels", "Requests may be forgotten or duplicated", "Create a central ticket record with a unique reference."],
            ["Ownership is unclear", "Users do not know who is responsible", "Support assignment and visible ticket ownership."],
            ["No consistent priority", "Urgent issues may compete with routine requests", "Configurable priority and triage."],
            ["Updates are scattered", "Communication history is incomplete", "Record messages/notes against the ticket."],
            ["Status is not visible", "Users repeatedly ask for progress", "Ticket status and self-service visibility."],
            ["Solutions are not reused", "Analysts repeatedly solve the same problem", "Knowledge-base capability."],
            ["Device context is separated", "Troubleshooting lacks asset history", "Asset records and user/asset associations."],
            ["Limited accountability", "Difficult to review what changed", "Ticket audit and system logging."],
        ],
        [W * 0.30, W * 0.34, W * 0.36],
    ))
    story.append(P("3.2 Proposed System Behaviour", "section"))
    story.append(P(
        "ICCTECH converts each support request into a persistent ticket and guides it through "
        "a controlled lifecycle. The system separates requester-facing activities from analyst "
        "and administrator functions, while using authentication and role/capability checks to "
        "protect administrative actions."
    ))

    story.append(PageBreak())
    story.append(P("3.3 Core Business Process", "section"))
    story.append(P(
        "Submitted → Open / triage → Categorise + Prioritise → Assign → In Progress → "
        "On Hold / Awaiting Response where necessary → In Progress → Resolve → Close → "
        "Reopen if further work is required."
    ))
    story.append(P(
        "The source database defines configurable ticket statuses rather than hard-coding "
        "business meaning into a single fixed workflow. Default statuses include Open, In "
        "Progress, On Hold, Awaiting Response and Closed. On Hold and Awaiting Response can "
        "pause the service-level agreement clock by default."
    ))
    story.append(P("3.4 Data Analysis", "section"))
    story.append(P(
        "The core data model revolves around tickets and their relationships to users, analysts, "
        "statuses, priorities and departments. Ticket notes and ticket audit records preserve "
        "operational history. Asset and user-asset records provide device context, while "
        "knowledge articles provide reusable support information. RBAC tables link analysts to "
        "roles and roles to granular capabilities."
    ))
    story.append(P("3.5 Role and Permission Analysis", "section"))
    story.append(P(
        "The analyst authentication flow includes password verification, failed-login tracking, "
        "account lockout and optional TOTP multi-factor authentication. Authorisation is "
        "implemented beyond interface visibility: server-side role and capability checks are "
        "used to determine whether an analyst can access protected modules or administrative "
        "functions. This supports the requirement that access control must be enforced according "
        "to role rather than simply hiding interface elements."
    ))
    story.append(P("3.6 Feasibility Analysis", "section"))
    story.append(P("Table 3.2. Feasibility assessment across five dimensions", "table_caption"))
    story.append(make_table(
        ["Dimension", "Assessment"],
        [
            ["Technical feasibility", "High. The required stack is available in the repository: PHP 8.4/Apache, MySQL 8.0, PDO, Docker and Docker Compose."],
            ["Operational feasibility", "High for the core workflow. End users, analysts and administrators have clear roles and a browser-based interface."],
            ["Schedule feasibility", "Feasible only with strict scope control. The 48-hour limit requires prioritising the core ticket lifecycle and evidence."],
            ["Deployment feasibility", "High. The application is containerised and already deployed to a Linode Linux server."],
            ["Security feasibility", "Reasonable for the examination scope, but production hardening such as HTTPS, secret rotation and infrastructure controls must be treated as ongoing work."],
        ],
        [150, W - 150],
    ))

    # ===== PAGES 8–12: Chapter 4 (one view per page) =====
    story += chapter("4. System Design — Architecture", "ch4")
    story.append(P(
        "The design selects artefacts that best communicate the application rather than "
        "producing every possible UML diagram. The most useful views for ICCTECH are the "
        "deployment/system architecture, use cases, ticket activity flow, core database "
        "relationships and a representative sequence for ticket creation and update."
    ))
    story.append(P(
        "The deployed design separates browser access, the Apache/PHP application service and "
        "MySQL database under Docker Compose on Linode. PDO provides application-to-database "
        "access and persistent volumes retain database data, attachments and keys."
    ))
    story.append(ArchitectureDiagram(height=395))
    story.append(P("Figure 4.1. ICCTECH containerised deployment architecture", "caption"))
    story.append(P(
        "Users access the application through a web browser. The Linode host exposes port 8080, "
        "which Docker maps to Apache port 80 inside the application container."
    ))

    story += chapter("4. System Design — Use Cases", "ch4-uc", 1)
    story.append(UseCaseDiagram(height=455))
    story.append(P("Figure 4.2. Core ICCTECH use cases by user class", "caption"))
    story.append(P(
        "The use-case design separates end-user, analyst and administrator responsibilities "
        "while keeping authentication as the protected entry point. End users focus on reporting "
        "and monitoring support requests. Analysts manage the operational ticket lifecycle. "
        "Administrators control users, roles, service settings and selected audit information. "
        "Detailed behavioural specifications are maintained in SRS.pdf."
    ))

    story += chapter("4. System Design — Ticket Activity", "ch4-act", 1)
    story.append(ActivityDiagram(height=478))
    story.append(P("Figure 4.3. Core ticket lifecycle activity flow", "caption"))
    story.append(P(
        "The activity flow is the primary service-desk process and includes the "
        "hold/awaiting-response decision, resolution, closure and controlled reopen path."
    ))

    story += chapter("4. System Design — Core Data Model", "ch4-er", 1)
    story.append(ERDiagram(height=448))
    story.append(P("Figure 4.4. Simplified ER view of examination-scope entities", "caption"))
    story.append(P(
        "Core entities include users, analysts, tickets, statuses, priorities, departments, "
        "notes, audit records, assets, user-asset links, knowledge articles and RBAC "
        "role/capability tables. Foreign-key relationships retain requester, ownership, history "
        "and access-control context. The full database schema is substantially larger than the "
        "examination scope; the diagram focuses on the entities required to explain the core helpdesk workflow."
    ))

    story += chapter("4. System Design — Representative Sequence", "ch4-seq", 1)
    story.append(SequenceDiagram(height=478))
    story.append(P("Figure 4.5. Representative sequence for ticket creation and analyst update", "caption"))
    story.append(P(
        "The sequence shows validated ticket creation and subsequent analyst update: "
        "authenticated requests are authorised, persisted in MySQL and accompanied by "
        "audit/note history. Server-side capability checks protect privileged updates."
    ))

    # ===== PAGES 13–15: Chapter 5 =====
    story += chapter("5. Implementation", "ch5")
    story.append(P("5.1 Technology Stack", "section"))
    story.append(P("Table 5.1. Implementation evidence for each technology component", "table_caption"))
    story.append(make_table(
        ["Component", "Implementation Evidence / Purpose"],
        [
            ["PHP 8.4 + Apache", "The Dockerfile is based on php:8.4-apache and enables the required PHP extensions."],
            ["MySQL 8.0", "docker-compose.yml defines a separate MySQL 8.0 service and imports database/freeitsm.sql on initial creation."],
            ["PDO / pdo_mysql", "Application database communication uses PDO and the MySQL driver."],
            ["Docker / Docker Compose", "Application and database are containerised and orchestrated as separate services."],
            ["HTML / CSS / JavaScript", "Provides browser-based user and administrative interfaces."],
            ["Git / GitHub", "Maintains the source repository and project history."],
            ["Linode Linux server", "Hosts the live deployment on port 8080."],
        ],
        [160, W - 160],
    ))
    story.append(P("5.2 Application Structure", "section"))
    story.append(P(
        "The codebase is organised into web modules, API endpoints, shared includes/services, "
        "database scripts, Docker configuration, documentation and tests. Relevant paths for "
        "the examination scope include <i>auth/</i>, <i>api/auth/</i>, <i>api/tickets/</i>, "
        "<i>asset-management/</i>, <i>knowledge/</i>, <i>includes/</i>, <i>database/</i>, "
        "<i>docker/</i> and <i>tests/</i>."
    ))
    story.append(NoteBox(
        "Key project files",
        "Dockerfile | docker-compose.yml | auth/login.php | includes/rbac.php | "
        "api/tickets/create_ticket.php | api/tickets/assign_ticket.php | "
        "api/tickets/get_ticket_audit.php | database/freeitsm.sql",
    ))
    story.append(P("5.3 Authentication Implementation", "section"))
    story.append(P(
        "The analyst login implementation in <i>auth/login.php</i> retrieves analyst "
        "authentication state, verifies local passwords with <i>password_verify()</i>, tracks "
        "failed login attempts and supports account lockout. The same flow also contains optional "
        "TOTP multi-factor authentication and trusted-device handling. Password reset code uses "
        "<i>password_hash()</i> with PHP’s default password algorithm. The source also contains "
        "optional external authentication integrations, but these are not required for the core "
        "examination workflow."
    ))

    story.append(PageBreak())
    story.append(P("5.4 Authorisation and RBAC", "section"))
    story.append(P(
        "Role-based access is implemented through analyst roles and granular capabilities. The "
        "database contains <i>rbac_roles</i>, <i>rbac_role_capabilities</i> and "
        "<i>rbac_analyst_roles</i>. Shared RBAC code in <i>includes/rbac.php</i> and related "
        "settings code performs capability checks for protected functions. This is important "
        "because security is enforced server-side rather than relying only on whether a menu "
        "item is visible."
    ))
    story.append(P("5.5 Ticket Management", "section"))
    story.append(P(
        "The ticket subsystem exposes endpoints for ticket creation, assignment, status/priority "
        "retrieval, user-ticket viewing, notes, audit history, restore/reopen operations, "
        "deletion/trash handling and dashboard data. The central <i>tickets</i> table links the "
        "request to a user, assigned analyst, status, priority and department. Related "
        "<i>ticket_notes</i> and <i>ticket_audit</i> records preserve communication and change history."
    ))
    story.append(P("5.6 Knowledge and Asset Functions", "section"))
    story.append(P(
        "Knowledge articles are persisted in <i>knowledge_articles</i> with author, publication, "
        "review and version information. Asset records include device identity and lifecycle "
        "attributes such as hostname, manufacturer, model, operating system, service tag, status "
        "and location. <i>users_assets</i> links assets to end users and records who made the assignment."
    ))
    story.append(P("5.7 Database Persistence", "section"))
    story.append(P(
        "MySQL 8.0 provides persistent storage. The initial schema is stored in "
        "<i>database/freeitsm.sql</i> and Docker Compose mounts the database directory to a named "
        "volume. This ensures that operational records are not stored only inside a disposable "
        "container layer."
    ))
    story.append(P("5.8 Validation, Error Handling and Security Controls", "section"))
    story += bullets([
        "Password hashing and verification using PHP password functions.",
        "Failed-login counting and configurable lockout logic for analysts.",
        "Optional TOTP MFA support.",
        "Role and capability checks for protected analyst functions.",
        "Prepared PDO statements are used throughout key database operations.",
        "Persistent encryption-key storage outside the web document root in the Docker image design.",
        "Application separation from the database through the Docker internal service network.",
        "Input validation and server-side checks are used by application/API endpoints where relevant.",
    ])

    story.append(PageBreak())
    story.append(P("5.9 Requirement-to-Source Traceability", "section"))
    story.append(P(
        "Table 5.2. Examination evidence for persistence, deployability, testing and source control",
        "table_caption",
    ))
    story.append(make_table(
        ["Requirement / Area", "Source Evidence", "Examination Contribution Demonstrated"],
        [
            [
                "NFR-06, NFR-09, NFR-11 — Persistence &amp; deployability",
                "Dockerfile; docker-compose.yml; database/freeitsm.sql; named volumes",
                "Configured and deployed the PHP/MySQL application on Linode using Docker Compose, then verified database-backed persistence after controlled service restart.",
            ],
            [
                "Testing and deployment evidence",
                "tests/; live Linode deployment; GitHub repository",
                "Executed the examination-specific test cycle, documented results, and maintained the deployable source repository for examiner verification.",
            ],
        ],
        [W * 0.28, W * 0.32, W * 0.40],
    ))
    story.append(Spacer(1, 8))
    story.append(NoteBox(
        "Traceability note",
        "This table records what was demonstrated and validated for the examination. It does "
        "not represent every upstream module in the wider repository as newly authored during "
        "the 48-hour period.",
    ))
    story.append(P("5.10 Reuse and Third-Party Components", "section"))
    story.append(NoteBox(
        "Academic-integrity statement",
        "The repository contains substantial upstream FreeITSM functionality and third-party "
        "components. The examination documentation should distinguish the student’s "
        "project-specific analysis, configuration, implementation, validation, deployment and "
        "documentation work from inherited platform functionality. The upstream project and "
        "relevant libraries/frameworks should be acknowledged in the References section rather "
        "than representing the entire codebase as newly authored during the 48-hour examination.",
    ))
    story.append(P("5.11 Implementation Outcome", "section"))
    story.append(P(
        "The implemented and deployed project provides the functional foundation required to "
        "demonstrate the prioritised ITSM workflow in a live environment. The requirement-to-source "
        "traceability above, together with screenshots, final test results and repository history, "
        "allows the examiner to connect documented requirements to working functionality while "
        "keeping project-specific examination work distinct from inherited platform components."
    ))

    # ===== PAGE 16: Chapter 6 =====
    story += chapter("6. Testing and Technical Debt Summary", "ch6")
    story.append(P("Testing", "section"))
    story.append(P(
        "The final examination cycle executed 17 formal tests against the deployed "
        "Linode/Docker environment. All 17 passed; none failed or were blocked, and no "
        "final-cycle defect remained open. Coverage includes valid/invalid authentication, "
        "RBAC, ticket creation through reopen, administration, knowledge, assets, persistence "
        "after service restart, live deployment, representative page-response performance and "
        "responsive-interface usability. Full procedures, expected/actual results and "
        "traceability are in Testing_Report.pdf."
    ))
    story.append(P("Technical debt", "section"))
    story += bullets([
        f"{b('TD-01 Critical:')} externalise and rotate development/default credentials.",
        f"{b('TD-02 Critical:')} replace HTTP-only public access with HTTPS/TLS.",
        f"{b('TD-03 High:')} remove or strictly restrict the published MySQL host port.",
        f"{b('TD-04 High:')} expand requirements-mapped automated regression and add CI.",
        f"{b('TD-05 High:')} implement independent off-host backup and tested restore.",
        f"{b('TD-06 Medium:')} add production monitoring and automated alerts.",
        f"{b('TD-07 Medium:')} single Linode host remains a resilience/scalability limitation.",
        f"{b('TD-08 Medium:')} refactor legacy/upstream internal naming incrementally.",
        f"{b('TD-09 Medium:')} freeze/tag the final release to prevent documentation/evidence drift.",
    ])
    story.append(P(
        "The complete Debt → Cause → Impact → Priority → Proposed Resolution records and "
        "repayment roadmap are in Technical_Debt_Plan.pdf."
    ))

    # ===== PAGE 17: Chapter 7 =====
    story += chapter("7. Deployment and Accessibility", "ch7")
    story.append(P(
        "The application is deployed on a Linode Linux host with Docker Compose. Host port 8080 "
        "maps to Apache in the PHP application container; MySQL 8.0 runs as a separate service "
        "and named volumes persist database/application data. Deployment verification covers "
        "service startup, database connectivity, authentication, ticket creation and retrieval, "
        "restart persistence and live browser reachability. Production hardening priorities are "
        "HTTPS, externalised secrets, restricted database exposure, off-host backups and monitoring."
    ))
    story.append(ArchitectureDiagram(height=360))
    story.append(P("Figure 7.1. Deployment architecture", "caption"))

    # ===== PAGE 18: Chapters 8 and 9 =====
    story += chapter("8. Maintenance, Future Evolution, Limitations and Conclusion", "ch8")
    story.append(P(
        f"{b('Maintenance.')} Corrective work addresses verified defects; adaptive maintenance "
        "handles platform/dependency/environment changes; perfective work improves usability, "
        "workflow and reporting; preventive maintenance covers updates, backups, secret rotation, "
        "access review and health/log monitoring. Releases should use identified Git revisions, "
        "regression testing, rollback planning and updated documentation."
    ))
    story.append(P(
        f"{b('Future evolution.')} Near-term priorities are HTTPS, CI/regression automation, "
        "off-host backup/restore verification, monitoring and refined dashboards. Later evolution "
        "can add governed identity/integration features, SLA/escalation automation, richer "
        "knowledge/asset links and higher-availability architecture when justified by scale."
    ))
    story.append(P(
        f"{b('Limitations.')} The 48-hour examination restricts long-term UAT, exhaustive "
        "cross-browser/device testing, penetration testing, large-scale load testing, "
        "disaster-recovery exercises and broad enterprise customisation. The IP-based HTTP "
        "deployment is suitable for demonstration rather than hardened production. Substantial "
        "FreeITSM/upstream capability is reused and acknowledged; repository size is not claimed "
        "as work authored entirely during the examination."
    ))
    story.append(P(
        f"{b('Conclusion.')} ICCTECH demonstrates the complete software-engineering lifecycle: "
        "scoped requirements, quantified effort, analysis/design, implementation, deployment, "
        "formal verification, technical-debt management, documentation, maintenance and evolution. "
        "The prioritised workflow is demonstrable online and all 17 formal acceptance tests passed."
    ))
    # Chapter 9 shares the final page so the document stays at 18 pages.
    story.append(Spacer(1, 6))
    story.append(Bookmark("ch9", "9. References and Acknowledgements", 0))
    story.append(P("9. References and Acknowledgements", "chapter"))
    story += bullets([
        "ICCTECH repository: https://github.com/Clemzy123/ICCTECH and live deployment: http://45.79.223.146:8080/index.php.",
        "PHP, Apache HTTP Server, MySQL 8.0, Docker/Docker Compose and Linode/Akamai documentation.",
        "Upstream FreeITSM platform and third-party libraries used by the inherited codebase, acknowledged as reused rather than newly authored during the examination.",
    ])
    return story


def main():
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Project_Documentation.pdf"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

    doc = BaseDocTemplate(
        out,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH Project Documentation",
        author="Clement Asamoah",
        subject="CSCD602 Advanced Software Engineering — Individual Project Documentation",
        creator="ICCTECH document production",
    )
    frame = Frame(
        LEFT_MARGIN, BOTTOM_MARGIN, CONTENT_W, CONTENT_H,
        id="normal", showBoundary=0,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=draw_header_footer),
    ])
    story = build_story()
    doc.build(story)

    import pymupdf
    n = pymupdf.open(out).page_count
    print(f"Wrote {out} ({n} pages)")
    if n > 18:
        print("ERROR: document exceeds the 18-page source length.", file=sys.stderr)
        sys.exit(2)
    if n != 18:
        print(f"WARNING: expected 18 pages, got {n}", file=sys.stderr)
    return n


if __name__ == "__main__":
    main()
