# Roadmap

## Done

- Synthetic data generator, DuckDB build, SQL views and 9 queries
- Seven charts with takeaway callouts, notebook, 5-slide deck (`.pptx` and `.pdf`), CLI
- Monthly churn-trend query and chart
- Tests, pre-commit, release-please, GitHub Actions CI (Ruff and pytest)

## Next

- Split the churn trend by acquisition channel
- Add a coverage threshold to CI
- Enable Dependabot for GitHub Actions versions

## Technical debt / known limits

- Views bake in `as_of_date`; changing it requires `build-db` again.
- `insightstory all` renders charts twice (`charts`, then `deck`).
- The PDF is a matplotlib re-layout of the deck, so fonts differ slightly from the `.pptx`.
- Churn trend skips the first `churn_days` of history (warm-up). Part of the early rise reflects the customer base
  ageing, not only behaviour change.
- Data is synthetic; findings illustrate the method, not a real business.
