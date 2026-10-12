"""Business Logic Layer — the only class the UI talks to.

Wires analyser + palette engine + repository together and implements the
data-processing algorithms: search, filter, sort and statistics.
"""

from collections import Counter
from datetime import date, datetime
from typing import Dict, List, Optional, Sequence

from src.ai_advisory import AIAdvisory
from src.data_store import DataStore
from src.emotion_client import EmotionAnalyzer, validate_text
from src.exceptions import InvalidInputError
from src.models import ALL_LABELS, AnalysisRecord
from src.palette_engine import PaletteEngine

SORT_FIELDS = {
    "id": lambda r: r.id or 0,
    "date": lambda r: r.created_at,
    "confidence": lambda r: r.confidence,
    "emotion": lambda r: r.emotion,
    "text": lambda r: r.input_text.lower(),
}


class AnalysisService:
    """Use-cases of the application."""

    def __init__(self, analyzer: EmotionAnalyzer, store: DataStore,
                 palette_engine=PaletteEngine, advisory=AIAdvisory):
        self.analyzer = analyzer
        self.store = store
        self.palette_engine = palette_engine
        self.advisory = advisory
        self.last_was_duplicate = False

    # ---------------------------------------------------------------- CRUD
    def analyze(self, text: str, save: bool = True) -> AnalysisRecord:
        """Create: analyse text, build palette and (optionally) save it.

        If the same text (ignoring case and extra spaces) is already saved,
        the existing record is updated instead of adding a duplicate;
        ``last_was_duplicate`` tells the caller which one happened.
        """
        text = validate_text(text)
        result = self.analyzer.get_emotion(text)
        record = AnalysisRecord(
            input_text=text,
            emotion=result.label,
            confidence=result.score,
            hex_colors=self.palette_engine.get_palette(result.label),
        )
        self.last_was_duplicate = False
        if not save:
            return record
        existing = self.store.find_by_text(text)
        if existing is not None:
            existing.input_text = record.input_text
            existing.emotion = record.emotion
            existing.confidence = record.confidence
            existing.hex_colors = record.hex_colors
            self.last_was_duplicate = True
            return self.store.update(existing)
        return self.store.add(record)

    def get(self, record_id: int) -> AnalysisRecord:
        return self.store.get(self._parse_id(record_id))

    def list_history(self, limit: Optional[int] = None) -> List[AnalysisRecord]:
        if limit is None:
            return self.store.list_all()
        return self.store.get_history(limit)

    def update_text(self, record_id: int, new_text: str) -> AnalysisRecord:
        """Update: change the text of a record and re-analyse it."""
        record = self.get(record_id)
        fresh = self.analyze(new_text, save=False)
        record.input_text = fresh.input_text
        record.emotion = fresh.emotion
        record.confidence = fresh.confidence
        record.hex_colors = fresh.hex_colors
        return self.store.update(record)

    def delete(self, record_id: int) -> None:
        self.store.delete(self._parse_id(record_id))

    def clear_history(self) -> int:
        return self.store.clear()

    # ---------------------------------------------- search / filter / sort
    @staticmethod
    def search(records: Sequence[AnalysisRecord], keyword: str) -> List[AnalysisRecord]:
        """Case-insensitive linear search in text, emotion and colours. O(n)."""
        keyword = (keyword or "").strip().lower()
        if not keyword:
            raise InvalidInputError("คำค้นหาต้องไม่เป็นค่าว่าง")
        return [
            r for r in records
            if keyword in r.input_text.lower()
            or keyword == r.emotion
            or any(keyword == c.lower() for c in r.hex_colors)
        ]

    @staticmethod
    def filter(records: Sequence[AnalysisRecord], emotion: Optional[str] = None,
               min_confidence: Optional[float] = None,
               max_confidence: Optional[float] = None,
               date_from: Optional[date] = None,
               date_to: Optional[date] = None) -> List[AnalysisRecord]:
        """Filter by emotion, confidence range (0–1) and date range."""
        if emotion is not None:
            emotion = emotion.strip().lower()
            if emotion not in ALL_LABELS:
                raise InvalidInputError(
                    f"ไม่รู้จักอารมณ์ '{emotion}' (ใช้ได้: {', '.join(ALL_LABELS)})"
                )
        for value in (min_confidence, max_confidence):
            if value is not None and not 0 <= value <= 1:
                raise InvalidInputError("ค่าความมั่นใจต้องอยู่ระหว่าง 0 ถึง 1")
        if (min_confidence is not None and max_confidence is not None
                and min_confidence > max_confidence):
            raise InvalidInputError("ค่าต่ำสุดต้องไม่มากกว่าค่าสูงสุด")
        if date_from and date_to and date_from > date_to:
            raise InvalidInputError("วันที่เริ่มต้องไม่อยู่หลังวันที่สิ้นสุด")

        def keep(r: AnalysisRecord) -> bool:
            if emotion and r.emotion != emotion:
                return False
            if min_confidence is not None and r.confidence < min_confidence:
                return False
            if max_confidence is not None and r.confidence > max_confidence:
                return False
            if date_from or date_to:
                day = datetime.fromisoformat(r.created_at).date()
                if date_from and day < date_from:
                    return False
                if date_to and day > date_to:
                    return False
            return True

        return [r for r in records if keep(r)]

    @staticmethod
    def sort(records: Sequence[AnalysisRecord], by: str = "date",
             descending: bool = True,
             then_by: Optional[str] = None) -> List[AnalysisRecord]:
        """Stable multi-key sort (Timsort, O(n log n))."""
        for field_name in filter(None, (by, then_by)):
            if field_name not in SORT_FIELDS:
                raise InvalidInputError(
                    f"เรียงตาม '{field_name}' ไม่ได้ (ใช้ได้: {', '.join(SORT_FIELDS)})"
                )
        result = list(records)
        # Python's sort is stable: sort by the secondary key first.
        if then_by:
            result.sort(key=SORT_FIELDS[then_by])
        result.sort(key=SORT_FIELDS[by], reverse=descending)
        return result

    # ------------------------------------------------------------- reports
    def statistics(self) -> Dict[str, object]:
        records = self.store.list_all()
        counts = Counter(r.emotion for r in records)
        avg = sum(r.confidence for r in records) / len(records) if records else 0.0
        return {
            "total": len(records),
            "by_emotion": dict(counts.most_common()),
            "average_confidence": round(avg, 4),
        }

    def insight_report(self) -> str:
        return self.advisory.generate_insight_report(self.store.list_all())

    @staticmethod
    def _parse_id(record_id) -> int:
        try:
            value = int(str(record_id).strip())
        except (TypeError, ValueError) as exc:
            raise InvalidInputError(f"id ต้องเป็นตัวเลข: {record_id!r}") from exc
        if value <= 0:
            raise InvalidInputError("id ต้องเป็นจำนวนเต็มบวก")
        return value
