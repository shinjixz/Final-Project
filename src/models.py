"""Domain models."""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List, Optional

EMOTIONS = ("joy", "sadness", "anger", "fear", "love", "surprise")
ALL_LABELS = EMOTIONS + ("neutral",)  # neutral = keyword fallback found nothing


@dataclass
class EmotionResult:
    """Output of an emotion analyser."""

    label: str
    score: float
    source: str = "model"  # "model" or "keyword" (offline fallback)


@dataclass
class AnalysisRecord:
    """One saved analysis in the history."""

    input_text: str
    emotion: str
    confidence: float
    hex_colors: List[str]
    id: Optional[int] = None
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    @property
    def palette_size(self) -> int:
        return len(self.hex_colors)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["palette_size"] = self.palette_size
        return data
