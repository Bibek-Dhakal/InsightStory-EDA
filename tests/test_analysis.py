import pandas as pd
import pytest

from insightstory import analysis


def test_render_sql_fills_placeholders(cfg):
    out = analysis.render_sql("DATE '{{as_of_date}}' > {{churn_days}}", cfg)
    assert "{{" not in out
    assert cfg.as_of_date in out
    assert str(cfg.churn_days) in out


def test_every_query_returns_rows(frames):
    assert len(frames) == 9
    for name, frame in frames.items():
        assert len(frame) > 0, name


def test_kpi_revenue_reconciles_with_raw_tables(frames):
    revenue_sql = float(frames["q01_kpi_summary"].loc[0, "revenue"])
    revenue_raw = float(frames["q08_reconciliation"].loc[0, "revenue_raw"])
    assert abs(revenue_sql - revenue_raw) < 0.01


def test_views_use_completed_orders_only(db, tables, frames):
    completed = int((tables["orders"]["status"] == "completed").sum())
    assert int(frames["q01_kpi_summary"].loc[0, "orders"]) == completed
    bad = db.execute(
        "SELECT COUNT(*) FROM v_order_lines v JOIN orders o USING (order_id) "
        "WHERE o.status <> 'completed'"
    ).fetchone()[0]
    assert bad == 0


def test_rfm_segments_cover_all_active_customers(frames):
    active = int(frames["q01_kpi_summary"].loc[0, "active_customers"])
    assert int(frames["q03_rfm_segments"]["customers"].sum()) == active


def test_rfm_revenue_reconciles(frames):
    revenue_sql = float(frames["q01_kpi_summary"].loc[0, "revenue"])
    revenue_rfm = float(frames["q03_rfm_segments"]["revenue"].sum())
    assert abs(revenue_sql - revenue_rfm) < 5.0


def test_profit_deciles_sum_to_100(frames):
    conc = frames["q07_profit_concentration"]
    assert abs(conc["profit_share_pct"].sum() - 100) < 0.1
    assert abs(conc["cumulative_profit_pct"].iloc[-1] - 100) < 0.1


def test_cohort_month_zero_is_100_percent(frames):
    coh = frames["q05_cohort_retention"]
    assert (coh.loc[coh["month_index"] == 0, "retention_pct"] == 100).all()


def test_churn_counts_are_consistent(frames):
    chn = frames["q04_churn_by_channel"]
    assert (chn["churned"] <= chn["customers"]).all()
    assert chn["churn_rate_pct"].between(0, 100).all()


def test_churn_trend_is_consistent(frames):
    ct = frames["q09_churn_trend"]
    assert (ct["churned"] <= ct["customers_seen"]).all()
    assert ct["churn_rate_pct"].between(0, 100).all()
    assert ct["customers_seen"].is_monotonic_increasing


def test_churn_trend_last_month_matches_channel_totals(frames, cfg):
    ct, chn = frames["q09_churn_trend"], frames["q04_churn_by_channel"]
    last = ct.iloc[-1]
    if pd.Timestamp(last["month_end"]) != pd.Timestamp(cfg.as_of_date):
        pytest.skip("last month does not end on the as-of date")
    assert int(last["churned"]) == int(chn["churned"].sum())
    assert int(last["customers_seen"]) == int(chn["customers"].sum())
