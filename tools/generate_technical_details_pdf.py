#!/usr/bin/env python3
"""Generate the technical-details PDF for the longest increasing run."""

from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "Documents" / "Longest-Increasing-Run-Technical-Details.pdf"
FONT_DIR = Path(r"C:\Windows\Fonts")

pdfmetrics.registerFont(TTFont("Segoe", str(FONT_DIR / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Bold", str(FONT_DIR / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-Italic", str(FONT_DIR / "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("Segoe-BoldItalic", str(FONT_DIR / "segoeuiz.ttf")))
pdfmetrics.registerFontFamily(
    "Segoe",
    normal="Segoe",
    bold="Segoe-Bold",
    italic="Segoe-Italic",
    boldItalic="Segoe-BoldItalic",
)
pdfmetrics.registerFont(TTFont("Consolas", str(FONT_DIR / "consola.ttf")))
pdfmetrics.registerFont(TTFont("Consolas-Bold", str(FONT_DIR / "consolab.ttf")))

INK = HexColor("#1C2421")
MUTED = HexColor("#3E4C48")
FAINT = HexColor("#5E6E69")
LINE = HexColor("#D5DED9")
TEAL = HexColor("#14302C")
TEAL_MID = HexColor("#1F4A44")
TEAL_SOFT = HexColor("#E5F0ED")
CREAM = HexColor("#F7F4EE")
GOLD = HexColor("#8C6A32")
GOLD_SOFT = HexColor("#F4EBD9")
CLAY = HexColor("#8A4B1F")
CLAY_SOFT = HexColor("#F6E6DA")
PAPER = HexColor("#F4F7F5")
WHITE = white

PAGE_W, PAGE_H = A4
LEFT = 16 * mm
RIGHT = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT


def styles() -> dict[str, ParagraphStyle]:
    return {
        "h1": ParagraphStyle(
            "h1",
            fontName="Segoe-Bold",
            fontSize=18,
            leading=22,
            textColor=TEAL,
            spaceAfter=4,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Segoe-Bold",
            fontSize=13,
            leading=16,
            textColor=TEAL,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="Segoe-Bold",
            fontSize=11,
            leading=14,
            textColor=TEAL_MID,
            spaceBefore=6,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Segoe",
            fontSize=9.5,
            leading=13,
            textColor=INK,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Segoe",
            fontSize=9.5,
            leading=12.5,
            textColor=INK,
            leftIndent=12,
            bulletIndent=0,
            spaceAfter=1,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Segoe-Italic",
            fontSize=8,
            leading=10.5,
            textColor=MUTED,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Consolas",
            fontSize=8.5,
            leading=11,
            textColor=INK,
        ),
        "th": ParagraphStyle(
            "th",
            fontName="Segoe-Bold",
            fontSize=8,
            leading=10,
            textColor=WHITE,
        ),
        "td": ParagraphStyle(
            "td",
            fontName="Segoe",
            fontSize=8,
            leading=10.5,
            textColor=INK,
        ),
        "tdm": ParagraphStyle(
            "tdm",
            fontName="Consolas",
            fontSize=8,
            leading=10.5,
            textColor=INK,
        ),
    }


S = styles()


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph("•   " + item, S["bullet"]) for item in items]


def section_rule() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=1, spaceAfter=6)


class Drawing(Flowable):
    def __init__(self, height: float, painter):
        super().__init__()
        self._height = height
        self._painter = painter

    def wrap(self, aw, ah):
        self.width = aw
        return aw, self._height

    def draw(self):
        self._painter(self.canv, self.width, self._height)


def _arrow(c, x1, y1, x2, y2, color=TEAL_MID):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.15)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 6.5
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2 - size * math.cos(angle - 0.42), y2 - size * math.sin(angle - 0.42))
    path.lineTo(x2 - size * math.cos(angle + 0.42), y2 - size * math.sin(angle + 0.42))
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def _round_box(c, x, y, w, h, fill, stroke=None, radius=5):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def _center_text(c, text, x, y, w, h, font="Segoe", size=8.5, color=INK, leading=None):
    leading = leading or size + 2
    lines = text.split("\n")
    total = leading * len(lines)
    top = y + (h + total) / 2 - leading + 1
    c.setFillColor(color)
    c.setFont(font, size)
    for index, line in enumerate(lines):
        c.drawCentredString(x + w / 2, top - index * leading, line)


