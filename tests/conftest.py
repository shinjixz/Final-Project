"""Shared fixtures. The real AI model is never loaded in tests."""
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.analysis_service import AnalysisService  # noqa: E402
from src.data_store import DataStore  # noqa: E402
from src.emotion_client import EmotionAnalyzer, validate_text  # noqa: E402
from src.models import EmotionResult  # noqa: E402


class FakeAnalyzer(EmotionAnalyzer):
    """Deterministic analyser: the first known emotion word wins."""

    name = "fake"

    def get_emotion(self, text):
        text = validate_text(text).lower()
        for label in ("joy", "sadness", "anger", "fear", "love", "surprise"):
            if label in text:
                return EmotionResult(label=label, score=0.9)
        return EmotionResult(label="joy", score=0.55)


@pytest.fixture
def store(tmp_path):
    return DataStore(str(tmp_path / "data" / "test.db"))


@pytest.fixture
def service(store):
    return AnalysisService(FakeAnalyzer(), store)


@pytest.fixture
def seeded(service):
    """Service with five known records."""
    for text in ("pure joy today", "deep sadness", "anger issues",
                 "love letter", "fear of the dark"):
        service.analyze(text)
    return service
