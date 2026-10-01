# Testing

```bash
pytest                    # all tests with coverage
pytest tests/test_analysis.py -q
```

| Tier        | Files                                                | What it checks                                                                                                                          |
|-------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Unit        | `test_config.py`, `test_data_gen.py`                 | Settings, determinism, referential integrity, value ranges                                                                              |
| Integration | `test_analysis.py`, `test_insights.py`               | Views and queries on a small DuckDB (400 customers), KPI vs raw reconciliation, segment and decile totals, churn trend vs channel churn |
| Output      | `test_charts.py`, `test_deck.py`, `test_deck_pdf.py` | Every chart has a takeaway callout; deck has 5 slides; PDF has 5 pages and is written                                                   |

Tests build a temporary database in a pytest temp directory, so no real data or output is touched.

## CI

`.github/workflows/ci.yml` runs on every pull request and every push to `main`:

| Job    | What it runs                               |
|--------|--------------------------------------------|
| `lint` | `ruff check .` and `ruff format --check .` |
| `test` | `pytest` on Python 3.10 and 3.13           |

The suite also runs locally as a `pre-push` hook (see [Code quality](code_quality.md)).
