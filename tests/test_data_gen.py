import pandas as pd

from insightstory.data_gen import DISCOUNT_LEVELS, generate_tables


def test_expected_tables(tables, cfg):
    assert set(tables) == {"customers", "products", "orders", "order_items"}
    assert len(tables["customers"]) == cfg.n_customers
    assert len(tables["products"]) == cfg.n_products


def test_deterministic_for_same_seed(cfg, tables):
    again = generate_tables(cfg)
    for name in tables:
        pd.testing.assert_frame_equal(tables[name], again[name])


def test_referential_integrity(tables):
    orders, items = tables["orders"], tables["order_items"]
    assert items["order_id"].isin(orders["order_id"]).all()
    assert items["product_id"].isin(tables["products"]["product_id"]).all()
    assert orders["customer_id"].isin(tables["customers"]["customer_id"]).all()


def test_value_ranges(tables, cfg):
    items, products, orders = tables["order_items"], tables["products"], tables["orders"]
    assert items["discount_pct"].isin(DISCOUNT_LEVELS).all()
    assert (items["quantity"] >= 1).all()
    assert (products["unit_cost"] <= products["unit_price"]).all()
    dates = pd.to_datetime(orders["order_date"])
    assert dates.between(pd.Timestamp(cfg.start_date), pd.Timestamp(cfg.end_date)).all()
