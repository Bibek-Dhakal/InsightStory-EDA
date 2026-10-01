from dataclasses import replace

import matplotlib

matplotlib.use("Agg")

import pytest  # noqa: E402

from insightstory import analysis  # noqa: E402
from insightstory.config import load_settings  # noqa: E402
from insightstory.data_gen import generate_tables  # noqa: E402
from insightstory.db import build_database, connect  # noqa: E402


@pytest.fixture(scope="session")
def cfg(tmp_path_factory):
    base = tmp_path_factory.mktemp("insightstory")
    return replace(
        load_settings(),
        db_path=base / "test.duckdb",
        output_dir=base / "outputs",
        n_customers=400,
        n_products=40,
    )


@pytest.fixture(scope="session")
def tables(cfg):
    return generate_tables(cfg)


@pytest.fixture(scope="session")
def db(cfg, tables):
    build_database(cfg, tables)
    con = connect(cfg, read_only=True)
    yield con
    con.close()


@pytest.fixture(scope="session")
def frames(db, cfg):
    return analysis.run_all(db, cfg)
