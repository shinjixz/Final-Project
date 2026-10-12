import pytest

from src.ai_advisory import AIAdvisory
from src.models import EMOTIONS, AnalysisRecord


@pytest.mark.parametrize("emotion", EMOTIONS)
def test_every_emotion_has_specific_advice(emotion):
    advice = AIAdvisory.get_advice(emotion.upper())
    assert advice != AIAdvisory.DEFAULT_ADVICE
    assert set(advice) == {"theme", "font", "usage"}


@pytest.mark.parametrize("emotion", ["neutral", "", None])
def test_default_advice(emotion):
    assert AIAdvisory.get_advice(emotion) == AIAdvisory.DEFAULT_ADVICE


def test_insight_empty():
    assert "ยังไม่มีประวัติ" in AIAdvisory.generate_insight_report([])


def test_insight_flags_low_confidence():
    records = [AnalysisRecord("a", "joy", 0.9, ["#000000"]),
               AnalysisRecord("b", "joy", 0.3, ["#000000"]),
               AnalysisRecord("c", "fear", 0.8, ["#000000"])]
    report = AIAdvisory.generate_insight_report(records)
    assert "JOY" in report and "Vibrant Sunburst" in report
    assert "1 รายการที่ความมั่นใจต่ำ" in report
