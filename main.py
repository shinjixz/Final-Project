"""Entry point.

Examples
--------
python main.py                         # interactive CLI (AI model, falls back to keyword)
python main.py --offline               # CLI without downloading the AI model
python main.py --batch data/sample_batch.csv
python main.py --db data/demo.db       # use another database file
"""

import argparse
import sys

from src.analysis_service import AnalysisService
from src.cli_app import CLIApp
from src.data_store import DEFAULT_DB_PATH, DataStore
from src.emotion_client import create_emotion_client
from src.exceptions import AppError
from src.report_generator import ReportGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smart Art & Palette Sentiment Analyzer")
    parser.add_argument("--batch", metavar="CSV",
                        help="ประมวลผลไฟล์ CSV ที่มีคอลัมน์ 'text'")
    parser.add_argument("--output", default="exports/batch_output.csv",
                        help="ไฟล์ผลลัพธ์ของโหมด batch")
    parser.add_argument("--offline", action="store_true",
                        help="ไม่โหลดโมเดล AI ใช้ keyword analyser แทน")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="path ฐานข้อมูล SQLite")
    parser.add_argument("--no-color", action="store_true",
                        help="ไม่แสดงสีในเทอร์มินัล")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    print("กำลังเริ่มต้นระบบ...")
    try:
        analyzer = create_emotion_client(offline=args.offline)
        if analyzer.last_error:
            print(f"ℹ️ ใช้ keyword analyser แทนโมเดล AI: {analyzer.last_error}")
        service = AnalysisService(analyzer, DataStore(args.db))

        if args.batch:
            rows = ReportGenerator.process_batch_csv(args.batch, service)
            out = ReportGenerator.write_batch_output(rows, args.output)
            failed = sum(1 for row in rows if row["error"])
            print(f"✅ ประมวลผล {len(rows)} แถว (ผิดพลาด {failed}) → {out}")
            return 0

        CLIApp(service, use_color=not args.no_color).run()
        return 0
    except AppError as exc:
        print(f"❌ {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
