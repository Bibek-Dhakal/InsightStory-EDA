import matplotlib.pyplot as plt

from insightstory import charts, insights


def test_every_chart_has_takeaway_callout(frames, cfg):
    ins = insights.build(frames, cfg)
    for stem, func, frame_key, takeaway_key in charts.SPECS:
        fig = func(frames[frame_key], ins.takeaways[takeaway_key])
        assert any(t.get_text().startswith("Takeaway:") for t in fig.texts), stem
        plt.close(fig)


def test_render_all_writes_pngs(frames, cfg):
    ins = insights.build(frames, cfg)
    paths = charts.render_all(frames, ins.takeaways, cfg)
    assert len(paths) == len(charts.SPECS)
    assert all(p.exists() and p.suffix == ".png" for p in paths.values())
