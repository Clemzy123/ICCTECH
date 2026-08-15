#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH Software Requirements Specification PDF.

Typography: Times New Roman, 12 pt justified body at 1.0 single spacing,
14 pt bold chapter headings on new pages, 1.0 in margins on all sides.
Tables wrap cleanly. Architecture and lifecycle diagrams are PDF-native
vectors. Black and white only. Target: 12 pages (same as the source).
"""

from __future__ import annotations

import os
import sys

from reportlab.lib.colors import Color, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
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

PAGE_W, PAGE_H = A4
LEFT_MARGIN = 1.0 * inch
RIGHT_MARGIN = 1.0 * inch
TOP_MARGIN = 1.0 * inch
BOTTOM_MARGIN = 1.0 * inch
CONTENT_W = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
CONTENT_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN

GRAY_HEADER = Color(0.18, 0.18, 0.18)
GRAY_ROW = Color(0.94, 0.94, 0.94)
GRAY_FILL = Color(0.96, 0.96, 0.96)


def _styles():
    s = {}
    s["body"] = ParagraphStyle(
        "Body", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=7, textColor=black, splitLongWords=True,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter", fontName="TimesNewRoman-Bold", fontSize=14, leading=17,
        alignment=TA_LEFT, spaceAfter=8, textColor=black, keepWithNext=True,
    )
    s["section"] = ParagraphStyle(
        "Section", fontName="TimesNewRoman-Bold", fontSize=12, leading=14,
        alignment=TA_LEFT, spaceBefore=7, spaceAfter=4, textColor=black, keepWithNext=True,
    )
    s["uc"] = ParagraphStyle(
        "UC", fontName="TimesNewRoman-Bold", fontSize=11, leading=13,
        alignment=TA_LEFT, spaceBefore=3, spaceAfter=2, textColor=black, keepWithNext=True,
    )
    s["title_univ"] = ParagraphStyle(
        "TitleUniv", fontName="TimesNewRoman-Bold", fontSize=16, leading=20,
        alignment=TA_CENTER, textColor=black, spaceAfter=3,
    )
    s["title_dept"] = ParagraphStyle(
        "TitleDept", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
        alignment=TA_CENTER, textColor=black, spaceAfter=2,
    )
    s["title_doc"] = ParagraphStyle(
        "TitleDoc", fontName="TimesNewRoman-Bold", fontSize=13, leading=16,
        alignment=TA_CENTER, textColor=black, spaceBefore=4, spaceAfter=4,
    )
    s["title_proj"] = ParagraphStyle(
        "TitleProj", fontName="TimesNewRoman-Bold", fontSize=22, leading=26,
        alignment=TA_CENTER, textColor=black, spaceBefore=10, spaceAfter=4,
    )
    s["title_sub"] = ParagraphStyle(
        "TitleSub", fontName="TimesNewRoman-Italic", fontSize=13, leading=16,
        alignment=TA_CENTER, textColor=black, spaceAfter=14,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=3, spaceAfter=6, textColor=black,
    )
    s["table_caption"] = ParagraphStyle(
        "TableCaption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=3, spaceAfter=3, textColor=black, keepWithNext=True,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=white,
    )
    s["th_c"] = ParagraphStyle(
        "THc", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_CENTER, textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="TimesNewRoman", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_c"] = ParagraphStyle(
        "TDc", fontName="TimesNewRoman", fontSize=8, leading=10,
        alignment=TA_CENTER, textColor=black,
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
    s["cover_link"] = ParagraphStyle(
        "CoverLink", fontName="TimesNewRoman", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=black, spaceBefore=2,
    )
    s["uc_th"] = ParagraphStyle(
        "UCTH", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=white,
    )
    s["uc_lab"] = ParagraphStyle(
        "UCLab", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=black,
    )
    s["uc_val"] = ParagraphStyle(
        "UCVal", fontName="TimesNewRoman", fontSize=8, leading=10,
        alignment=TA_JUSTIFY, textColor=black,
    )
    return s


S = _styles()


def P(text, style="body"):
    return Paragraph(text, S[style] if isinstance(style, str) else style)


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
    def __init__(self, title, body, width=CONTENT_W):
        Flowable.__init__(self)
        self.title = title
        self.body = body
        self.box_width = width
        self._header_h = 15
        self._pad = 6

    def wrap(self, aw, ah):
        self.box_width = min(self.box_width, aw)
        inner = self.box_width - 2 * self._pad
        self._bp = Paragraph(self.body, S["note"])
        _bw, bh = self._bp.wrap(inner, ah)
        self.width = self.box_width
        self.height = self._header_h + bh + 2 * self._pad
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.setStrokeColor(black)
        c.setLineWidth(0.7)
        c.setFillColor(GRAY_HEADER)
        c.rect(0, self.height - self._header_h, self.width, self._header_h, fill=1, stroke=1)
        c.setFillColor(white)
        c.setFont("TimesNewRoman-Bold", 10)
        c.drawString(self._pad, self.height - self._header_h + 3.5, self.title)
        c.setFillColor(GRAY_FILL)
        c.rect(0, 0, self.width, self.height - self._header_h, fill=1, stroke=1)
        self._bp.drawOn(c, self._pad, self._pad)


def make_table(headers, rows, col_widths, numeric=None, header_center=None, font=8):
    numeric = set(numeric or [])
    header_center = set(header_center or numeric)
    head = [Paragraph(h, S["th_c"] if i in header_center else S["th"]) for i, h in enumerate(headers)]
    data = [head]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            style = S["td_c"] if i in numeric else (S["td_b"] if i == 0 and "FR-" in str(cell) or str(cell).startswith("NFR-") else S["td"])
            if i == 0 and (str(cell).startswith("FR-") or str(cell).startswith("NFR-")):
                style = S["td_b"]
            cells.append(Paragraph(str(cell), style))
        data.append(cells)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            commands.append(("BACKGROUND", (0, r), (-1, r), GRAY_ROW))
    tbl.setStyle(TableStyle(commands))
    return tbl


def spec_table(rows, width=CONTENT_W):
    data = [[
        Paragraph("Field", S["uc_th"]),
        Paragraph("Specification", S["uc_th"]),
    ]]
    for lab, val in rows:
        data.append([
            Paragraph(lab, S["uc_lab"]),
            Paragraph(val, S["uc_val"]),
        ])
    tbl = Table(data, colWidths=[118, width - 118], repeatRows=1)
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("BACKGROUND", (0, 1), (0, -1), GRAY_ROW),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
    ]
    tbl.setStyle(TableStyle(commands))
    return tbl


def bullets(items):
    return [Paragraph(f"•  {item}", S["bullet"]) for item in items]


def _round_box(c, x, y, w, h, lines, radius=4, fill=GRAY_FILL):
    c.setFillColor(fill)
    c.setStrokeColor(black)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.setFillColor(black)
    n = len(lines)
    line_h = 10
    start = y + h / 2 + (n - 1) * line_h / 2 - 2
    for i, line in enumerate(lines):
        name, sz, txt = line if isinstance(line, tuple) else ("TimesNewRoman", 8, line)
        c.setFont(name, sz)
        c.drawCentredString(x + w / 2, start - i * line_h, txt)


def _arrow(c, x1, y1, x2, y2, label=None, label_off=(0, 3)):
    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setLineWidth(0.9)
    c.line(x1, y1, x2, y2)
    direction_x = 1 if x2 >= x1 else -1
    direction_y = 1 if y2 >= y1 else -1
    if abs(x2 - x1) >= abs(y2 - y1):
        c.line(x2, y2, x2 - 6 * direction_x, y2 + 3)
        c.line(x2, y2, x2 - 6 * direction_x, y2 - 3)
    else:
        c.line(x2, y2, x2 - 3, y2 - 6 * direction_y)
        c.line(x2, y2, x2 + 3, y2 - 6 * direction_y)
    if label:
        c.setFont("TimesNewRoman-Italic", 7)
        c.drawCentredString((x1 + x2) / 2 + label_off[0], (y1 + y2) / 2 + label_off[1], label)


class ArchitectureDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=310):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        cx = w / 2
        client_w, client_h = 280, 36
        _round_box(c, cx - client_w / 2, h - client_h - 2, client_w, client_h, [
            ("TimesNewRoman-Bold", 8, "Client Tier"),
            ("TimesNewRoman", 8, "Modern desktop / mobile-sized web browser"),
        ])
        _arrow(c, cx, h - client_h - 2, cx, h - client_h - 22, "HTTP · port 8080", (52, 0))

        host_y = 6
        host_h = h - client_h - 30
        host_x = 18
        host_w = w - 36
        c.setStrokeColor(black)
        c.setLineWidth(1.1)
        c.setFillColor(white)
        c.roundRect(host_x, host_y, host_w, host_h, 5, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman-Bold", 9)
        c.drawCentredString(cx, host_y + host_h - 14, "Linode Linux Cloud Server")

        dash_x, dash_y = host_x + 12, host_y + 52
        dash_w, dash_h = host_w - 24, host_h - 72
        c.setDash(3, 2)
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.setFillColor(Color(0.98, 0.98, 0.98))
        c.roundRect(dash_x, dash_y, dash_w, dash_h, 4, fill=1, stroke=1)
        c.setDash()
        c.setFillColor(black)
        c.setFont("TimesNewRoman-Italic", 8)
        c.drawCentredString(cx, dash_y + dash_h - 12, "Docker Compose orchestration")

        box_w, box_h = 168, 40
        gap = 28
        app_x = dash_x + 16
        db_x = dash_x + dash_w - 16 - box_w
        box_y = dash_y + (dash_h - box_h) / 2 + 4
        _round_box(c, app_x, box_y, box_w, box_h, [
            ("TimesNewRoman-Bold", 8, "Application Container"),
            ("TimesNewRoman", 8, "Apache HTTP Server + PHP 8.4"),
        ])
        _round_box(c, db_x, box_y, box_w, box_h, [
            ("TimesNewRoman-Bold", 8, "Database Container"),
            ("TimesNewRoman", 8, "MySQL 8.0"),
        ])
        _arrow(c, app_x + box_w, box_y + box_h / 2, db_x, box_y + box_h / 2, "PDO / pdo_mysql", (0, 6))

        vol_h = 32
        vol_y = host_y + 10
        _round_box(c, host_x + 28, vol_y, host_w - 56, vol_h, [
            ("TimesNewRoman-Bold", 8, "Persistent Docker Volumes"),
            ("TimesNewRoman", 7.5, "Database data, application files and keys"),
        ], radius=10)
        _arrow(c, app_x + box_w / 2, box_y, host_x + 28 + (host_w - 56) * 0.32, vol_y + vol_h)
        _arrow(c, db_x + box_w / 2, box_y, host_x + 28 + (host_w - 56) * 0.68, vol_y + vol_h)


class LifecycleDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=145):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        labels_top = ["Submit Ticket", "Triage", "Categorise / Prioritise", "Assign"]
        labels_bot = ["Investigate / Communicate", "Resolve", "Close"]
        bw, bh = 96, 28
        gap = (w - 4 * bw) / 5
        top_y = h - bh - 8
        xs = [gap + i * (bw + gap) for i in range(4)]
        for i, lab in enumerate(labels_top):
            fill = GRAY_HEADER if i == 0 else GRAY_FILL
            tc = white if i == 0 else black
            c.setFillColor(fill)
            c.setStrokeColor(black)
            c.setLineWidth(0.8)
            c.roundRect(xs[i], top_y, bw, bh, 5, fill=1, stroke=1)
            c.setFillColor(tc)
            c.setFont("TimesNewRoman-Bold" if i == 0 else "TimesNewRoman", 7.5)
            c.drawCentredString(xs[i] + bw / 2, top_y + 10, lab)
            if i < 3:
                _arrow(c, xs[i] + bw, top_y + bh / 2, xs[i + 1], top_y + bh / 2)

        bot_y = 18
        bot_span = 3 * bw + 2 * gap
        bot_left = (w - bot_span) / 2
        bxs = [bot_left + i * (bw + gap) for i in range(3)]
        for i, lab in enumerate(labels_bot):
            fill = GRAY_HEADER if lab == "Close" else GRAY_FILL
            tc = white if lab == "Close" else black
            c.setFillColor(fill)
            c.setStrokeColor(black)
            c.roundRect(bxs[i], bot_y, bw, bh, 5, fill=1, stroke=1)
            c.setFillColor(tc)
            c.setFont("TimesNewRoman-Bold" if lab == "Close" else "TimesNewRoman", 7)
            c.drawCentredString(bxs[i] + bw / 2, bot_y + 10, lab)
            if i < 2:
                _arrow(c, bxs[i] + bw, bot_y + bh / 2, bxs[i + 1], bot_y + bh / 2)

        # Assign down to Investigate
        _arrow(c, xs[3] + bw / 2, top_y, bxs[0] + bw / 2, bot_y + bh)
        # Reopen: Close back to Assign
        c.setDash(2, 1.5)
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        rx = w - 8
        c.line(bxs[2] + bw, bot_y + bh / 2, rx, bot_y + bh / 2)
        c.line(rx, bot_y + bh / 2, rx, top_y + bh / 2)
        c.setDash()
        _arrow(c, rx, top_y + bh / 2, xs[3] + bw, top_y + bh / 2)
        c.setFont("TimesNewRoman-Italic", 7)
        c.setFillColor(black)
        c.drawString(rx - 36, (top_y + bot_y) / 2 + 8, "Reopen")


def draw_header_footer(canv, doc):
    canv.saveState()
    if doc.page == 1:
        canv.restoreState()
        return
    canv.setFillColor(black)
    canv.setStrokeColor(black)
    canv.setFont("TimesNewRoman-Italic", 8)
    canv.drawString(LEFT_MARGIN, PAGE_H - 0.62 * inch, "ICCTECH — Software Requirements Specification (SRS)")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 0.62 * inch, "Version 1.0 — Final Baseline")
    canv.setLineWidth(0.6)
    canv.line(LEFT_MARGIN, PAGE_H - 0.72 * inch, PAGE_W - RIGHT_MARGIN, PAGE_H - 0.72 * inch)
    canv.line(LEFT_MARGIN, 0.62 * inch, PAGE_W - RIGHT_MARGIN, 0.62 * inch)
    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, 0.42 * inch, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, 0.42 * inch, f"Page {doc.page}")
    canv.restoreState()


def chapter(title, key, level=0):
    return [PageBreak(), Bookmark(key, title, level), P(title, "chapter")]


def uc_block(title, rows):
    return [P(title, "uc"), spec_table(rows), Spacer(1, 2)]


def build_story():
    story = []
    W = CONTENT_W

    # ===== PAGE 1: Cover =====
    story.append(Bookmark("cover", "Cover", 0))
    story.append(Spacer(1, 22))
    story.append(P("UNIVERSITY OF GHANA", "title_univ"))
    story.append(P("DEPARTMENT OF COMPUTER SCIENCE", "title_dept"))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1.0, color=black, spaceAfter=10))
    box = Table(
        [[P("SOFTWARE REQUIREMENTS SPECIFICATION (SRS)", "title_doc")]],
        colWidths=[W],
    )
    box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.4, black),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    story.append(box)
    story.append(P("ICCTECH", "title_proj"))
    story.append(P("A Web-Based IT Service Management and Helpdesk System", "title_sub"))

    cover_rows = [
        ["Student Name", "Clement Asamoah"],
        ["Student ID", "22424193"],
        ["Course", "CSCD602 – Advanced Software Engineering"],
        ["Academic Year", "2025/2026"],
        ["Examination Duration", "48 Hours"],
        ["Document Version", "1.0 – Final Baseline"],
        ["Document Status", "Final requirements baseline for examination submission"],
    ]
    cover_data = [[Paragraph(a, S["td_b"]), Paragraph(b_, S["td"])] for a, b_ in cover_rows]
    cover_tbl = Table(cover_data, colWidths=[170, W - 170])
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.5, black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (0, -1), GRAY_ROW),
    ]
    cover_tbl.setStyle(TableStyle(cmds))
    story.append(cover_tbl)
    story.append(Spacer(1, 16))
    story.append(P(f"{b('Live Application:')} http://45.79.223.146:8080/index.php", "cover_link"))
    story.append(P(f"{b('Source Repository:')} https://github.com/Clemzy123/ICCTECH", "cover_link"))

    # ===== PAGE 2: Chapter 1 =====
    story += chapter("1. Purpose, Scope and Product Perspective", "ch1")
    story.append(P(
        "This SRS is the final requirements baseline for ICCTECH. It defines the functions, "
        "quality attributes, users and acceptance conditions for the 48-hour examination scope. "
        "End users submit and monitor requests; analysts triage, prioritise, assign, communicate, "
        "update and resolve tickets; administrators manage users, roles, permissions and essential configuration."
    ))
    story.append(P("Scope", "section"))
    story.append(P(
        "Scope includes authentication and RBAC, unique ticket references, categorisation, "
        "priority and assignment, communication and status, resolution, closure and reopen, knowledge, basic assets, "
        "user/permission administration, basic operational information, persistent MySQL storage "
        "and browser-based cloud access. Wider repository functionality is outside acceptance "
        "unless explicitly listed."
    ))
    story.append(P("Primary users", "section"))
    story += bullets([
        f"{b('End User')} (low privilege): submit and monitor permitted support tickets and use published knowledge.",
        f"{b('IT Support Analyst')} (medium privilege): triage, categorise, prioritise, assign, communicate, update and resolve tickets.",
        f"{b('System Administrator')} (high privilege): manage users, analysts, roles, permissions and essential configuration.",
        f"{b('IT managers / secondary stakeholders:')} receive only granted operational views.",
    ])
    story.append(P(
        "This baseline contains 16 functional requirements and 12 non-functional requirements. "
        "Must-Have items define the minimum viable examination workflow; Should-Have and "
        "Could-Have items provide supporting capability. Companion verification evidence is "
        "maintained in the Testing Report."
    ))

    # ===== PAGE 3: Chapter 2 =====
    story += chapter("2. Overall Description", "ch2")
    story.append(P("2.1 Product Perspective", "section"))
    story.append(P(
        "ICCTECH is a centralised browser-based helpdesk application intended to replace "
        "fragmented support channels such as verbal reports, telephone calls, messaging "
        "applications, email threads and spreadsheets with a traceable ticket lifecycle. The "
        "examination deployment operates on a Linode Linux server using Docker Compose, with "
        "an Apache/PHP application service and a separate MySQL 8.0 database service."
    ))
    story.append(NoteBox(
        "System boundary",
        "The SRS covers the prioritised ICCTECH examination workflow. The repository contains "
        "a broader upstream platform and third-party components; features outside this baseline "
        "are not treated as mandatory deliverables unless explicitly listed as requirements below.",
    ))
    story.append(Spacer(1, 8))
    story.append(ArchitectureDiagram(height=300))
    story.append(P(
        "Figure 1. ICCTECH examination deployment architecture, showing the client tier, "
        "Linode host, Docker Compose services and persistent volumes (Sections 2.1 and 6.2).",
        "caption",
    ))
    story.append(P("2.2 Major Product Functions", "section"))
    story += bullets([
        "Authenticate users and enforce role/capability restrictions.",
        "Allow end users to create and monitor support tickets.",
        "Generate a unique reference and status for each submitted ticket.",
        "Allow analysts to triage, categorise, prioritise and assign work.",
        "Maintain communication and notes within the ticket record.",
        "Support ticket status transitions, resolution, closure and reopening.",
        "Provide knowledge-base access for self-service support.",
        "Maintain relevant IT asset records.",
        "Allow administrators to manage users, analysts, roles and permissions.",
    ])

    # ===== PAGE 4: Chapter 3 =====
    story += chapter("3. Requirements Elicitation and Analysis", "ch3")
    story.append(P(
        "Requirements were derived from representative stakeholder scenarios, analysis of typical "
        "IT support processes, review of the examination brief, source repository and working "
        "system, use-case analysis and validation against the deployed solution."
    ))
    story.append(P("3.1 Analysed Business Needs", "section"))
    story += bullets([
        "Every support request requires a persistent, uniquely identifiable record and a visible lifecycle state.",
        "Users need progress visibility; support teams need ownership, category and priority.",
        "Communication and investigation history must remain attached to the ticket.",
        "Privileged functions require role/capability restrictions.",
        "Operational data must survive a normal service restart.",
        "The selected workflow must be demonstrable, testable and deployable within the 48-hour examination period.",
    ])
    story.append(P("3.2 Core Ticket Lifecycle", "section"))
    story.append(P(
        "The principal business workflow used to derive and prioritise requirements is Submit "
        "Ticket → Triage → Categorise/Prioritise → Assign → Investigate/Communicate → Resolve → "
        "Close. A closed ticket may be reopened when additional work is required. The lifecycle, "
        "shown in Figure 2, is the primary acceptance path for the examination project."
    ))
    story.append(LifecycleDiagram(height=148))
    story.append(P(
        "Figure 2. Core ICCTECH ticket lifecycle, including the reopen path (Section 3.2).",
        "caption",
    ))

    # ===== PAGE 5: Chapter 4 =====
    story += chapter("4. Functional Requirements", "ch4")
    story.append(P(
        "The following functional requirements form the baseline for implementation and "
        "verification. “Must” requirements are required for the minimum viable examination "
        "workflow; “Should” and “Could” requirements provide supporting capability."
    ))
    story.append(P("Table 1. Functional requirements baseline", "table_caption"))
    fr = [
        ["FR-01", "The system shall allow authorised users to authenticate using supported credentials.", "Must", "User presents credentials and, if valid, enters the authorised workspace."],
        ["FR-02", "The system shall restrict protected functionality according to the authenticated user’s role and capabilities.", "Must", "Unauthorised functions are not accessible; authorised functions remain available."],
        ["FR-03", "An end user shall be able to create a support ticket.", "Must", "A valid ticket submission creates a persistent record."],
        ["FR-04", "A submitted ticket shall receive a unique reference and an initial status.", "Must", "The created ticket displays a unique reference and initial lifecycle state."],
        ["FR-05", "An end user shall be able to view tickets they are authorised to access.", "Must", "Requester can retrieve permitted tickets without gaining access to unauthorised records."],
        ["FR-06", "A support analyst shall be able to view incoming tickets.", "Must", "Authorised analyst can retrieve tickets awaiting support action."],
        ["FR-07", "A support analyst shall be able to categorise and prioritise a ticket.", "Must", "Selected category/priority changes are saved and remain visible after reload."],
        ["FR-08", "A ticket shall be assignable to an appropriate analyst or team where configured.", "Must", "Assignment is saved and visible as ticket ownership."],
        ["FR-09", "Authorised users shall be able to add communication or notes to a ticket.", "Must", "A submitted message/note appears in the ticket record/history."],
        ["FR-10", "A support analyst shall be able to change a ticket’s status.", "Must", "Valid status transition is stored and displayed."],
        ["FR-11", "A support analyst shall be able to record a resolution and close a completed ticket.", "Must", "Resolution details and closed/resolved state are retained."],
        ["FR-12", "A closed ticket shall be able to be reopened where further work is required.", "Must", "Authorised reopen action returns the ticket to an active state and preserves history."],
        ["FR-13", "An administrator shall be able to manage users, analysts, roles and permissions.", "Must", "Administrative changes are permitted only to authorised accounts and are retained."],
        ["FR-14", "Users shall be able to search for and read knowledge articles available to them.", "Should", "Published/authorised knowledge content can be located and opened."],
        ["FR-15", "Authorised staff shall be able to create, view or maintain relevant IT asset records.", "Should", "Permitted asset data can be created/retrieved/updated according to access rights."],
        ["FR-16", "Authorised administrative users shall be able to view relevant audit or operational information.", "Could", "Permitted audit/operational views can be accessed without exposing them to unauthorised users."],
    ]
    story.append(make_table(
        ["ID", "Functional Requirement", "Priority", "Acceptance Summary"],
        fr, [40, W * 0.40, 48, W * 0.60 - 88],
    ))

    # ===== PAGE 6: Chapter 5 =====
    story += chapter("5. Non-Functional Requirements", "ch5")
    story.append(P(
        "The non-functional requirements below define the quality attributes that the delivered "
        "system must satisfy, together with the method used to verify each one."
    ))
    story.append(P("Table 2. Non-functional requirements and verification methods", "table_caption"))
    nfr = [
        ["NFR-01", "Usability", "Core ticket tasks should be understandable without specialist user training.", "Complete representative workflow without specialist instruction."],
        ["NFR-02", "Performance", "Normal pages should respond within approximately three seconds under the expected examination workload, excluding network or hosting delays.", "Representative pages meet the target under the defined test conditions."],
        ["NFR-03", "Security", "Protected functions shall require authentication and role/capability checks.", "Unauthenticated/unauthorised access attempts are denied."],
        ["NFR-04", "Security", "User input shall be validated before processing or persistence where applicable.", "Invalid/unsafe input is rejected or handled without bypassing controls."],
        ["NFR-05", "Security", "User account passwords shall be stored and verified using secure password-hashing mechanisms rather than plaintext storage.", "Authentication uses password hashing/verification mechanisms."],
        ["NFR-06", "Reliability", "Tickets, users, assets and other operational records shall be stored persistently in MySQL.", "Records remain available after reload and normal service restart."],
        ["NFR-07", "Availability", "The deployed application shall remain accessible for evaluation subject to Linode and network availability.", "Live URL responds during verification."],
        ["NFR-08", "Compatibility", "The solution shall operate through modern web browsers in the deployed PHP/MySQL environment.", "Core workflow works in the browser used for final evaluation."],
        ["NFR-09", "Deployability", "The application shall be deployable through Docker Compose to a Linux cloud server.", "Application and database services start and operate in the target environment."],
        ["NFR-10", "Maintainability", "Project configuration, architecture and key implementation decisions shall be documented.", "Submission contains sufficient technical documentation to understand the deployed configuration."],
        ["NFR-11", "Data Persistence", "Operational data, attachments and application keys shall remain available following normal container or service restart through persistent storage.", "Controlled service restart does not remove persisted data/files."],
        ["NFR-12", "Responsiveness", "Core pages should remain usable on desktop and mobile-sized screens.", "Key pages remain readable and operable at representative desktop/mobile viewport sizes."],
    ]
    story.append(make_table(
        ["ID", "Category", "Requirement", "Verification Summary"],
        nfr, [46, 78, W * 0.46, W * 0.54 - 124],
    ))

    # ===== PAGE 7: Chapter 6 =====
    story += chapter("6. External Interface Requirements", "ch6")
    story.append(P("6.1 User Interface", "section"))
    story += bullets([
        "The system shall be accessible through a standard web browser.",
        "Login interfaces shall request appropriate credentials and return clear success/failure behaviour.",
        "End-user interfaces shall provide ticket creation, ticket viewing and knowledge access.",
        "Analyst interfaces shall expose permitted ticket triage, assignment, communication and resolution actions.",
        "Administrator interfaces shall expose user, role, permission and configuration functions according to granted access.",
        "Core pages should remain usable on desktop and mobile-sized screens.",
    ])
    story.append(P("6.2 Software Interfaces", "section"))
    story.append(P("Table 3. Software interface requirements", "table_caption"))
    story.append(make_table(
        ["Interface", "Requirement"],
        [
            ["MySQL 8.0", "The application shall store/retrieve persistent operational data using the configured MySQL database service."],
            ["PDO / pdo_mysql", "PHP shall communicate with MySQL through the configured PDO database-access layer."],
            ["Docker Compose", "The application and database services shall be orchestrated as separate services for deployment."],
            ["Web Server", "Apache shall serve the PHP application within the application container."],
        ],
        [120, W - 120],
    ))
    story.append(P("6.3 Communication Interfaces", "section"))
    story.append(P(
        "Users communicate with the application over HTTP in the examination deployment using "
        "the Linode server and port 8080. HTTPS/TLS is a documented production-hardening "
        "requirement and technical-debt item rather than a completed core requirement for the "
        "current examination deployment."
    ))
    story.append(P("6.4 Hardware Interfaces", "section"))
    story.append(P(
        "No specialised client hardware is required. Users need a network-capable device with a "
        "compatible web browser. The server-side environment requires sufficient CPU, memory and "
        "storage to run the Linux host, application container, MySQL container and persistent volumes."
    ))

    # ===== PAGES 8–10: Chapter 7 =====
    story += chapter("7. Use-Case Specifications", "ch7")
    story.append(P(
        "Each use case below expands the interactions implied by the functional requirements "
        "and identifies the requirements it verifies."
    ))
    story += uc_block("UC-01 – Authenticate User", [
        ("Primary Actor(s)", "End User / Analyst / Administrator"),
        ("Preconditions", "User has an active account."),
        ("Trigger", "User submits valid credentials."),
        ("Main Success Flow", "1. User opens login page.<br/>2. User enters credentials.<br/>3. System validates credentials.<br/>4. System establishes an authorised session.<br/>5. User is directed to the permitted workspace."),
        ("Alternative / Exception Flow", "Invalid credentials are rejected; locked/restricted account remains denied."),
        ("Postconditions", "Authenticated session exists and access is limited by role/capabilities."),
        ("Related Requirements", "FR-01, FR-02; NFR-03, NFR-05"),
    ])
    story += uc_block("UC-02 – Submit Support Ticket", [
        ("Primary Actor(s)", "End User"),
        ("Preconditions", "User is authenticated and has ticket-submission permission."),
        ("Trigger", "User selects the new-ticket function."),
        ("Main Success Flow", "1. User enters required ticket information.<br/>2. System validates input.<br/>3. System creates the ticket.<br/>4. System assigns a unique reference and initial status.<br/>5. System confirms submission."),
        ("Alternative / Exception Flow", "Validation failure prevents invalid submission and prompts correction."),
        ("Postconditions", "Persistent ticket exists and is visible to authorised users."),
        ("Related Requirements", "FR-03, FR-04; NFR-04, NFR-06"),
    ])
    story += uc_block("UC-03 – View and Track Ticket", [
        ("Primary Actor(s)", "End User / Analyst"),
        ("Preconditions", "User is authenticated and authorised for the requested ticket."),
        ("Trigger", "User opens a permitted ticket list or ticket reference."),
        ("Main Success Flow", "1. System checks permission.<br/>2. System retrieves the ticket and related permitted information.<br/>3. System displays status, ownership and communication history."),
        ("Alternative / Exception Flow", "Unauthorised ticket access is denied."),
        ("Postconditions", "User sees the current persistent ticket state."),
        ("Related Requirements", "FR-05, FR-06; FR-02"),
    ])

    story.append(PageBreak())
    story += uc_block("UC-04 – Triage, Prioritise and Assign Ticket", [
        ("Primary Actor(s)", "Analyst / Administrator"),
        ("Preconditions", "Ticket exists; actor has ticket-management capability."),
        ("Trigger", "Actor opens an incoming ticket."),
        ("Main Success Flow", "1. Review request.<br/>2. Select category.<br/>3. Set priority.<br/>4. Assign analyst/team.<br/>5. Save changes.<br/>6. System retains updated ownership and triage data."),
        ("Alternative / Exception Flow", "Invalid or unauthorised changes are rejected."),
        ("Postconditions", "Ticket has a defined category, priority and owner where applicable."),
        ("Related Requirements", "FR-07, FR-08"),
    ])
    story += uc_block("UC-05 – Communicate and Update Ticket", [
        ("Primary Actor(s)", "End User / Analyst / Administrator"),
        ("Preconditions", "Ticket exists and actor has access."),
        ("Trigger", "Actor adds a message/note or analyst changes status."),
        ("Main Success Flow", "1. Actor opens ticket.<br/>2. Actor enters permitted communication/update.<br/>3. System validates and stores it.<br/>4. System displays updated history/status."),
        ("Alternative / Exception Flow", "Unauthorised notes/status changes are denied."),
        ("Postconditions", "Communication/status update is retained in ticket history."),
        ("Related Requirements", "FR-09, FR-10"),
    ])
    story += uc_block("UC-06 – Resolve, Close and Reopen Ticket", [
        ("Primary Actor(s)", "Analyst / Administrator"),
        ("Preconditions", "Ticket exists; actor can resolve/close/reopen."),
        ("Trigger", "Support work is complete or further work becomes necessary."),
        ("Main Success Flow", "1. Analyst records resolution.<br/>2. System stores resolution.<br/>3. Ticket is marked resolved/closed.<br/>4. If further work is required, authorised actor reopens the ticket.<br/>5. System preserves previous history."),
        ("Alternative / Exception Flow", "Invalid status transition or unauthorised action is denied."),
        ("Postconditions", "Ticket reaches the appropriate lifecycle state with history retained."),
        ("Related Requirements", "FR-11, FR-12"),
    ])

    story.append(PageBreak())
    story += uc_block("UC-07 – Manage Users, Roles and Permissions", [
        ("Primary Actor(s)", "Administrator"),
        ("Preconditions", "Administrator is authenticated with required capabilities."),
        ("Trigger", "Administrator opens user/access administration."),
        ("Main Success Flow", "1. Search/create/select account.<br/>2. Modify permitted account/role information.<br/>3. System validates privilege.<br/>4. System saves change."),
        ("Alternative / Exception Flow", "Non-administrator/insufficient capability is denied."),
        ("Postconditions", "Access configuration is updated and enforced."),
        ("Related Requirements", "FR-13, FR-02"),
    ])
    story += uc_block("UC-08 – Search Knowledge Base", [
        ("Primary Actor(s)", "End User / Analyst / Administrator"),
        ("Preconditions", "User has access to the knowledge function."),
        ("Trigger", "User searches or browses knowledge content."),
        ("Main Success Flow", "1. User enters search/browse criteria.<br/>2. System retrieves available articles.<br/>3. User opens an authorised article."),
        ("Alternative / Exception Flow", "Unavailable/unpublished content is not exposed."),
        ("Postconditions", "User reads permitted troubleshooting information."),
        ("Related Requirements", "FR-14"),
    ])
    story += uc_block("UC-09 – Maintain Asset Record", [
        ("Primary Actor(s)", "Authorised Analyst / Administrator"),
        ("Preconditions", "Actor has asset-management permission."),
        ("Trigger", "Actor opens asset function."),
        ("Main Success Flow", "1. Search/create/select asset.<br/>2. Enter or update permitted information.<br/>3. System validates and stores changes.<br/>4. Updated asset record is displayed."),
        ("Alternative / Exception Flow", "Unauthorised modification is denied."),
        ("Postconditions", "Persistent asset information is available to permitted users."),
        ("Related Requirements", "FR-15"),
    ])

    # ===== PAGE 11: Chapter 8 =====
    story += chapter("8. Data, Prioritisation and Acceptance Criteria", "ch8")
    story.append(P("8.1 Data Integrity and Persistence", "section"))
    story.append(P(
        "Tickets, users, analysts, statuses, priorities, communication/notes, audit/system logs, "
        "assets, knowledge and RBAC data must retain referential and access-control integrity. "
        "Unique ticket references must remain unique; permitted state, priority, assignment and "
        "history updates must persist; MySQL-backed operational records and persistent application "
        "data must survive a normal restart."
    ))
    story.append(P("8.2 MoSCoW Baseline", "section"))
    story.append(P(
        f"{b('Must:')} FR-01 to FR-13. {b('Should:')} FR-14 knowledge and FR-15 assets. "
        f"{b('Could:')} FR-16 audit/operational information. {b('Out of scope:')} native mobile "
        "apps, WhatsApp/SMS, full email-to-ticket, production external identity integration, "
        "advanced AI/predictive analytics, large-scale performance testing, enterprise "
        "disaster-recovery automation and non-essential integrations."
    ))
    story.append(P("8.3 Acceptance Criteria", "section"))
    story += bullets([
        "Valid users authenticate; invalid/unauthorised access is denied.",
        "Ticket submission creates a persistent unique-reference record visible to the authorised requester.",
        "Category, priority, ownership, communication and status changes persist.",
        "Resolution/closure is retained and eligible tickets can reopen without losing history.",
        "Authorised administrators can manage access; ordinary accounts cannot perform protected administrative actions.",
        "Knowledge and permitted asset functions are available to authorised users.",
        "Operational data survives normal restart and the live Linode deployment is reachable.",
        "Representative normal pages meet the approximately three-second target and core pages remain usable at desktop/mobile viewport sizes.",
    ])
    story.append(P("8.4 Change Control", "section"))
    story.append(P(
        "After baseline, each proposed change identifies affected FR/NFRs, value, effort, risk "
        "and schedule impact; accepted changes are re-prioritised and require corresponding SRS, "
        "traceability and test updates. Features present in the wider repository are not silently "
        "added to scope."
    ))

    # ===== PAGE 12: Chapter 9 =====
    story += chapter("9. Requirements Traceability and Final Baseline", "ch9")
    story.append(P(
        "The matrix below is the authoritative mapping from each FR/NFR to its stakeholder or "
        "quality concern and verification evidence. The baseline contains 16 functional and 12 "
        "non-functional requirements. Traceability is maintained by keeping requirement identifiers "
        "stable across the SRS, implementation discussion and Testing Report. A change to a "
        "baselined requirement should therefore trigger review of its related design, implementation "
        "and test evidence."
    ))
    story.append(P("Table 4. Requirements traceability matrix", "table_caption"))
    tm = [
        ["FR-01", "Administrator / security", "Must", "TC-01, TC-02"],
        ["FR-02", "Administrator / security", "Must", "TC-02, TC-10"],
        ["FR-03", "End user", "Must", "TC-03"],
        ["FR-04", "End user", "Must", "TC-03"],
        ["FR-05", "End user", "Must", "TC-03 / workflow evidence"],
        ["FR-06", "Support analyst", "Must", "TC-04 / workflow evidence"],
        ["FR-07", "Support analyst", "Must", "TC-04"],
        ["FR-08", "Support analyst", "Must", "TC-05"],
        ["FR-09", "End user", "Must", "TC-06"],
        ["FR-10", "Support analyst", "Must", "TC-07"],
        ["FR-11", "Support analyst", "Must", "TC-08"],
        ["FR-12", "Support analyst", "Must", "TC-09"],
        ["FR-13", "Administrator / security", "Must", "TC-10, TC-11"],
        ["FR-14", "End user", "Should", "TC-12"],
        ["FR-15", "Asset/support operations", "Should", "TC-13"],
        ["FR-16", "Administrator / security", "Could", "Operational/audit evidence"],
        ["NFR-01", "Usability", "Required quality attribute", "UAT / workflow observation"],
        ["NFR-02", "Performance", "Required quality attribute", "TC-16"],
        ["NFR-03", "Security", "Required quality attribute", "TC-02, TC-10"],
        ["NFR-04", "Security", "Required quality attribute", "Input-validation/security checks"],
        ["NFR-05", "Security", "Required quality attribute", "Implementation/security inspection"],
        ["NFR-06", "Reliability", "Required quality attribute", "TC-03, TC-14"],
        ["NFR-07", "Availability", "Required quality attribute", "TC-15"],
        ["NFR-08", "Compatibility", "Required quality attribute", "Browser system test"],
        ["NFR-09", "Deployability", "Required quality attribute", "TC-15"],
        ["NFR-10", "Maintainability", "Required quality attribute", "Documentation review"],
        ["NFR-11", "Data Persistence", "Required quality attribute", "TC-14"],
        ["NFR-12", "Responsiveness", "Required quality attribute", "TC-17"],
    ]
    story.append(make_table(
        ["Requirement", "Source / Concern", "Priority / Type", "Verification Evidence"],
        tm, [70, W * 0.30, 120, W * 0.70 - 190],
    ))
    return story


def main():
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "SRS.pdf"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = BaseDocTemplate(
        out,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH Software Requirements Specification",
        author="Clement Asamoah",
        subject="CSCD602 — Software Requirements Specification (Final Baseline)",
        creator="ICCTECH document production",
    )
    frame = Frame(
        LEFT_MARGIN, BOTTOM_MARGIN, CONTENT_W, CONTENT_H,
        id="normal", showBoundary=0,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=draw_header_footer)])
    doc.build(build_story())
    import pymupdf
    n = pymupdf.open(out).page_count
    print(f"Wrote {out} ({n} pages)")
    if n > 12:
        print("ERROR: document exceeds the 12-page source length.", file=sys.stderr)
        sys.exit(2)
    if n != 12:
        print(f"WARNING: expected 12 pages, got {n}", file=sys.stderr)
    return n


if __name__ == "__main__":
    main()
