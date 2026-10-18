#!/usr/bin/env python3
"""Generate the GitHub Actions continuous-integration note."""

from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
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
    KeepTogether,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "Documents" / "Continuous-Integration-GitHub-Actions.pdf"
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
        "h1": ParagraphStyle("h1", fontName="Segoe-Bold", fontSize=18, leading=22, textColor=TEAL, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName="Segoe-Bold", fontSize=13, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="Segoe", fontSize=9.5, leading=13, textColor=INK, spaceAfter=6),
        "caption": ParagraphStyle("caption", fontName="Segoe-Italic", fontSize=8, leading=10.5, textColor=MUTED, spaceBefore=2, spaceAfter=8),
        "code": ParagraphStyle("code", fontName="Consolas", fontSize=8, leading=11, textColor=INK),
        "th": ParagraphStyle("th", fontName="Segoe-Bold", fontSize=8, leading=10, textColor=WHITE),
        "td": ParagraphStyle("td", fontName="Segoe", fontSize=8, leading=10.5, textColor=INK),
        "tdm": ParagraphStyle("tdm", fontName="Consolas", fontSize=7.5, leading=10, textColor=INK),
    }


S = styles()


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


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
    c.setLineWidth(1.1)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 6
    path = c.beginPath()
    path.moveTo(x2, y2)
    path.lineTo(x2 - size * math.cos(angle - 0.42), y2 - size * math.sin(angle - 0.42))
    path.lineTo(x2 - size * math.cos(angle + 0.42), y2 - size * math.sin(angle + 0.42))
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def _box(c, x, y, w, h, text, fill, stroke, font="Segoe", size=8, color=INK):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    lines = text.split("\n")
    leading = size + 2
    total = leading * len(lines)
    top = y + (h + total) / 2 - leading + 1
    c.setFillColor(color)
    c.setFont(font, size)
    for index, line in enumerate(lines):
        c.drawCentredString(x + w / 2, top - index * leading, line)


