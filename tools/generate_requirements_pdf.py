#!/usr/bin/env python3
"""Generate the longest-increasing-run requirements specification (PDF)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    HRFlowable,
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

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "code-test.md"
PDF_PATH = ROOT / "Downloads" / "Longest-Increasing-Subsequence-Requirements.pdf"
FIXTURE_PATH = ROOT / "Downloads" / "acceptance-fixtures.json"

pdfmetrics.registerFont(TTFont("Inter", "/usr/share/fonts/truetype/macos/Inter-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Med", "/usr/share/fonts/truetype/macos/Inter-Medium.ttf"))
pdfmetrics.registerFont(TTFont("Inter-SmB", "/usr/share/fonts/truetype/macos/Inter-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Bold", "/usr/share/fonts/truetype/macos/Inter-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Inter-Italic", "/usr/share/fonts/truetype/macos/Inter-Italic.ttf"))
pdfmetrics.registerFontFamily(
    "Inter",
    normal="Inter",
    bold="Inter-Bold",
    italic="Inter-Italic",
    boldItalic="Inter-Bold",
)
pdfmetrics.registerFont(TTFont("Mono", "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Mono-Med", "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"))

INK = HexColor("#1C2421")
MUTED = HexColor("#3E4C48")
FAINT = HexColor("#5E6E69")
LINE = HexColor("#D9E0DC")
RULE = HexColor("#C5D0CB")
TEAL = HexColor("#14302C")
TEAL_MID = HexColor("#1F4A44")
CREAM = HexColor("#F6F4EF")
PAPER = HexColor("#F3F6F4")
GOLD = HexColor("#8C6A32")
SHOULD = HexColor("#8A4B1F")
WHITE = white

PAGE_W, PAGE_H = A4
CONTENT_W = 174 * mm


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_cases() -> list[dict]:
    text = SOURCE.read_text(encoding="utf-8")
    blocks = [block.strip("\n") for block in re.findall(r"```\s*\n(.*?)\n```", text, re.S)]
    if len(blocks) != 22:
        raise SystemExit(f"Expected 22 fenced blocks in {SOURCE}, found {len(blocks)}")
    cases = []
    for index, (raw_input, raw_output) in enumerate(zip(blocks[0::2], blocks[1::2]), start=1):
        numbers = [int(token) for token in raw_input.split()]
        expected = raw_output.strip()
        cases.append(
            {
                "id": f"AT-{index:02d}",
                "input": raw_input,
                "expected": expected,
                "sha256": sha256_text(raw_input),
                "count": len(numbers),
                "output_length": len(expected.split()),
                "minimum": min(numbers),
                "maximum": max(numbers),
            }
        )
    return cases


CASES = load_cases()

RULE_CHECKS = [
    {
        "id": "RC-01",
        "purpose": "A one-element input is already a complete run.",
        "input": "42",
        "expected": "42",
    },
    {
        "id": "RC-02",
        "purpose": "An input that is strictly increasing throughout is returned unchanged.",
        "input": "1 2 3 4",
        "expected": "1 2 3 4",
    },
    {
        "id": "RC-03",
        "purpose": "Every value is its own run of length 1, so the earliest run is the first value.",
        "input": "9 7 5 3",
        "expected": "9",
    },
    {
        "id": "RC-04",
        "purpose": "Two runs share the maximum length. The one with the smaller starting index is returned.",
        "input": "1 3 2 4",
        "expected": "1 3",
    },
    {
        "id": "RC-05",
        "purpose": "An equal neighbour is not an increase, so the run ends. The earliest longest run is returned.",
        "input": "1 2 2 3",
        "expected": "1 2",
    },
    {
        "id": "RC-06",
        "purpose": "The step may be any positive amount. A step of 1 is not required.",
        "input": "1 100 101",
        "expected": "1 100 101",
    },
    {
        "id": "RC-07",
        "purpose": "Comparison is numeric, so zero and negative integers follow the same rule.",
        "input": "-5 -1 0 4 1",
        "expected": "-5 -1 0 4",
    },
    {
        "id": "RC-08",
        "purpose": "A later run is ignored when an earlier run is strictly longer.",
        "input": "1 2 3 0 1",
        "expected": "1 2 3",
    },
]


def styles() -> dict[str, ParagraphStyle]:
    base = dict(fontName="Inter", textColor=INK, alignment=TA_LEFT, splitLongWords=1)
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker",
            fontName="Inter-Med",
            fontSize=9,
            leading=12,
            textColor=TEAL_MID,
            tracking=0.6,
            spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Inter-Bold",
            fontSize=26,
            leading=30,
            textColor=TEAL,
            spaceAfter=0,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="Inter-Med",
            fontSize=13,
            leading=17,
            textColor=GOLD,
            spaceBefore=10,
            spaceAfter=12,
        ),
        "cover_deck": ParagraphStyle(
            "cover_deck",
            fontName="Inter",
            fontSize=10,
            leading=14.5,
            textColor=MUTED,
        ),
        "contents": ParagraphStyle(
            "contents",
            fontName="Inter-Bold",
            fontSize=15,
            leading=19,
            textColor=TEAL,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1",
            fontName="Inter-Bold",
            fontSize=15,
            leading=19,
            textColor=TEAL,
            spaceBefore=2,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Inter-SmB",
            fontSize=12,
            leading=15.5,
            textColor=TEAL,
            spaceBefore=11,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="Inter-SmB",
            fontSize=10.5,
            leading=13.5,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "body",
            **base,
            fontSize=9.5,
            leading=13.2,
            spaceAfter=6,
        ),
        "body_tight": ParagraphStyle(
            "body_tight",
            **base,
            fontSize=9.5,
            leading=13.2,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="Inter",
            fontSize=8,
            leading=10.8,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "ac_head": ParagraphStyle(
            "ac_head",
            fontName="Inter-SmB",
            fontSize=9.5,
            leading=13,
            textColor=INK,
            spaceBefore=2,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "ac": ParagraphStyle(
            "ac",
            fontName="Inter",
            fontSize=9,
            leading=12.4,
            textColor=INK,
            leftIndent=4,
            spaceBefore=1,
            spaceAfter=3,
        ),
        "cell": ParagraphStyle(
            "cell",
            fontName="Inter",
            fontSize=8,
            leading=10.6,
            textColor=INK,
        ),
        "cell_head": ParagraphStyle(
            "cell_head",
            fontName="Inter-SmB",
            fontSize=7.5,
            leading=9.5,
            textColor=WHITE,
        ),
        "cell_id": ParagraphStyle(
            "cell_id",
            fontName="Mono-Med",
            fontSize=7.5,
            leading=10,
            textColor=TEAL,
        ),
        "mono": ParagraphStyle(
            "mono",
            fontName="Mono",
            fontSize=7.5,
            leading=10.2,
            textColor=INK,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Inter-Italic",
            fontSize=8,
            leading=10.5,
            textColor=FAINT,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Inter",
            fontSize=8,
            leading=10,
            textColor=FAINT,
        ),
        "toc_h": ParagraphStyle(
            "toc_h",
            fontName="Inter",
            fontSize=10.5,
            leading=14,
            textColor=INK,
            spaceBefore=7,
        ),
        "toc_s": ParagraphStyle(
            "toc_s",
            fontName="Inter",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            leftIndent=10,
            spaceBefore=1,
        ),
        "req_title": ParagraphStyle(
            "req_title",
            fontName="Inter-SmB",
            fontSize=10.5,
            leading=13.5,
            textColor=INK,
        ),
        "req_id": ParagraphStyle(
            "req_id",
            fontName="Mono-Med",
            fontSize=8.5,
            leading=11,
            textColor=TEAL,
        ),
        "priority": ParagraphStyle(
            "priority",
            fontName="Inter-SmB",
            fontSize=7.5,
            leading=9,
            alignment=TA_RIGHT,
            textColor=WHITE,
        ),
        "check": ParagraphStyle(
            "check",
            fontName="Inter",
            fontSize=8,
            leading=10.6,
            textColor=INK,
        ),
        "meta_label": ParagraphStyle(
            "meta_label",
            fontName="Inter-Med",
            fontSize=8,
            leading=11,
            textColor=FAINT,
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName="Inter",
            fontSize=9,
            leading=12,
            textColor=INK,
        ),
    }


S = styles()


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def P(text: str, style: str = "body") -> Paragraph:
    def _keep_short_runs(match: re.Match) -> str:
        inner = match.group(2)
        if len(inner) <= 48:
            inner = inner.replace(" ", "&nbsp;")
        return match.group(1) + inner + match.group(3)

    text = re.sub(r'(<font face="Mono"[^>]*>)(.*?)(</font>)', _keep_short_runs, text)
    return Paragraph(text, S[style])


def rule() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.4, color=RULE, spaceBefore=1, spaceAfter=8)


def section_rule() -> list:
    return [Spacer(1, 2), HRFlowable(width="100%", thickness=0.6, color=TEAL, spaceBefore=0, spaceAfter=8)]


def code_block(text: str) -> Table:
    paragraph = Paragraph(esc(text).replace("\n", "<br/>"), S["mono"])
    table = Table([[paragraph]], colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("LINEBEFORE", (0, 0), (0, -1), 2.5, TEAL_MID),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def shaded_table(headers: list[str], rows: list[list], widths: list[float]) -> Table:
    head = [Paragraph(esc(header), S["cell_head"]) for header in headers]
    body = []
    for row in rows:
        body.append([cell if isinstance(cell, Paragraph) else Paragraph(esc(str(cell)), S["cell"]) for cell in row])
    table = Table([head] + body, colWidths=widths, repeatRows=1)
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Inter-SmB"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, LINE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.4, RULE),
    ]
    for row_index in range(1, len(body) + 1):
        if row_index % 2 == 0:
            style_commands.append(("BACKGROUND", (0, row_index), (-1, row_index), PAPER))
    table.setStyle(TableStyle(style_commands))
    return table


def priority_chip(priority: str) -> tuple[str, Color]:
    if priority == "Must":
        return "MUST", TEAL_MID
    return "SHOULD", SHOULD


def requirement_block(item: dict) -> list:
    label, color = priority_chip(item["priority"])
    chip = Table([[Paragraph(label, S["priority"])]], colWidths=[22 * mm])
    chip.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    header = Table(
        [
            [Paragraph(item["id"], S["req_id"]), chip],
            [Paragraph(esc(item["title"]), S["req_title"]), ""],
        ],
        colWidths=[CONTENT_W - 32 * mm, 32 * mm],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                ("SPAN", (0, 1), (-1, 1)),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("VALIGN", (0, 1), (-1, 1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (0, -1), 8),
                ("RIGHTPADDING", (0, 0), (0, -1), 6),
                ("LEFTPADDING", (1, 0), (1, 0), 4),
                ("RIGHTPADDING", (1, 0), (1, 0), 6),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
                ("TOPPADDING", (0, 1), (-1, 1), 1),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 7),
            ]
        )
    )
    flow = [Spacer(1, 8), header, Spacer(1, 6)]
    for paragraph in item["body"]:
        flow.append(P(paragraph))
    flow.append(P("Acceptance criteria", "ac_head"))
    for criterion in item["criteria"]:
        flow.append(
            P(
                f'<font color="#1F4A44"><b>{criterion["id"]}</b></font>&nbsp;&nbsp;{criterion["text"]}',
                "ac",
            )
        )
    return flow


REQUIREMENTS: list[dict] = [
    {
        "id": "FR-01",
        "priority": "Must",
        "title": "Accept one string of space-separated integers",
        "body": [
            "The solution provides one function that takes a single string. That string holds the integers of the problem, separated by a single space character (U+0020). Each published case is one line: no leading space, no trailing space, and no newline inside the string passed to the function.",
            "The count of integers is not fixed. The largest published input, AT-09, contains 8,192 integers. Every published value is an integer from 1 to 32,762 inclusive, so a 32-bit signed integer is sufficient for the published suite. The function compares values numerically.",
            "Supporting functions are allowed. The brief does not prescribe the function name, the project layout, or the algorithm.",
        ],
        "criteria": [
            {
                "id": "AC-01.1",
                "text": "The function can be called with one string argument. No second argument is required to select formatting, length, or tie-break behaviour.",
            },
            {
                "id": "AC-01.2",
                "text": "Each published input splits on a single space into the element count in Section 8, and every token parses as a base-10 integer.",
            },
            {
                "id": "AC-01.3",
                "text": "Calling the function with the 8,192-element input AT-09 returns the expected string for that case. The input is in scope for the automated test run.",
            },
        ],
    },
    {
        "id": "FR-02",
        "priority": "Must",
        "title": "Return the longest strictly increasing run",
        "body": [
            "A <b>run</b> is a contiguous segment of the input. Values stay in their original order, and no value lying between the first and the last chosen value is omitted.",
            "A run is <b>strictly increasing</b> when each value after the first is greater than the value immediately before it. The result is a strictly increasing run whose length is greater than or equal to the length of every other strictly increasing run in the input.",
            "Decision D-01 fixes this meaning for acceptance. The brief says “subsequence”. The published outputs are the longest contiguous runs. On AT-10 the contiguous result <font face=\"Mono\">2 4 6</font> is required. Skipping values to build <font face=\"Mono\">2 4 5 9</font> or <font face=\"Mono\">2 4 6 9</font> fails that case.",
        ],
        "criteria": [
            {
                "id": "AC-02.1",
                "text": "Every pair of neighbours in the result is strictly increasing, and the result occurs as a contiguous segment of the input.",
            },
            {
                "id": "AC-02.2",
                "text": "No strictly increasing run in the input is longer than the result.",
            },
            {
                "id": "AC-02.3",
                "text": "Given <font face=\"Mono\">6 1 5 9 2</font>, the result is <font face=\"Mono\">1 5 9</font>. This is AT-01.",
            },
            {
                "id": "AC-02.4",
                "text": "Given <font face=\"Mono\">6 2 4 6 1 5 9 2</font>, the result is <font face=\"Mono\">2 4 6</font>. The strings <font face=\"Mono\">2 4 5 9</font> and <font face=\"Mono\">2 4 6 9</font> fail AT-10.",
            },
        ],
    },
    {
        "id": "FR-03",
        "priority": "Must",
        "title": "Treat any positive step as an increase",
        "body": [
            "The brief says the sequence is “increased by any number”. For acceptance, each step is a positive difference of any size. Successive values do not have to differ by one.",
        ],
        "criteria": [
            {
                "id": "AC-03.1",
                "text": "Given <font face=\"Mono\">1 100 101</font>, the result is <font face=\"Mono\">1 100 101</font>. This is RC-06.",
            },
            {
                "id": "AC-03.2",
                "text": "AT-02, AT-03, and AT-09 return their expected runs. Those runs contain steps greater than 1.",
            },
        ],
    },
    {
        "id": "FR-04",
        "priority": "Must",
        "title": "Break length ties by choosing the earliest run",
        "body": [
            "When more than one strictly increasing run has the maximum length, the function returns the earliest. Earliest means the run whose first element has the smallest index in the input.",
            "Decision D-02 records that reading. On AT-10 the runs <font face=\"Mono\">2 4 6</font> and <font face=\"Mono\">1 5 9</font> both have length 3. The required output is <font face=\"Mono\">2 4 6</font>, which starts at index 1. Indexes are zero-based in this explanation; the implementation does not have to expose indexes.",
        ],
        "criteria": [
            {
                "id": "AC-04.1",
                "text": "When two or more strictly increasing runs share the maximum length, the returned run has the smallest starting index.",
            },
            {
                "id": "AC-04.2",
                "text": "Given <font face=\"Mono\">1 3 2 4</font>, the result is <font face=\"Mono\">1 3</font>. This is RC-04. The later run <font face=\"Mono\">2 4</font> has the same length.",
            },
            {
                "id": "AC-04.3",
                "text": "Given <font face=\"Mono\">6 2 4 6 1 5 9 2</font>, <font face=\"Mono\">2 4 6</font> is returned and <font face=\"Mono\">1 5 9</font> is not. This is AT-10.",
            },
            {
                "id": "AC-04.4",
                "text": "Given <font face=\"Mono\">9 7 5 3</font>, the result is <font face=\"Mono\">9</font>. This is RC-03. Each value is a run of length 1, and the first value starts earliest.",
            },
        ],
    },
    {
        "id": "FR-05",
        "priority": "Must",
        "title": "Emit the run as a single space-separated string",
        "body": [
            "The observable result is one string. It contains the chosen integers in order, written in ordinary base-10 form, separated by a single space. There is no leading whitespace, no trailing whitespace, and no trailing newline. A run of one integer is that integer alone.",
            "The function may return that string directly, or it may return the integers in order. In the second form, the tests and the verification instructions show the rendering that produces this exact string. Published tokens have no leading zeros and no leading plus signs, and the expected strings match those tokens.",
        ],
        "criteria": [
            {
                "id": "AC-05.1",
                "text": "For every case AT-01 through AT-11, the observable string is identical to the expected string in Section 8.",
            },
            {
                "id": "AC-05.2",
                "text": "Given <font face=\"Mono\">42</font>, the observable string is <font face=\"Mono\">42</font>. This is RC-01.",
            },
            {
                "id": "AC-05.3",
                "text": "Given <font face=\"Mono\">1 2 3 4</font>, the observable string is <font face=\"Mono\">1 2 3 4</font>. This is RC-02.",
            },
            {
                "id": "AC-05.4",
                "text": "A result that matches the expected integers and then adds a trailing space or newline fails the exact-string comparison.",
            },
        ],
    },
    {
        "id": "FR-06",
        "priority": "Must",
        "title": "End a run when the next value does not increase",
        "body": [
            "An equal neighbour has not increased. The run ends when the next value is less than or equal to the current value. Decision D-03 records this reading of “increased”.",
            "None of AT-01 through AT-11 contains adjacent equal values. A solution that treated equals as a continuation would still pass the published suite. RC-05 is therefore part of acceptance, so the comparison rule is fixed for every reviewer.",
        ],
        "criteria": [
            {
                "id": "AC-06.1",
                "text": "Given <font face=\"Mono\">1 2 2 3</font>, the result is <font face=\"Mono\">1 2</font>. This is RC-05. The later run <font face=\"Mono\">2 3</font> has the same length and a later start.",
            },
        ],
    },
    {
        "id": "FR-07",
        "priority": "Must",
        "title": "Apply the same numeric rule to every integer",
        "body": [
            "The brief asks for integers, and the published suite happens to use only positive values. Zero and negative integers are still integers. They are ordered by numeric value, with the same run and tie-break rules.",
        ],
        "criteria": [
            {
                "id": "AC-07.1",
                "text": "Given <font face=\"Mono\">-5 -1 0 4 1</font>, the result is <font face=\"Mono\">-5 -1 0 4</font>. This is RC-07. The final <font face=\"Mono\">1</font> is smaller than <font face=\"Mono\">4</font>, so it ends the run.",
            },
            {
                "id": "AC-07.2",
                "text": "Given <font face=\"Mono\">1 2 3 0 1</font>, the result is <font face=\"Mono\">1 2 3</font>. This is RC-08.",
            },
        ],
    },
    {
        "id": "FR-08",
        "priority": "Must",
        "title": "Pass the eleven published cases",
        "body": [
            "The brief says the function should pass the test cases supplied with the exercise. Those cases are normative. Section 8 is the catalogue. The input identity of each case is the SHA-256 digest of its exact string. The machine-readable copy is <font face=\"Mono\">acceptance-fixtures.json</font>, embedded in this PDF and stored beside it.",
            "A function that returns the eleven expected strings only for those exact inputs, and fails the rule checks in Section 9, does not meet FR-02 through FR-07.",
        ],
        "criteria": [
            {
                "id": "AC-08.1",
                "text": "For each case AT-01 through AT-11, the observable output equals the expected string in Section 8.",
            },
            {
                "id": "AC-08.2",
                "text": "The input used for each published case has the SHA-256 digest listed for that case. The digest is computed over the UTF-8 bytes of the string, with no byte-order mark and no trailing newline.",
            },
            {
                "id": "AC-08.3",
                "text": "The function also returns the expected string for RC-01 through RC-08.",
            },
        ],
    },
    {
        "id": "QR-01",
        "priority": "Must",
        "title": "Implement the solution in C# on .NET",
        "body": [
            "The brief requires a C# .NET solution and a clear demonstration of that platform. The code that implements the function, and the tests that call it, are C#. A supported .NET SDK builds and tests the solution with the <font face=\"Mono\">dotnet</font> tool.",
            "The brief does not name a target framework. The verification instructions name the SDK major version a reviewer needs.",
        ],
        "criteria": [
            {
                "id": "AC-09.1",
                "text": "The function under test is written in C#, in a project the .NET SDK can build.",
            },
            {
                "id": "AC-09.2",
                "text": "From a clean checkout, the documented <font face=\"Mono\">dotnet</font> commands restore, build, and test the solution.",
            },
            {
                "id": "AC-09.3",
                "text": "The verification instructions state the required .NET SDK version.",
            },
        ],
    },
    {
        "id": "QR-02",
        "priority": "Must",
        "title": "Keep the solution readable",
        "body": [
            "The brief asks for clean code that is easy to read and understand. Acceptance uses observable checks rather than a style preference.",
        ],
        "criteria": [
            {
                "id": "AC-10.1",
                "text": "The verification instructions name the project, type, and method a reviewer should read first.",
            },
            {
                "id": "AC-10.2",
                "text": "The method name, or the names immediately around it, tell a reader that the method finds the longest increasing run.",
            },
            {
                "id": "AC-10.3",
                "text": "<font face=\"Mono\">dotnet build</font> completes with no compiler errors. Any compiler warning that remains is explained in the verification instructions.",
            },
            {
                "id": "AC-10.4",
                "text": "The eleven published results are produced by the run algorithm. A table that maps those eleven inputs to their outputs, and does not implement the rule, fails AC-08.3.",
            },
        ],
    },
    {
        "id": "QR-03",
        "priority": "Must",
        "title": "Unit-test the function",
        "body": [
            "The brief asks the author to demonstrate unit testing. The automated suite is the evidence. Tests call the function directly. A manual console session is not a substitute for the suite.",
        ],
        "criteria": [
            {
                "id": "AC-11.1",
                "text": "The suite includes AT-01 through AT-11. Each test asserts exact equality with the expected string in Section 8.",
            },
            {
                "id": "AC-11.2",
                "text": "<font face=\"Mono\">dotnet test</font> exits successfully when those tests pass.",
            },
            {
                "id": "AC-11.3",
                "text": "The tests are deterministic. They do not depend on the network, the clock, or a particular machine name.",
            },
            {
                "id": "AC-11.4",
                "text": "A failing published case causes <font face=\"Mono\">dotnet test</font> to fail.",
            },
        ],
    },
    {
        "id": "SR-01",
        "priority": "Must",
        "title": "Publish a public GitHub repository named with a UUID",
        "body": [
            "The brief asks for a public GitHub repository. The repository name is a UUID version 4, in the canonical hyphenated textual form recommended by the generator linked from the brief. Lower-case hexadecimal is the accepted form.",
        ],
        "criteria": [
            {
                "id": "AC-12.1",
                "text": "The repository is on GitHub and its visibility is public. The code is visible without signing in.",
            },
            {
                "id": "AC-12.2",
                "text": 'The repository name matches this lowercase pattern, and nothing else:<br/><font face="Mono" size="7.5">^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$</font>',
            },
        ],
    },
    {
        "id": "SR-02",
        "priority": "Must",
        "title": "Commit while the solution is being developed",
        "body": [
            "The brief asks the author to keep committing as the solution is developed, and then to share the repository URL with the person who set the exercise.",
        ],
        "criteria": [
            {
                "id": "AC-13.1",
                "text": "The default branch contains at least two commits that add or change C# source or test files. A history whose only solution commit is one finished snapshot does not meet this criterion.",
            },
            {
                "id": "AC-13.2",
                "text": "The repository URL has been given to the person who set the exercise. Acceptance of the submission is recorded by that person.",
            },
        ],
    },
    {
        "id": "SR-03",
        "priority": "Must",
        "title": "Leave the commissioning organisation unnamed",
        "body": [
            "The brief says not to commit the company name in any documentation or code. This baseline does not repeat that name. The check covers files in the repository and the commit messages on the submitted history.",
        ],
        "criteria": [
            {
                "id": "AC-14.1",
                "text": "A case-insensitive search of the repository files and of <font face=\"Mono\">git log</font> does not find the name of the organisation that issued the exercise.",
            },
        ],
    },
    {
        "id": "VR-01",
        "priority": "Must",
        "title": "Tell a reviewer how to verify the solution",
        "body": [
            "The brief asks for clear instructions on how to verify the solution. A reviewer who has the required .NET SDK, and nothing else installed for this exercise, can follow those instructions from a clean checkout.",
            "Docker, continuous integration, linting, and coverage are secondary. The primary instructions stand on their own when those extras are absent.",
        ],
        "criteria": [
            {
                "id": "AC-15.1",
                "text": "The instructions include the SDK version, the build command, the test command, and the location of the function under test.",
            },
            {
                "id": "AC-15.2",
                "text": "A reviewer who follows the instructions reaches a successful <font face=\"Mono\">dotnet test</font> run on a checkout of the submitted commit.",
            },
            {
                "id": "AC-15.3",
                "text": "The instructions are in the repository. They do not depend on a private document or an unstated local path.",
            },
        ],
    },
    {
        "id": "NR-01",
        "priority": "Should",
        "title": "Build and test continuously with GitHub Actions",
        "body": [
            "A secondary objective is continuous integration with GitHub Actions. This criterion is scored. It does not overturn a solution that meets every Must criterion.",
        ],
        "criteria": [
            {
                "id": "AC-16.1",
                "text": "A workflow file under <font face=\"Mono\">.github/workflows</font> runs on push to the default branch.",
            },
            {
                "id": "AC-16.2",
                "text": "That workflow builds the solution and runs the unit tests, including AT-01 through AT-11.",
            },
            {
                "id": "AC-16.3",
                "text": "The workflow run for the submitted commit succeeds on GitHub.",
            },
        ],
    },
    {
        "id": "NR-02",
        "priority": "Should",
        "title": "Containerise the solution with Docker",
        "body": [
            "A secondary objective is containerisation with Docker. The image builds from the repository using a documented command.",
        ],
        "criteria": [
            {
                "id": "AC-17.1",
                "text": "The repository contains a Dockerfile, and the verification instructions include the <font face=\"Mono\">docker build</font> command.",
            },
            {
                "id": "AC-17.2",
                "text": "Following those instructions produces an image. A documented command runs the unit tests in that image, or runs the function against a published case and shows the expected string.",
            },
        ],
    },
    {
        "id": "NR-03",
        "priority": "Should",
        "title": "Lint the code",
        "body": [
            "A secondary objective is code linting. The tool is the author’s choice. <font face=\"Mono\">dotnet format</font>, editorconfig rules, and Roslyn analyzers all qualify when the command is documented and it is actually run.",
        ],
        "criteria": [
            {
                "id": "AC-18.1",
                "text": "The repository configures a linter and the instructions include the command that runs it.",
            },
            {
                "id": "AC-18.2",
                "text": "Running that command on the submitted commit reports no remaining issues, or the workflow in NR-01 runs the same command and succeeds.",
            },
        ],
    },
    {
        "id": "NR-04",
        "priority": "Should",
        "title": "Report code coverage",
        "body": [
            "A secondary objective is code coverage reporting. The brief sets no percentage threshold, and this baseline does not add one. The report has to be produced, and the published cases have to be part of the run being measured.",
        ],
        "criteria": [
            {
                "id": "AC-19.1",
                "text": "A documented command produces a coverage report for the unit-test run.",
            },
            {
                "id": "AC-19.2",
                "text": "The measured run includes AT-01 through AT-11. The instructions say where the report is written.",
            },
        ],
    },
]


class SpecDoc(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs):
        super().__init__(filename, **kwargs)
        self._heading_seq = 0
        self._seen_h1 = False

    def beforeDocument(self):
        super().beforeDocument()
        self._heading_seq = 0
        self._seen_h1 = False

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ("H1", "H2"):
            level = 0 if flowable.style.name == "H1" else 1
            if level == 0:
                self._seen_h1 = True
            elif not self._seen_h1:
                level = 0
            text = flowable.getPlainText()
            key = f"h{self._heading_seq}"
            self._heading_seq += 1
            self.canv.bookmarkPage(key)
            try:
                self.canv.addOutlineEntry(text, key, level=level, closed=0)
            except Exception:
                self.canv.addOutlineEntry(text, key, level, 0)
            self.notify("TOCEntry", (level, text, self.page, key))


def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, 68 * mm, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(68 * mm, 0, 1.6 * mm, PAGE_H, stroke=0, fill=1)

    canvas.setFillColor(HexColor("#E7E1D4"))
    canvas.setFont("Inter-Med", 8.5)
    canvas.drawString(12 * mm, PAGE_H - 28 * mm, "SRS-LIS-001")
    canvas.setStrokeColor(HexColor("#3E625C"))
    canvas.setLineWidth(0.6)
    canvas.line(12 * mm, PAGE_H - 32 * mm, 56 * mm, PAGE_H - 32 * mm)
    canvas.setFillColor(WHITE)
    canvas.setFont("Inter", 9)
    canvas.drawString(12 * mm, PAGE_H - 42 * mm, "Acceptance")
    canvas.drawString(12 * mm, PAGE_H - 47 * mm, "baseline")
    canvas.setFont("Inter", 8.5)
    canvas.setFillColor(HexColor("#D5DDD9"))
    canvas.drawString(12 * mm, 22 * mm, "17 October 2026")
    canvas.drawString(12 * mm, 16 * mm, "Version 1.0")

    canvas.setFillColor(FAINT)
    canvas.setFont("Inter", 8)
    canvas.drawRightString(PAGE_W - 14 * mm, 12 * mm, "Page 1")
    canvas.restoreState()


def draw_body(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 8 * mm, PAGE_W, 8 * mm, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(0, PAGE_H - 9.2 * mm, PAGE_W, 1.2 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Inter", 8)
    canvas.drawString(16 * mm, PAGE_H - 5.4 * mm, "SRS-LIS-001")
    canvas.setFont("Inter", 8)
    canvas.drawRightString(PAGE_W - 16 * mm, PAGE_H - 5.4 * mm, "Longest increasing run")

    canvas.setFillColor(FAINT)
    canvas.setFont("Inter", 8)
    canvas.drawString(16 * mm, 8 * mm, "Acceptance baseline  ·  17 October 2026")
    canvas.drawRightString(PAGE_W - 16 * mm, 8 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(16 * mm, 13 * mm, PAGE_W - 16 * mm, 13 * mm)
    canvas.restoreState()


def meta_table() -> Table:
    rows = [
        ("Document", "Requirements specification and acceptance criteria"),
        ("Identifier", "SRS-LIS-001"),
        ("Version", "1.0"),
        ("Date", "17 October 2026"),
        ("Status", "Baseline for acceptance"),
        ("Source", "code-test.md, the coding-exercise brief"),
        ("Subject", "Longest strictly increasing run"),
        ("Platform", "C# on .NET"),
    ]
    data = []
    for label, value in rows:
        data.append([Paragraph(label, S["meta_label"]), Paragraph(esc(value), S["meta_value"])])
    table = Table(data, colWidths=[28 * mm, 78 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LINEBELOW", (0, 0), (-1, -2), 0.2, LINE),
            ]
        )
    )
    return table


def index_table() -> Table:
    headers = ["Index", "0", "1", "2", "3", "4", "5", "6", "7"]
    values = ["Value", "6", "2", "4", "6", "1", "5", "9", "2"]
    run_a = ["Run A", "", "2", "4", "6", "", "", "", ""]
    run_b = ["Run B", "", "", "", "", "1", "5", "9", ""]
    head = [Paragraph(h, S["cell_head"]) for h in headers]
    def row(cells, emphasis=None):
        out = []
        for i, cell in enumerate(cells):
            style = S["cell_id"] if i == 0 else S["cell"]
            text = f"<b>{esc(cell)}</b>" if emphasis and i in emphasis and cell else esc(cell)
            out.append(Paragraph(text, style))
        return out
    table = Table(
        [head, row(values), row(run_a, {2, 3, 4}), row(run_b, {5, 6, 7})],
        colWidths=[22 * mm] + [19 * mm] * 8,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("BACKGROUND", (0, 1), (0, -1), PAPER),
                ("BACKGROUND", (2, 2), (4, 2), HexColor("#E5F0EC")),
                ("BACKGROUND", (5, 3), (7, 3), HexColor("#F4EFE4")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.3, LINE),
                ("LINEBEFORE", (2, 2), (2, 2), 1.5, TEAL_MID),
                ("LINEAFTER", (4, 2), (4, 2), 1.5, TEAL_MID),
            ]
        )
    )
    return table


def case_summary_table() -> Table:
    rows = []
    for case in CASES:
        rows.append(
            [
                Paragraph(case["id"], S["cell_id"]),
                Paragraph(f"{case['count']:,}", S["cell"]),
                Paragraph(str(case["output_length"]), S["cell"]),
                Paragraph(f'<font face="Mono" size="7.5">{esc(case["expected"])}</font>', S["cell"]),
            ]
        )
    return shaded_table(
        ["Case", "Input integers", "Result length", "Expected output"],
        rows,
        [22 * mm, 32 * mm, 28 * mm, 92 * mm],
    )


def digest_table() -> Table:
    rows = []
    for case in CASES:
        rows.append(
            [
                Paragraph(case["id"], S["cell_id"]),
                Paragraph(f'<font face="Mono" size="6.6">{case["sha256"]}</font>', S["cell"]),
            ]
        )
    return shaded_table(["Case", "SHA-256 of the exact input string"], rows, [22 * mm, 152 * mm])


def short_case_blocks() -> list:
    flow = []
    for case in CASES:
        if len(case["input"]) > 1500:
            continue
        block = [
            P(f'<b>{case["id"]}</b>  ·  {case["count"]} integers  ·  result length {case["output_length"]}', "h3"),
            P("Input", "small"),
            code_block(case["input"]),
            Spacer(1, 3),
            P("Expected output", "small"),
            code_block(case["expected"]),
            Spacer(1, 6),
        ]
        flow.append(KeepTogether(block))
    return flow


def long_case_notes() -> list:
    flow = [P("The remaining published inputs are identified by digest, length, and a short preview. The full string is in the fixture file.", "body")]
    rows = []
    for case in CASES:
        if len(case["input"]) <= 1500:
            continue
        numbers = case["input"].split()
        preview = " ".join(numbers[:4]) + " … " + " ".join(numbers[-3:])
        rows.append(
            [
                Paragraph(case["id"], S["cell_id"]),
                Paragraph(f"{case['count']:,}", S["cell"]),
                Paragraph(f'<font face="Mono" size="7">{esc(preview)}</font>', S["cell"]),
                Paragraph(f'<font face="Mono" size="7">{esc(case["expected"])}</font>', S["cell"]),
            ]
        )
    flow.append(
        shaded_table(
            ["Case", "Count", "Preview", "Expected output"],
            rows,
            [18 * mm, 18 * mm, 78 * mm, 60 * mm],
        )
    )
    flow.append(P("Preview shows the first four integers, then the last three. It is a reading aid. The digest is the identity check.", "caption"))
    return flow


def rule_table() -> Table:
    rows = []
    for check in RULE_CHECKS:
        rows.append(
            [
                Paragraph(check["id"], S["cell_id"]),
                Paragraph(esc(check["purpose"]), S["cell"]),
                Paragraph(f'<font face="Mono" size="7">{esc(check["input"])}</font>', S["cell"]),
                Paragraph(f'<font face="Mono" size="7">{esc(check["expected"])}</font>', S["cell"]),
            ]
        )
    return shaded_table(
        ["Check", "What it fixes", "Input", "Expected"],
        rows,
        [16 * mm, 70 * mm, 46 * mm, 42 * mm],
    )


def checklist_table() -> Table:
    rows = []
    for item in REQUIREMENTS:
        for criterion in item["criteria"]:
            rows.append(
                [
                    Paragraph(criterion["id"], S["cell_id"]),
                    Paragraph(item["priority"], S["cell"]),
                    Paragraph(esc(item["title"]), S["check"]),
                ]
            )
    table = shaded_table(["Criterion", "Priority", "Requirement"], rows, [24 * mm, 22 * mm, 128 * mm])
    return table


def decision_table() -> Table:
    rows = [
        [
            Paragraph("D-01", S["cell_id"]),
            Paragraph("The accepted sequence is a contiguous run.", S["cell"]),
            Paragraph(
                "AT-10 requires <font face=\"Mono\">2 4 6</font>. Skipping values produces a longer selection and fails the published output.",
                S["cell"],
            ),
        ],
        [
            Paragraph("D-02", S["cell_id"]),
            Paragraph("Earliest means the smallest starting index.", S["cell"]),
            Paragraph(
                "The brief says to output the earliest sequence when several share the longest length. On AT-10, <font face=\"Mono\">2 4 6</font> starts before <font face=\"Mono\">1 5 9</font>.",
                S["cell"],
            ),
        ],
        [
            Paragraph("D-03", S["cell_id"]),
            Paragraph("An increase is strict.", S["cell"]),
            Paragraph(
                "“Increased by any number” is a positive change of any size. An equal neighbour has not increased. RC-05 makes that rule testable, because the published suite has no adjacent equals.",
                S["cell"],
            ),
        ],
    ]
    return shaded_table(["Decision", "Rule", "Why it is fixed this way"], rows, [20 * mm, 52 * mm, 102 * mm])


def build_story(toc) -> list:
    story: list = []
    story.append(NextPageTemplate("Body"))
    story.append(Spacer(1, 18 * mm))
    story.append(P("CODING EXERCISE", "cover_kicker"))
    story.append(P("Requirements specification<br/>and acceptance criteria", "cover_title"))
    story.append(P("Longest increasing run", "cover_sub"))
    story.append(
        P(
            "This baseline turns the coding-exercise brief into checks a reviewer can mark pass or fail. "
            "It covers the function, the eleven published cases, the C# submission, and the secondary engineering objectives.",
            "cover_deck",
        )
    )
    story.append(Spacer(1, 6 * mm))
    story.append(meta_table())
    story.append(Spacer(1, 8 * mm))
    story.append(
        P(
            "A solution is accepted when every Must criterion passes. Should criteria are scored and recorded. "
            "They do not overturn a solution that meets every Must criterion.",
            "cover_deck",
        )
    )
    story.append(PageBreak())

    story.append(P("Contents", "contents"))
    story.append(rule())
    story.append(toc)
    story.append(Spacer(1, 6))
    story.append(P("How to read the identifiers", "h2"))
    story.append(
        P(
            "<b>Must</b> items are required for acceptance. <b>Should</b> items are the brief’s secondary objectives. "
            "FR is a functional requirement, QR a quality requirement, SR a submission requirement, VR a verification requirement, and NR a secondary objective. "
            "AT is a published case from the brief. RC is a rule check that makes the general rule testable beyond those eleven strings. "
            "AC is an acceptance criterion. D is an interpretation decision."
        )
    )
    story.append(PageBreak())

    story.append(P("1. Purpose and authority", "h1"))
    story.extend(section_rule())
    story.append(P("1.1 Purpose", "h2"))
    story.append(
        P(
            "This document is the acceptance baseline for the coding exercise in <b>code-test.md</b>. "
            "A reviewer uses it to decide whether a submitted C# solution meets the brief. "
            "The author of a solution uses it to see which behaviour, tests, and repository conditions are required."
        )
    )
    story.append(P("1.2 What the brief asks for", "h2"))
    story.append(
        P(
            "The primary objective is a working solution that shows C# and .NET, readable code, unit tests, and instructions a reviewer can follow. "
            "The problem is one function. It receives a string of integers separated by single spaces and returns the longest increasing subsequence. "
            "When more than one subsequence has that longest length, the function returns the earliest. Supporting functions are allowed. "
            "The function must pass the eleven cases in the brief."
        )
    )
    story.append(
        P(
            "The secondary objectives are GitHub Actions, Docker, linting, and coverage reporting. "
            "They are scored separately in Section 7."
        )
    )
    story.append(
        P(
            "The submission is a public GitHub repository whose name is a UUID version 4. "
            "Work is committed as it proceeds. The commissioning organisation’s name is left out of the code, the documentation, and the history. "
            "When the work is finished, the repository URL is sent to the person who set the exercise."
        )
    )
    story.append(P("1.3 Authority", "h2"))
    story.append(
        P(
            "The published inputs and outputs are normative. Section 2 records three decisions that are required to apply those outputs consistently. "
            "Where a textbook reading of “subsequence” would allow skipped values, the published output of AT-10 is the authority."
        )
    )
    story.append(
        P(
            "This document does not name the organisation that issued the exercise."
        )
    )
    story.append(P("1.4 Acceptance decision", "h2"))
    story.append(
        P(
            "Mark each Must criterion pass or fail. The solution is accepted only when every Must criterion passes. "
            "One failed published case is enough to reject the functional behaviour. "
            "Record each Should criterion as met or not met. A missing Dockerfile, workflow, linter, or coverage report leaves the primary decision unchanged."
        )
    )

    story.append(P("2. Normative interpretation", "h1"))
    story.extend(section_rule())
    story.append(P("2.1 Terms", "h2"))
    story.append(
        shaded_table(
            ["Term", "Meaning in this baseline"],
            [
                [Paragraph("Input sequence", S["cell"]), Paragraph("The integers produced by splitting the input on a single space and reading each token as a base-10 integer.", S["cell"])],
                [Paragraph("Run", S["cell"]), Paragraph("A contiguous segment. Order is preserved and no integer between the ends of the segment is left out.", S["cell"])],
                [Paragraph("Strictly increasing", S["cell"]), Paragraph("Each value after the first is greater than the value immediately before it. The difference may be any positive number.", S["cell"])],
                [Paragraph("Length", S["cell"]), Paragraph("The number of integers in the run.", S["cell"])],
                [Paragraph("Earliest", S["cell"]), Paragraph("Among runs of equal length, the run whose first integer has the smallest index.", S["cell"])],
                [Paragraph("Observable result", S["cell"]), Paragraph("The space-separated base-10 string a test compares with the expected output. No leading or trailing whitespace.", S["cell"])],
                [Paragraph("Published case", S["cell"]), Paragraph("One of AT-01 through AT-11, taken from the fenced examples in the brief, in that order.", S["cell"])],
            ],
            [36 * mm, 138 * mm],
        )
    )
    story.append(Spacer(1, 8))
    story.append(P("2.2 Decisions", "h2"))
    story.append(
        P(
            "These three decisions are part of the baseline. They exist so that two reviewers, working from the brief alone, reach the same pass or fail."
        )
    )
    story.append(decision_table())
    story.append(Spacer(1, 8))
    story.append(P("2.3 Worked example: AT-10", "h2"))
    story.append(
        P(
            "Input <font face=\"Mono\">6 2 4 6 1 5 9 2</font>. The contiguous strictly increasing runs include Run A, <font face=\"Mono\">2 4 6</font>, and Run B, <font face=\"Mono\">1 5 9</font>. Both have length 3. Run A starts earlier."
        )
    )
    story.append(Spacer(1, 2))
    story.append(index_table())
    story.append(P("Run A is the required result. Run B is a longest run that starts later, so it is not returned.", "caption"))
    story.append(
        P(
            "A selection such as <font face=\"Mono\">2 4 5 9</font> skips the second 6 and is longer than Run A. It is not a run under D-01, and it is not the published output."
        )
    )
    story.append(P("2.4 Worked example: AT-11", "h2"))
    story.append(
        P(
            "Input <font face=\"Mono\">6 2 4 3 1 5 9</font>. The runs are <font face=\"Mono\">6</font>, <font face=\"Mono\">2 4</font>, <font face=\"Mono\">3</font>, and <font face=\"Mono\">1 5 9</font>. "
            "The longest run is <font face=\"Mono\">1 5 9</font>. The earlier run <font face=\"Mono\">2 4</font> is shorter, so the tie-break does not apply. The required output is <font face=\"Mono\">1 5 9</font>."
        )
    )
    story.append(P("2.5 Worked example: AT-01", "h2"))
    story.append(
        P(
            "Input <font face=\"Mono\">6 1 5 9 2</font>. The longest run is <font face=\"Mono\">1 5 9</font>. The leading 6 is a run of length 1, and the final 2 does not extend <font face=\"Mono\">1 5 9</font>."
        )
    )

    story.append(P("3. Functional requirements", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "Each requirement states the behaviour and the criteria that demonstrate it. "
            "Examples written with a monospaced face are exact strings."
        )
    )
    for item in REQUIREMENTS:
        if not item["id"].startswith("FR-"):
            continue
        story.extend(requirement_block(item))

    story.append(P("4. Solution and engineering requirements", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "These requirements come from the primary objectives in the brief: C# and .NET, readable code, and unit tests."
        )
    )
    for item in REQUIREMENTS:
        if item["id"].startswith("QR-"):
            story.extend(requirement_block(item))

    story.append(P("5. Repository and submission requirements", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "These requirements come from the “Get started” instructions in the brief."
        )
    )
    for item in REQUIREMENTS:
        if item["id"].startswith("SR-"):
            story.extend(requirement_block(item))

    story.append(P("6. Verification requirements", "h1"))
    story.extend(section_rule())
    for item in REQUIREMENTS:
        if item["id"].startswith("VR-"):
            story.extend(requirement_block(item))

    story.append(P("7. Secondary objectives", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "The brief lists these as secondary objectives. Each one has acceptance criteria so it can be marked met or not met. "
            "None of them is required for the primary acceptance decision in Section 1.4."
        )
    )
    for item in REQUIREMENTS:
        if item["id"].startswith("NR-"):
            story.extend(requirement_block(item))

    story.append(P("8. Published acceptance tests", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "The eleven cases below are the fenced examples in the brief, in the order they appear. "
            "AT-01 is the first example and AT-11 is the last. The expected string is exact."
        )
    )
    story.append(case_summary_table())
    story.append(Spacer(1, 4))
    story.append(
        P(
            "Across the eleven inputs there are 16,340 integers. The smallest published value is 1 and the largest is 32,762. "
            "No published input contains a zero, a negative, or two equal neighbours."
        )
    )
    story.append(P("8.1 Input identity", "h2"))
    story.append(
        P(
            "Compute SHA-256 over the UTF-8 bytes of the input string. Do not include a byte-order mark or a trailing newline. "
            "The digest must equal the value in this table. The same strings are stored in <font face=\"Mono\">acceptance-fixtures.json</font>."
        )
    )
    story.append(digest_table())
    story.append(Spacer(1, 8))
    story.append(P("8.2 Short inputs in full", "h2"))
    story.append(
        P(
            "AT-01, AT-04, AT-05, AT-06, AT-10, and AT-11 are short enough to print in full. "
            "Copying from the fixture file is the reliable way to obtain the exact bytes."
        )
    )
    story.extend(short_case_blocks())
    story.append(P("8.3 Long inputs", "h2"))
    story.extend(long_case_notes())

    story.append(P("9. Rule checks", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "These checks are not printed in the brief. They are acceptance criteria for the general rule in Section 3. "
            "A solution that returns the eleven published strings and fails a rule check has memorised the sample list. That solution fails AC-08.3."
        )
    )
    story.append(
        P(
            "The submitted unit tests must include AT-01 through AT-11. They may also include these rule checks. "
            "Whether or not the author added them, the function must return the expected string when a reviewer calls it with the input below."
        )
    )
    story.append(CondPageBreak(125 * mm))
    story.append(rule_table())
    story.append(Spacer(1, 6))
    story.append(
        P(
            "RC-01 through RC-08 are included in <font face=\"Mono\">acceptance-fixtures.json</font> under <font face=\"Mono\">ruleChecks</font>."
        )
    )

    story.append(P("10. Traceability", "h1"))
    story.extend(section_rule())
    story.append(
        P(
            "The register lists every acceptance criterion in this baseline. Use it as the review checklist. "
            "Priority follows the parent requirement."
        )
    )
    story.append(checklist_table())
    story.append(Spacer(1, 8))
    story.append(
        shaded_table(
            ["Source in the brief", "Where it is tested"],
            [
                [Paragraph("Longest increasing subsequence, earliest on a tie", S["cell"]), Paragraph("FR-02, FR-03, FR-04, D-01, D-02, AT-01 to AT-11", S["cell"])],
                [Paragraph("One string of integers separated by single whitespace", S["cell"]), Paragraph("FR-01, FR-05, Section 8", S["cell"])],
                [Paragraph("Pass the supplied test cases", S["cell"]), Paragraph("FR-08, AC-08.1, AC-11.1", S["cell"])],
                [Paragraph("Supporting functions are allowed", S["cell"]), Paragraph("FR-01. No layout or algorithm is mandated.", S["cell"])],
                [Paragraph("C# .NET, readable code, unit tests, verification instructions", S["cell"]), Paragraph("QR-01, QR-02, QR-03, VR-01", S["cell"])],
                [Paragraph("Public GitHub repository named with a UUID, incremental commits, share the URL", S["cell"]), Paragraph("SR-01, SR-02", S["cell"])],
                [Paragraph("Do not commit the company name", S["cell"]), Paragraph("SR-03. The name is intentionally absent from this baseline.", S["cell"])],
                [Paragraph("GitHub Actions, Docker, linting, coverage", S["cell"]), Paragraph("NR-01 to NR-04. Secondary. Scored, not gating.", S["cell"])],
            ],
            [78 * mm, 96 * mm],
        )
    )

    story.append(P("11. Assumptions and exclusions", "h1"))
    story.extend(section_rule())
    story.append(P("11.1 Assumptions", "h2"))
    assumptions = [
        "Well-formed published inputs use a single space between integers and contain no leading or trailing space.",
        "The observable comparison is an exact string match against the expected output, including the spaces between numbers.",
        "A 32-bit signed integer can hold every published value. The baseline does not require arbitrary-precision arithmetic.",
        "The entry point may be a method on a class, a static method, or a function-shaped member. The instructions identify it.",
        "Returning a string, or returning the integers together with a documented rendering, are both acceptable when the observable string matches.",
        "Rule checks RC-01 through RC-08 are in force even though the brief did not print them. They stop a lookup of the eleven samples from passing.",
    ]
    for line in assumptions:
        story.append(P("•  " + line, "body"))
    story.append(P("11.2 Exclusions", "h2"))
    story.append(
        P(
            "The brief does not define the following inputs. Behaviour on them is out of scope. A reviewer does not fail a solution for the way it handles them, and does not require a solution to handle them."
        )
    )
    exclusions = [
        "The empty string, or a string of only whitespace.",
        "Leading or trailing spaces, repeated spaces, tabs, or a newline inside the argument.",
        "Tokens that are not base-10 integers, including leading zeros, leading plus signs, decimal points, and thousands separators.",
        "Integers outside the range of a 32-bit signed integer.",
        "A performance budget, a required algorithmic complexity, or a coverage percentage.",
        "A required function name, a required console interface, or a required project layout.",
        "Authentication, persistence, a user interface, or any behaviour other than the function and the submission conditions in this baseline.",
    ]
    for line in exclusions:
        story.append(P("•  " + line, "body"))
    story.append(P("11.3 Fixture file", "h2"))
    story.append(
        P(
            "<font face=\"Mono\">acceptance-fixtures.json</font> is embedded in this PDF and is also stored in the Downloads folder beside it. "
            "It contains every published input, every expected output, every digest, and the eight rule checks. "
            "A test project may load that file. The strings there are the same strings hashed in Section 8."
        )
    )
    story.append(Spacer(1, 8))
    story.append(rule())
    story.append(
        P(
            "End of SRS-LIS-001, version 1.0. The eleven published outputs and the three interpretation decisions are the functional baseline. "
            "The repository conditions in Sections 4 to 6 are required. The objectives in Section 7 are secondary.",
            "small",
        )
    )
    return story


def write_fixtures() -> None:
    payload = {
        "document": "SRS-LIS-001",
        "version": "1.0",
        "hash": "SHA-256 over the UTF-8 bytes of the string. No byte-order mark. No trailing newline.",
        "publishedCases": [
            {
                "id": case["id"],
                "input": case["input"],
                "expected": case["expected"],
                "sha256": case["sha256"],
                "elementCount": case["count"],
            }
            for case in CASES
        ],
        "ruleChecks": [
            {
                "id": check["id"],
                "purpose": check["purpose"],
                "input": check["input"],
                "expected": check["expected"],
                "sha256": sha256_text(check["input"]),
            }
            for check in RULE_CHECKS
        ],
    }
    FIXTURE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def embed_fixture(pdf_path: Path) -> None:
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    writer.append(reader)
    writer.add_attachment("acceptance-fixtures.json", FIXTURE_PATH.read_bytes())
    if reader.metadata:
        writer.add_metadata(reader.metadata)
    writer.add_metadata(
        {
            "/Title": "Requirements Specification and Acceptance Criteria — Longest Increasing Run",
            "/Subject": "SRS-LIS-001 version 1.0 acceptance baseline",
            "/Keywords": "SRS-LIS-001, acceptance criteria, longest increasing run",
        }
    )
    with pdf_path.open("wb") as handle:
        writer.write(handle)


def main() -> None:
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_fixtures()

    from reportlab.platypus.tableofcontents import TableOfContents

    toc = TableOfContents()
    toc.dotsMinLevel = 0
    toc.levelStyles = [S["toc_h"], S["toc_s"]]
    toc.tableStyle = TableStyle(
        [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]
    )

    doc = SpecDoc(
        str(PDF_PATH),
        pagesize=A4,
        title="Requirements Specification and Acceptance Criteria — Longest Increasing Run",
        author="SRS-LIS-001",
        subject="Acceptance baseline derived from the coding-exercise brief",
        creator="SRS-LIS-001",
    )
    cover_frame = Frame(
        82 * mm,
        16 * mm,
        PAGE_W - 82 * mm - 14 * mm,
        PAGE_H - 30 * mm,
        id="cover",
        showBoundary=0,
    )
    body_frame = Frame(
        16 * mm,
        18 * mm,
        PAGE_W - 32 * mm,
        PAGE_H - 18 * mm - 16 * mm,
        id="body",
        showBoundary=0,
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="Body", frames=[body_frame], onPage=draw_body),
        ]
    )
    passes = doc.multiBuild(build_story(toc))
    embed_fixture(PDF_PATH)
    print(f"Wrote {PDF_PATH} in {passes} passes")
    print(f"Wrote {FIXTURE_PATH}")


if __name__ == "__main__":
    main()
