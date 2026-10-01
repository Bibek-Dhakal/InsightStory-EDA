# InsightStory-EDA

SQL-driven exploratory analysis of e-commerce customer behavior, turned into a 5-slide executive deck.
It answers three questions: why churn is rising, which customers and products drive profit, and where margin leaks.

All data is **synthetic** and deterministic (seeded), so results are reproducible.

## What you get

- DuckDB database with `customers`, `products`, `orders`, `order_items` and SQL views (`v_order_lines`, `v_rfm`)
- 9 analytical queries (aggregations, window functions, RFM scoring, cohorts, churn trend) in `sql/queries/`
- 7 minimalist charts, each with a business-takeaway callout
- `outputs/InsightStory-EDA_Executive_Deck.pptx` and a matching `.pdf` (Situation, Complication, Data Analysis x2,
  Recommendation)
- Notebook `notebooks/01_insightstory_eda.ipynb` documenting the full analysis and a reconciliation check

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -e ".[dev,notebooks]"
cp .env.example .env              # optional
insightstory all                  # build-db -> analyze -> charts -> deck (.pptx + .pdf)
```

## Documentation

- [Usage](docs/usage.md): commands and environment variables
- [Architecture](docs/architecture.md): data flow and module map
- [Testing](docs/testing.md): test tiers, how to run them, CI
- [Code quality](docs/code_quality.md): Ruff, pre-commit, commit messages
- [Roadmap](docs/roadmap.md): status, technical debt, next steps
- [Contributing](CONTRIBUTING.md)

## License

MIT. See [LICENSE](LICENSE).
