"""Export the executive deck to PDF with matplotlib (no Office or LibreOffice needed)."""

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from .config import Settings
from .deck import (
    CHART_SLIDES,
    DARK,
    DECK_NAME,
    FOOTER,
    GREY,
    KPI_LABELS,
    SITUATION_CHART,
    SLIDE_H,
    SLIDE_W,
    fmt_kpi,
)
from .insights import Insights

PDF_NAME = Path(DECK_NAME).with_suffix(".pdf").name


def _rgb(color: tuple[int, int, int]) -> tuple[float, float, float]:
    return tuple(v / 255 for v in color)


class _Slide:
    """One 13.333 x 7.5 in page; coordinates are inches from the top-left, like the .pptx."""

    def __init__(self, title: str):
        self.fig = plt.figure(figsize=(SLIDE_W, SLIDE_H))
        self.text(0.6, 0.35, 12.1, [title], size=28, bold=True, color=DARK)
        self.text(0.6, 7.0, 8.0, [FOOTER], size=10)

    def text(self, x, y, w, lines, size=16, bold=False, color=GREY) -> float:
        """Draw wrapped paragraphs; returns the estimated height used, in inches."""
        chars = max(int(w * 72 / (size * (0.65 if bold else 0.55))), 8)
        wrapped = "\n".join(textwrap.fill(line, chars, break_long_words=False) for line in lines)
        self.fig.text(
            x / SLIDE_W,
            1 - y / SLIDE_H,
            wrapped,
            ha="left",
            va="top",
            fontsize=size,
            fontweight="bold" if bold else "normal",
            color=_rgb(color),
        )
        return (wrapped.count("\n") + 1) * size * 1.4 / 72

    def image(self, path: Path, x: float, y: float, w: float) -> None:
        img = plt.imread(str(path))
        h = w * img.shape[0] / img.shape[1]
        ax = self.fig.add_axes((x / SLIDE_W, 1 - (y + h) / SLIDE_H, w / SLIDE_W, h / SLIDE_H))
        ax.imshow(img)
        ax.axis("off")


def build_slides(ins: Insights, chart_dir: Path) -> list[Figure]:
    """Return one figure per slide, mirroring deck.build_deck. Caller closes the figures."""
    figs = []

    slide = _Slide(ins.titles["situation"])
    for i, (label, key) in enumerate(KPI_LABELS):
        x = 0.6 + i * 3.1
        slide.text(x, 1.35, 2.9, [fmt_kpi(key, ins.kpis[key])], size=30, bold=True, color=DARK)
        slide.text(x, 1.95, 2.9, [label], size=14)
    slide.image(chart_dir / SITUATION_CHART, 0.6, 2.5, 8.0)
    slide.text(9.0, 2.6, 3.8, ins.notes["situation"], size=15)
    figs.append(slide.fig)

    for key, image in CHART_SLIDES:
        slide = _Slide(ins.titles[key])
        slide.image(chart_dir / image, 0.6, 1.4, 8.6)
        slide.text(9.5, 1.6, 3.4, ins.notes[key], size=15)
        figs.append(slide.fig)

    slide = _Slide(ins.titles["recommendation"])
    for i, rec in enumerate(ins.recommendations):
        y = 1.5 + i * 1.8
        used = slide.text(
            0.6, y, 12.1, [f"{i + 1}. {rec['title']}"], size=20, bold=True, color=DARK
        )
        slide.text(0.9, y + used + 0.05, 11.8, [f"Evidence: {rec['evidence']}"], size=14)
    figs.append(slide.fig)

    return figs


def build_pdf(ins: Insights, chart_dir: Path, cfg: Settings) -> Path:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.output_dir / PDF_NAME
    figs = build_slides(ins, chart_dir)
    try:
        with PdfPages(path) as pdf:
            for fig in figs:
                pdf.savefig(fig)
    finally:
        for fig in figs:
            plt.close(fig)
    return path
