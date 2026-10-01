import matplotlib.pyplot as plt

from insightstory import charts, deck_pdf, insights


def test_pdf_slides_match_deck_structure(frames, cfg):
    ins = insights.build(frames, cfg)
    charts.render_all(frames, ins.takeaways, cfg)
    figs = deck_pdf.build_slides(ins, cfg.output_dir / "charts")
    assert len(figs) == 5
    for fig in figs:
        plt.close(fig)


def test_pdf_is_written(frames, cfg):
    ins = insights.build(frames, cfg)
    charts.render_all(frames, ins.takeaways, cfg)
    path = deck_pdf.build_pdf(ins, cfg.output_dir / "charts", cfg)
    assert path.suffix == ".pdf"
    assert path.read_bytes().startswith(b"%PDF")
