from insightstory.config import load_settings


def test_sql_dir_resolves_inside_repo():
    cfg = load_settings()
    assert cfg.sql_dir.is_absolute()
    assert (cfg.sql_dir / "queries").is_dir()
    assert (cfg.sql_dir / "views").is_dir()


def test_env_override(monkeypatch):
    monkeypatch.setenv("INSIGHTSTORY_CHURN_DAYS", "30")
    monkeypatch.setenv("INSIGHTSTORY_SEED", "7")
    cfg = load_settings()
    assert cfg.churn_days == 30
    assert cfg.seed == 7
