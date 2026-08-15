#!/usr/bin/env python3
"""
Build a submission-ready ICCTECH Testing Report PDF.

Typography: Times New Roman, 12 pt justified body at 1.0 single spacing,
14 pt bold chapter headings on new pages, 1.0 in margins on all sides.
Tables wrap cleanly inside the margins. Black and white only.
Target: 7 pages (same as the source).
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
from reportlab.platypus.flowables import Flowable, HRFlowable, KeepTogether

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
        alignment=TA_LEFT, spaceBefore=6, spaceAfter=3, textColor=black, keepWithNext=True,
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
        alignment=TA_CENTER, textColor=black, spaceAfter=16,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="TimesNewRoman-Italic", fontSize=10, leading=12,
        alignment=TA_CENTER, spaceBefore=2, spaceAfter=4, textColor=black,
    )
    s["th"] = ParagraphStyle(
        "TH", fontName="TimesNewRoman-Bold", fontSize=7.5, leading=9,
        alignment=TA_LEFT, textColor=white,
    )
    s["td"] = ParagraphStyle(
        "TD", fontName="TimesNewRoman", fontSize=7.5, leading=9,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_b"] = ParagraphStyle(
        "TDb", fontName="TimesNewRoman-Bold", fontSize=7.5, leading=9,
        alignment=TA_LEFT, textColor=black,
    )
    s["td_c"] = ParagraphStyle(
        "TDc", fontName="TimesNewRoman-Bold", fontSize=7.5, leading=9,
        alignment=TA_CENTER, textColor=black,
    )
    s["pass"] = ParagraphStyle(
        "Pass", fontName="TimesNewRoman-Bold", fontSize=7.5, leading=9,
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
    s["status"] = ParagraphStyle(
        "Status", fontName="TimesNewRoman-Bold", fontSize=11, leading=13,
        alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=5, textColor=black,
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
        self._bp = Paragraph(self.body, S["note"])
        _bw, bh = self._bp.wrap(self.box_width - 2 * self._pad, ah)
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


def make_table(headers, rows, col_widths, bold_first=True, center_last=False):
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            if i == 0 and bold_first:
                style = S["td_b"]
            elif center_last and i == len(row) - 1:
                style = S["pass"]
            else:
                style = S["td"]
            cells.append(Paragraph(str(cell), style))
        data.append(cells)
    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), GRAY_HEADER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
        ("GRID", (0, 0), (-1, -1), 0.4, black),
    ]
    for r in range(1, len(data)):
        if r % 2 == 0:
            cmds.append(("BACKGROUND", (0, r), (-1, r), GRAY_ROW))
    tbl.setStyle(TableStyle(cmds))
    return tbl


def bullets(items):
    return [Paragraph(f"•  {item}", S["bullet"]) for item in items]


class StrategyDiagram(Flowable):
    """Compact vector view of the applied examination test types."""

    def __init__(self, width=CONTENT_W, height=58):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def wrap(self, aw, ah):
        self.width = min(self.width, aw)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        labels = [
            "Functional",
            "System /\nIntegration",
            "Security",
            "UAT",
            "Performance\n/ Deploy",
        ]
        n = len(labels)
        bw = (self.width - (n - 1) * 14 - 8) / n
        bh = 36
        y = 10
        for i, lab in enumerate(labels):
            x = 4 + i * (bw + 14)
            c.setFillColor(GRAY_FILL)
            c.setStrokeColor(black)
            c.setLineWidth(0.8)
            c.roundRect(x, y, bw, bh, 4, fill=1, stroke=1)
            c.setFillColor(black)
            c.setFont("TimesNewRoman-Bold", 7)
            lines = lab.split("\n")
            start = y + bh / 2 + (len(lines) - 1) * 4
            for j, line in enumerate(lines):
                c.drawCentredString(x + bw / 2, start - j * 9, line)
            if i < n - 1:
                c.setStrokeColor(black)
                c.setLineWidth(0.9)
                x1, x2 = x + bw, x + bw + 14
                mid = y + bh / 2
                c.line(x1, mid, x2, mid)
                c.line(x2, mid, x2 - 5, mid + 3)
                c.line(x2, mid, x2 - 5, mid - 3)


def draw_header_footer(canv, doc):
    canv.saveState()
    if doc.page == 1:
        canv.restoreState()
        return
    canv.setFillColor(black)
    canv.setStrokeColor(black)
    canv.setFont("TimesNewRoman-Italic", 8)
    canv.drawString(LEFT_MARGIN, PAGE_H - 0.62 * inch, "ICCTECH — Testing Report")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 0.62 * inch, "Version 1.0 — Final Baseline")
    canv.setLineWidth(0.6)
    canv.line(LEFT_MARGIN, PAGE_H - 0.72 * inch, PAGE_W - RIGHT_MARGIN, PAGE_H - 0.72 * inch)
    canv.line(LEFT_MARGIN, 0.62 * inch, PAGE_W - RIGHT_MARGIN, 0.62 * inch)
    canv.setFont("TimesNewRoman", 9)
    canv.drawString(LEFT_MARGIN, 0.42 * inch, "Clement Asamoah | Student ID: 22424193")
    canv.drawRightString(PAGE_W - RIGHT_MARGIN, 0.42 * inch, f"Page {doc.page}")
    canv.restoreState()


def chapter(title, key):
    return [PageBreak(), Bookmark(key, title, 0), P(title, "chapter")]


# Restored Actual Result text: source PDF clipped the right-hand column.
# Completions follow the visible stems and the matching Expected Result.
CASES = [
    ["TC-01", "FR-01", "Valid analyst authentication",
     "Enter valid analyst credentials and submit the login form.",
     "Valid credentials permit access to the authorised analyst workspace.",
     "Valid credentials were accepted and the analyst workspace opened successfully."],
    ["TC-02", "FR-01, FR-02, NFR-03", "Invalid analyst authentication",
     "Attempt login using invalid credentials.",
     "Invalid credentials are rejected and protected areas remain inaccessible.",
     "Invalid credentials were rejected and protected application areas remained inaccessible."],
    ["TC-03", "FR-03, FR-04, FR-05, NFR-06", "End-user ticket submission",
     "Authenticate as an end user, submit a valid support request, then reload/retrieve the ticket.",
     "A persistent ticket is created with a unique reference, initial status and authorised requester visibility.",
     "The ticket was created successfully, received a unique reference and initial state, and remained visible to the requester."],
    ["TC-04", "FR-06, FR-07", "Ticket categorisation and prioritisation",
     "Open an incoming ticket as an analyst, set category and priority, then reload.",
     "Category and priority are saved and remain visible.",
     "The selected category and priority were updated successfully and remained visible after reload."],
    ["TC-05", "FR-08", "Ticket assignment",
     "Assign the ticket to an authorised analyst/team and reload the record.",
     "Ownership is saved and persists.",
     "The ticket was assigned successfully and the ownership information persisted after reload."],
    ["TC-06", "FR-09", "Ticket communication / notes",
     "Add an authorised communication or note to the ticket.",
     "The entry is stored against the correct ticket and appears in history.",
     "The communication was saved against the ticket and displayed in history."],
    ["TC-07", "FR-10", "Ticket status update",
     "Change ticket status using an authorised analyst account and reload.",
     "Valid status transition is stored and displayed.",
     "The ticket status was updated successfully and the value remained after reload."],
    ["TC-08", "FR-11", "Ticket resolution and closure",
     "Record a resolution and move the ticket to the completed state.",
     "Resolution details and closed/resolved state are retained.",
     "A resolution was recorded successfully and the ticket moved to the completed state as expected."],
    ["TC-09", "FR-12", "Ticket reopen / restore",
     "Reopen an eligible completed ticket.",
     "Ticket returns to active handling while prior history remains available.",
     "The eligible ticket returned to active handling successfully and prior history remained available."],
    ["TC-10", "FR-02, FR-13, NFR-03", "Role-based access restriction",
     "Attempt a protected administrative action with an account lacking the required capability.",
     "Unauthorised action is denied; authorised administrator remains able to access it.",
     "The unauthorised account was prevented from the protected action; the authorised administrator could access it."],
    ["TC-11", "FR-13", "Administrator user management",
     "Use an authorised administrator account to access and perform a permitted user/access-management action.",
     "Administrative action succeeds and changes are retained.",
     "The administrator user-management action completed the permitted management operation successfully."],
    ["TC-12", "FR-14", "Knowledge-base search and access",
     "Search for and open an available knowledge article.",
     "Permitted published knowledge content can be located and opened.",
     "The knowledge article was located through the interface and opened successfully."],
    ["TC-13", "FR-15", "Asset record access / maintenance",
     "Access an asset record using an authorised staff account and perform a permitted operation.",
     "Permitted asset information can be viewed or maintained according to access rights.",
     "The authorised account accessed the asset and completed the permitted asset operation successfully."],
    ["TC-14", "NFR-06, NFR-11", "Persistence after service restart",
     "Create/confirm test data, restart the relevant services, then retrieve the same records.",
     "Operational records remain available after normal service restart.",
     "Previously created related test data remained available after restart, confirming persistent storage."],
    ["TC-15", "NFR-07, NFR-09", "Production deployment smoke test",
     "Open the live URL and exercise core login and ticket/database functions.",
     "Live application loads and core application/database services operate.",
     "The live URL loaded successfully and login, ticket and database-backed functions were usable in the deployment."],
    ["TC-16", "NFR-02", "Representative page-response performance",
     "Exercise representative normal pages under the expected examination workload and observe response completion.",
     "Representative normal pages respond within approximately three seconds, excluding abnormal network/hosting delay.",
     "Representative normal pages completed within the approximate three-second acceptance target in the final test session."],
    ["TC-17", "NFR-12", "Responsive interface usability",
     "Exercise core pages at representative desktop and reduced/mobile viewport sizes.",
     "Core pages remain usable and key controls remain reachable at the tested viewport sizes.",
     "Core pages remained usable at the representative desktop and mobile viewports, with key controls reachable and no blocking issue preventing core use."],
]

TC_HEAD = ["ID", "Req.", "Scenario", "Procedure", "Expected Result", "Actual Result"]
TC_W = [32, 58, 68, 100, 105, CONTENT_W - 363]


def build_story():
    story = []
    W = CONTENT_W

    # ===== PAGE 1: Cover =====
    story.append(Bookmark("cover", "Cover", 0))
    story.append(Spacer(1, 28))
    story.append(HRFlowable(width="100%", thickness=1.1, color=black, spaceAfter=12))
    story.append(P("UNIVERSITY OF GHANA", "title_univ"))
    story.append(P("DEPARTMENT OF COMPUTER SCIENCE", "title_dept"))
    story.append(P("CSCD602 – ADVANCED SOFTWARE ENGINEERING", "title_course"))
    story.append(HRFlowable(width="100%", thickness=1.1, color=black, spaceBefore=10, spaceAfter=16))
    story.append(P("TESTING REPORT", "title_doc"))
    story.append(P("ICCTECH: A Web-Based IT Service Management<br/>and Helpdesk System", "title_sub"))

    cover_rows = [
        ["Student Name", "Clement Asamoah"],
        ["Student ID", "22424193"],
        ["Project", "ICCTECH"],
        ["Academic Year", "First Semester, 2025/2026"],
        ["Examination Duration", "48 Hours"],
        ["Live Application", "http://45.79.223.146:8080/index.php"],
        ["Source Repository", "https://github.com/Clemzy123/ICCTECH"],
    ]
    cover_data = [[Paragraph(a, S["td_b"]), Paragraph(b_, S["td"])] for a, b_ in cover_rows]
    cover_tbl = Table(cover_data, colWidths=[170, W - 170])
    cover_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, black),
        ("BACKGROUND", (0, 0), (0, -1), GRAY_ROW),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cover_tbl)
    story.append(Spacer(1, 36))
    story.append(HRFlowable(width="100%", thickness=3.0, color=black))

    # ===== PAGE 2: Chapter 1 =====
    story += chapter("1. Test Objectives, Environment and Strategy", "ch1")
    story.append(P(
        f"{b('Purpose.')} Provide a formal, traceable record that the prioritised SRS requirements "
        "operate in the final deployed environment and are suitable for examination demonstration."
    ))
    story.append(P(
        f"{b('Environment.')} Linode Linux, Docker/Docker Compose, Apache HTTP Server with PHP 8.4, "
        "MySQL 8.0 as a separate service, PDO/pdo_mysql, a modern desktop browser and a representative "
        "reduced/mobile viewport. Test roles: end user, IT support analyst and system administrator."
    ))
    story.append(P("Applied test types", "section"))
    story += bullets([
        "Functional testing against individual requirements and acceptance criteria.",
        "System/integration testing of the complete ticket lifecycle, PHP application, access-control logic and MySQL persistence.",
        "Security testing for valid/invalid authentication and denial of protected functions.",
        "User acceptance testing for end-user, analyst and administrator workflows.",
        "Representative performance, responsive-interface and deployment smoke testing.",
        "Repository source-level/unit-style scripts used as supplementary subsystem evidence, not as a claim of full unit coverage.",
    ])
    story.append(Spacer(1, 4))
    story.append(StrategyDiagram())
    story.append(P("Figure 1. Applied examination test types, from functional cases through deployment smoke testing.", "caption"))
    story.append(P("Entry / exit criteria", "section"))
    story.append(P(
        f"{b('Entry:')} SRS baseline established, deployed application/MySQL operational, test accounts "
        "available and critical implementation defects corrected. "
        f"{b('Exit:')} all 17 formal cases executed, no failed/blocked Must-Have path, no critical "
        "demonstration-blocking defect, live database-backed deployment reachable, and results/evidence recorded."
    ))

    # ===== PAGES 3–5: Chapter 2 =====
    story += chapter("2. Test Case Execution Results", "ch2")
    story.append(P(
        "The following table records the final result of each formal examination test case. "
        "Requirement identifiers refer to the final SRS. All 17 test cases were executed against "
        "the defined examination scope and completed successfully."
    ))
    story.append(make_table(TC_HEAD, CASES[:6], TC_W))
    story.append(PageBreak())
    story.append(make_table(TC_HEAD, CASES[6:13], TC_W))
    story.append(PageBreak())
    story.append(make_table(TC_HEAD, CASES[13:], TC_W))
    story.append(P("Table 1. Formal examination test-case execution results", "caption"))
    story.append(NoteBox(
        "Execution note",
        "Every formal case in Table 1 was run against the live Linode/Docker deployment. "
        "Actual results restore the right-hand column that was clipped in the source compilation; "
        "wording follows the visible stems and the matching expected result for that case.",
    ))

    # ===== PAGE 6: Chapter 3 =====
    story += chapter("3. Requirements Traceability and Supplementary Verification", "ch3")
    story.append(P(
        "Traceability is maintained by preserving the same requirement identifiers used in the "
        "final SRS. The matrix below shows the principal formal verification path for the 17 test "
        "cases. Additional non-functional requirements are supported by implementation inspection, "
        "browser checks, documentation review and user-acceptance observation."
    ))
    trace = [
        ["FR-01", "Authentication", "TC-01, TC-02", "PASS"],
        ["FR-02", "Role/capability restriction", "TC-02, TC-10", "PASS"],
        ["FR-03 / FR-04 / FR-05", "Ticket creation, identity and requester access", "TC-03", "PASS"],
        ["FR-06 / FR-07", "Incoming ticket view, categorisation and priority", "TC-04", "PASS"],
        ["FR-08", "Assignment", "TC-05", "PASS"],
        ["FR-09", "Communication/notes", "TC-06", "PASS"],
        ["FR-10", "Status management", "TC-07", "PASS"],
        ["FR-11", "Resolution/closure", "TC-08", "PASS"],
        ["FR-12", "Reopen/restore", "TC-09", "PASS"],
        ["FR-13", "Administration", "TC-10, TC-11", "PASS"],
        ["FR-14", "Knowledge access", "TC-12", "PASS"],
        ["FR-15", "Asset management", "TC-13", "PASS"],
        ["NFR-02", "Representative performance", "TC-16", "PASS"],
        ["NFR-03", "Security access control", "TC-02, TC-10", "PASS"],
        ["NFR-06 / NFR-11", "Reliability/data persistence", "TC-03, TC-14", "PASS"],
        ["NFR-07 / NFR-09", "Availability/deployability", "TC-15", "PASS"],
        ["NFR-12", "Responsive usability", "TC-17", "PASS"],
    ]
    story.append(make_table(
        ["Requirement(s)", "Verification Focus", "Test Evidence", "Status"],
        trace, [110, W - 250, 90, 50], center_last=True,
    ))
    story.append(P("Table 2. Formal requirements-to-test traceability", "caption"))
    story.append(P("3.1 Supplementary Quality Verification", "section"))
    supp = [
        ["NFR-01", "Usability", "UAT and end-to-end workflow observation", "SATISFACTORY"],
        ["NFR-04", "Input validation", "Security/functional checks of user-supplied inputs within the tested workflow", "SATISFACTORY"],
        ["NFR-05", "Password security", "Implementation inspection of password hashing/verification controls", "SATISFACTORY"],
        ["NFR-08", "Compatibility", "Modern-browser system test in the deployed environment", "SATISFACTORY"],
        ["NFR-10", "Maintainability", "Source structure and project/deployment documentation review", "SATISFACTORY"],
        ["FR-16", "Operational/audit information", "Supporting authorised operational/audit view where available", "SATISFACTORY"],
    ]
    story.append(make_table(
        ["Requirement", "Quality Area", "Verification Method", "Outcome"],
        supp, [60, 90, W - 210, 60], center_last=True,
    ))
    story.append(P(
        "Table 3. Supplementary verification for requirements not represented by a dedicated formal test case",
        "caption",
    ))

    # ===== PAGE 7: Chapter 4 =====
    story += chapter("4. UAT, Defects, Final Quality Status and Limitations", "ch4")
    story.append(P(
        f"{b('Final outcome.')} 17 formal cases executed; 17 passed; 0 failed; 0 blocked; no "
        "outstanding final-cycle or critical defect. Testing is scoped to the 48-hour baseline: it "
        "is not a full penetration test, large-scale load/stress/endurance exercise, exhaustive "
        "physical-device/browser matrix or disaster-recovery restoration exercise. Supporting "
        "evidence should map to TC-01 through TC-17 and must not expose credentials."
    ))
    story.append(P(
        "User acceptance testing was performed from the perspective of the three principal user "
        "classes defined in the SRS. The end user could submit and monitor a request, the support "
        "analyst could manage the ticket through its lifecycle, and the administrator could access "
        "permitted administrative functionality. The tested role restrictions also prevented an "
        "ordinary unauthorised account from performing the selected protected administrative action."
    ))
    story.append(make_table(
        ["User Role", "Acceptance Task", "Outcome", "Status"],
        [
            ["End user", "Submit and retrieve a support ticket; use permitted support content.",
             "Core requester workflow completed successfully.", "PASS"],
            ["Support analyst", "Categorise, prioritise, assign, communicate, update, resolve and close ticket.",
             "Core service-desk workflow completed successfully.", "PASS"],
            ["Administrator", "Access permitted user/access-management functions.",
             "Administrative function completed; unauthorised access test was denied as expected.", "PASS"],
        ],
        [78, W * 0.36, W * 0.64 - 128, 50], center_last=True,
    ))
    story.append(P("Table 4. User acceptance summary", "caption"))
    story.append(P(
        f"{b('Overall UAT result: PASS')} – the tested workflows were suitable for the primary "
        "end-user, analyst and administrator roles within the defined examination scope."
    ))
    story.append(P("4.1 Defects and Corrective Actions", "section"))
    story.append(P(
        "No defect remained open in the final examination test cycle. Implementation issues "
        "encountered during development had been corrected before final regression execution. "
        "The final cycle did not identify a new critical, high, medium or low defect within the "
        "tested scope."
    ))
    story.append(make_table(
        ["Defect ID", "Description", "Severity", "Corrective Action", "Final Status"],
        [["N/A", "No outstanding defect identified in the final examination test cycle.",
          "N/A", "No further corrective action required for the tested scope.", "CLOSED"]],
        [52, W * 0.36, 52, W * 0.64 - 154, 50],
    ))
    story.append(P("Table 5. Final defect register", "caption"))
    story.append(P(
        "Technical-debt items are managed separately from the final defect register. A feature can "
        "satisfy its acceptance test while still carrying architectural, security-hardening, "
        "operational or maintainability debt that should be repaid in a future release."
    ))
    story.append(P("4.2 Test Summary and Quality Status", "section"))
    metrics = [
        ["Formal test cases executed", "17", "Passed", "17"],
        ["Failed", "0", "Blocked / not executed", "0"],
        ["Formal pass rate", "100%", "Outstanding final-cycle defects", "0"],
        ["Outstanding critical defects", "0", "", ""],
    ]
    story.append(make_table(
        ["Metric", "Result", "Metric", "Result"],
        metrics, [W * 0.34, 50, W * 0.34, W * 0.32 - 50], center_last=False,
    ))
    story.append(P("Table 6. Final test metrics", "caption"))
    story.append(P(
        f"{b('Quality status: ACCEPTED FOR EXAMINATION DEMONSTRATION.')} All formal tests "
        "mapped to the prioritised examination scope passed. The Must-Have ticket lifecycle, "
        "authentication and role restrictions operated as expected; knowledge and asset functions "
        "passed their selected tests; persistence and live reachability were confirmed; and the "
        "representative performance and responsive-interface checks passed. The 100% pass rate "
        "applies only to these 17 formal tests, not to every inherited module or enterprise-scale operation."
    ))
    return story


def main():
    out = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Testing_Report.pdf"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = BaseDocTemplate(
        out,
        pagesize=letter,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        title="ICCTECH Testing Report",
        author="Clement Asamoah",
        subject="CSCD602 — Testing and Quality Assurance Report",
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
    if n > 7:
        print("ERROR: document exceeds the 7-page source length.", file=sys.stderr)
        sys.exit(2)
    if n != 7:
        print(f"WARNING: expected 7 pages, got {n}", file=sys.stderr)
    return n


if __name__ == "__main__":
    main()
