"""Presentation Layer — interactive menu-driven CLI.

The CLI only reads input, calls ``AnalysisService`` and prints results.
All business rules live in the service; every expected error is an
``AppError`` and is shown as a warning so the loop never crashes.
"""

from datetime import date
from typing import Callable, List, Optional

from src.analysis_service import SORT_FIELDS, AnalysisService
from src.exceptions import AppError, InvalidInputError
from src.models import ALL_LABELS, EMOTIONS, AnalysisRecord
from src.report_generator import ReportGenerator
from src.visualizer import PaletteVisualizer

MENU = """
================ เมนูหลัก ================
 1) วิเคราะห์ข้อความ (Create)
 2) ดูประวัติทั้งหมด (Read)
 3) ดูรายละเอียด + คำแนะนำดีไซน์ + WCAG
 4) แก้ไขข้อความและวิเคราะห์ใหม่ (Update)
 5) ลบรายการ (Delete)
 6) ค้นหา (Search)
 7) กรอง (Filter)
 8) เรียงลำดับ (Sort)
 9) ส่งออกจานสี JSON / CSS
10) ประมวลผลไฟล์ CSV (Batch)
11) สถิติ + AI Insight Report
 0) ออกจากโปรแกรม (หรือพิมพ์ quit)
==========================================="""

QUIT_WORDS = {"0", "q", "quit", "exit", "ออก"}