def _label(c, text, x, y, font="Segoe", size=8, color=MUTED):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def paint_architecture(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)

    caller_w, caller_h = 168, 36
    caller_x = (w - caller_w) / 2
    caller_y = h - 50
    _round_box(c, caller_x, caller_y, caller_w, caller_h, TEAL)
    _center_text(
        c,
        "Caller\nCLI, tests, or host",
        caller_x,
        caller_y,
        caller_w,
        caller_h,
        "Segoe",
        8.5,
        WHITE,
        11,
    )

    find_w, find_h = 268, 36
    find_x = (w - find_w) / 2
    find_y = caller_y - 78
    _round_box(c, find_x, find_y, find_w, find_h, TEAL_SOFT, TEAL_MID)
    _center_text(
        c,
        "LongestIncreasingRunFinder.Find(string)",
        find_x,
        find_y,
        find_w,
        find_h,
        "Segoe-Bold",
        8.5,
        TEAL,
    )
    _arrow(c, w / 2, caller_y, w / 2, find_y + find_h)

    boxes = [
        ("Parse", "string to int[]", TEAL_SOFT),
        ("SelectEarliestLongestRun", "int[] to Run", GOLD_SOFT),
        ("Format", "Run to string", TEAL_SOFT),
    ]
    gap = 12
    box_w = (w - 28 - gap * 2) / 3
    box_h = 46
    box_y = 22
    x = 14
    centers = []
    for title, subtitle, fill in boxes:
        _round_box(c, x, box_y, box_w, box_h, fill, TEAL_MID)
        _center_text(c, title + "\n" + subtitle, x, box_y, box_w, box_h, "Segoe", 8, INK, 11)
        centers.append(x + box_w / 2)
        x += box_w + gap

    for center in centers:
        _arrow(c, w / 2, find_y, center, box_y + box_h)

    _label(c, "Private steps, called in this order", 14, 8, "Segoe-Italic", 8, FAINT)


