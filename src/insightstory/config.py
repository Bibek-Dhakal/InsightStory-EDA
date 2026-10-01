"""Central configuration loaded from environment variables / .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


def _get(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def _path(name: str, default: str) -> Path:
    path = Path(_get(name, default))
    return path if path.is_absolute() else ROOT / path


@dataclass(frozen=True)
class Settings:
    db_path: Path
    output_dir: Path
    sql_dir: Path
    seed: int
    n_customers: int
    n_products: int
    start_date: str
    end_date: str
    as_of_date: str
    churn_days: int


def load_settings() -> Settings:
    load_dotenv(ROOT / ".env")
    end_date = _get("INSIGHTSTORY_END_DATE", "2025-12-31")
    return Settings(
        db_path=_path("INSIGHTSTORY_DB_PATH", "data/insightstory.duckdb"),
        output_dir=_path("INSIGHTSTORY_OUTPUT_DIR", "outputs"),
        sql_dir=_path("INSIGHTSTORY_SQL_DIR", "sql"),
        seed=int(_get("INSIGHTSTORY_SEED", "42")),
        n_customers=int(_get("INSIGHTSTORY_N_CUSTOMERS", "5000")),
        n_products=int(_get("INSIGHTSTORY_N_PRODUCTS", "150")),
        start_date=_get("INSIGHTSTORY_START_DATE", "2024-01-01"),
        end_date=end_date,
        as_of_date=_get("INSIGHTSTORY_AS_OF_DATE", end_date),
        churn_days=int(_get("INSIGHTSTORY_CHURN_DAYS", "90")),
    )
