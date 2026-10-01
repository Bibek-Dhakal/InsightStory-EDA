"""Turn query results into takeaways, slide titles and metric-backed recommendations."""

from dataclasses import dataclass

import pandas as pd

from .config import Settings


@dataclass
class Insights:
    kpis: dict[str, float]
    takeaways: dict[str, str]
    titles: dict[str, str]
    notes: dict[str, list[str]]
    recommendations: list[dict[str, str]]


def _money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def _label(text: str) -> str:
    return str(text).replace("_", " ")


def build(frames: dict[str, pd.DataFrame], cfg: Settings) -> Insights:
    kpi = frames["q01_kpi_summary"].iloc[0]
    cat = frames["q02_category_margin"]
    seg = frames["q03_rfm_segments"]
    chn = frames["q04_churn_by_channel"]
    coh = frames["q05_cohort_retention"]
    trend = frames["q06_monthly_trend"]
    conc = frames["q07_profit_concentration"]
    ct = frames["q09_churn_trend"]

    kpis = {
        "revenue": float(kpi["revenue"]),
        "profit": float(kpi["profit"]),
        "margin_pct": float(kpi["margin_pct"]),
        "orders": float(kpi["orders"]),
        "active_customers": float(kpi["active_customers"]),
        "aov": float(kpi["aov"]),
    }

    overall_churn = 100 * chn["churned"].sum() / chn["customers"].sum()
    last3 = float(trend["revenue_3m_avg"].iloc[-1])
    ref_idx = -7 if len(trend) >= 7 else 0
    ref = float(trend["revenue_3m_avg"].iloc[ref_idx])
    growth = 100 * (last3 - ref) / ref if ref else 0.0

    churn_now = float(ct["churn_rate_pct"].iloc[-1])
    churn_then = float(ct["churn_rate_pct"].iloc[-7 if len(ct) >= 7 else 0])
    churn_delta = churn_now - churn_then
    churn_direction = "up" if churn_delta > 0 else "down" if churn_delta < 0 else "flat"

    worst, best = chn.iloc[0], chn.iloc[-1]
    worst_name, best_name = _label(worst["channel"]), _label(best["channel"])
    worst_churn, best_churn = float(worst["churn_rate_pct"]), float(best["churn_rate_pct"])
    worst_one_time = float(worst["one_time_pct"])
    recoverable = float(worst["customers"]) * (worst_churn - best_churn) / 100

    core = seg[seg["segment"].isin(["Champions", "Loyal"])]
    core_cust = float(core["customer_share_pct"].sum())
    core_rev = float(core["revenue_share_pct"].sum())
    at_risk = seg[seg["segment"] == "At Risk"]
    ar_cust = int(at_risk["customers"].sum())
    ar_rev = float(at_risk["revenue"].sum())

    top_cat = cat.iloc[0]
    low = cat.loc[cat["margin_pct"].idxmin()]
    low_name, low_margin = str(low["category"]), float(low["margin_pct"])
    low_disc = float(low["avg_discount_pct"])
    top_cat_name, top_cat_margin = str(top_cat["category"]), float(top_cat["margin_pct"])

    m1 = float(coh.loc[coh["month_index"] == 1, "retention_pct"].mean())
    m3 = float(coh.loc[coh["month_index"] == 3, "retention_pct"].mean())
    top10 = float(conc.iloc[0]["profit_share_pct"])
    top20 = float(conc.loc[conc["decile"] == 2, "cumulative_profit_pct"].iloc[0])

    takeaways = {
        "revenue_trend": (
            f"3-month average revenue is {growth:+.1f}% vs six months earlier, yet "
            f"{overall_churn:.0f}% of customers have not ordered in {cfg.churn_days}+ days."
        ),
        "category_margin": (
            f"{top_cat_name} is the top profit earner at {top_cat_margin:.1f}% margin; "
            f"{low_name} keeps only {low_margin:.1f}% after {low_disc:.1f}% average discounts."
        ),
        "rfm_segments": (
            f"Champions + Loyal are {core_cust:.0f}% of customers but {core_rev:.0f}% of revenue; "
            f"{ar_cust:,} At Risk customers hold {_money(ar_rev)} of past revenue."
        ),
        "churn_by_channel": (
            f"{worst_name} churn is {worst_churn:.1f}% vs {best_churn:.1f}% for {best_name}; "
            f"{worst_one_time:.0f}% of {worst_name} buyers never order again."
        ),
        "cohort_retention": (
            f"On average only {m1:.0f}% of a cohort orders again in month 1 and "
            f"{m3:.0f}% in month 3."
        ),
        "profit_concentration": (
            f"The top 10% of customers deliver {top10:.0f}% of profit; "
            f"the top 20% deliver {top20:.0f}%."
        ),
        "churn_trend": (
            f"Churn is {churn_direction}: {churn_then:.1f}% six months ago vs {churn_now:.1f}% "
            f"now ({churn_delta:+.1f} pts)."
        ),
    }

    titles = {
        "situation": (
            f"Situation: {_money(kpis['revenue'])} revenue at a {kpis['margin_pct']:.1f}% margin"
        ),
        "complication": (
            f"Complication: {overall_churn:.0f}% of customers have lapsed "
            f"({churn_delta:+.0f} pts in six months)"
        ),
        "rfm": f"Core buyers: {core_cust:.0f}% of customers drive {core_rev:.0f}% of revenue",
        "margin": f"Margin leak: {low_name} earns only {low_margin:.1f}% after discounts",
        "recommendation": "Recommendations: three moves tied to the numbers",
    }

    notes = {
        "situation": [
            f"{kpis['orders']:,.0f} completed orders from {kpis['active_customers']:,.0f} customers.",
            f"Average order value: {_money(kpis['aov'])}.",
            "Growth is only sustainable if buyers come back.",
        ],
        "complication": [
            f"Overall churn: {overall_churn:.1f}% (no order in {cfg.churn_days}+ days).",
            f"Six months ago: {churn_then:.1f}% ({churn_delta:+.1f} pts).",
            f"Month-1 repeat rate: {m1:.0f}%; month-3: {m3:.0f}%.",
            f"{worst_name} is weakest: {worst_churn:.1f}% churn vs {best_churn:.1f}% for {best_name}.",
        ],
        "rfm": [
            f"Top 10% of customers = {top10:.0f}% of profit.",
            f"At Risk: {ar_cust:,} customers, {_money(ar_rev)} historic revenue.",
        ],
        "margin": [
            f"Best margin: {top_cat_name} ({top_cat_margin:.1f}%).",
            f"{low_name}: {low_margin:.1f}% margin, {low_disc:.1f}% average discount.",
        ],
    }

    recommendations = [
        {
            "title": f"Fix acquisition quality: add a second-order programme for {worst_name}",
            "evidence": (
                f"{worst_name} churn {worst_churn:.1f}% vs {best_churn:.1f}% for {best_name}; "
                f"{worst_one_time:.0f}% never reorder. Matching the best channel would keep "
                f"about {recoverable:,.0f} more customers active."
            ),
            "source": "q04_churn_by_channel",
        },
        {
            "title": "Protect core buyers and win back At Risk customers",
            "evidence": (
                f"Champions + Loyal: {core_cust:.0f}% of customers, {core_rev:.0f}% of revenue; "
                f"top 20% of customers give {top20:.0f}% of profit; At Risk group holds "
                f"{_money(ar_rev)} of past revenue ({ar_cust:,} customers)."
            ),
            "source": "q03_rfm_segments, q07_profit_concentration",
        },
        {
            "title": f"Cap discounts in {low_name} to stop the margin leak",
            "evidence": (
                f"{low_name} margin is {low_margin:.1f}% with {low_disc:.1f}% average discount, "
                f"versus {top_cat_margin:.1f}% margin for {top_cat_name}."
            ),
            "source": "q02_category_margin",
        },
    ]

    return Insights(
        kpis=kpis,
        takeaways=takeaways,
        titles=titles,
        notes=notes,
        recommendations=recommendations,
    )
