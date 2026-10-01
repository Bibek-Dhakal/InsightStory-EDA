# Contributing

Thanks for your interest in InsightStory-EDA!

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (use `source .venv/bin/activate` on macOS/Linux)
pip install -e ".[dev,notebooks]"
pre-commit install
```

`pre-commit install` registers both the code-quality hook (Ruff) and the commit-message hook.

## Code style

- Ruff handles formatting, import sorting and linting (config in `pyproject.toml`).
- Run manually: `ruff check . --fix` and `ruff format .`
- Keep configuration in `.env` / `config.py`; do not repeat constants in several places.

## Conventional Commits (strict)

Every commit message **and PR title** must follow `type(scope): description`.
These messages drive automated versioning and `CHANGELOG.md` generation through
`release-please` Release PRs.

| Prefix | Meaning | Version effect |
|--------|---------|----------------|
| `feat:` | New feature | minor |
| `fix:` | Bug fix | patch |
| `feat!:` / `BREAKING CHANGE:` | Breaking change | major |
| `docs:` `chore:` `refactor:` `perf:` `test:` `style:` `build:` `ci:` | Non-release work | none / grouped |

Example: `fix(sql): correct recency calculation in RFM view`

## Pull requests

1. Branch from `main`.
2. Keep PRs focused and explain the business or analytical reason for the change.
3. Make sure `insightstory all` still runs end to end and the notebook reconciliation cell passes.
4. Use a Conventional Commit PR title.
