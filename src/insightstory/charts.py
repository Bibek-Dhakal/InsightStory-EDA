"""Minimalist charts. Every chart carries a callout box with the business takeaway."""

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

from .config import Settings

PRIMARY = "#1F4E79"
ACCENT = "#E07A1F"
MUTED = "#9AA5B1"
FIG_SIZE = (10, 5.6)


def _new_figure(title: str, size: tuple[float, float] = FIG_SIZE):
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=size)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold")
    return fig, ax


def _finish(fig: Figure, takeaway: str) -> Figure:
    wrapped = textwrap.fill(f"Takeaway: {takeaway}", width=100)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.text(
        0.015,
        0.02,
        wrapped,
        ha="left",
        va="bottom",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#FFF4D6", "edgecolor": "#E0A800"},
    )
    return fig


def revenue_trend(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Monthly revenue and 3-month average")
    months = pd.to_datetime(df["month"])
    ax.plot(months, df["revenue"], marker="o", color=PRIMARY, label="Monthly revenue")
    ax.plot(months, df["revenue_3m_avg"], linestyle="--", color=ACCENT, label="3-month average")
    ax.set_ylabel("Revenue ($)")
    ax.set_xlabel("")
    ax.legend(loc="upper left")
    return _finish(fig, takeaway)


def category_margin(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Profit margin by category")
    d = df.sort_values("margin_pct")
    lowest = d["margin_pct"].min()
    colors = [ACCENT if m == lowest else PRIMARY for m in d["margin_pct"]]
    ax.barh(d["category"], d["margin_pct"], color=colors)
    for y, (margin, share) in enumerate(zip(d["margin_pct"], d["revenue_share_pct"], strict=True)):
        ax.text(margin + 0.5, y, f"{margin:.1f}% margin | {share:.0f}% of revenue", va="center", fontsize=9)
    ax.set_xlim(min(0, lowest * 1.2), d["margin_pct"].max() * 1.5)
    ax.set_xlabel("Profit margin (%)")
    return _finish(fig, takeaway)


def rfm_segments(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("RFM segments: share of customers vs share of revenue")
    d = df.sort_values("revenue_share_pct").reset_index(drop=True)
    pos = list(range(len(d)))
    h = 0.38
    ax.barh([p - h / 2 for p in pos], d["customer_share_pct"], height=h, color=MUTED, label="% of customers")
    ax.barh([p + h / 2 for p in pos], d["revenue_share_pct"], height=h, color=PRIMARY, label="% of revenue")
    ax.set_yticks(pos)
    ax.set_yticklabels(d["segment"])
    ax.set_xlabel("Share (%)")
    ax.legend(loc="lower right")
    return _finish(fig, takeaway)


def churn_by_channel(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Churn rate by acquisition channel")
    d = df.sort_values("churn_rate_pct")
    highest = d["churn_rate_pct"].max()
    colors = [ACCENT if v == highest else PRIMARY for v in d["churn_rate_pct"]]
    labels = [str(c).replace("_", " ") for c in d["channel"]]
    ax.barh(labels, d["churn_rate_pct"], color=colors)
    for y, (rate, one_time) in enumerate(zip(d["churn_rate_pct"], d["one_time_pct"], strict=True)):
        ax.text(rate + 0.5, y, f"{rate:.1f}% churned | {one_time:.0f}% one-time", va="center", fontsize=9)
    ax.set_xlim(0, highest * 1.5)
    ax.set_xlabel("Customers with no recent order (%)")
    return _finish(fig, takeaway)


def churn_trend(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Churn rate over time: share of customers lapsed at each month end")
    months = pd.to_datetime(df["month_end"])
    ax.plot(months, df["churn_rate_pct"], marker="o", color=PRIMARY, label="Churn rate")
    ax.plot(months, df["churn_3m_avg_pct"], linestyle="--", color=ACCENT, label="3-month average")
    last_rate = float(df["churn_rate_pct"].iloc[-1])
    ax.annotate(
        f"{last_rate:.1f}%",
        (months.iloc[-1], last_rate),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=10,
        fontweight="bold",
        color=ACCENT,
    )
    ax.set_ylim(0, max(float(df["churn_rate_pct"].max()) * 1.2, 1.0))
    ax.set_ylabel("Customers lapsed (%)")
    ax.set_xlabel("")
    ax.legend(loc="upper left")
    return _finish(fig, takeaway)


def cohort_heatmap(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Monthly cohort retention (%)", size=(10, 7.5))
    pivot = (
        df.assign(cohort=pd.to_datetime(df["cohort_month"]).dt.strftime("%Y-%m"))
        .pivot(index="cohort", columns="month_index", values="retention_pct")
        .sort_index()
    )
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="Blues",
        vmin=0,
        vmax=100,
        annot=True,
        fmt=".0f",
        annot_kws={"size": 7},
        cbar_kws={"label": "% of cohort active"},
    )
    ax.set_xlabel("Months since first order")
    ax.set_ylabel("")
    return _finish(fig, takeaway)


def profit_concentration(df: pd.DataFrame, takeaway: str) -> Figure:
    fig, ax = _new_figure("Profit concentration by customer decile")
    ax.bar(df["decile"], df["profit_share_pct"], color=PRIMARY, label="% of profit in decile")
    ax.plot(df["decile"], df["cumulative_profit_pct"], marker="o", color=ACCENT, label="Cumulative % of profit")
    ax.set_xticks(df["decile"])
    ax.set_xlabel("Customer decile (1 = most profitable)")
    ax.set_ylabel("Share of profit (%)")
    ax.legend(loc="center right")
    return _finish(fig, takeaway)


# (file stem, chart function, frame key, takeaway key)
SPECS = [
    ("01_revenue_trend", revenue_trend, "q06_monthly_trend", "revenue_trend"),
    ("02_category_margin", category_margin, "q02_category_margin", "category_margin"),
    ("03_rfm_segments", rfm_segments, "q03_rfm_segments", "rfm_segments"),
    ("04_churn_by_channel", churn_by_channel, "q04_churn_by_channel", "churn_by_channel"),
    ("05_cohort_retention", cohort_heatmap, "q05_cohort_retention", "cohort_retention"),
    ("06_profit_concentration", profit_concentration, "q07_profit_concentration", "profit_concentration"),
    ("07_churn_trend", churn_trend, "q09_churn_trend", "churn_trend"),
]


def save_chart(fig: Figure, stem: str, cfg: Settings) -> Path:
    out_dir = cfg.output_dir / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def render_all(frames: dict[str, pd.DataFrame], takeaways: dict[str, str], cfg: Settings) -> dict[str, Path]:
    paths = {}
    for stem, func, frame_key, takeaway_key in SPECS:
        fig = func(frames[frame_key], takeaways[takeaway_key])
        paths[stem] = save_chart(fig, stem, cfg)
    return paths