def paint_flowchart(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)

    cx = w * 0.36
    box_w = 210
    box_h = 28

    def process(y, text, fill=WHITE):
        x = cx - box_w / 2
        _round_box(c, x, y, box_w, box_h, fill, TEAL_MID, 4)
        _center_text(c, text, x, y, box_w, box_h, "Segoe", 8, INK)
        return y

    def diamond(y, text, dw=196, dh=42):
        x = cx
        path = c.beginPath()
        path.moveTo(x, y + dh)
        path.lineTo(x + dw / 2, y + dh / 2)
        path.lineTo(x, y)
        path.lineTo(x - dw / 2, y + dh / 2)
        path.close()
        c.setFillColor(GOLD_SOFT)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.drawPath(path, fill=1, stroke=1)
        _center_text(c, text, x - dw / 2, y, dw, dh, "Segoe", 7.5, INK, 10)
        return y

    y = h - 46
    process(y, "Start: int[] values")
    y2 = y - 52
    diamond(y2, "values.Length == 0 ?")
    _arrow(c, cx, y, cx, y2 + 42)
    empty_x = cx + 118
    _round_box(c, empty_x, y2 + 6, 118, 30, CLAY_SOFT, CLAY, 4)
    _center_text(c, "return Run(0, 0)", empty_x, y2 + 6, 118, 30, "Segoe", 8, CLAY)
    c.setStrokeColor(CLAY)
    c.setFillColor(CLAY)
    c.setLineWidth(1.1)
    c.line(cx + 98, y2 + 21, empty_x, y2 + 21)
    _arrow(c, empty_x - 8, y2 + 21, empty_x, y2 + 21, CLAY)
    _label(c, "yes", cx + 100, y2 + 25, "Segoe", 7.5, CLAY)

    y3 = y2 - 50
    process(y3, "bestStart = 0, bestLength = 1, runStart = 0", TEAL_SOFT)
    _arrow(c, cx, y2, cx, y3 + box_h)
    _label(c, "no", cx + 6, y2 - 12, "Segoe", 7.5, TEAL_MID)

    y4 = y3 - 58
    diamond(y4, "index = 1 .. n − 1")
    _arrow(c, cx, y3, cx, y4 + 42)

    y5 = y4 - 62
    diamond(y5, "values[i] > values[i − 1] ?", dw=210, dh=44)
    _arrow(c, cx, y4, cx, y5 + 44)

    loop_x = cx + 130
    _round_box(c, loop_x, y5 + 7, 92, 30, TEAL_SOFT, TEAL_MID, 4)
    _center_text(c, "continue\nnext index", loop_x, y5 + 7, 92, 30, "Segoe", 7.5, TEAL, 10)
    c.setStrokeColor(TEAL_MID)
    c.line(cx + 105, y5 + 22, loop_x, y5 + 22)
    _arrow(c, loop_x - 8, y5 + 22, loop_x, y5 + 22)
    _label(c, "yes", cx + 108, y5 + 26, "Segoe", 7.5, TEAL_MID)
    cont_right = loop_x + 92
    cont_top = y5 + 37
    c.setStrokeColor(TEAL_MID)
    c.setDash(2, 2)
    c.setLineWidth(0.9)
    c.line(cont_right, cont_top, cont_right, y4 + 21)
    c.setDash()
    _arrow(c, cont_right, y4 + 21, cx + 98, y4 + 21)

    y6 = y5 - 64
    process(y6, "length = index − runStart", CREAM)
    _arrow(c, cx, y5, cx, y6 + box_h)
    _label(c, "no  (equal or smaller)", cx + 8, y5 - 12, "Segoe", 7.5, GOLD)

    y7 = y6 - 46
    process(y7, "if length > bestLength: keep this run", GOLD_SOFT)
    _arrow(c, cx, y6, cx, y7 + box_h)

    y8 = y7 - 46
    process(y8, "runStart = index, then next index", WHITE)
    _arrow(c, cx, y7, cx, y8 + box_h)

    # loop-back from continue and from runStart to the for-loop diamond
    c.setStrokeColor(TEAL_MID)
    c.setDash(2, 2)
    c.setLineWidth(0.9)
    back_x = 16
    c.line(cx - box_w / 2, y8 + box_h / 2, back_x, y8 + box_h / 2)
    c.line(back_x, y8 + box_h / 2, back_x, y4 + 21)
    c.setDash()
    _arrow(c, back_x, y4 + 21, cx - 98, y4 + 21)
    _label(c, "loop", back_x + 4, y4 + 28, "Segoe-Italic", 7.5, FAINT)

    y9 = y8 - 50
    process(y9, "Close the final run the same way", GOLD_SOFT)
    _arrow(c, cx, y8, cx, y9 + box_h)
    _label(c, "loop finished", cx + 8, y8 - 12, "Segoe", 7.5, TEAL_MID)

    y10 = y9 - 48
    x10 = cx - box_w / 2
    _round_box(c, x10, y10, box_w, box_h, TEAL, TEAL, 4)
    _center_text(
        c,
        "return Run(bestStart, bestLength)",
        x10,
        y10,
        box_w,
        box_h,
        "Segoe-Bold",
        8,
        WHITE,
    )
    _arrow(c, cx, y9, cx, y10 + box_h)


