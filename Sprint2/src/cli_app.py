"""
Module: cli_app.py
Role: Coder 2 (ภีม) & Debugger (ปลั๊ก)
Description: CLI Loop + Input Validation + Batch (Sprint 1)
             + บันทึก DB / คำแนะนำดีไซน์ / WCAG / Export (Sprint 2)
"""
import os
from src.report_generator import ReportGenerator


class CLIApp:
    def __init__(self, emotion_client, palette_engine, visualizer,
                 data_store=None, advisory=None, export_dir=None):
        self.client = emotion_client
        self.engine = palette_engine
        self.viz = visualizer
        self.db = data_store
        self.advisory = advisory
        self.export_dir = export_dir

    def analyze(self, text: str) -> dict:
        res = self.client.get_emotion(text)
        pal = self.engine.get_palette(res['label'])
        return {"text": text, "label": res['label'], "score": res['score'],
                "palette": pal, "fallback": res.get('fallback', False)}

    def _persist(self, r: dict):
        """บันทึก DB อย่างปลอดภัย: ถ้า DB พัง ไม่ให้ทั้งโปรแกรมล้ม"""
        if not self.db:
            return
        try:
            self.db.save_palette(r['text'], r['label'], r['score'], r['palette'])
        except Exception as e:
            print(f"⚠️ บันทึกฐานข้อมูลไม่สำเร็จ: {e}")

    def _export(self, r: dict):
        if not self.export_dir:
            return
        j = ReportGenerator.export_to_json(
            r['label'], r['palette'], os.path.join(self.export_dir, "palette.json"), r['score'])
        c = ReportGenerator.export_to_css(
            r['palette'], os.path.join(self.export_dir, "palette.css"), r['label'])
        print(f"📁 Export แล้ว: {j}, {c}")

    def run(self):
        print("==================================================")
        print("  Smart Art & Palette Sentiment Analyzer (CLI)")
        print("==================================================")

        while True:
            try:
                user_input = input("\nกรอกข้อความภาษาอังกฤษ (หรือพิมพ์ 'quit' เพื่อออก): ").strip()

                if not user_input:
                    print("⚠️ คำเตือน: ข้อความต้องไม่เป็นค่าว่าง!")
                    continue
                if user_input.lower() in ['quit', 'exit']:
                    print("ขอบคุณที่ใช้งานระบบ! ปิดการทำงานเรียบร้อยครับ")
                    break

                r = self.analyze(user_input)
                print(f"\nผลการวิเคราะห์: {r['label'].upper()} (Confidence: {r['score']*100:.2f}%)")
                if r['fallback']:
                    print("ℹ️ ผลนี้มาจากโหมด Fallback (ไม่ได้ใช้โมเดลจริง)")
                print(f"จานสีที่แนะนำ: {r['palette']}")

                if hasattr(self.engine, "accessibility_report"):
                    acc = self.engine.accessibility_report(r['label'])
                    bp = acc['best_pair']
                    print(f"♿ WCAG: คู่สีอ่านง่ายสุด {bp['foreground']} บน {bp['background']} "
                          f"= {bp['contrast_ratio']}:1 {bp['status']} "
                          f"({acc['pairs_passing_aa']}/{acc['total_pairs']} คู่ผ่าน AA)")
                if self.advisory:
                    print("\n" + self.advisory.format_advice(r['label']))

                self._persist(r)
                self._export(r)
                self.viz.plot_palette(r['label'], r['palette'], r['score'])

            except KeyboardInterrupt:
                print("\n\nยกเลิกการทำงานอย่างสุภาพเรียบร้อยครับ")
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")

    def run_batch(self, filepath: str, output_path: str = None) -> list:
        results = ReportGenerator.process_batch_csv(filepath, self.client, self.engine)
        for r in results:
            print(f"[{r['label'].upper():8}] {r['score']*100:6.2f}%  {r['text']}")
            self._persist(r)
        if output_path:
            ReportGenerator.write_batch_csv(results, output_path)
            print(f"\n💾 บันทึกผลลัพธ์ที่ {output_path}")
        return results

    def show_history(self, limit: int = 10):
        if not self.db:
            print("ไม่ได้เปิดใช้งานฐานข้อมูล")
            return []
        rows = self.db.get_history(limit)
        if not rows:
            print("ยังไม่มีประวัติ")
        for h in rows:
            cloud = "☁️" if h['synced'] else "  "
            print(f"#{h['id']:<4}{cloud} [{h['emotion'].upper():8}] {h['confidence']*100:6.2f}%  "
                  f"{h['input_text']}  ({h['created_at']})")
        return rows
