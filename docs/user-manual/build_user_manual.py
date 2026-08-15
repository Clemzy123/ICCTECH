#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH User Manual PDF.

Typography: Times New Roman, 12 pt justified body at 1.0 single spacing,
14 pt bold chapter headings on new pages, 1.0 in margins on all sides.
Tables wrap cleanly. Process diagrams are PDF-native vectors.
Black and white only. Target: 6 pages.
"""

from __future__ import annotations

import os
import sys

from reportlab.lib.colors import Color, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.rl_config as rl_config
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

FONT_DIR = "/usr/share/fonts/truetype/liberation"
_FONT_CACHE = os.path.join(os.path.dirname(__file__), ".fontcache")


def _times_face(src_name, family, subfamily, ps_name, out_name):
    from fontTools.ttLib import TTFont as _TT

    os.makedirs(_FONT_CACHE, exist_ok=True)
    dest = os.path.join(_FONT_CACHE, out_name)
    font = _TT(os.path.join(FONT_DIR, src_name))
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
GRAY_FILL = Color(0.96, 0.96, 0.96)
GRAY_MID = Color(0.86, 0.86, 0.86)
GRAY_DARK = Color(0.32, 0.32, 0.32)


def _styles():
    s = {}
    s["body"] = ParagraphStyle(
        "Body", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, spaceAfter=5, textColor=black, splitLongWords=True,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter", fontName="TimesNewRoman-Bold", fontSize=14, leading=17,
        alignment=TA_LEFT, spaceAfter=6, textColor=black, keepWithNext=True,
    )
    s["section"] = ParagraphStyle(
        "Section", fontName="TimesNewRoman-Bold", fontSize=12, leading=14,
        alignment=TA_LEFT, spaceBefore=5, spaceAfter=3, textColor=black, keepWithNext=True,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=4, textColor=black,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="TimesNewRoman", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb", fontName="TimesNewRoman-Bold", fontSize=8, leading=10,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_j"] = ParagraphStyle(
        "TDj", fontName="TimesNewRoman", fontSize=8, leading=10,
        alignment=TA_JUSTIFY, textColor=black,
    )
    s["step"] = ParagraphStyle(
        "Step", fontName="TimesNewRoman", fontSize=12, leading=14,
        alignment=TA_JUSTIFY, leftIndent=16, firstLineIndent=-14,
        spaceBefore=0, spaceAfter=1, textColor=black,
    )
    s["note"] = ParagraphStyle(
        "Note", fontName="TimesNewRoman-Italic", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, textColor=black, spaceBefore=1, spaceAfter=1,
    )
    return s


S = _styles()


def P(text, style="body"):
    return Paragraph(text, S[style] if isinstance(style, str) else style)


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


def make_table(headers, rows, col_widths, first_bold=True):
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for row in rows:
        cells = []
        for i, c in enumerate(row):
            style = S["td_b"] if (first_bold and i == 0) else S["td_j"]
            cells.append(Paragraph(str(c), style))
        data.append(cells)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            cmds.append(("BACKGROUND", (0, r), (-1, r), GRAY_ROW))
    tbl.setStyle(TableStyle(cmds))
    return tbl


def callout(text, width=CONTENT_W):
    inner = Paragraph(text, S["note"])
    tbl = Table([[inner]], colWidths=[width - 10])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GRAY_FILL),
        ("BOX", (0, 0), (-1, -1), 0.7, black),
        ("LINEBEFORE", (0, 0), (0, -1), 3.0, GRAY_HEADER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def _box(c, x, y, w, h, lines, fill=GRAY_FILL, radius=3, tcolor=black, bold=False):
    c.setFillColor(fill)
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.setFillColor(tcolor)
    n = len(lines)
    lh = 8.4
    start = y + h / 2 + (n - 1) * lh / 2 - 2
    for i, line in enumerate(lines):
        name, sz, txt = line if isinstance(line, tuple) else ("TimesNewRoman-Bold" if bold else "TimesNewRoman", 7, line)
        c.setFont(name, sz)
        c.drawCentredString(x + w / 2, start - i * lh, txt)


def _arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setLineWidth(0.8)
    c.line(x1, y1, x2, y2)
    if abs(x2 - x1) >= abs(y2 - y1):
        d = 1 if x2 >= x1 else -1
        c.line(x2, y2, x2 - 5 * d, y2 + 2.5)
        c.line(x2, y2, x2 - 5 * d, y2 - 2.5)
    else:
        d = 1 if y2 >= y1 else -1
        c.line(x2, y2, x2 - 2.5, y2 - 5 * d)
        c.line(x2, y2, x2 + 2.5, y2 - 5 * d)


class RolesDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=196):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        top_w, top_h = 168, 22
        _box(c, (w - top_w) / 2, h - top_h - 2, top_w, top_h, [
            ("TimesNewRoman-Bold", 8, "ICCTECH live application"),
        ], fill=GRAY_HEADER, tcolor=white)
        mid_w, mid_h = 150, 32
        lx = 28
        rx = w - 28 - mid_w
        my = h - 78
        _box(c, lx, my, mid_w, mid_h, [
            ("TimesNewRoman-Bold", 7.5, "Self-service portal"),
            ("TimesNewRoman", 7, "/self-service/login.php"),
        ], fill=GRAY_MID)
        _box(c, rx, my, mid_w, mid_h, [
            ("TimesNewRoman-Bold", 7.5, "Staff / analyst / admin"),
            ("TimesNewRoman", 7, "/login"),
        ], fill=GRAY_ROW)
        top_cx = w / 2
        top_by = h - top_h - 2
        _arrow(c, top_cx - 30, top_by, lx + mid_w / 2, my + mid_h)
        _arrow(c, top_cx + 30, top_by, rx + mid_w / 2, my + mid_h)

        bw, bh = 128, 40
        gap = (w - 3 * bw) / 4
        by = 38
        roles = [
            (GRAY_MID, "End User", "Submit, track, reply,", "search knowledge"),
            (GRAY_FILL, "IT Support Analyst", "Triage, update,", "resolve tickets"),
            (GRAY_ROW, "System Administrator", "Users, roles, config,", "least privilege"),
        ]
        xs = [gap + i * (bw + gap) for i in range(3)]
        for i, (fill, t1, t2, t3) in enumerate(roles):
            _box(c, xs[i], by, bw, bh, [
                ("TimesNewRoman-Bold", 7.5, t1),
                ("TimesNewRoman", 6.8, t2),
                ("TimesNewRoman", 6.8, t3),
            ], fill=fill)
        _arrow(c, lx + mid_w / 2, my, xs[0] + bw / 2, by + bh)
        _arrow(c, rx + mid_w / 2 - 18, my, xs[1] + bw / 2, by + bh)
        _arrow(c, rx + mid_w / 2 + 18, my, xs[2] + bw / 2, by + bh)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(w / 2, 12, "Examiner uses supplied test/admin credentials to verify the deployed workflow.")


class SignInDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=168):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        col_w = (w - 36) / 2
        cols = [
            (8, GRAY_MID, [
                ("End-user sign-in", "self-service/login.php"),
                ("Email or user identifier",),
                ("Password  (+ MFA if enabled)",),
                ("Self-service dashboard",),
            ]),
            (28 + col_w, GRAY_ROW, [
                ("Staff / analyst / administrator", "http://.../login"),
                ("Staff username",),
                ("Password  (+ MFA if enabled)",),
                ("Module landing page",),
            ]),
        ]
        for x, head_fill, steps in cols:
            hy = h - 36
            _box(c, x, hy, col_w, 32, [
                ("TimesNewRoman-Bold", 7.5, steps[0][0]),
                ("TimesNewRoman", 7, steps[0][1]),
            ], fill=head_fill)
            prev = hy
            for i, step in enumerate(steps[1:]):
                y = hy - 36 - i * 36
                _box(c, x + 18, y, col_w - 36, 24, [
                    ("TimesNewRoman", 7.2, step[0]),
                ])
                _arrow(c, x + col_w / 2, prev, x + col_w / 2, y + 24)
                prev = y


class TicketProcess(Flowable):
    def __init__(self, width=CONTENT_W, height=92):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        labels = [
            (GRAY_MID, ["Dashboard"]),
            (GRAY_FILL, ["New Ticket"]),
            (GRAY_FILL, ["Subject &", "description"]),
            (GRAY_FILL, ["Priority &", "attachments"]),
            (GRAY_FILL, ["Submit"]),
            (GRAY_MID, ["Track &", "reply"]),
        ]
        n = len(labels)
        bw = (w - 10 - (n - 1) * 14) / n
        y = 28
        for i, (fill, lines) in enumerate(labels):
            x = 5 + i * (bw + 14)
            _box(c, x, y, bw, 38, [
                ("TimesNewRoman-Bold" if len(lines) == 1 else "TimesNewRoman", 7, t) for t in lines
            ], fill=fill)
            if i < n - 1:
                _arrow(c, x + bw, y + 19, x + bw + 14, y + 19)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(w / 2, 10, "Optional first: search Knowledge / Help Centre before opening a new ticket.")


class TriageDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=118):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        steps = [
            ["Open ticket", "read subject,", "files"],
            ["Classify", "category /", "queue"],
            ["Prioritise", "urgency and", "impact"],
            ["Assign", "analyst or", "team"],
            ["Update status", "next stage", "of work"],
        ]
        n = len(steps)
        bw = (w - 10 - (n - 1) * 12) / n
        y = 52
        for i, lines in enumerate(steps):
            x = 5 + i * (bw + 12)
            _box(c, x, y, bw, 44, [
                ("TimesNewRoman-Bold", 7, lines[0]),
                ("TimesNewRoman", 6.6, lines[1]),
                ("TimesNewRoman", 6.6, lines[2]),
            ])
            if i < n - 1:
                _arrow(c, x + bw, y + 22, x + bw + 12, y + 22)
        _box(c, 5, 6, w - 10, 36, [
            ("TimesNewRoman", 7, "Triage confirms that the request has enough information, an appropriate classification,"),
            ("TimesNewRoman", 7, "established urgency and clear ownership before investigation proceeds."),
        ], fill=GRAY_FILL)


class LifecycleDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=132):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        top = [
            ["Open /", "Awaiting Triage"],
            ["Assigned", "ownership set"],
            ["In Progress", "active work"],
            ["On Hold /", "Awaiting Response"],
        ]
        n = 4
        bw = (w - 16 - (n - 1) * 16) / n
        ty = h - 48
        xs = []
        for i, lines in enumerate(top):
            x = 8 + i * (bw + 16)
            xs.append(x)
            fill = GRAY_ROW if i == 3 else GRAY_FILL
            _box(c, x, ty, bw, 36, [
                ("TimesNewRoman-Bold", 7, lines[0]),
                ("TimesNewRoman", 6.6, lines[1]),
            ], fill=fill)
            if i < 2:
                _arrow(c, x + bw, ty + 18, x + bw + 16, ty + 18)
        # bidirectional In Progress <-> On Hold
        x2, x3 = xs[2], xs[3]
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.line(x2 + bw, ty + 24, x3, ty + 24)
        c.line(x3, ty + 12, x2 + bw, ty + 12)
        c.line(x3, ty + 24, x3 - 5, ty + 26.5)
        c.line(x3, ty + 24, x3 - 5, ty + 21.5)
        c.line(x2 + bw, ty + 12, x2 + bw + 5, ty + 14.5)
        c.line(x2 + bw, ty + 12, x2 + bw + 5, ty + 9.5)

        bot_w = 118
        rx = w / 2 - bot_w - 18
        cx = w / 2 + 18
        by = 18
        _box(c, rx, by, bot_w, 36, [
            ("TimesNewRoman-Bold", 7.5, "Resolved"),
            ("TimesNewRoman", 6.6, "solution recorded"),
        ], fill=GRAY_MID)
        _box(c, cx, by, bot_w, 36, [
            ("TimesNewRoman-Bold", 7.5, "Closed"),
            ("TimesNewRoman", 6.6, "process complete"),
        ], fill=GRAY_HEADER, tcolor=white)
        _arrow(c, xs[2] + bw / 2, ty, rx + bot_w / 2, by + 36)
        _arrow(c, rx + bot_w, by + 18, cx, by + 18)
        # reopen loop
        c.setStrokeColor(black)
        c.setLineWidth(0.8)
        c.line(rx, by + 18, 8, by + 18)
        c.line(8, by + 18, 8, ty + 18)
        _arrow(c, 8, ty + 18, xs[0], ty + 18)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 6.5)
        c.drawString(12, by + 28, "Reopen if further")
        c.drawString(12, by + 20, "work is required")


class PrivilegeDiagram(Flowable):
    def __init__(self, width=CONTENT_W, height=118):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        tw = 200
        _box(c, (w - tw) / 2, h - 24, tw, 20, [
            ("TimesNewRoman-Bold", 8, "Principle of least privilege"),
        ], fill=GRAY_HEADER, tcolor=white)
        roles = [
            (GRAY_MID, "End User", "No analyst or", "admin functions"),
            (GRAY_FILL, "Analyst", "Tickets and supporting", "functions for the role"),
            (GRAY_ROW, "Administrator", "Trusted accounts only;", "verify with a test login"),
        ]
        bw = (w - 36) / 3
        y = 28
        for i, (fill, t1, t2, t3) in enumerate(roles):
            x = 6 + i * (bw + 12)
            _box(c, x, y, bw, 44, [
                ("TimesNewRoman-Bold", 7.5, t1),
                ("TimesNewRoman", 6.8, t2),
                ("TimesNewRoman", 6.8, t3),
            ], fill=fill)
            _arrow(c, w / 2, h - 24, x + bw / 2, y + 44)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(w / 2, 10, "After changing roles or permissions, verify the result using a test account.")


class AssetFlow(Flowable):
    def __init__(self, width=CONTENT_W, height=88):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        steps = [
            (GRAY_FILL, ["Open Asset", "Management"]),
            (GRAY_FILL, ["Search /", "select asset"]),
            (GRAY_FILL, ["View record", "(tag, status,", "location)"]),
            (GRAY_ROW, ["Update", "authorised fields"]),
            (GRAY_ROW, ["Assign to user", "(+ return date)"]),
        ]
        n = len(steps)
        bw = (w - 10 - (n - 1) * 12) / n
        y = 26
        for i, (fill, lines) in enumerate(steps):
            x = 5 + i * (bw + 12)
            packed = [("TimesNewRoman-Bold" if i == 0 else "TimesNewRoman", 6.8, t) for i, t in enumerate(lines)]
            _box(c, x, y, bw, 42, packed, fill=fill)
            if i < n - 1:
                _arrow(c, x + bw, y + 21, x + bw + 12, y + 21)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(w / 2, 8, "Only authorised staff should modify ownership, status or custody information.")


class DemoWorkflow(Flowable):
    def __init__(self, width=CONTENT_W, height=188):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        cells = [
            (GRAY_MID, "1  End User", "Sign in to self-service"),
            (GRAY_MID, "2  End User", "Create a support ticket"),
            (GRAY_FILL, "3  Analyst", "Open the new ticket"),
            (GRAY_FILL, "4  Analyst", "Categorise, prioritise, assign"),
            (GRAY_FILL, "5  Analyst", "Add an update"),
            (GRAY_MID, "6  End User", "Reply through self-service"),
            (GRAY_FILL, "7  Analyst", "Record resolution"),
            (GRAY_FILL, "8  Analyst", "Close the ticket"),
            (GRAY_ROW, "9  Administrator", "Verify role restriction"),
        ]
        bw = (w - 28) / 3
        bh = 36
        gap_x, gap_y = 14, 18
        boxes = []
        for i, (fill, t1, t2) in enumerate(cells):
            col, row = i % 3, i // 3
            x = 0 + col * (bw + gap_x)
            y = h - 8 - (row + 1) * bh - row * gap_y
            _box(c, x, y, bw, bh, [
                ("TimesNewRoman-Bold", 7.5, t1),
                ("TimesNewRoman", 7, t2),
            ], fill=fill)
            boxes.append((x, y, bw, bh))
        # 1→2→3, wrap to 4; 4→5→6, wrap to 7; 7→8→9
        pairs = [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8)]
        for a, b in pairs:
            ax, ay, aw, ah = boxes[a]
            bx, by, bw_, bh_ = boxes[b]
            _arrow(c, ax + aw, ay + ah / 2, bx, by + bh_ / 2)
        for a, b in [(2, 3), (5, 6)]:
            ax, ay, aw, ah = boxes[a]
            bx, by, bw_, bh_ = boxes[b]
            mid_y = (ay + by + bh_) / 2
            c.setStrokeColor(black)
            c.setFillColor(black)
            c.setLineWidth(0.8)
            c.line(ax + aw / 2, ay, ax + aw / 2, mid_y)
            c.line(ax + aw / 2, mid_y, bx + bw_ / 2, mid_y)
            _arrow(c, bx + bw_ / 2, mid_y, bx + bw_ / 2, by + bh_)
        c.setFillColor(black)
        c.setFont("TimesNewRoman", 7)
        c.drawCentredString(w / 2, 6, "Recommended quick demonstration of the examination scope.")


class VerifySequence(Flowable):
    def __init__(self, width=CONTENT_W, height=128):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        left = [
            "Verification sequence",
            "1. Confirm site reachable",
            "2. End-user self-service sign-in",
            "3. Create demonstration ticket",
            "4. Sign out; analyst/admin sign-in",
            "5. Locate ticket; set priority; assign",
        ]
        right = [
            "(continued)",
            "6. Add analyst response; update status",
            "7. End-user sees response/status",
            "8. Record resolution and close",
            "9. Open Knowledge and Assets",
            "10. Confirm restricted admin action",
        ]
        bw = (w - 36) / 2
        for x, lines, head_fill in ((4, left, GRAY_HEADER), (32 + bw, right, GRAY_DARK)):
            c.setFillColor(GRAY_FILL)
            c.setStrokeColor(black)
            c.setLineWidth(0.7)
            c.roundRect(x, 4, bw, h - 8, 4, fill=1, stroke=1)
            c.setFillColor(head_fill)
            c.rect(x, h - 26, bw, 18, fill=1, stroke=1)
            c.setFillColor(white)
            c.setFont("TimesNewRoman-Bold", 8)
            c.drawCentredString(x + bw / 2, h - 20, lines[0])
            c.setFillColor(black)
            c.setFont("TimesNewRoman", 7.4)
            for i, line in enumerate(lines[1:]):
                c.drawCentredString(x + bw / 2, h - 42 - i * 13, line)
        _arrow(c, 4 + bw, h / 2, 32 + bw, h / 2)


def draw_header_footer(canv, doc):
    canv.saveState()
    canv.setFillColor(black)
    canv.setStrokeColor(black)
    canv.setFont("TimesNewRoman-Italic", 8)
    canv.drawString(LEFT_MARGIN, PAGE_H - 0.62 * inch, "ICCTECH — User Manual")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 0.62 * inch, "CSCD602 | University of Ghana")
    canv.setLineWidth(0.6)
    canv.line(LEFT_MARGIN, PAGE_H - 0.72 * inch, PAGE_W - RIGHT_MARGIN, PAGE_H - 0.72 * inch)
    canv.line(LEFT_MARGIN, 0.62 * inch, PAGE_W - RIGHT_MARGIN, 0.62 * inch)
    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, 0.42 * inch, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, 0.42 * inch, f"Page {doc.page}")
    canv.restoreState()


def chapter(title, key, first=False):
    items = []
    if not first:
        items.append(PageBreak())
    items.append(Bookmark(key, title, 0))
    items.append(P(title, "chapter"))
    return items


def fig(flowable, caption):
    return KeepTogether([flowable, P(caption, "caption")])


def steps(items):
    return [Paragraph(f"{i}.  {text}", S["step"]) for i, text in enumerate(items, 1)]


def build_story():
    story = []
    W = CONTENT_W

    # ===== PAGE 1 =====
    story += chapter("1. Access, Roles and Sign-In", "ch1", first=True)
    story.append(P(
        "This condensed manual covers the complete ICCTECH examination workflow for end users, "
        "IT support analysts, system administrators and the examiner. It focuses on authentication, "
        "ticket handling, role-based access, knowledge, assets and evaluation support."
    ))
    story.append(P("Table 1. Access information", "caption"))
    story.append(make_table(
        ["Purpose", "Address / Source"],
        [
            ["Live application", "http://45.79.223.146:8080/index.php"],
            ["Staff / analyst / administrator sign-in", "http://45.79.223.146:8080/login"],
            ["End-user self-service sign-in", "http://45.79.223.146:8080/self-service/login.php"],
            ["Source repository", "https://github.com/Clemzy123/ICCTECH"],
            ["Credentials", "Use the accounts listed in Deployment_and_Source_Links.txt supplied with the examination package."],
        ],
        [190, W - 190],
    ))
    story.append(Spacer(1, 6))
    story.append(callout(
        "<b>Security note.</b> Do not place examiner passwords or production credentials in the "
        "public GitHub repository. The submission package contains the credentials separately in "
        "Deployment_and_Source_Links.txt."
    ))
    story.append(Spacer(1, 8))
    story.append(fig(RolesDiagram(), "Figure 1. ICCTECH user roles and access portals"))
    story.append(P("Role responsibilities", "section"))
    story.append(P(
        f"<b>End User:</b> submit, track and reply to tickets and use published knowledge.  "
        f"<b>IT Support Analyst:</b> triage, categorise, prioritise, assign, investigate, update, "
        f"resolve and reopen tickets.  <b>System Administrator:</b> manage users, roles, permissions "
        f"and essential configuration under least privilege."
    ))

    # ===== PAGE 2 =====
    story += chapter("2. Getting Started and End-User Self-Service", "ch2")
    story.append(fig(SignInDiagram(), "Figure 2. Staff and end-user sign-in paths"))
    story.append(P("Sign-in and sign-out", "section"))
    story.append(P(
        "Staff/analyst/administrator: open /login, enter the supplied username and password, then "
        "provide the MFA verification code when enabled. End user: open /self-service/login.php, "
        "enter the configured email/user identifier and password, and complete MFA when prompted. "
        "Always sign out on shared devices."
    ))
    story.append(fig(TicketProcess(), "Figure 3. End-user support-ticket process"))
    story.append(P("End-user ticket procedure", "section"))
    story += steps([
        "Select New Ticket and enter a clear subject and description.",
        "Select the relevant queue/category and priority; attach useful evidence when required.",
        "Submit and retain the generated ticket reference.",
        "Open Your Tickets to review status, priority, ownership and history.",
        "Reply through the ticket record when more information is requested.",
        "Search Knowledge / Help Centre before or during ticket handling when appropriate.",
    ])

    # ===== PAGE 3 =====
    story += chapter("3. IT Support Analyst Workflow", "ch3")
    story.append(fig(TriageDiagram(), "Figure 4. Analyst triage sequence"))
    story.append(P("Triage, priority and communication", "section"))
    story.append(P(
        "Open the incoming ticket, review the subject/description/attachments, confirm the category "
        "or queue, set High/Normal/Low priority according to impact and urgency, assign the "
        "appropriate analyst or team, and record investigation notes or requester-facing responses "
        "in the ticket history."
    ))
    story.append(P("Table 2. Typical ticket status meanings", "caption"))
    story.append(make_table(
        ["Typical status", "Meaning"],
        [
            ["Open / Awaiting Triage", "Ticket has been received and requires review."],
            ["Assigned", "Ownership has been established."],
            ["In Progress", "An analyst is actively investigating or working on the request."],
            ["On Hold / Awaiting Response", "Further action depends on information, an external dependency or the requester."],
            ["Resolved", "A solution has been recorded and the issue is considered fixed."],
            ["Closed", "The support process is complete."],
        ],
        [150, W - 150],
    ))
    story.append(Spacer(1, 6))
    story.append(fig(LifecycleDiagram(), "Figure 5. Typical ticket status lifecycle"))

    # ===== PAGE 4 =====
    story += chapter("4. Administration, Knowledge and Asset Management", "ch4")
    story.append(fig(PrivilegeDiagram(), "Figure 6. Role-based access and least privilege"))
    story.append(P("Administrator controls", "section"))
    story.append(P(
        "Use the Administration/System area to create or update users/analysts, assign "
        "roles/teams/capabilities and verify access using an appropriate test account. Grant only "
        "the minimum permissions required. Use unique passwords, enable MFA where configured, "
        "disable unused test accounts and review privileges periodically."
    ))
    story.append(P("Knowledge Base", "section"))
    story.append(P(
        "Search the Help Centre / Knowledge area using relevant keywords, open authorised articles "
        "and follow documented troubleshooting. Authorised knowledge managers may maintain content "
        "according to their assigned capabilities. If self-service does not resolve the issue, "
        "create or continue a support ticket."
    ))
    story.append(fig(AssetFlow(), "Figure 7. Asset view, update and assignment flow"))
    story.append(P("Asset procedure", "section"))
    story.append(P(
        "Locate the asset record, review identifying and operational information, update only "
        "authorised fields, and use Assign to link the asset to a user (including a return date "
        "where required). Verify that the saved value or assigned user is displayed correctly."
    ))

    # ===== PAGE 5 =====
    story += chapter("5. End-to-End Workflow and Examiner Verification", "ch5")
    story.append(fig(DemoWorkflow(), "Figure 8. Core end-to-end demonstration workflow"))
    story.append(Spacer(1, 6))
    story.append(fig(VerifySequence(), "Figure 9. Examiner quick-verification sequence"))
    story.append(P("Verification outcome", "section"))
    story.append(P(
        "The sequence above verifies site reachability, end-user ticket creation, analyst "
        "triage/assignment/communication, requester visibility, resolution/closure, Knowledge and "
        "Asset access, and denial of a restricted administrative action to an account without the "
        "required capability."
    ))

    # ===== PAGE 6 =====
    story += chapter("6. Troubleshooting, Security and Responsible Use", "ch6")
    story.append(P("Table 3. Troubleshooting", "caption"))
    story.append(make_table(
        ["Problem", "Recommended action"],
        [
            ["Live page does not open", "Confirm the URL and internet connection. Retry after a short period. If the application remains unavailable, verify Linode/server and Docker service status."],
            ["Login rejected", "Check the username/email and password in Deployment_and_Source_Links.txt. Confirm the correct portal is being used. Do not repeatedly guess passwords."],
            ["MFA prompt appears", "Enter the current verification code for the configured account. If the examiner account was not intended to use MFA, use the supplied alternative test account."],
            ["A module is missing", "Module visibility is role-based. Confirm that the signed-in account has permission for that module."],
            ["Cannot perform an administrative action", "The account may not have the required capability. Verify the assigned role rather than attempting to bypass access controls."],
            ["Ticket update does not appear", "Refresh/reopen the ticket and confirm that the save/send operation succeeded. Check for an error message before retrying."],
            ["Database-related error", "Confirm MySQL service availability and application database connectivity. Production database access should remain restricted to authorised administrators."],
            ["Uploaded file fails", "Confirm that the file type/size is accepted by the application and that storage permissions are available."],
            ["Slow response", "Retry the page and confirm server/network conditions. Persistent performance problems should be recorded for maintenance investigation."],
        ],
        [140, W - 140],
    ))
    story.append(P("During evaluation", "section"))
    story.append(P(
        "If a problem occurs during grading, record the exact page, action performed, time, visible "
        "error message and account role. This helps distinguish a user-access issue from an "
        "application, database or hosting issue."
    ))
    story.append(P("Security and responsible use", "section"))
    story.append(P(
        "Use only the accounts and permissions supplied for evaluation. Do not publish credentials, "
        "reuse database/server credentials as application passwords, bypass role controls or expose "
        "database/server secrets. Sign out after testing on shared devices and avoid entering "
        "unnecessary sensitive information into demonstration records. The current examination "
        "deployment uses HTTP; HTTPS, stronger secret management, database hardening, backups and "
        "monitoring remain production-hardening items documented in the Technical Debt Plan."
    ))
    story.append(P("Reference", "section"))
    story.append(P(
        "Live application: http://45.79.223.146:8080/index.php &nbsp;|&nbsp; "
        "Repository: https://github.com/Clemzy123/ICCTECH &nbsp;|&nbsp; "
        "Credentials: Deployment_and_Source_Links.txt in the submission package."
    ))
    return story


def main():
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "User_Manual.pdf"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = BaseDocTemplate(
        out,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH User Manual",
        author="Clement Asamoah",
        subject="CSCD602 — User Manual",
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
    if n > 6:
        print("ERROR: document exceeds the 6-page source length.", file=sys.stderr)
        sys.exit(2)
    if n != 6:
        print(f"WARNING: expected 6 pages, got {n}", file=sys.stderr)
    return n


if __name__ == "__main__":
    main()
