"""Data Access Layer — SQLite repository for analysis history (CRUD).

Resilience:
* creates the ``data/`` folder automatically if it is missing
* if the database file is corrupted, it is renamed to ``*.corrupt-<time>``
  and a fresh database is created, so the program never crashes on start
* every SQLite error is wrapped in ``StorageError``
"""

import json
import os
import shutil
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime
from typing import List, Optional

from src.exceptions import RecordNotFoundError, StorageError
from src.models import AnalysisRecord

DEFAULT_DB_PATH = os.path.join("data", "palette_history.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS palette_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_text TEXT NOT NULL,
    predicted_emotion TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    hex_colors TEXT NOT NULL,
    palette_size INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
"""

_COLUMNS = ("id, input_text, predicted_emotion, confidence_score, "
            "hex_colors, created_at")


class DataStore:
    """CRUD repository over a single SQLite table."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.recovered_from: Optional[str] = None
        self._init_db()

    # ---------------------------------------------------------------- setup
    @contextmanager
    def _connect(self):
        """Open a connection, commit on success and always close it."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:  # transaction: commit or rollback
                yield conn

    def _init_db(self) -> None:
        folder = os.path.dirname(self.db_path)
        try:
            if folder:
                os.makedirs(folder, exist_ok=True)
            self._create_schema()
        except sqlite3.DatabaseError:
            self._recover_corrupted_db()
        except OSError as exc:
            raise StorageError(f"สร้างฐานข้อมูลไม่ได้: {exc}") from exc

    def _create_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(_SCHEMA)
            conn.execute("SELECT COUNT(*) FROM palette_history").fetchone()

    def _recover_corrupted_db(self) -> None:
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup = f"{self.db_path}.corrupt-{stamp}"
        try:
            shutil.move(self.db_path, backup)
            self._create_schema()
        except (OSError, sqlite3.DatabaseError) as exc:
            raise StorageError(f"กู้คืนฐานข้อมูลที่เสียหายไม่สำเร็จ: {exc}") from exc
        self.recovered_from = backup

    @staticmethod
    def _row_to_record(row) -> AnalysisRecord:
        try:
            colors = json.loads(row[4])
        except (TypeError, ValueError):
            colors = []
        return AnalysisRecord(
            id=row[0], input_text=row[1], emotion=row[2],
            confidence=row[3], hex_colors=colors, created_at=row[5],
        )

    def _execute(self, sql: str, params: tuple = ()):
        try:
            with self._connect() as conn:
                cursor = conn.execute(sql, params)
                return cursor.fetchall(), cursor.lastrowid, cursor.rowcount
        except sqlite3.Error as exc:
            raise StorageError(f"ฐานข้อมูลผิดพลาด: {exc}") from exc

    # ----------------------------------------------------------------- CRUD
    def add(self, record: AnalysisRecord) -> AnalysisRecord:
        """Create: insert a record and return it with its new id."""
        _, last_id, _ = self._execute(
            "INSERT INTO palette_history (input_text, predicted_emotion, "
            "confidence_score, hex_colors, palette_size, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (record.input_text, record.emotion, record.confidence,
             json.dumps(record.hex_colors), record.palette_size,
             record.created_at),
        )
        record.id = last_id
        return record

    def get(self, record_id: int) -> AnalysisRecord:
        """Read one record or raise ``RecordNotFoundError``."""
        rows, _, _ = self._execute(
            f"SELECT {_COLUMNS} FROM palette_history WHERE id = ?", (record_id,)
        )
        if not rows:
            raise RecordNotFoundError(record_id)
        return self._row_to_record(rows[0])

    def list_all(self) -> List[AnalysisRecord]:
        """Read every record (newest first)."""
        rows, _, _ = self._execute(
            f"SELECT {_COLUMNS} FROM palette_history ORDER BY id DESC"
        )
        return [self._row_to_record(row) for row in rows]

    def get_history(self, limit: int = 10) -> List[AnalysisRecord]:
        """Read the most recent ``limit`` records."""
        rows, _, _ = self._execute(
            f"SELECT {_COLUMNS} FROM palette_history ORDER BY id DESC LIMIT ?",
            (int(limit),),
        )
        return [self._row_to_record(row) for row in rows]

    def update(self, record: AnalysisRecord) -> AnalysisRecord:
        """Update every field of an existing record."""
        if record.id is None:
            raise RecordNotFoundError(-1)
        _, _, changed = self._execute(
            "UPDATE palette_history SET input_text = ?, predicted_emotion = ?, "
            "confidence_score = ?, hex_colors = ?, palette_size = ? WHERE id = ?",
            (record.input_text, record.emotion, record.confidence,
             json.dumps(record.hex_colors), record.palette_size, record.id),
        )
        if changed == 0:
            raise RecordNotFoundError(record.id)
        return record

    def delete(self, record_id: int) -> None:
        """Delete one record or raise ``RecordNotFoundError``."""
        _, _, changed = self._execute(
            "DELETE FROM palette_history WHERE id = ?", (record_id,)
        )
        if changed == 0:
            raise RecordNotFoundError(record_id)

    def clear(self) -> int:
        """Delete every record and return how many were removed."""
        _, _, changed = self._execute("DELETE FROM palette_history")
        return changed

    def count(self) -> int:
        rows, _, _ = self._execute("SELECT COUNT(*) FROM palette_history")
        return rows[0][0]