class CLIApp:
    """Menu loop. ``input_func``/``output_func`` are injectable for tests."""

    def __init__(self, service: AnalysisService,
                 input_func: Callable[[str], str] = input,
                 output_func: Callable[[str], None] = print,
                 use_color: bool = True):
        self.service = service
        self._input = input_func
        self._print = output_func
        self.use_color = use_color
        self.actions = {
            "1": self.do_analyze, "2": self.do_list, "3": self.do_detail,
            "4": self.do_update, "5": self.do_delete, "6": self.do_search,
            "7": self.do_filter, "8": self.do_sort, "9": self.do_export,
            "10": self.do_batch, "11": self.do_stats,
        }

    # -------------------------------------------------------------- helpers
    def ask(self, prompt: str) -> str:
        return self._input(prompt).strip()

    def ask_optional_float(self, prompt: str) -> Optional[float]:
        raw = self.ask(prompt)
        if not raw:
            return None
        try:
            value = float(raw)
        except ValueError as exc:
            raise InvalidInputError(f"'{raw}' ไม่ใช่ตัวเลข") from exc
        return value / 100 if value > 1 else value  # accept 80 or 0.8

    def ask_optional_date(self, prompt: str) -> Optional[date]:
        raw = self.ask(prompt)
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError as exc:
            raise InvalidInputError("รูปแบบวันที่ต้องเป็น YYYY-MM-DD") from exc

    def show_record(self, record: AnalysisRecord) -> None:
        self._print(
            f"[{record.id}] {record.emotion.upper():8} {record.confidence:6.1%}  "
            f"{record.created_at}  \"{record.input_text[:50]}\""
        )

    def show_records(self, records: List[AnalysisRecord]) -> None:
        if not records:
            self._print("(ไม่พบรายการ)")
            return
        for record in records:
            self.show_record(record)
        self._print(f"รวม {len(records)} รายการ")

    def show_palette(self, colors: List[str]) -> None:
        if self.use_color:
            self._print(PaletteVisualizer.render_text(colors))
        else:
            self._print(" ".join(colors))

    # -------------------------------------------------------------- actions
    def do_analyze(self) -> None:
        text = self.ask("กรอกข้อความภาษาอังกฤษ: ")
        record = self.service.analyze(text)
        self._print(f"\nผลการวิเคราะห์: {record.emotion.upper()} "
                    f"(Confidence: {record.confidence:.2%})")
        if getattr(self.service.analyzer, "last_error", None):
            self._print("ℹ️ ใช้โหมดสำรอง (keyword) เพราะโมเดล AI ไม่พร้อม")
        self.show_palette(record.hex_colors)
        if self.service.last_was_duplicate:
            self._print(f"ℹ️ ข้อความนี้มีในประวัติแล้ว "
                        f"อัปเดตรายการเดิม id={record.id} แทนการบันทึกซ้ำ")
        else:
            self._print(f"✅ บันทึกแล้ว id={record.id}")

    def do_list(self) -> None:
        self.show_records(self.service.list_history())

    def do_detail(self) -> None:
        record = self.service.get(self.ask("id ที่ต้องการดู: "))
        self.show_record(record)
        self.show_palette(record.hex_colors)
        advice = self.service.advisory.get_advice(record.emotion)
        self._print(f"ธีม: {advice['theme']}\nฟอนต์: {advice['font']}\n"
                    f"เหมาะกับ: {advice['usage']}")
        pair = self.service.palette_engine.best_text_pair(record.hex_colors)
        self._print(f"คู่สีอ่านง่ายที่สุด: {pair['foreground']} บน {pair['background']}"
                    f" = {pair['contrast_ratio']}:1 → {pair['status']}")

    def do_update(self) -> None:
        record_id = self.ask("id ที่ต้องการแก้ไข: ")
        self.service.get(record_id)  # fail fast if it does not exist
        record = self.service.update_text(record_id, self.ask("ข้อความใหม่: "))
        self._print("✅ แก้ไขแล้ว")
        self.show_record(record)

    def do_delete(self) -> None:
        record_id = self.ask("id ที่ต้องการลบ: ")
        record = self.service.get(record_id)
        self.show_record(record)
        if self.ask("ยืนยันการลบ? (y/n): ").lower() == "y":
            self.service.delete(record_id)
            self._print("🗑️ ลบแล้ว")
        else:
            self._print("ยกเลิกการลบ")

    def do_search(self) -> None:
        keyword = self.ask("คำค้นหา (ข้อความ / อารมณ์ / รหัสสี): ")
        self.show_records(self.service.search(self.service.list_history(), keyword))

    def do_filter(self) -> None:
        emotion = self.ask(f"อารมณ์ ({'/'.join(EMOTIONS)}, เว้นว่าง = ทั้งหมด): ").lower()
        if emotion and emotion not in ALL_LABELS:  # fail fast, before more prompts
            raise InvalidInputError(f"ไม่รู้จักอารมณ์ '{emotion}'")
        min_c = self.ask_optional_float("ความมั่นใจต่ำสุด % (เว้นว่างได้): ")
        max_c = self.ask_optional_float("ความมั่นใจสูงสุด % (เว้นว่างได้): ")
        d_from = self.ask_optional_date("ตั้งแต่วันที่ YYYY-MM-DD (เว้นว่างได้): ")
        d_to = self.ask_optional_date("ถึงวันที่ YYYY-MM-DD (เว้นว่างได้): ")
        records = self.service.filter(
            self.service.list_history(), emotion=emotion or None,
            min_confidence=min_c, max_confidence=max_c,
            date_from=d_from, date_to=d_to,
        )
        self.show_records(records)

    def do_sort(self) -> None:
        fields = "/".join(SORT_FIELDS)
        by = self.ask(f"เรียงตาม ({fields}) [date]: ").lower() or "date"
        if by not in SORT_FIELDS:
            raise InvalidInputError(f"เรียงตาม '{by}' ไม่ได้ (ใช้ได้: {fields})")
        then_by = self.ask(f"เรียงรองตาม ({fields}, เว้นว่างได้): ") or None
        order = self.ask("มาก→น้อย? (y/n) [y]: ").lower() or "y"
        if order not in ("y", "n"):
            raise InvalidInputError("ตอบ y หรือ n เท่านั้น")
        self.show_records(self.service.sort(
            self.service.list_history(), by=by,
            descending=order == "y", then_by=then_by,
        ))

    def do_export(self) -> None:
        record = self.service.get(self.ask("id ของจานสีที่จะส่งออก: "))
        base = f"exports/palette_{record.id}"
        json_path = ReportGenerator.export_to_json(
            record.emotion, record.hex_colors, base + ".json")
        css_path = ReportGenerator.export_to_css(record.hex_colors, base + ".css")
        self._print(f"✅ ส่งออก {json_path} และ {css_path}")

    def do_batch(self) -> None:
        path = self.ask("path ไฟล์ CSV (เช่น data/sample_batch.csv): ")
        rows = ReportGenerator.process_batch_csv(path, self.service)
        out = ReportGenerator.write_batch_output(rows, "exports/batch_output.csv")
        failed = sum(1 for row in rows if row["error"])
        self._print(f"✅ ประมวลผล {len(rows)} แถว (ผิดพลาด {failed}) → {out}")

    def do_stats(self) -> None:
        self._print(self.service.insight_report())

    # ------------------------------------------------------------ main loop
    def handle(self, choice: str) -> bool:
        """Run one menu choice. Returns False when the user wants to quit."""
        choice = choice.strip().lower()
        if choice in QUIT_WORDS:
            return False
        action = self.actions.get(choice)
        if action is None:
            self._print("⚠️ ไม่มีเมนูนี้ กรุณาเลือก 0–11")
            return True
        try:
            action()
        except AppError as exc:
            self._print(f"⚠️ {exc}")
        return True

    def run(self) -> None:
        self._print("==================================================")
        self._print("  Smart Art & Palette Sentiment Analyzer (CLI)")
        self._print(f"  Analyzer: {self.service.analyzer.name}")
        self._print("==================================================")
        recovered = getattr(self.service.store, "recovered_from", None)
        if recovered:
            self._print(f"⚠️ ฐานข้อมูลเดิมเสียหาย ย้ายไปไว้ที่ {recovered} "
                        "และสร้างฐานข้อมูลใหม่แล้ว")
        while True:
            try:
                self._print(MENU)
                if not self.handle(self.ask("เลือกเมนู: ")):
                    self._print("ขอบคุณที่ใช้งานระบบ! ปิดการทำงานเรียบร้อยครับ")
                    break
            except (KeyboardInterrupt, EOFError):
                self._print("\nยกเลิกการทำงานเรียบร้อยครับ")
                break
            except Exception as exc:  # last line of defence: never crash
                self._print(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {exc}")
