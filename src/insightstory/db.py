"""DuckDB helpers."""

import duckdb
import pandas as pd

from . import analysis
from .config import Settings


def connect(cfg: Settings, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(cfg.db_path), read_only=read_only)


def build_database(cfg: Settings, tables: dict[str, pd.DataFrame]) -> dict[str, int]:
    """Create a fresh database from DataFrames, then create the SQL views."""
    cfg.db_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", ".wal"):
        stale = cfg.db_path.with_name(cfg.db_path.name + suffix)
        if stale.exists():
            stale.unlink()

    con = connect(cfg)
    try:
        counts = {}
        for name, frame in tables.items():
            con.register("_src", frame)
            con.execute(f"CREATE TABLE {name} AS SELECT * FROM _src")
            con.unregister("_src")
            counts[name] = len(frame)
        analysis.create_views(con, cfg)
    finally:
        con.close()
    return counts