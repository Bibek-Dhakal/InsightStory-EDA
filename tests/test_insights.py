from insightstory import charts, insights


def test_three_metric_backed_recommendations(frames, cfg):
    ins = insights.build(frames, cfg)
    assert len(ins.recommendations) == 3
    for rec in ins.recommendations:
        assert any(ch.isdigit() for ch in rec["evidence"])
        for source in rec["source"].split(","):
            assert source.strip() in frames


def test_takeaways_cover_every_chart(frames, cfg):
    ins = insights.build(frames, cfg)
    assert {spec[3] for spec in charts.SPECS} <= set(ins.takeaways)
    assert {"situation", "complication", "rfm", "margin", "recommendation"} <= set(ins.titles)
