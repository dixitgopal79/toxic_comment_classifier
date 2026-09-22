from backend.services.text_service import basic_text_stats
from backend.services.metrics_service import MetricsService

def test_text_stats():
    result = basic_text_stats("Hello WORLD!")
    assert result["characters"] == 12
    assert result["words"] == 2
    assert result["uppercase_ratio"] > 0

def test_metrics_empty():
    result = MetricsService().summarize([])
    assert result["total"] == 0
    assert result["toxic"] == 0

def test_metrics_rows():
    rows = [
        {
            "overall_toxic": True,
            "risk_level": "HIGH",
            "labels": {"toxic": True, "insult": True},
        },
        {
            "overall_toxic": False,
            "risk_level": "LOW",
            "labels": {"toxic": False},
        },
    ]
    result = MetricsService().summarize(rows)
    assert result["total"] == 2
    assert result["toxic"] == 1
    assert result["label_counts"]["toxic"] == 1
