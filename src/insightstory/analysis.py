"""Render and run the SQL files in sql/views and sql/queries."""

import duckdb
import pandas as pd

from .config import Settings


def render_sql(text: str, cfg: Settings) -> str:
    """Fill {{as_of_date}} and {{churn_days}} from settings (trusted config values)."""
    return text.replace("{{as_of_date}}", cfg.as_of_date).replace(
        "{{churn_days}}", str(int(cfg.churn_days))
    )


def create_views(con: duckdb.DuckDBPyConnection, cfg: Settings) -> None:
    for path in sorted((cfg.sql_dir / "views").glob("*.sql")):
        con.execute(render_sql(path.read_text(encoding="utf-8"), cfg))


def run_query(con: duckdb.DuckDBPyConnection, cfg: Settings, name: str) -> pd.DataFrame:
    path = cfg.sql_dir / "queries" / f"{name}.sql"
    return con.execute(render_sql(path.read_text(encoding="utf-8"), cfg)).df()


def run_all(con: duckdb.DuckDBPyConnection, cfg: Settings) -> dict[str, pd.DataFrame]:
    return {
        path.stem: run_query(con, cfg, path.stem)
        for path in sorted((cfg.sql_dir / "queries").glob("*.sql"))
    }
