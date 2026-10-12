"""Emotion analysers (Strategy pattern).

* ``TransformerEmotionClient`` — Hugging Face DistilBERT (needs transformers + torch)
* ``KeywordEmotionClient``     — offline rule-based fallback, no dependencies
* ``FallbackEmotionClient``    — tries the model first, falls back to keywords
                                 if the model cannot load or crashes

``create_emotion_client()`` picks the best analyser available, so the app keeps
working when the model download fails or there is no internet.
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.exceptions import AnalysisError, InvalidInputError
from src.models import EMOTIONS, EmotionResult

DEFAULT_MODEL = "bhadresh-savani/distilbert-base-uncased-emotion"
MAX_TEXT_LENGTH = 1000


def validate_text(text) -> str:
    """Return cleaned text or raise ``InvalidInputError``."""
    if not isinstance(text, str):
        raise InvalidInputError("ข้อความต้องเป็นตัวอักษร (string)")
    cleaned = text.strip()
    if not cleaned:
        raise InvalidInputError("ข้อความต้องไม่เป็นค่าว่าง")
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise InvalidInputError(
            f"ข้อความยาวเกิน {MAX_TEXT_LENGTH} ตัวอักษร ({len(cleaned)})"
        )
    return cleaned


class EmotionAnalyzer(ABC):
    """Interface every analyser implements."""

    name = "base"

    @abstractmethod
    def get_emotion(self, text: str) -> EmotionResult:
        """Analyse ``text`` and return the top emotion."""


class TransformerEmotionClient(EmotionAnalyzer):
    """Wraps a Hugging Face text-classification pipeline."""

    name = "distilbert"

    def __init__(self, model_name: str = DEFAULT_MODEL, classifier=None):
        if classifier is None:
            try:
                from transformers import pipeline  # heavy import, done lazily
            except ImportError as exc:
                raise AnalysisError(
                    "ไม่ได้ติดตั้ง transformers/torch (pip install -r requirements-ml.txt)"
                ) from exc
            try:
                classifier = pipeline(
                    "text-classification", model=model_name, top_k=None
                )
            except Exception as exc:  # network error, missing weights, ...
                raise AnalysisError(f"โหลดโมเดลไม่สำเร็จ: {exc}") from exc
        self.classifier = classifier

    @staticmethod
    def _flatten(results) -> List[Dict]:
        """Pipelines return [{..}], [[{..}, ..]] or [{..}, ..] by version."""
        if not results:
            raise AnalysisError("โมเดลไม่คืนผลลัพธ์")
        if isinstance(results[0], list):
            return results[0]
        return results

    def get_emotion(self, text: str) -> EmotionResult:
        text = validate_text(text)
        try:
            scores = self._flatten(self.classifier(text))
            top = max(scores, key=lambda item: item["score"])
        except AnalysisError:
            raise
        except Exception as exc:
            raise AnalysisError(f"วิเคราะห์อารมณ์ไม่สำเร็จ: {exc}") from exc
        return EmotionResult(
            label=str(top["label"]).lower(),
            score=round(float(top["score"]), 4),
            source="model",
        )


class KeywordEmotionClient(EmotionAnalyzer):
    """Small lexicon-based analyser used when the ML model is unavailable."""

    name = "keyword"

    LEXICON: Dict[str, tuple] = {
        "joy": ("happy", "joy", "glad", "excited", "great", "awesome", "fun",
                "amazing", "wonderful", "delighted", "cheerful", "bright", "yay"),
        "sadness": ("sad", "lonely", "gloomy", "cry", "depressed", "miss",
                    "unhappy", "tired", "hopeless", "sorrow", "down", "lost"),
        "anger": ("angry", "furious", "mad", "hate", "annoyed", "rage",
                  "irritated", "terrible", "worst", "unfair", "bad"),
        "fear": ("afraid", "scared", "fear", "anxious", "worried", "nervous",
                 "terrified", "panic", "dark", "horror"),
        "love": ("love", "adore", "darling", "sweet", "romantic", "heart",
                 "care", "beloved", "kiss", "crush"),
        "surprise": ("surprise", "surprised", "unexpected", "wow", "shocked",
                     "suddenly", "unbelievable", "amazed", "cannot believe"),
    }

    def get_emotion(self, text: str) -> EmotionResult:
        text = validate_text(text).lower()
        words = re.findall(r"[a-z']+", text)
        counts = {emotion: 0 for emotion in EMOTIONS}
        for emotion, keywords in self.LEXICON.items():
            for keyword in keywords:
                if " " in keyword:
                    counts[emotion] += text.count(keyword)
                else:
                    counts[emotion] += words.count(keyword)
        total = sum(counts.values())
        if total == 0:
            # No keyword matched: say so honestly instead of guessing.
            return EmotionResult(label="neutral", score=0.0, source="keyword")
        label = max(EMOTIONS, key=lambda e: counts[e])
        # share of matches x evidence factor (1 match -> 0.5, 3 -> 0.75):
        # a single keyword never claims 100 % confidence.
        evidence = counts[label] / (counts[label] + 1)
        score = (counts[label] / total) * evidence
        return EmotionResult(label=label, score=round(score, 4), source="keyword")


class FallbackEmotionClient(EmotionAnalyzer):
    """Use ``primary`` but switch to ``fallback`` if it raises."""

    def __init__(self, primary: Optional[EmotionAnalyzer],
                 fallback: Optional[EmotionAnalyzer] = None):
        self.primary = primary
        self.fallback = fallback or KeywordEmotionClient()
        self.last_error: Optional[str] = None

    @property
    def name(self) -> str:
        return self.primary.name if self.primary else self.fallback.name

    def get_emotion(self, text: str) -> EmotionResult:
        validate_text(text)  # bad input is the user's fault: do not fall back
        if self.primary is not None:
            try:
                return self.primary.get_emotion(text)
            except AnalysisError as exc:
                self.last_error = str(exc)
        return self.fallback.get_emotion(text)


def create_emotion_client(offline: bool = False,
                          model_name: str = DEFAULT_MODEL) -> FallbackEmotionClient:
    """Return the best analyser available in this environment."""
    primary = None
    error = None
    if not offline:
        try:
            primary = TransformerEmotionClient(model_name)
        except AnalysisError as exc:
            error = str(exc)
    client = FallbackEmotionClient(primary)
    client.last_error = error
    return client
