# Code Quality

> Checks run via **pre-commit** on `git commit` (Ruff, commit-message validation) and on `git push` (pytest).
> The same Ruff and pytest checks also run in GitHub Actions CI on pull requests and pushes to `main`.
> Every check can also be run manually with the commands below.

## Environment Setup

```bash
pip install -e ".[dev]"
pre-commit install
```

The config declares `commit-msg` and `pre-push` hook types, so `pre-commit install` registers all three.

## Manual Execution Commands

```bash
# All files
pre-commit run --all-files

# Staged files only
pre-commit run

# Changes against a branch
pre-commit run --from-ref origin/main --to-ref HEAD

# Specific files
pre-commit run --files src/insightstory/charts.py

# Pre-push hook (tests)
pre-commit run --hook-stage pre-push --all-files
```

## Isolated Tool Commands

```bash
ruff check .            # lint only
ruff check . --fix      # lint and auto-fix
ruff format .           # format only
ruff format --check .   # verify formatting
pytest                  # tests only
```

## Maintenance & Cache

```bash
pre-commit autoupdate   # bump hook versions to latest
pre-commit clean        # clear pre-commit cache
ruff clean              # clear Ruff cache
```

## Emergency Bypassing

```bash
git commit --no-verify
git push --no-verify
SKIP=ruff-check git commit -m "fix: hotfix"   # skip one hook (PowerShell: $env:SKIP="ruff-check")
```

Use these only for real emergencies. CI and reviewers still expect Conventional Commit messages and passing checks.
