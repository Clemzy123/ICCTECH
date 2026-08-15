#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH Technical Debt Plan PDF.

Typography: Times New Roman, 12 pt justified body at 1.0 single spacing,
14 pt bold chapter headings on new pages, 1.0 in margins on all sides.
Tables wrap cleanly. Architecture, classification, roadmap and governance
diagrams are PDF-native vectors. Black and white only. Target: 6 pages.
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
    s["tdtitle"] = ParagraphStyle(
        "TDTitle", fontName="TimesNewRoman-Bold", fontSize=10, leading=12,
        alignment=TA_LEFT, spaceBefore=4, spaceAfter=2, textColor=black, keepWithNext=True,
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
        "TitleCourse", fontName="TimesNewRoman", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=black, spaceAfter=2,
    )
    s["title_doc"] = ParagraphStyle(
        "TitleDoc", fontName="TimesNewRoman-Bold", fontSize=18, leading=22,
        alignment=TA_CENTER, textColor=black, spaceBefore=10, spaceAfter=6,
    )
    s["title_sub"] = ParagraphStyle(
        "TitleSub", fontName="TimesNewRoman-Bold", fontSize=12, leading=15,
        alignment=TA_CENTER, textColor=black, spaceAfter=14,
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
    s["bullet"] = ParagraphStyle(
        "Bullet", fontName="TimesNewRoman", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, leftIndent=14, bulletIndent=4,
        spaceBefore=0, spaceAfter=1, textColor=black,
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


def make_table(headers, rows, col_widths):
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), S["td_j"] if i else S["td_b"]) for i, c in enumerate(row)])
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


def debt_card(title, pairs, width=CONTENT_W):
    data = []
    for lab, val in pairs:
        data.append([Paragraph(lab, S["th"]), Paragraph(val, S["td_j"])])
    tbl = Table(data, colWidths=[92, width - 92])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), GRAY_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.4),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
    ]))
    return [P(title, "tdtitle"), tbl]


def bullets(items):
    return [Paragraph(f"•  {item}", S["bullet"]) for item in items]


def _box(c, x, y, w, h, lines, fill=GRAY_FILL, radius=3, tcolor=black, bold=False):
    c.setFillColor(fill)
    c.setStrokeColor(black)
    c.setLineWidth(0.7)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    c.setFillColor(tcolor)
    n = len(lines)
    lh = 8.5
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


class IdentifyDiagram(Flowable):
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
        src = [
            "Source code and\nconfiguration",
            "Deployment\narchitecture",
            "Testing and\ntraceability",
            "Security\nhardening",
            "Maintainability\nand naming",
            "Operations and\nresilience",
        ]
        bw, bh = (w - 20) / 3 - 6, 28
        for i, lab in enumerate(src):
            col, row = i % 3, i // 3
            x = 10 + col * (bw + 10)
            y = h - 8 - (row + 1) * (bh + 6)
            _box(c, x, y, bw, bh, lab.split("\n"))
        chain = ["Debt", "Cause", "Impact", "Priority", "Resolution"]
        cw = (w - 40) / 5
        cy = 46
        for i, lab in enumerate(chain):
            x = 8 + i * (cw + 6)
            _box(c, x, cy, cw - 2, 20, [lab], bold=True)
            if i < 4:
                _arrow(c, x + cw - 2, cy + 10, x + cw + 6, cy + 10)
        _arrow(c, w / 2, h - 8 - 2 * (bh + 6), w / 2, cy + 20)
        _box(c, 8, 6, w - 16, 28, [
            ("TimesNewRoman-Bold", 8, "Technical Debt Register (TD-01 to TD-09)"),
            ("TimesNewRoman", 7, "Classification, target timeframe and source evidence recorded so repayment is tracked"),
        ], fill=GRAY_HEADER, tcolor=white)
        _arrow(c, w / 2, cy, w / 2, 34)


