"""Command-line interface: build-db | analyze | charts | deck | all."""

import argparse
import logging

import matplotlib

matplotlib.use("Agg")

from . import analysis, charts, deck, deck_pdf, insights  # noqa: E402
from .config import Settings, load_settings  # noqa: E402
from .data_gen import generate_tables  # noqa: E402
from .db import build_database, connect  # noqa: E402

log = logging.getLogger("insightstory")


def _frames(cfg: Settings):
    con = connect(cfg, read_only=True)
    try:
        return analysis.run_all(con, cfg)
    finally:
        con.close()


def cmd_build_db(cfg: Settings) -> None:
    counts = build_database(cfg, generate_tables(cfg))
    log.info("Database built at %s", cfg.db_path)
    for name, n in counts.items():
        log.info("  %-12s %8d rows", name, n)


def cmd_analyze(cfg: Settings) -> None:
    frames = _frames(cfg)
    tables_dir = cfg.output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        frame.to_csv(tables_dir / f"{name}.csv", index=False)
    ins = insights.build(frames, cfg)
    log.info("KPIs: %s", {k: round(v, 2) for k, v in ins.kpis.items()})
    for i, rec in enumerate(ins.recommendations, start=1):
        log.info("Recommendation %d: %s", i, rec["title"])
        log.info("  Evidence: %s [%s]", rec["evidence"], rec["source"])
    log.info("Tables written to %s", tables_dir)


def cmd_charts(cfg: Settings) -> None:
    frames = _frames(cfg)
    ins = insights.build(frames, cfg)
    for stem, path in charts.render_all(frames, ins.takeaways, cfg).items():
        log.info("Chart %s -> %s", stem, path)


def cmd_deck(cfg: Settings) -> None:
    frames = _frames(cfg)
    ins = insights.build(frames, cfg)
    charts.render_all(frames, ins.takeaways, cfg)
    chart_dir = cfg.output_dir / "charts"
    log.info("Deck written to %s", deck.build_deck(ins, chart_dir, cfg))
    log.info("PDF written to %s", deck_pdf.build_pdf(ins, chart_dir, cfg))


COMMANDS = {
    "build-db": cmd_build_db,
    "analyze": cmd_analyze,
    "charts": cmd_charts,
    "deck": cmd_deck,
}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(prog="insightstory", description=__doc__)
    parser.add_argument("command", choices=[*COMMANDS, "all"])
    args = parser.parse_args()
    cfg = load_settings()
    if args.command == "all":
        for name in ("build-db", "analyze", "charts", "deck"):
            COMMANDS[name](cfg)
    else:
        COMMANDS[args.command](cfg)


if __name__ == "__main__":
    main()
