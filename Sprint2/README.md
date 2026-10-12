# Sprint 2: Persistence, Report & AI Advisory

**ส่งงาน:** สัปดาห์ที่ 13 | กำหนดส่ง: 25/9/2569

## 🎯 เป้าหมาย Sprint 2

ต่อยอดจาก Sprint 1 (วิเคราะห์อารมณ์ → จานสี) ด้วยการเก็บประวัติลง SQLite พร้อมรองรับ Sync ขึ้น Cloud, ส่งออกจานสีเป็น JSON/CSS, ประมวลผล Batch CSV, ให้คำแนะนำด้านดีไซน์และฟอนต์ตามอารมณ์ และตรวจความอ่านง่ายของสีด้วย WCAG 2.1

## 🔗 ความต่อเนื่องจาก Sprint 1

| ส่วน                                                         | Sprint 1                         | Sprint 2 (สิ่งที่เปลี่ยน)                                        |
| ---------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------------------ |
| `emotion_client.py`                                            | HF Pipeline + Defensive Fallback | ไม่เปลี่ยน                                                           |
| `visualizer.py`                                                | Matplotlib Swatches              | ไม่เปลี่ยน                                                           |
| `palette_engine.py`                                            | แมป 6 อารมณ์ → 8 สี  | **+ WCAG 2.1 Contrast Ratio**                                            |
| `cli_app.py`                                                   | Interactive + Validation + Batch | **+ บันทึก DB, คำแนะนำดีไซน์, WCAG, Export, History** |
| `main.py`                                                      | `--batch`, `--output`        | **+ `--history`, `--sync`, `--export-dir`, `--db`**              |
| `data_store.py` / `report_generator.py` / `ai_advisory.py` | —                               | **ใหม่ทั้งหมด**                                               |

เทสต์ของ Sprint 1 (7 เทส) ยังอยู่ใน `tests/test_emotion_client.py` และผ่านครบ (Regression)

## ✅ Deliverables ที่ส่งมอบ

### 1. OOP Class Architecture (ส่วนที่เพิ่ม)

| คลาส                     | ไฟล์                    | หน้าที่                                                                      |
| ---------------------------- | --------------------------- | ----------------------------------------------------------------------------------- |
| `DataStore`                | `src/data_store.py`       | SQLite`data/palette_history.db` (Create + Read) + Cloud Sync                      |
| `HttpUploader`             | `src/data_store.py`       | ส่งข้อมูลขึ้น Cloud ผ่าน HTTP POST (JSON)                          |
| `ReportGenerator`          | `src/report_generator.py` | Export JSON/CSS + ประมวลผล/เขียน Batch CSV                             |
| `AIAdvisory`               | `src/ai_advisory.py`      | แนวคิดดีไซน์ + Font Pairings + การใช้งาน ครบ 6 อารมณ์ |
| `PaletteEngine` (ขยาย) | `src/palette_engine.py`   | Relative Luminance, Contrast Ratio, WCAG AA/AAA                                     |

### 2. SQLite Persistence + Cloud Sync

- ตาราง `palette_history`: id, input_text, predicted_emotion, confidence_score, hex_colors (JSON), palette_size, created_at, **synced**
- สร้างโฟลเดอร์ `data/` อัตโนมัติ และ **migrate DB เก่าจาก Sprint 1** (เพิ่มคอลัมน์ `synced`) โดยไม่ทำให้ข้อมูลหาย
- `sync_to_cloud()` ส่งเฉพาะแถวที่ยังไม่ sync ทีละ batch แล้วทำเครื่องหมายเมื่อสำเร็จ
- Defensive: ถ้า Cloud ล่ม/ไม่ตอบ ข้อมูลยังอยู่ใน SQLite และถูกส่งใหม่รอบหน้า โปรแกรมไม่พัง
- ตั้งปลายทางด้วยตัวแปรสภาพแวดล้อม `CLOUD_SYNC_URL` (ถ้าไม่ตั้ง ระบบข้ามการ Sync อย่างปลอดภัย)

> หมายเหตุ: `HttpUploader` ส่ง `POST {"records": [...]}` ไปยัง URL ที่กำหนด — ต้องมี endpoint ฝั่ง Cloud ที่รับรูปแบบนี้ (หรือเขียน uploader ใหม่ที่เป็น `callable(records) -> bool` แล้วส่งเข้า `sync_to_cloud(uploader=...)`)

### 3. Report & Export

- `export_to_json` → `{"emotion", "colors", "confidence"}`
- `export_to_css` → ตัวแปร `:root { --color-1 … --color-8 }`
- `process_batch_csv` → อ่านคอลัมน์ `text` ข้ามแถวว่าง และข้ามแถวที่พังโดยไม่หยุดทั้งไฟล์
- `write_batch_csv` → บันทึกผลเป็น CSV (text, emotion, score, palette)

