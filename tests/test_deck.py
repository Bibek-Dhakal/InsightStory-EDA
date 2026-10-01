from pptx import Presentation

from insightstory import charts, deck, insights


def test_deck_has_five_slides(frames, cfg):
    ins = insights.build(frames, cfg)
    charts.render_all(frames, ins.takeaways, cfg)
    path = deck.build_deck(ins, cfg.output_dir / "charts", cfg)
    assert path.exists()
    assert len(Presentation(str(path)).slides) == 5