class ClassDiagram(Flowable):
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
        rows = [
            (0.46, "CRITICAL / IMMEDIATE", "Resolve before long-term public / production operation"),
            (0.70, "HIGH / SCHEDULED", "Schedule into production hardening or first maintenance release"),
            (0.94, "MEDIUM / MANAGED", "Temporarily acceptable; maintainability, resilience, scalability"),
        ]
        y = h - 4
        for frac, title, sub in rows:
            bw = w * frac
            x = (w - bw) / 2
            bh = 26
            y -= bh + 3
            fill = GRAY_HEADER if title.startswith("CRITICAL") else (GRAY_ROW if title.startswith("HIGH") else GRAY_FILL)
            tc = white if title.startswith("CRITICAL") else black
            _box(c, x, y, bw, bh, [
                ("TimesNewRoman-Bold", 7.5, title),
                ("TimesNewRoman", 6.5, sub),
            ], fill=fill, tcolor=tc)


class CurrentArch(Flowable):
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
        _box(c, w / 2 - 90, h - 22, 180, 18, ["Internet / examiner clients"], bold=True)
        c.setFont("TimesNewRoman-Italic", 7)
        c.setFillColor(black)
        c.drawCentredString(w / 2, h - 34, "HTTP :8080 (TD-02 — no TLS)")
        _arrow(c, w / 2, h - 22, w / 2, h - 42)
        c.setStrokeColor(black)
        c.setLineWidth(1.0)
        c.setFillColor(white)
        c.roundRect(8, 22, w - 16, h - 66, 4, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman-Bold", 8)
        c.drawCentredString(w / 2, h - 54, "Linode VPS — single host (TD-07: single point of failure)")
        c.setDash(2, 2)
        c.roundRect(18, 48, w - 36, h - 108, 3, fill=0, stroke=1)
        c.setDash()
        c.setFont("TimesNewRoman-Italic", 7)
        c.drawString(24, h - 70, "Docker Compose")
        _box(c, 28, 78, 170, 36, [
            ("TimesNewRoman-Bold", 7, "PHP application"),
            ("TimesNewRoman", 6.5, "ICCTECH / FreeITSM"),
            ("TimesNewRoman", 6.5, "port 8080"),
        ])
        _box(c, 230, 78, 150, 36, [
            ("TimesNewRoman-Bold", 7, "MySQL 8"),
            ("TimesNewRoman", 6.5, "container :3306"),
            ("TimesNewRoman", 6.5, "volume persist"),
        ])
        _arrow(c, 198, 96, 230, 96)
        _box(c, 28, 52, 200, 20, ["Default / development credentials in Compose (TD-01)"])
        _box(c, 300, 36, 150, 28, [
            ("TimesNewRoman-Bold", 7, "Host port 3307 published"),
            ("TimesNewRoman", 6.5, "(TD-03) attack surface"),
        ])
        _arrow(c, 305, 78, 360, 64)
        c.setFont("TimesNewRoman", 6.5)
        c.drawCentredString(w / 2, 8, "No independent off-host backup (TD-05)  ·  Limited monitoring/alerting (TD-06)  ·  No CI workflow (TD-04)")


class TargetArch(Flowable):
    def __init__(self, width=CONTENT_W, height=158):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        _box(c, w / 2 - 70, h - 20, 140, 16, ["Internet / clients"], bold=True)
        c.setFont("TimesNewRoman-Italic", 7)
        c.drawCentredString(w / 2, h - 32, "HTTPS :443 (TD-02 repaid)")
        _arrow(c, w / 2, h - 20, w / 2, h - 40)
        c.setStrokeColor(black)
        c.setFillColor(white)
        c.setLineWidth(1.0)
        c.roundRect(8, 6, w - 16, h - 48, 4, fill=1, stroke=1)
        c.setFillColor(black)
        c.setFont("TimesNewRoman-Bold", 7.5)
        c.drawCentredString(w / 2, h - 52, "Hardened production host — secrets externalised, TLS terminated, DB internal")
        boxes = [
            (18, 78, 140, 36, ["Reverse proxy", "TLS certificate", "HTTP → HTTPS"]),
            (170, 78, 140, 36, ["PHP application", "internal network", "no public secrets"]),
            (322, 78, 128, 36, ["MySQL", "internal only", "no host :3307"]),
        ]
        for x, y, bw, bh, lines in boxes:
            _box(c, x, y, bw, bh, [
                ("TimesNewRoman-Bold", 7, lines[0]),
                ("TimesNewRoman", 6.5, lines[1]),
                ("TimesNewRoman", 6.5, lines[2]),
            ])
        _arrow(c, 158, 96, 170, 96)
        _arrow(c, 310, 96, 322, 96)
        low = [
            (18, 18, 140, 44, ["Secrets (TD-01)", "env / Docker secrets", "not in source control"]),
            (170, 18, 140, 44, ["Off-host backups (TD-05)", "scheduled + restore test", "independent of VPS"]),
            (322, 18, 128, 44, ["Monitoring (TD-06)", "uptime, host, DB", "TLS expiry alerts"]),
        ]
        for x, y, bw, bh, lines in low:
            _box(c, x, y, bw, bh, [
                ("TimesNewRoman-Bold", 7, lines[0]),
                ("TimesNewRoman", 6.5, lines[1]),
                ("TimesNewRoman", 6.5, lines[2]),
            ])


class Roadmap(Flowable):
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
        phases = [
            ("Phase 1", "Immediate / pre-production", ["TD-01 credentials", "TD-02 HTTPS", "TD-03 DB port", "TD-09 freeze release"]),
            ("Phase 2", "First maintenance", ["TD-04 tests + CI", "TD-05 off-host backup", "TD-06 monitoring"]),
            ("Phase 3", "Future evolution", ["TD-07 split / HA", "TD-08 naming"]),
        ]
        bw = (w - 36) / 3
        for i, (ph, sub, items) in enumerate(phases):
            x = 6 + i * (bw + 12)
            c.setFillColor(GRAY_FILL)
            c.setStrokeColor(black)
            c.roundRect(x, 22, bw, h - 28, 4, fill=1, stroke=1)
            c.setFillColor(GRAY_HEADER)
            c.rect(x, h - 28, bw, 22, fill=1, stroke=1)
            c.setFillColor(white)
            c.setFont("TimesNewRoman-Bold", 8)
            c.drawCentredString(x + bw / 2, h - 16, ph)
            c.setFillColor(black)
            c.setFont("TimesNewRoman-Italic", 7)
            c.drawCentredString(x + bw / 2, h - 40, sub)
            c.setFont("TimesNewRoman", 7)
            for j, it in enumerate(items):
                c.drawString(x + 8, h - 56 - j * 11, "•  " + it)
            if i < 2:
                _arrow(c, x + bw, 22 + (h - 28) / 2, x + bw + 12, 22 + (h - 28) / 2)
        c.setFont("TimesNewRoman", 6.5)
        c.drawCentredString(w / 2, 8, "Exit: secrets + TLS + restricted DB + frozen release  →  CI + backup/restore + alerts  →  HA + naming")


class Governance(Flowable):
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
        cx, cy = w / 2, h / 2
        nodes = [
            (cx, h - 22, "1. Review open items", "confirm impact & priority"),
            (w - 70, h - 48, "2. Record new debt", "from impl. / test / deploy"),
            (w - 70, 28, "3. Identify repaid debt", "retain resolution evidence"),
            (cx, 14, "4. Re-prioritise", "security, reliability, delay"),
            (70, 28, "5. Protect critical debt", "do not defer security"),
            (70, h - 48, "6. Update artefacts", "roadmap, notes, docs"),
        ]
        _box(c, cx - 78, cy - 18, 156, 36, [
            ("TimesNewRoman-Bold", 7, "Debt register"),
            ("TimesNewRoman", 6.5, "reviewed each release"),
            ("TimesNewRoman", 6.5, "and on major change"),
        ], fill=GRAY_HEADER, tcolor=white)
        for x, y, t1, t2 in nodes:
            _box(c, x - 62, y - 14, 124, 28, [
                ("TimesNewRoman-Bold", 6.5, t1),
                ("TimesNewRoman", 6, t2),
            ])
            _arrow(c, cx, cy, x, y)


class TestVsDebt(Flowable):
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
        bw = (w - 20) / 2
        _box(c, 4, 28, bw, h - 32, [
            ("TimesNewRoman-Bold", 8, "Functional testing"),
            ("TimesNewRoman", 7, "Do the defined requirements"),
            ("TimesNewRoman", 7, "behave as expected?"),
            ("TimesNewRoman-Italic", 7, "Example: login tests pass"),
        ])
        _box(c, 16 + bw, 28, bw, h - 32, [
            ("TimesNewRoman-Bold", 8, "Technical-debt management"),
            ("TimesNewRoman", 7, "Is the solution hardened,"),
            ("TimesNewRoman", 7, "maintainable, recoverable?"),
            ("TimesNewRoman-Italic", 7, "Example: HTTPS still required"),
        ])
        c.setFont("TimesNewRoman-Bold", 7)
        c.setFillColor(black)
        c.drawCentredString(w / 2, 14, "A 100% pass rate for selected functional tests can coexist with open debt items.")
        c.setFont("TimesNewRoman-Italic", 6.5)
        c.drawCentredString(w / 2, 4, "Acceptance testing ≠ elimination of engineering risk.")


def draw_header_footer(canv, doc):
    canv.saveState()
    if doc.page == 1:
        canv.restoreState()
        return
    canv.setFillColor(black)
    canv.setStrokeColor(black)
    canv.setFont("TimesNewRoman-Italic", 8)
    canv.drawString(LEFT_MARGIN, PAGE_H - 0.62 * inch, "ICCTECH — Technical Debt Plan")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 0.62 * inch, "CSCD602 | University of Ghana")
    canv.setLineWidth(0.6)
    canv.line(LEFT_MARGIN, PAGE_H - 0.72 * inch, PAGE_W - RIGHT_MARGIN, PAGE_H - 0.72 * inch)
    canv.line(LEFT_MARGIN, 0.62 * inch, PAGE_W - RIGHT_MARGIN, 0.62 * inch)
    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, 0.42 * inch, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, 0.42 * inch, f"Page {doc.page}")
    canv.restoreState()