def paint_pipeline(c, w, h):
    c.setFillColor(PAPER)
    c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
    steps = [
        ("Push or pull request", TEAL, WHITE, "Segoe-Bold"),
        ("GitHub starts workflow ci", TEAL_SOFT, TEAL, "Segoe"),
        ("Checkout the commit", WHITE, TEAL_MID, "Segoe"),
        ("Install the .NET 9 SDK from global.json", WHITE, TEAL_MID, "Segoe"),
        ("Restore max-run.slnx", WHITE, TEAL_MID, "Segoe"),
        ("Lint: dotnet format --verify-no-changes", GOLD_SOFT, GOLD, "Segoe"),
        ("Test in Release and write coverage", TEAL_SOFT, TEAL, "Segoe"),
        ("Upload the coverage artifact", TEAL, WHITE, "Segoe-Bold"),
    ]
    box_w = 280
    box_h = 24
    x = (w - box_w) / 2
    y = h - 36
    for text, fill, color, font in steps:
        _box(c, x, y, box_w, box_h, text, fill, TEAL_MID if fill != TEAL else TEAL, font, 8, color)
        if y > 20:
            _arrow(c, w / 2, y, w / 2, y - 12)
        y -= 36

    fail_x = x + box_w + 16
    fail_w = w - fail_x - 12
    _box(c, fail_x, h - 36 - 36 * 5, fail_w, 48, "Lint or tests fail\nThe run stops\nThe check is red", CLAY_SOFT, CLAY, "Segoe", 7.5, CLAY)
    lint_mid_y = h - 36 - 36 * 5 + 12
    _arrow(c, x + box_w, lint_mid_y, fail_x, h - 36 - 36 * 5 + 24, CLAY)


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 12 * mm, PAGE_W, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Segoe", 8)
    canvas.drawString(LEFT, PAGE_H - 7.5 * mm, "Longest strictly increasing run")
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7.5 * mm, "Continuous integration")
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Segoe", 8)
    canvas.drawString(LEFT, 4 * mm, ".github/workflows/ci.yml")
    canvas.drawRightString(PAGE_W - RIGHT, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def command_block(text: str) -> Preformatted:
    block = Preformatted(text, S["code"], maxLineLength=88)
    data = [[block]]
    table = Table(data, colWidths=[CONTENT_W])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def data_table(header: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    head = [Paragraph(cell, S["th"]) for cell in header]
    body = [[Paragraph(cell, S["td"]) for cell in row] for row in rows]
    table = Table([head] + body, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
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


def build_story() -> list:
    story: list = []
    story.append(Spacer(1, 2))
    story.append(P("Continuous integration", "h1"))
    story.append(
        P(
            "GitHub Actions runs the same restore, lint, and coverage commands that can be run on a workstation. "
            "The workflow file is <font face='Consolas'>.github/workflows/ci.yml</font>. "
            "The job is named <font face='Consolas'>build</font> and the workflow is named <font face='Consolas'>ci</font>."
        )
    )
    story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=1, spaceAfter=6))

    story.append(P("When GitHub runs it", "h2"))
    story.append(
        P(
            "A run starts for every push, including a push to the default branch, and for every pull request. "
            "GitHub checks out that commit on a fresh <font face='Consolas'>ubuntu-latest</font> machine. "
            "Nothing from a previous run is kept on the machine. The coverage report is the only file kept afterwards, and it is stored as a downloadable artifact, not as a commit."
        )
    )
    story.append(Drawing(300, paint_pipeline))
    story.append(P("Figure 1. GitHub starts the build job after a push or pull request. A failed lint or test stops the run.", "caption"))

    story.append(P("What each step does", "h2"))
    story.append(
        data_table(
            ["Step", "What happens", "If it fails"],
            [
                ["Checkout", "actions/checkout@v4 copies the commit onto the runner.", "The run stops. Later steps do not start."],
                ["Install .NET SDK", "actions/setup-dotnet@v4 reads global.json and installs SDK 9.0.319, or a newer 9.x SDK.", "The run stops before restore."],
                ["Restore", "dotnet restore max-run.slnx downloads the test packages.", "The run stops. Lint and tests are skipped."],
                ["Lint", "dotnet format checks the tree against EditorConfig and changes nothing.", "The check on the commit turns red. The diff that format would have made is in the step log."],
                ["Test with coverage", "Release tests run. coverlet writes a Cobertura report for the LongestIncreasingRun assembly.", "A failed test or a build warning stops the run. The log names the test."],
                ["Upload coverage", "The coverage directory is saved as an artifact named coverage.", "The step fails if that directory is missing."],
            ],
            [CONTENT_W * 0.20, CONTENT_W * 0.46, CONTENT_W * 0.34],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        P(
            "Warnings are errors, so a compiler warning fails the test step. "
            "A clean lint prints that no files were formatted and exits 0. "
            "The coverage file is <font face='Consolas'>coverage/&lt;guid&gt;/coverage.cobertura.xml</font>. "
            "<font face='Consolas'>coverage/</font> is listed in <font face='Consolas'>.gitignore</font>, so the report is not committed."
        )
    )

    story.append(
        KeepTogether(
            [
                P("How to run the same checks locally", "h2"),
                P(
                    "Install the .NET SDK 9. From the repository root, run the three commands the workflow runs. "
                    "The local lint command restores as well, because a separate restore step is not required on a workstation."
                ),
                command_block(
                    "dotnet restore max-run.slnx\n"
                    "dotnet format max-run.slnx --verify-no-changes\n"
                    "dotnet test max-run.slnx -c Release --settings coverage.runsettings ^\n"
                    "  --collect:\"XPlat Code Coverage\" --results-directory ./coverage"
                ),
            ]
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "On macOS or Linux, replace the caret with a backslash. "
            "The test command prints the path of <font face='Consolas'>coverage.cobertura.xml</font>. "
            "Open that file to see the line rate and branch rate for <font face='Consolas'>LongestIncreasingRunFinder</font>."
        )
    )

    story.append(P("What you see on GitHub", "h2"))
    story.append(
        P(
            "Open the repository, then the <font face='Segoe-Bold'>Actions</font> tab. "
            "Each push and each pull request has a run titled <font face='Consolas'>ci</font>. "
            "The row shows the branch, the commit, and who started it."
        )
    )
    story.append(
        data_table(
            ["Where", "What you find"],
            [
                ["Actions, then the ci run", "A green tick when every step exited 0. A red cross when one step failed."],
                ["The build job", "One log per step. Open Lint or Test with coverage to read the command output."],
                ["Artifacts, coverage", "A zip of the coverage directory. It is kept with the run and is not added to the repository."],
                ["The commit or pull request", "The same green tick or red cross, beside the commit message and in the pull request checks."],
            ],
            [CONTENT_W * 0.32, CONTENT_W * 0.68],
        )
    )
    story.append(Spacer(1, 6))
    story.append(
        P(
            "A failed run does not change the code. Fix the formatting or the test on a new commit and push again. "
            "GitHub starts a new run for that commit. The earlier red run stays in the Actions list as history."
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
        title="Continuous integration with GitHub Actions",
        author="LongestIncreasingRun",
    )
    frame = Frame(LEFT, 16 * mm, CONTENT_W, PAGE_H - 34 * mm, id="body", showBoundary=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])
    doc.build(build_story())
    print(PDF_PATH)


if __name__ == "__main__":
    main()