def paint_sequence(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
    values = ["6", "2", "4", "6", "1", "5", "9", "2"]
    fills = [
        CLAY_SOFT,
        GOLD_SOFT,
        GOLD_SOFT,
        GOLD_SOFT,
        TEAL_SOFT,
        TEAL_SOFT,
        TEAL_SOFT,
        CREAM,
    ]
    strokes = [CLAY, GOLD, GOLD, GOLD, TEAL_MID, TEAL_MID, TEAL_MID, FAINT]
    note = ["len 1", "best", "best", "best", "tie", "tie", "tie", "len 1"]
    margin = 16
    gap = 8
    cell = (w - margin * 2 - gap * 7) / 8
    top = h - 36
    _label(c, "Input  6 2 4 6 1 5 9 2", margin, h - 18, "Segoe-Bold", 9, TEAL)
    for index, value in enumerate(values):
        x = margin + index * (cell + gap)
        _round_box(c, x, top - 58, cell, 46, fills[index], strokes[index], 4)
        _center_text(c, value, x, top - 58, cell, 46, "Consolas-Bold", 12, INK)
        c.setFillColor(FAINT)
        c.setFont("Segoe", 7)
        c.drawCentredString(x + cell / 2, top - 70, str(index))
        c.setFillColor(strokes[index])
        c.setFont("Segoe", 7)
        c.drawCentredString(x + cell / 2, top - 84, note[index])

    # brackets under groups
    yb = 28
    groups = [
        (0, 0, "discarded"),
        (1, 3, "kept: 2 4 6"),
        (4, 6, "same length, later"),
        (7, 7, "discarded"),
    ]
    c.setStrokeColor(TEAL_MID)
    c.setLineWidth(1)
    for start, end, caption in groups:
        x1 = margin + start * (cell + gap)
        x2 = margin + end * (cell + gap) + cell
        c.line(x1 + 4, yb + 16, x1 + 4, yb + 8)
        c.line(x2 - 4, yb + 16, x2 - 4, yb + 8)
        c.line(x1 + 4, yb + 8, x2 - 4, yb + 8)
        c.setFillColor(MUTED)
        c.setFont("Segoe", 7.5)
        c.drawCentredString((x1 + x2) / 2, yb - 4, caption)


def paint_skip(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
    _label(c, "Contiguous run versus a subsequence that skips", 14, h - 18, "Segoe-Bold", 9, TEAL)

    def row(y, values, marks, caption, caption_color):
        x = 14
        cell = 28
        for value, mark in zip(values, marks):
            fill = GOLD_SOFT if mark == "keep" else (CLAY_SOFT if mark == "skip" else WHITE)
            stroke = GOLD if mark == "keep" else (CLAY if mark == "skip" else LINE)
            _round_box(c, x, y, cell - 4, 22, fill, stroke, 3)
            _center_text(c, value, x, y, cell - 4, 22, "Consolas", 8, INK)
            x += cell
        c.setFillColor(caption_color)
        c.setFont("Segoe", 8)
        c.drawString(x + 8, y + 6, caption)

    row(h - 52, ["6", "2", "4", "6", "1", "5", "9", "2"], ["out", "keep", "keep", "keep", "out", "out", "out", "out"], "Run 2 4 6 is returned", TEAL)
    row(h - 82, ["6", "2", "4", "6", "1", "5", "9", "2"], ["out", "keep", "keep", "skip", "out", "keep", "keep", "out"], "2 4 5 9 skips 6, so it is not a run", CLAY)


def paint_cli(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
    bw, bh = 230, 32
    cx = 36
    dx = cx + bw / 2

    def box(x, y, text, fill, stroke, tw=bw, th=bh, font="Segoe", size=8, color=INK):
        _round_box(c, x, y, tw, th, fill, stroke, 4)
        _center_text(c, text, x, y, tw, th, font, size, color, 10)

    def decision(y, text, dw=188, dh=46):
        path = c.beginPath()
        path.moveTo(dx, y + dh)
        path.lineTo(dx + dw / 2, y + dh / 2)
        path.lineTo(dx, y)
        path.lineTo(dx - dw / 2, y + dh / 2)
        path.close()
        c.setFillColor(GOLD_SOFT)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.drawPath(path, fill=1, stroke=1)
        _center_text(c, text, dx - dw / 2, y, dw, dh, "Segoe", 8, INK, 10)
        return dw

    y0 = h - 42
    box(cx, y0, "Program starts", TEAL, TEAL, color=WHITE, font="Segoe-Bold")
    y1 = y0 - 56
    dw = decision(y1, "How many arguments?")
    _arrow(c, dx, y0, dx, y1 + 46)

    side_x = dx + dw / 2 + 28
    side_w = w - side_x - 14
    box(side_x, y1 + 6, "more than one\nusage text, exit 1", CLAY_SOFT, CLAY, side_w, 36, size=7.5, color=CLAY)
    _arrow(c, dx + dw / 2, y1 + 23, side_x, y1 + 24, CLAY)

    y2 = y1 - 54
    box(cx, y2, "one argument\nFind once, print the run, exit 0", TEAL_SOFT, TEAL_MID, bw, 40)
    _arrow(c, dx, y1, dx, y2 + 40)
    _label(c, "one", dx + 8, y1 - 12, "Segoe", 7.5, TEAL_MID)

    y3 = y2 - 48
    box(cx, y3, "none: prompt  Enter the string:", CREAM, GOLD, bw, 32)
    _arrow(c, dx, y2, dx, y3 + 32)
    _label(c, "none", dx + 8, y2 - 12, "Segoe", 7.5, GOLD)

    y4 = y3 - 54
    dw4 = decision(y4, "Line empty or end of input?")
    _arrow(c, dx, y3, dx, y4 + 46)
    box(side_x, y4 + 6, "yes\nexit 0", CLAY_SOFT, CLAY, side_w, 36, size=8, color=CLAY)
    _arrow(c, dx + dw4 / 2, y4 + 23, side_x, y4 + 24, CLAY)

    y5 = y4 - 50
    box(cx, y5, "print the labelled run\nthen ask again", TEAL_SOFT, TEAL_MID, bw, 40)
    _arrow(c, dx, y4, dx, y5 + 40)
    _label(c, "no", dx + 8, y4 - 12, "Segoe", 7.5, TEAL_MID)

    c.setStrokeColor(TEAL_MID)
    c.setDash(2, 2)
    c.setLineWidth(0.9)
    back = 16
    c.line(cx, y5 + 20, back, y5 + 20)
    c.line(back, y5 + 20, back, y3 + 16)
    c.setDash()
    _arrow(c, back, y3 + 16, cx, y3 + 16)


def data_table(header: list[str], rows: list[list[str]], col_widths: list[float]) -> Table:
    head = [Paragraph(cell, S["th"]) for cell in header]
    body = []
    for row in rows:
        body.append([Paragraph(cell, S["tdm"] if index == 0 else S["td"]) for index, cell in enumerate(row)])
    table = Table([head] + body, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, CREAM]),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Segoe", 8)
    canvas.drawString(LEFT, PAGE_H - 7.5 * mm, "Longest strictly increasing run")
    canvas.setFont("Segoe", 8)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Technical details")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Segoe", 8)
    canvas.drawString(LEFT, 4 * mm, ".NET 9  ·  LongestIncreasingRunFinder.Find")
    canvas.drawRightString(PAGE_W - RIGHT, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def build_story() -> list:
    story: list = []
    story.append(Spacer(1, 4))
    story.append(P("Technical details", "h1"))
    story.append(
        P(
            "This document describes the function that returns the earliest longest strictly increasing run, "
            "the single left-to-right scan that finds it, and the console program that calls it."
        )
    )
    story.append(section_rule())

    story.append(P("Problem", "h2"))
    story.append(
        P(
            "<font face='Consolas'>Find</font> takes one string of integers separated by single spaces and returns one string. "
            "The result is the contiguous stretch that is strictly increasing, is at least as long as every other such stretch, "
            "and starts earliest when lengths are equal. A single value is a run of length one. An empty string returns an empty string."
        )
    )
    story.append(
        P(
            "Comparison is numeric and culture-invariant. <font face='Consolas'>-5 -1 0 4</font> increases. "
            "<font face='Consolas'>9</font> is not greater than <font face='Consolas'>10</font>. "
            "An equal neighbour ends the run. The step may be any positive amount, so <font face='Consolas'>1 100 101</font> is one run."
        )
    )

    story.append(P("A run is not a subsequence that skips values", "h2"))
    story.append(
        P(
            "The classic longest increasing subsequence may skip values and is a different problem, usually solved in "
            "<font face='Consolas'>O(n log n)</font> time. That answer is rejected here. "
            "For <font face='Consolas'>6 2 4 6 1 5 9 2</font>, both <font face='Consolas'>2 4 5 9</font> and "
            "<font face='Consolas'>2 4 6 9</font> are longer than <font face='Consolas'>2 4 6</font>, and both skip a value that sits between the chosen numbers. "
            "The function returns <font face='Consolas'>2 4 6</font>."
        )
    )
    story.append(Drawing(118, paint_skip))
    story.append(P("Figure 1. Gold cells are kept. Clay cells are the values a longer subsequence would have to skip.", "caption"))

    story.append(P("Components", "h2"))
    story.append(
        P(
            "The library method is <font face='Consolas'>LongestIncreasingRunFinder.Find</font>. "
            "It rejects null with <font face='Consolas'>ArgumentNullException</font>, then runs three private steps. "
            "Parsing and formatting stay private. Callers pass one string and receive one string."
        )
    )
    story.append(Drawing(210, paint_architecture))
    story.append(P("Figure 2. Call path from a host into the three private steps.", "caption"))

    story.append(
        data_table(
            ["Step", "Responsibility"],
            [
                ["Parse", "Split on a single space and parse each token with CultureInfo.InvariantCulture. An empty string becomes an empty array."],
                ["SelectEarliestLongestRun", "One forward pass. Record the start index and length of the earliest longest maximal run."],
                ["Format", "Write values[start .. start+length) separated by one space. Length zero returns an empty string. No leading or trailing space."],
            ],
            [CONTENT_W * 0.32, CONTENT_W * 0.68],
        )
    )
    story.append(Spacer(1, 8))

    story.append(P("Selection algorithm", "h2"))
    story.append(
        P(
            "A maximal run is already ended by the first value that is not strictly greater than its predecessor. "
            "The scan therefore does not search every pair of endpoints. It walks the array once, closes a run when the increase stops, "
            "and replaces the recorded answer only when the closed run is strictly longer. Equal length leaves the earlier start in place."
        )
    )
    story.extend(
        bullets(
            [
                "An empty array returns <font face='Consolas'>Run(0, 0)</font>.",
                "Otherwise the first value is a run of length 1, so <font face='Consolas'>bestLength</font> starts at 1.",
                "Inside the loop, <font face='Consolas'>index</font> is the first value that does not extend the current run. Its length is <font face='Consolas'>index − runStart</font>.",
                "The final run has no following value, so it is closed once after the loop with the same length test.",
                "The search performs <font face='Consolas'>n − 1</font> comparisons. Every value is read, which matches the lower bound: an unread value could extend a run or start a longer one.",
            ]
        )
    )
    story.append(Drawing(560, paint_flowchart))
    story.append(P("Figure 3. Control flow of SelectEarliestLongestRun. The dashed line returns to the next index.", "caption"))

    story.append(P("State while scanning the tie", "h2"))
    story.append(
        P(
            "Input <font face='Consolas'>6 2 4 6 1 5 9 2</font>. Indexes are zero-based. "
            "A new run replaces the best run only when its length is greater. The second length-3 run does not replace the first."
        )
    )
    story.append(Drawing(168, paint_sequence))
    story.append(P("Figure 4. The four maximal runs. The gold run is the one returned.", "caption"))

    story.append(
        data_table(
            ["Event", "Closed run", "Length", "bestStart", "bestLength", "Recorded answer"],
            [
                ["Start at 6", "—", "—", "0", "1", "6"],
                ["2 does not increase", "6", "1", "0", "1", "6  (equal length, keep)"],
                ["1 does not increase", "2 4 6", "3", "1", "3", "2 4 6"],
                ["2 does not increase", "1 5 9", "3", "1", "3", "2 4 6  (tie, keep earlier)"],
                ["Close the final run", "2", "1", "1", "3", "2 4 6"],
            ],
            [
                CONTENT_W * 0.22,
                CONTENT_W * 0.14,
                CONTENT_W * 0.10,
                CONTENT_W * 0.13,
                CONTENT_W * 0.14,
                CONTENT_W * 0.27,
            ],
        )
    )
    story.append(Spacer(1, 4))
    story.append(P("Table 1. Recorded answer after each time a run is closed.", "caption"))

    story.append(P("The shorter published example", "h3"))
    story.append(
        P(
            "<font face='Consolas'>6 1 5 9 2</font> has maximal runs <font face='Consolas'>6</font>, "
            "<font face='Consolas'>1 5 9</font>, and <font face='Consolas'>2</font>. "
            "Length 3 replaces length 1, and the final length 1 does not replace it. The result is <font face='Consolas'>1 5 9</font>."
        )
    )

    story.append(P("Cost", "h2"))
    story.append(
        data_table(
            ["Resource", "Bound", "Where it is spent"],
            [
                ["Time", "O(n)", "n − 1 numeric comparisons, plus a linear parse and a linear format of the chosen run."],
                ["Extra memory", "O(n)", "The integer array. The search itself stores a few indexes: bestStart, bestLength, runStart, and the loop index."],
                ["Output", "O(k)", "k is the length of the chosen run. Formatting writes only that span."],
            ],
            [CONTENT_W * 0.18, CONTENT_W * 0.14, CONTENT_W * 0.68],
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "A variant can avoid the integer array by remembering the character span of the best run and returning that slice of the original string. "
            "The indexes stay a handful of integers. <font face='Consolas'>Find</font> uses the array form so the tie is visible as value indexes rather than character offsets."
        )
    )

    story.append(P("Console program", "h2"))
    story.append(
        P(
            "<font face='Consolas'>LongestIncreasingRun.Cli</font> is a thin host. "
            "One command-line argument is the whole sequence, including its spaces, and the process prints the raw run and exits. "
            "With no argument it prompts on standard error, reads one line, and repeats. "
            "An empty line, or the end of input, exits with code 0. More than one argument prints usage and exits with code 1."
        )
    )
    story.append(
        P(
            "Interactive output is prefixed. The printed line is "
            "<font face='Consolas'>Longest increasing subsequence is: </font> followed by the run. "
            "The one-argument path does not add that prefix. The library method itself returns only the run."
        )
    )
    story.append(
        P(
            "The solution targets <font face='Consolas'>net9.0</font>. "
            "<font face='Consolas'>global.json</font> pins SDK 9.0.319 and allows a newer 9.x SDK. "
            "The container build uses <font face='Consolas'>mcr.microsoft.com/dotnet/sdk:9.0</font> and "
            "<font face='Consolas'>mcr.microsoft.com/dotnet/runtime:9.0</font>."
        )
    )
    story.append(Drawing(348, paint_cli))
    story.append(P("Figure 5. Console control flow. The dashed arrow returns to the prompt.", "caption"))

    story.append(P("Project map", "h2"))
    story.append(
        data_table(
            ["Path", "Role"],
            [
                ["src/LongestIncreasingRun/<br/>LongestIncreasingRunFinder.cs", "Find, Parse, SelectEarliestLongestRun, and Format."],
                ["src/LongestIncreasingRun.Cli/<br/>Program.cs", "Argument handling, the prompt loop, and printing."],
                ["tests/LongestIncreasingRun.Tests/<br/>RunRulesTests.cs", "One case per rule, plus a brute-force oracle over random sequences."],
                ["tests/LongestIncreasingRun.Tests/<br/>AcceptanceFixtureTests.cs", "Acceptance cases AT-01 through AT-11 and RC-01 through RC-08."],
                ["Downloads/acceptance-fixtures.json", "Exact inputs, expected strings, and SHA-256 digests loaded by the acceptance tests."],
            ],
            [CONTENT_W * 0.46, CONTENT_W * 0.54],
        )
    )
    story.append(Spacer(1, 8))
    story.append(P("What the tests lock down", "h2"))
    story.extend(
        bullets(
            [
                "A single value is returned unchanged. A strictly increasing input is returned unchanged.",
                "A strictly decreasing input returns the first value, because every later run has length 1.",
                "Equal neighbours end the run: <font face='Consolas'>1 2 2 3</font> returns <font face='Consolas'>1 2</font>.",
                "Equal lengths keep the earlier start: <font face='Consolas'>1 3 2 4</font> returns <font face='Consolas'>1 3</font>.",
                "Negative numbers and zero compare numerically.",
                "Null throws <font face='Consolas'>ArgumentNullException</font>. An empty string returns an empty string.",
                "Two hundred random sequences of length 1 to 31 must match a brute-force scan of every maximal run.",
            ]
        )
    )
    return story


def main() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Longest strictly increasing run — technical details",
        author="LongestIncreasingRun",
    )
    frame = Frame(LEFT, 16 * mm, CONTENT_W, PAGE_H - 34 * mm, id="body", showBoundary=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])
    doc.build(build_story())
    print(PDF_PATH)


if __name__ == "__main__":
    main()