def chapter(title, key):
    return [PageBreak(), Bookmark(key, title, 0), P(title, "chapter")]


def td(title, debt, cause, impact, priority, classification, resolution, target, evidence):
    return debt_card(title, [
        ("Debt", debt),
        ("Cause", cause),
        ("Impact", impact),
        ("Priority", priority),
        ("Classification", classification),
        ("Proposed Resolution", resolution),
        ("Target", target),
        ("Source Evidence", evidence),
    ])


def build_story():
    story = []
    W = CONTENT_W

    # ===== PAGE 1: Cover =====
    story.append(Bookmark("cover", "Cover", 0))
    story.append(Spacer(1, 26))
    story.append(HRFlowable(width="100%", thickness=1.1, color=black, spaceAfter=12))
    story.append(P("UNIVERSITY OF GHANA", "title_univ"))
    story.append(P("DEPARTMENT OF COMPUTER SCIENCE", "title_dept"))
    story.append(P("CSCD602 — ADVANCED SOFTWARE ENGINEERING", "title_course"))
    story.append(HRFlowable(width="100%", thickness=1.1, color=black, spaceBefore=10, spaceAfter=16))
    story.append(P("TECHNICAL DEBT PLAN", "title_doc"))
    story.append(P("ICCTECH: A Web-Based IT Service Management<br/>and Helpdesk System", "title_sub"))
    cover = [
        ["Student Name", "Clement Asamoah"],
        ["Student ID", "22424193"],
        ["Project", "ICCTECH"],
        ["Academic Year", "First Semester, 2025/2026"],
        ["Live Application", "http://45.79.223.146:8080/index.php"],
        ["Source Repository", "https://github.com/Clemzy123/ICCTECH"],
    ]
    data = [[Paragraph(a, S["td_b"]), Paragraph(b_, S["td"])] for a, b_ in cover]
    tbl = Table(data, colWidths=[170, W - 170])
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, black),
        ("BACKGROUND", (0, 0), (0, -1), GRAY_ROW),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 36))
    story.append(HRFlowable(width="100%", thickness=3.0, color=black))

    # ===== PAGE 2: Chapter 1 =====
    story += chapter("1. Technical Debt Management Approach", "ch1")
    story.append(P(
        "Technical debt is treated as a visible engineering obligation rather than hidden unfinished "
        "work. Items are identified from source/configuration, deployment, testing/traceability, "
        "security, maintainability and operational-resilience review. Each record retains Debt → "
        "Cause → Impact → Priority → Proposed Resolution, plus classification, target and evidence."
    ))
    story.append(P("1.1 Identification Sources", "section"))
    story += bullets([
        "Source-code and configuration review, including Docker and database configuration.",
        "Deployment architecture review of the Linode-hosted environment.",
        "Testing and requirements traceability review.",
        "Security-hardening review of authentication, transport and network exposure.",
        "Maintainability review of internal naming, automation and release traceability.",
        "Operational review of backup, monitoring, resilience and future scaling needs.",
    ])
    story.append(IdentifyDiagram())
    story.append(P("Figure 1. Technical debt identification and recording process", "caption"))
    story.append(P("1.2 Priority and Classification", "section"))
    story.append(make_table(
        ["Classification", "Meaning", "Treatment"],
        [
            ["Critical / Immediate", "Creates unacceptable security or release risk for continued production use.", "Resolve before long-term public/production operation."],
            ["High / Scheduled", "Does not prevent examination demonstration but materially affects security, reliability or regression confidence.", "Schedule into production hardening or first maintenance release."],
            ["Medium / Managed", "Acceptable temporarily under the examination scope but affects maintainability, resilience or future scalability.", "Document, review each release and repay according to operational need."],
        ],
        [110, W * 0.46, W * 0.54 - 110],
    ))
    story.append(P("Table 1. Technical debt classification model", "caption"))
    story.append(ClassDiagram())
    story.append(P("Figure 2. Technical debt classification model", "caption"))

    # ===== PAGE 3: Chapter 2 =====
    story += chapter("2. Current Deployment Debt and Immediate Hardening", "ch2")
    story.append(CurrentArch())
    story.append(P(
        "Figure 3. Current ICCTECH deployment architecture and associated debt (TD-01, TD-02, TD-03, TD-07; TD-04/05/06 noted)",
        "caption",
    ))
    story += td(
        "TD-01 — Development/default credentials in Docker configuration",
        "Development/default credentials remain in Docker configuration.",
        "Rapid reproducible Docker setup.",
        "Public reuse can expose credentials and enable unauthorised database access.",
        "Critical", "Immediate resolution",
        "Rotate credentials; move production secrets to protected environment or Docker secrets.",
        "Before continued public/production use",
        "Compose declares database credential variables.",
    )
    story += td(
        "TD-02 — HTTP rather than HTTPS",
        "The live deployment currently uses HTTP.",
        "The IP:8080 deployment was completed without TLS.",
        "Authentication and application traffic is unencrypted in transit.",
        "Critical", "Immediate resolution",
        "Add a domain or reverse proxy, trusted TLS and HTTP-to-HTTPS redirect.",
        "Before long-term production use",
        "The live URL uses HTTP on port 8080.",
    )
    story += td(
        "TD-03 — Published MySQL host port",
        "The Compose deployment publishes the MySQL host port.",
        "Simplified development and direct database administration.",
        "Published database access increases the attack surface.",
        "High", "Production hardening",
        "Remove the public mapping; use the internal Docker network, an SSH tunnel or a restricted firewall.",
        "Before hardened production use",
        "Compose maps host 3307 to MySQL 3306.",
    )

    # ===== PAGE 4: Chapter 3 =====
    story += chapter("3. Regression, Recovery and Observability Debt", "ch3")
    story.append(TargetArch())
    story.append(P(
        "Figure 4. Target production-hardened architecture after repayment of TD-01, TD-02, TD-03, TD-05 and TD-06",
        "caption",
    ))
    story += td(
        "TD-04 — Limited project-specific regression automation / CI",
        "Requirements-mapped automated regression and CI are limited.",
        "The 48-hour scope prioritised the core workflow; no mapped CI suite is demonstrated.",
        "Future changes may create regressions detected late or only manually.",
        "High", "Scheduled for next release",
        "Automate mapped authentication, RBAC, ticket and persistence tests and add CI.",
        "First maintenance release",
        "tests/ exists; no CI workflow is demonstrated.",
    )
    story += td(
        "TD-05 — No automated independent off-host backup / restore",
        "No demonstrated automated off-host backup and restore process.",
        "Examination scope focused on persistence, not disaster-recovery automation.",
        "Volumes do not protect against host loss, corruption or destructive change.",
        "High", "Scheduled for next release",
        "Schedule off-host MySQL backups with retention/protection and restore tests.",
        "First maintenance release",
        "Volumes exist; no off-host restore workflow is demonstrated.",
    )
    story += td(
        "TD-06 — Limited production monitoring / alerts",
        "Production monitoring and automated alerting are limited.",
        "Effort focused on functionality, testing and deployment, not observability.",
        "Application, database, container or host failures may be noticed only after user reports.",
        "Medium", "Scheduled",
        "Add uptime, host/container/database metrics, alerts and TLS-expiry checks.",
        "Subsequent maintenance release",
        "No project production monitoring or alerting is demonstrated.",
    )

    # ===== PAGE 5: Chapter 4 =====
    story += chapter("4. Resilience, Naming and Release-Traceability Debt", "ch4")
    story.append(Roadmap())
    story.append(P("Figure 5. Technical debt repayment roadmap", "caption"))
    story.append(P(
        "Figure 5 presents the repayment sequence as a visual roadmap. Each phase must meet its "
        "exit condition before the next phase is treated as complete."
    ))
    story += td(
        "TD-07 — Single-host application and database",
        "Application and database share one Linode host.",
        "Single-server Docker was simplest for the examination.",
        "Single point of failure; limited high availability and horizontal scaling.",
        "Medium", "Temporarily acceptable / future evolution",
        "When justified, separate workloads; add a managed or replicated database, health checks and load balancing.",
        "Future production evolution",
        "Application and MySQL run on one Linode host.",
    )
    story += td(
        "TD-08 — Legacy/upstream internal naming",
        "Legacy/upstream identifiers remain in configuration and resources.",
        "Broad 48-hour renaming would add regression risk.",
        "Legacy names reduce maintainability and naming consistency.",
        "Medium", "Managed / scheduled refactoring",
        "Refactor incrementally with regression tests; preserve attribution and licences.",
        "Future refactoring releases",
        "FreeITSM identifiers remain in configuration and paths.",
    )
    story += td(
        "TD-09 — Documentation/evidence release drift",
        "Documentation and evidence can drift from the deployed release.",
        "Source, documents, screenshots and tests were produced rapidly in one window.",
        "Revision mismatch weakens traceability and can confuse examination evidence.",
        "Medium", "Resolve before submission",
        "Freeze or tag the final build; verify evidence against it; avoid untracked changes.",
        "Before final Sakai submission",
        "Traceability depends on the final repository and deployed state.",
    )

    # ===== PAGE 6: Chapter 5 =====
    story += chapter("5. Repayment Roadmap, Governance and Relationship to Testing", "ch5")
    story.append(P(
        f"{b('Repayment order.')} Immediate/pre-production: TD-01, TD-02, TD-03 and TD-09. "
        "First maintenance release: TD-04, TD-05 and TD-06. Future evolution: TD-07 and TD-08. "
        "A debt item is repaid only when the resolution is implemented and verified — for example, "
        "backup debt closes only after an independent backup is successfully restored."
    ))
    story.append(Governance())
    story.append(P("Figure 6. Review, governance and change-control cycle", "caption"))
    story.append(P(
        "The register is reviewed at each release or major architecture/security change. Critical "
        "security debt takes precedence over new features. High-priority reliability and "
        "test-automation debt is planned into the next release cycle. Medium-priority debt is ranked "
        "using user impact, operational risk, implementation effort and the likelihood that the debt "
        "will become more expensive to repay later."
    ))
    story.append(TestVsDebt())
    story.append(P("Figure 7. Functional testing versus technical-debt management", "caption"))
    story.append(P(
        "Functional acceptance and technical debt answer different questions: all selected tests may "
        "pass while hardening, recoverability, observability or scalability debt remains open. A login "
        "function may pass authentication tests while the deployment still requires HTTPS; ticket "
        "persistence may survive service restart while independent disaster-recovery backup remains "
        "future work (TD-05). Successful acceptance testing is not complete elimination of engineering risk."
    ))
    return story


def main():
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Technical_Debt_Plan.pdf"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = BaseDocTemplate(
        out,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH Technical Debt Plan",
        author="Clement Asamoah",
        subject="CSCD602 — Technical Debt Plan",
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
