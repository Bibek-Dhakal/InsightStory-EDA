"""Deterministic synthetic e-commerce data (customers, products, orders, order_items)."""

import numpy as np
import pandas as pd

from .config import Settings

# name: (median unit price, target margin, discount propensity multiplier)
CATEGORIES = {
    "Electronics": (180.0, 0.18, 1.6),
    "Home": (60.0, 0.38, 1.0),
    "Fashion": (45.0, 0.52, 1.2),
    "Beauty": (28.0, 0.62, 0.8),
    "Sports": (75.0, 0.35, 1.0),
    "Accessories": (22.0, 0.70, 0.7),
}
CHANNELS = ["organic", "email", "paid_social", "referral"]
CHANNEL_SHARE = [0.35, 0.20, 0.30, 0.15]
REGIONS = ["North", "South", "East", "West"]
ARCHETYPES = ["loyal", "occasional", "one_time", "lapsed"]
ARCHETYPE_MIX = {
    "organic": [0.20, 0.40, 0.25, 0.15],
    "email": [0.30, 0.40, 0.10, 0.20],
    "paid_social": [0.05, 0.25, 0.50, 0.20],
    "referral": [0.25, 0.40, 0.20, 0.15],
}
MONTHLY_ORDER_RATE = {"loyal": 1.4, "occasional": 0.4, "lapsed": 0.9}
DISCOUNT_LEVELS = np.array([0.0, 0.05, 0.10, 0.20, 0.30])
BASE_DISCOUNT_P = np.array([0.55, 0.15, 0.15, 0.10, 0.05])
STATUSES = ["completed", "returned", "cancelled"]
STATUS_P = [0.93, 0.04, 0.03]


def _make_products(rng: np.random.Generator, n: int):
    names = list(CATEGORIES)
    cats = rng.choice(names, size=n)
    median = np.array([CATEGORIES[c][0] for c in cats])
    margin = np.array([CATEGORIES[c][1] for c in cats])
    bias = np.array([CATEGORIES[c][2] for c in cats])
    price = np.round(median * rng.lognormal(0.0, 0.35, n), 2)
    cost = np.round(price * np.clip(1 - margin + rng.normal(0, 0.03, n), 0.05, 0.95), 2)
    popularity = rng.pareto(1.5, n) + 1
    popularity = popularity / popularity.sum()
    discount_p = np.tile(BASE_DISCOUNT_P, (n, 1))
    discount_p[:, 1:] *= bias[:, None]
    discount_p /= discount_p.sum(axis=1, keepdims=True)
    products = pd.DataFrame(
        {
            "product_id": np.arange(1, n + 1),
            "category": cats,
            "unit_price": price,
            "unit_cost": cost,
        }
    )
    return products, popularity, discount_p


def _make_customers(rng: np.random.Generator, cfg: Settings):
    n = cfg.n_customers
    start = pd.Timestamp(cfg.start_date)
    span = (pd.Timestamp(cfg.end_date) - start).days
    channels = rng.choice(CHANNELS, size=n, p=CHANNEL_SHARE)
    regions = rng.choice(REGIONS, size=n)
    signup = start + pd.to_timedelta(rng.integers(0, int(span * 0.75), n), unit="D")
    archetypes = np.array([rng.choice(ARCHETYPES, p=ARCHETYPE_MIX[c]) for c in channels])
    customers = pd.DataFrame(
        {
            "customer_id": np.arange(1, n + 1),
            "signup_date": signup.date,
            "region": regions,
            "channel": channels,
        }
    )
    return customers, signup, archetypes


def _order_dates(rng: np.random.Generator, signup: pd.Timestamp, end: pd.Timestamp, archetype: str):
    tenure = max((end - signup).days, 1)
    if archetype == "one_time":
        offset = int(rng.integers(0, min(14, tenure) + 1))
        return [signup + pd.Timedelta(days=offset)]
    active_days = tenure if archetype != "lapsed" else int(tenure * rng.uniform(0.2, 0.55))
    n_orders = max(2, int(rng.poisson(MONTHLY_ORDER_RATE[archetype] * max(active_days, 30) / 30)))
    offsets = np.sort(rng.integers(0, max(active_days, 1) + 1, n_orders))
    return [signup + pd.Timedelta(days=int(o)) for o in offsets]


def generate_tables(cfg: Settings) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(cfg.seed)
    end = pd.Timestamp(cfg.end_date)
    products, popularity, discount_p = _make_products(rng, cfg.n_products)
    customers, signups, archetypes = _make_customers(rng, cfg)

    orders, items = [], []
    order_id = 1
    for customer_id, signup, archetype in zip(
        customers["customer_id"], signups, archetypes, strict=True
    ):
        for order_date in _order_dates(rng, signup, end, archetype):
            status = rng.choice(STATUSES, p=STATUS_P)
            orders.append((order_id, int(customer_id), order_date, status))
            n_lines = int(rng.integers(1, 5))
            product_idx = rng.choice(cfg.n_products, size=n_lines, p=popularity)
            quantities = rng.integers(1, 4, size=n_lines)
            for idx, qty in zip(product_idx, quantities, strict=True):
                discount = float(rng.choice(DISCOUNT_LEVELS, p=discount_p[idx]))
                items.append((order_id, int(idx) + 1, int(qty), discount))
            order_id += 1

    orders_df = pd.DataFrame(orders, columns=["order_id", "customer_id", "order_date", "status"])
    orders_df["order_date"] = pd.to_datetime(orders_df["order_date"]).dt.date
    items_df = pd.DataFrame(items, columns=["order_id", "product_id", "quantity", "discount_pct"])
    return {
        "customers": customers,
        "products": products,
        "orders": orders_df,
        "order_items": items_df,
    }