### 4. AI Advisory

คืน `theme`, `concept`, `font_pairing {heading, body}`, `usage` สำหรับ joy / sadness / anger / fear / love / neutral (อารมณ์ที่ไม่รู้จัก → neutral)

### 5. WCAG 2.1 Contrast Ratio

- `calculate_contrast_ratio`, `evaluate_wcag_compliance` (AAA ≥ 7.0, AA ≥ 4.5)
- `best_contrast_pair` หาคู่สีตัวอักษร/พื้นหลังที่อ่านง่ายที่สุดในจานสี
- `accessibility_report` สรุปจำนวนคู่สีที่ผ่าน AA จาก 28 คู่ (C(8,2))
- CLI แสดงผล WCAG ทุกครั้งที่วิเคราะห์

### 6. Unit Tests (46/46 Passed — รวม Regression Sprint 1)

| ไฟล์                           | จำนวน | ครอบคลุม                                                                                       |
| ---------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| `tests/test_emotion_client.py`   | 7          | (Sprint 1) Parsing, Fallback, Palette Mapping, Batch                                                   |
| `tests/test_data_store.py`       | 7          | CRUD, ลำดับประวัติ, Validation, Sync สำเร็จ/ล้มเหลว/ไม่มี URL, Migration |
| `tests/test_report_generator.py` | 6          | JSON/CSS, Batch (แถวว่าง, ไม่มีคอลัมน์ text, แถวพัง), เขียน CSV          |
| `tests/test_ai_advisory.py`      | 10         | ครบ 6 อารมณ์, Fallback, ไม่สนตัวพิมพ์, คืนสำเนา, Format                  |
| `tests/test_palette_wcag.py`     | 13         | สูตร Contrast, AA/AAA/FAIL, Best Pair, รายงานทุกจานสี                                |
| `tests/test_cli_integration.py`  | 3          | Flow ครบ (บันทึก+Export+คำแนะนำ), DB พังแล้วไม่ล้ม, Batch→DB→History    |

```bash
pip install -r requirements.txt
pytest tests/ -v
python main.py                                   # Interactive
python main.py --batch in.csv --output out.csv   # Batch (บันทึก DB ด้วย)
python main.py --history 10                      # ดูประวัติ
python main.py --export-dir exports/             # Export JSON/CSS
CLOUD_SYNC_URL=https://example.com/api python main.py --sync
```

## 👥 บทบาทสมาชิก Sprint 2

| สมาชิก | บทบาท | งานที่ทำ                                                                   |
| ------------ | ---------- | ---------------------------------------------------------------------------------- |
| ท็อป     | Planner    | ออกแบบกฎ`AIAdvisory` และ Schema ฝั่ง Sync                         |
| กาย       | Coder 1    | `DataStore`, Cloud Sync, WCAG ใน `PaletteEngine`                             |
| ภีม       | Coder 2    | `ReportGenerator`, Export JSON/CSS, Batch, ต่อ CLI                            |
| ปลั๊ก   | Debugger   | Unit Tests, Migration DB, Defensive handling (DB/Cloud ล้มต้องไม่พัง) |

## 📝 Changelog — Sprint 2

### [v0.2.0] - Persistence, Report & AI Advisory

**Added**

- `DataStore` (SQLite) + `sync_to_cloud` / `HttpUploader` + คอลัมน์ `synced`
- `ReportGenerator` (JSON/CSS Export, Batch CSV)
- `AIAdvisory` ครบ 6 อารมณ์ พร้อม Font Pairings
- WCAG 2.1 Contrast Ratio ใน `PaletteEngine`
- CLI flags: `--history`, `--sync`, `--export-dir`, `--db`

**Changed**

- `CLIApp.run_batch` ใช้ `ReportGenerator` และบันทึกผลลง DB
- `get_history` เรียงตาม `id` แทน `created_at` (ป้องกันลำดับสลับเมื่อบันทึกในวินาทีเดียวกัน)

## 📂 ไฟล์ที่เกี่ยวข้อง

```
Sprint2/
├── src/
│   ├── ai_advisory.py       ← AI Advisory (คำแนะนำสี/พาเลตต์)
│   ├── cli_app.py           ← Interactive CLI
│   ├── data_store.py        ← Data Persistence (File I/O)
│   ├── palette_engine.py    ← Emotion→Palette + WCAG
│   └── report_generator.py  ← Report Generator
├── test/
│   ├── test_ai_advisory.py          ← ทดสอบ AI Advisory
│   ├── test_cli_integration.py      ← ทดสอบ CLI Integration
│   ├── test_data_store.py           ← ทดสอบ Data Store
│   ├── test_palette_wcag.py         ← ทดสอบ Palette + WCAG
│   └── test_report_generator.py     ← ทดสอบ Report Generator
├── main.py                  ← Entry Point
└── README.md
```
