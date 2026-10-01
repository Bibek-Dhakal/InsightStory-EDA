# Usage

## Commands

```bash
insightstory build-db   # generate synthetic data, load DuckDB, create views
insightstory analyze    # run all SQL queries, write CSVs to outputs/tables/
insightstory charts     # render PNG charts to outputs/charts/
insightstory deck       # render charts, then build the .pptx and .pdf deck
insightstory all        # all of the above, in order
```

`build-db` must run before the others. If you change `INSIGHTSTORY_AS_OF_DATE` or the data settings, run `build-db`
again, because the views bake in the as-of date.

## Environment variables

Set them in `.env` (copy from `.env.example`) or the shell.

| Name                       | Type | Default                    | Description                                               |
|----------------------------|------|----------------------------|-----------------------------------------------------------|
| `INSIGHTSTORY_DB_PATH`     | path | `data/insightstory.duckdb` | DuckDB file location                                      |
| `INSIGHTSTORY_OUTPUT_DIR`  | path | `outputs`                  | Charts, tables and deck output                            |
| `INSIGHTSTORY_SQL_DIR`     | path | `sql`                      | Folder holding `views/` and `queries/`                    |
| `INSIGHTSTORY_SEED`        | int  | `42`                       | Random seed for synthetic data                            |
| `INSIGHTSTORY_N_CUSTOMERS` | int  | `5000`                     | Number of customers                                       |
| `INSIGHTSTORY_N_PRODUCTS`  | int  | `150`                      | Number of products                                        |
| `INSIGHTSTORY_START_DATE`  | date | `2024-01-01`               | First possible signup date                                |
| `INSIGHTSTORY_END_DATE`    | date | `2025-12-31`               | Last order date                                           |
| `INSIGHTSTORY_AS_OF_DATE`  | date | `END_DATE`                 | Reference date for recency                                |
| `INSIGHTSTORY_CHURN_DAYS`  | int  | `90`                       | Days without an order before a customer counts as churned |

Relative paths resolve from the repository root.

## Notebook

```bash
jupyter lab notebooks/01_insightstory_eda.ipynb
```

Run `insightstory build-db` first. The notebook only runs the SQL in `sql/` and plots results.

## SQL files

| Path                           | Purpose                                                                                                                                             |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `sql/views/00_order_lines.sql` | Completed-order lines with revenue, cost, profit                                                                                                    |
| `sql/views/01_rfm.sql`         | RFM scores and segments (`NTILE(5)`)                                                                                                                |
| `sql/queries/q01` to `q09`     | KPIs, category margin, RFM segments, churn by channel, cohort retention, monthly trend, profit concentration, reconciliation, churn trend over time |

Placeholders `{{as_of_date}}` and `{{churn_days}}` are filled from settings.
