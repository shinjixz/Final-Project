"""Export palettes to JSON/CSS and process batch CSV files.

Uses only the standard library (csv/json) so it runs anywhere.
"""

import csv
import json
import os
from typing import Dict, List

from src.exceptions import InvalidInputError, StorageError
from src.palette_engine import PaletteEngine


class ReportGenerator:
    """File exports and batch processing."""

    @staticmethod
    def _ensure_folder(filename: str) -> None:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

    @classmethod
    def _write(cls, filename: str, content: str) -> str:
        try:
            cls._ensure_folder(filename)
            with open(filename, "w", encoding="utf-8") as handle:
                handle.write(content)
        except OSError as exc:
            raise StorageError(f"เขียนไฟล์ {filename} ไม่ได้: {exc}") from exc
        return filename

    @staticmethod
    def _validate_palette(palette: List[str]) -> None:
        if not palette:
            raise InvalidInputError("palette ว่างเปล่า")
        for color in palette:
            PaletteEngine.hex_to_rgb(color)  # raises InvalidInputError

    @classmethod
    def export_to_css(cls, palette: List[str], filename: str = "palette.css") -> str:
        cls._validate_palette(palette)
        lines = [":root {"]
        lines += [f"  --color-{i}: {color};" for i, color in enumerate(palette, 1)]
        lines.append("}")
        return cls._write(filename, "\n".join(lines) + "\n")

    @classmethod
    def export_to_json(cls, emotion: str, palette: List[str],
                       filename: str = "palette.json") -> str:
        cls._validate_palette(palette)
        data = {"emotion": emotion, "colors": palette}
        return cls._write(filename, json.dumps(data, indent=2, ensure_ascii=False))

    @classmethod
    def export_history_json(cls, records, filename: str) -> str:
        data = [r.to_dict() for r in records]
        return cls._write(filename, json.dumps(data, indent=2, ensure_ascii=False))

    @staticmethod
    def read_batch_csv(filepath: str) -> List[str]:
        """Return the non-empty values of the ``text`` column."""
        try:
            with open(filepath, newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames or "text" not in reader.fieldnames:
                    raise InvalidInputError("ไฟล์ CSV ต้องมีคอลัมน์ชื่อ 'text'")
                texts = [(row.get("text") or "").strip() for row in reader]
        except FileNotFoundError as exc:
            raise StorageError(f"ไม่พบไฟล์: {filepath}") from exc
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            raise StorageError(f"อ่านไฟล์ CSV ไม่ได้: {exc}") from exc
        return [t for t in texts if t]

    @classmethod
    def process_batch_csv(cls, filepath: str, service, save: bool = True) -> List[Dict]:
        """Analyse every row; rows that fail are reported, not fatal."""
        results = []
        for text in cls.read_batch_csv(filepath):
            try:
                record = service.analyze(text, save=save)
                results.append({
                    "text": text, "emotion": record.emotion,
                    "score": record.confidence,
                    "palette": " ".join(record.hex_colors), "error": "",
                })
            except Exception as exc:  # keep processing the other rows
                results.append({"text": text, "emotion": "", "score": "",
                                "palette": "", "error": str(exc)})
        return results

    @classmethod
    def write_batch_output(cls, rows: List[Dict], filename: str) -> str:
        try:
            cls._ensure_folder(filename)
            with open(filename, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=["text", "emotion", "score", "palette", "error"]
                )
                writer.writeheader()
                writer.writerows(rows)
        except OSError as exc:
            raise StorageError(f"เขียนไฟล์ {filename} ไม่ได้: {exc}") from exc
        return filename
