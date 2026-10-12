"""Measure CRUD/search/filter/sort speed on synthetic data.

Usage:  python scripts/benchmark.py            (prints a Markdown table)
        python scripts/benchmark.py --sizes 1000 10000 --out docs/BENCHMARK.md
"""

import argparse
import os
import platform
import random
import sys
import tempfile
import time
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analysis_service import AnalysisService  # noqa: E402
from src.data_store import DataStore  # noqa: E402
from src.emotion_client import KeywordEmotionClient  # noqa: E402
from src.models import EMOTIONS, AnalysisRecord  # noqa: E402
from src.palette_engine import PaletteEngine  # noqa: E402

WORDS = ("happy", "sad", "furious", "scared", "love", "wow", "project",
         "weather", "today", "team", "music", "dark", "bright", "coffee")


def timed(func, repeat=5):
    """Return (result, best time in ms) over ``repeat`` runs."""
    best = float("inf")
    result = None
    for _ in range(repeat):
        start = time.perf_counter()
        result = func()
        best = min(best, (time.perf_counter() - start) * 1000)
    return result, best


def run(size: int, rng: random.Random):
    with tempfile.TemporaryDirectory() as tmp:
        store = DataStore(os.path.join(tmp, "bench.db"))
        service = AnalysisService(KeywordEmotionClient(), store)
        records = []
        for _ in range(size):
            emotion = rng.choice(EMOTIONS)
            records.append(AnalysisRecord(
                input_text=" ".join(rng.choices(WORDS, k=8)),
                emotion=emotion, confidence=round(rng.random(), 4),
                hex_colors=PaletteEngine.get_palette(emotion),
            ))

        start = time.perf_counter()
        for record in records:
            store.add(record)
        insert_ms = (time.perf_counter() - start) * 1000

        rows, load_ms = timed(store.list_all)
        _, search_ms = timed(lambda: service.search(rows, "coffee"))
        _, filter_ms = timed(lambda: service.filter(
            rows, emotion="joy", min_confidence=0.5, date_to=date.today()))
        _, sort_ms = timed(lambda: service.sort(rows, by="confidence"))
        _, multi_ms = timed(lambda: service.sort(rows, by="emotion", then_by="confidence"))
        _, get_ms = timed(lambda: store.get(size // 2))

    return {
        "size": size, "insert_total": insert_ms, "insert_each": insert_ms / size,
        "load": load_ms, "get": get_ms, "search": search_ms, "filter": filter_ms,
        "sort": sort_ms, "multi": multi_ms,
    }


def analyze_speed(n=2000):
    client = KeywordEmotionClient()
    texts = ["I am so happy and excited about this new project today"] * n
    start = time.perf_counter()
    for text in texts:
        client.get_emotion(text)
    return n / (time.perf_counter() - start)


def to_markdown(results, per_second) -> str:
    lines = [
        "| ข้อมูล (แถว) | Insert ทั้งหมด | Insert/แถว | โหลดทั้งหมด | Get by id "
        "| Search | Filter | Sort | Multi-key sort |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['size']:,} | {r['insert_total']:.0f} ms | {r['insert_each']:.2f} ms "
            f"| {r['load']:.1f} ms | {r['get']:.2f} ms | {r['search']:.2f} ms "
            f"| {r['filter']:.2f} ms | {r['sort']:.2f} ms | {r['multi']:.2f} ms |"
        )
    lines.append("")
    lines.append(f"Keyword analyser (โหมดออฟไลน์): ~{per_second:,.0f} ข้อความ/วินาที")
    lines.append("")
    lines.append(f"เครื่องที่วัด: Python {platform.python_version()} บน "
                 f"{platform.system()} {platform.machine()} — ค่าที่รายงานคือเวลาดีที่สุดจาก 5 รอบ "
                 "(ยกเว้น Insert ที่วัดรอบเดียว; insert แต่ละแถว commit ลงดิสก์ทันที)")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 1000, 10000])
    parser.add_argument("--out", help="เขียนผลลงไฟล์ Markdown")
    args = parser.parse_args()
    rng = random.Random(42)
    table = to_markdown([run(size, rng) for size in args.sizes], analyze_speed())
    print(table)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write("# Benchmark Results\n\nสร้างโดย `python scripts/benchmark.py`\n\n")
            handle.write(table + "\n")


if __name__ == "__main__":
    main()
