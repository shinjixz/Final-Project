# 🧪 Test Cases Documentation — Smart Art & Palette

เอกสารจัดเก็บ Test Cases ของโปรเจกต์ Smart Art & Palette Sentiment Analyzer ส่วนแรกคือชุดทดสอบปัจจุบันที่รันกับโค้ดใน `src/` และ `web/` ส่วนท้ายคือบันทึกการทดสอบของ Sprint 1–3 (โค้ดในโฟลเดอร์ `Sprint1/`–`Sprint3/`) เก็บไว้เป็นประวัติ

## 🚀 Final Sprint — ชุดทดสอบอัตโนมัติปัจจุบัน (`pytest`)

**สรุป:** 125 test cases · ผ่าน 125 · coverage ของ `src/` ≈ 92% · รันอัตโนมัติบน GitHub Actions (Python 3.10 / 3.11 / 3.12)

```bash
pip install -r requirements-dev.txt
flake8 && pytest --cov=src --cov-report=term-missing
```

| ไฟล์ | จำนวน | ทดสอบอะไร |
| :--- | :---: | :--- |
| `tests/test_emotion_client.py` | 21 | ตรวจข้อความว่าง/ยาวเกิน/ไม่ใช่ string, keyword 6 อารมณ์ + neutral, output โมเดลแบบ nested/flat/ว่าง/crash, fallback |
| `tests/test_palette_engine.py` | 23 | จานสี 8 สีทุกอารมณ์, อารมณ์ไม่รู้จัก, HEX ผิดรูปแบบ, contrast 21:1, ระดับ AAA/AA/FAIL, คู่สีดีที่สุด |
| `tests/test_data_store.py` | 12 | CRUD, คงอยู่หลังเปิดใหม่, สร้างโฟลเดอร์ที่หาย, กู้ DB เสีย, JSON สีเสีย, ตารางถูกลบ, ค้นข้อความซ้ำ |
| `tests/test_analysis_service.py` | 29 | Create/Update/Delete, id ผิด 6 แบบ, search/filter/sort รวมเคสขอบเขต (ค่าติดลบ, >1, ช่วงกลับด้าน, วันที่, ฟิลด์ผิด, list ว่าง), กันบันทึกข้อความซ้ำ |
| `tests/test_report_generator.py` | 12 | Export CSS/JSON, palette ผิด, path เขียนไม่ได้, batch: แถวว่าง, แถวผิดไม่ทำให้ล้ม, ไฟล์หาย, ไม่มีคอลัมน์, ไฟล์ binary |
| `tests/test_ai_advisory.py` | 11 | คำแนะนำครบ 6 อารมณ์, ค่า default, insight report |
| `tests/test_cli.py` | 8 | ขับเมนู CLI จริงด้วยอินพุตจำลอง: QUIT/Quit/ออก, CRUD flow, อินพุตผิด 9 แบบไม่ crash, ยกเลิกลบ, Ctrl+C, ข้อความซ้ำ |
| `tests/test_main.py` | 2 | โหมด batch end-to-end, ไฟล์หายคืน exit code 1 |
| `tests/test_visualizer.py` | 2 | แสดงสีในเทอร์มินัล, บันทึก PNG |
| `tests/test_web.py` | 5 | ไม่มีค่าความมั่นใจปลอม/`localhost`, โหลด AI แบบ lazy, จานสี Python = เว็บ, keyword fallback JS = Python |

### QA Log — Final Sprint (Observation / Expected / Actual)

| รหัส | สิ่งที่ทำ (Observation) | ผลที่คาดหวัง (Expected) | ผลจริงก่อนแก้ (Actual — before) | ผลหลังแก้ | สถานะ |
| :--- | :--- | :--- | :--- | :--- | :---: |
| FT-01 | `python main.py` จาก repo ที่ clone ใหม่ | เปิดเมนูได้ | `ModuleNotFoundError: No module named 'Sprint4'` | เปิดเมนูได้ | PASSED |
| FT-02 | `pytest` | เทสต์รันได้ | error 10/10 ไฟล์ตอน collect | 125 passed | PASSED |
| FT-03 | วิเคราะห์ข้อความใน CLI | บันทึกลง DB | `AttributeError: save_analysis` | บันทึกแล้ว id=n | PASSED |
| FT-04 | ลบ id=99 ที่ไม่มีอยู่ | แจ้ง `RecordNotFoundError` ไม่พัง | ไม่มีเมนูลบ | `⚠️ ไม่พบรายการ id=99` | PASSED |
| FT-05 | ลบโฟลเดอร์ `data/` แล้วเปิดโปรแกรม | สร้างใหม่อัตโนมัติ | `sqlite3.OperationalError: unable to open database file` | สร้างใหม่ | PASSED |
| FT-06 | เขียนขยะทับไฟล์ `.db` | กู้คืนได้ | โปรแกรมพัง | สำรองเป็น `.corrupt-*` + DB ใหม่ | PASSED |
| FT-07 | เว็บ: CDN/โมเดลโหลดไม่ได้ | แจ้งผู้ใช้ ใช้โหมดสำรอง | แสดง `SADNESS 99.5%` ทุกครั้ง | แสดงผลด่วนทันที (`Joy 50.0% (ผลด่วน)`) แล้วอัปเดตเป็นผล AI เมื่อโหลดเสร็จ ถ้าโหลดไม่ได้คงผลด่วน + ข้อความเตือน (ทดสอบด้วย headless Chromium) | PASSED |
| FT-08 | เว็บ: อัปโหลดรูป | ไม่แสดงตัวเลขปลอม | ความมั่นใจสุ่ม 90–98% | แสดง “ประเมินจากโทนสี” | PASSED |
| FT-09 | กรองด้วยความมั่นใจ -5 ถึง 100 | ปฏิเสธค่าติดลบ | ไม่มีฟีเจอร์กรอง | `⚠️ ค่าความมั่นใจต้องอยู่ระหว่าง 0 ถึง 1` | PASSED |
| FT-10 | เรียง 10,000 แถวด้วยคีย์ผสม | < 50 ms | ไม่มีฟีเจอร์เรียง | ~3 ms (`scripts/benchmark.py`) | PASSED |
| FT-11 | วิเคราะห์ข้อความเดิมซ้ำ ("I'm Boring" × 6) | ไม่บันทึกซ้ำ | ประวัติมี 6 แถวเหมือนกัน | อัปเดตรายการเดิม 1 แถว (CLI และเว็บ) และเว็บรวมรายการซ้ำที่มีอยู่เดิมให้อัตโนมัติ | PASSED |
| FT-12 | เว็บ: เก็บประวัติเกิน 10 รายการ | เก็บได้มากขึ้น | เก็บได้แค่ 10 รายการ | สูงสุด 200, แสดงทีละ 10, ลบทีละรายการ, พื้นที่เต็มลบรายการเก่าสุดให้ | PASSED |
| FT-13 | เว็บ: ประวัติของรูปภาพ | แสดงรูปย่อ | แสดงข้อความ `data:image/...base64` | แสดงรูปย่อ + ชื่อไฟล์ (รายการเก่าก็แสดงได้) | PASSED |

---

## 📜 ประวัติการทดสอบ Sprint 1–3 (เก็บไว้เป็นบันทึก)

> ตารางด้านล่างเป็นผลการทดสอบของโค้ดเวอร์ชัน Sprint 1–3 (โฟลเดอร์ `Sprint1/`–`Sprint3/`) ซึ่งบางส่วน เช่น คำสำคัญภาษาไทยและ `pandas` ไม่ได้อยู่ในโค้ดปัจจุบันแล้ว ผลของโค้ดปัจจุบันดูที่ส่วน Final Sprint ด้านบน

## 📋 ตารางสรุปผลการทดสอบระบบ (Quality Assurance & Test Suite Matrix)

**สรุป:** 38 เคส · ผ่าน 36 · ไม่ผ่าน 2 (TC-09, TC-23)

### Sprint 1: Emotion Client, Advisory, CLI, Visualizer

| Test ID | หมวดการทดสอบ | รายละเอียดการทดสอบ                                           | อินพุต (Input)                  | ผลลัพธ์ที่คาดหวัง (Expected Output)                                                  | ผลการทดสอบจริง (Actual Output)           | สถานะ |
| ------- | ------------------------ | ------------------------------------------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------- |
| TC-01   | Emotion Client           | จัดการผลลัพธ์แบบ List ซ้อน List                            | `[[{SADNESS 0.1}, {JOY 0.912345}]]` | คืนอารมณ์ที่คะแนนสูงสุด ตัวพิมพ์เล็ก ปัดเศษ 4 ตำแหน่ง | `{'label': 'joy', 'score': 0.9123}`                  | PASSED     |
| TC-02   | Emotion Client           | จัดการผลลัพธ์แบบ List ชั้นเดียว                       | `[{ANGER 0.77777}]`                 | คืน`anger` คะแนนปัดเศษ                                                                | `{'label': 'anger', 'score': 0.7778}`                | PASSED     |
| TC-03   | AI Advisory              | ดึงคำแนะนำโดยไม่สนตัวพิมพ์                           | emotion = "JOY"                       | ธีม "Vibrant Sunburst"                                                                             | Vibrant Sunburst                                       | PASSED     |
| TC-04   | AI Advisory              | อารมณ์ที่ไม่มีในกฎ                                           | emotion = "zzz"                       | ใช้ค่าเริ่มต้น "Modern Neutral"                                                         | Modern Neutral                                         | PASSED     |
| TC-05   | CLI Validation           | ป้อนข้อความว่างหรือเว้นวรรค                         | `""`, `"   "`, `quit`           | แจ้งเตือนค่าว่าง วนถามใหม่ ไม่ crash                                      | แจ้งเตือน 2 ครั้ง แล้วออกปกติ | PASSED     |
| TC-06   | CLI Control              | ออกจากโปรแกรมไม่สนตัวพิมพ์                           | `QUIT`                              | แสดงข้อความปิดระบบและจบ loop                                                   | แสดงข้อความปิดระบบ                   | PASSED     |
| TC-07   | CLI Flow                 | วิเคราะห์ข้อความปกติ (ใช้ Mock client/store/visualizer) | "I am happy",`exit`                 | แสดงผล JOY, บันทึก 1 ครั้ง, วาดจานสี 1 ครั้ง                            | แสดง JOY, save 1 ครั้ง, plot 1 ครั้ง     | PASSED     |
| TC-08   | CLI Control              | กด Ctrl+C ระหว่างรอ input                                           | `KeyboardInterrupt`                 | แสดงข้อความยกเลิกอย่างสุภาพ และจบ                                     | แสดงข้อความยกเลิก                     | PASSED     |
| TC-09   | Visualizer               | เรนเดอร์จานสี Matplotlib                                          | emotion=joy, 8 สี, score=0.9        | วาดภาพได้ไม่มี error                                                                    | ทำงานสำเร็จ (backend Agg)                   | PASSED     |

### Sprint 2: PaletteEngine, DataStore, ReportGenerator

| Test ID | หมวดการทดสอบ | รายละเอียดการทดสอบ                       | อินพุต (Input)                             | ผลลัพธ์ที่คาดหวัง (Expected Output)         | ผลการทดสอบจริง (Actual Output) | สถานะ |
| ------- | ------------------------ | ---------------------------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------ | -------------------------------------------- | ---------- |
| TC-10   | Palette Mapping          | ดึงจานสี 8 สีตามอารมณ์                  | emotion = "joy"                                  | List 8 สี HEX                                              | 8 สี                                       | PASSED     |
| TC-11   | Palette Mapping          | อารมณ์ไม่รู้จัก / ค่าว่าง            | "x",`None`                                     | ใช้จานสี neutral                                     | ตรงกับ neutral ทั้งสองกรณี  | PASSED     |
| TC-12   | Palette Mapping          | Normalize ข้อความ                                   | `"  JOY "`                                     | ได้จานสีเดียวกับ "joy"                       | เท่ากัน                               | PASSED     |
| TC-13   | Color Utility            | แปลง HEX เป็น RGB                                  | `#FFD166`                                      | `(255, 209, 102)`                                          | `(255, 209, 102)`                          | PASSED     |
| TC-14   | Color Utility            | HEX รูปแบบผิด                                     | `#12`                                          | โยน`ValueError`                                         | `Invalid HEX color format: #12`            | PASSED     |
| TC-15   | WCAG Luminance           | ความสว่างขอบเขต                             | (0,0,0) และ (255,255,255)                     | 0.0 และ 1.0                                               | 0.0 และ 1.0                               | PASSED     |
| TC-16   | WCAG Contrast            | อัตราส่วนคอนทราสต์ขาว-ดำ            | `#000000` / `#FFFFFF` (สลับที่ได้) | 21.0 ทั้งสองทิศทาง, สีเดียวกัน = 1.0  | 21.0, 21.0, 1.0                              | PASSED     |
| TC-17   | WCAG Evaluation          | ระดับ AAA (≥ 7.0)                                    | `#073B4C` บน `#FFFCF9`                     | PASS (AAA)                                                   | 11.81 → PASS (AAA)                          | PASSED     |
| TC-18   | WCAG Evaluation          | ระดับ AA (4.5–6.99)                                  | `#767676` บน `#FFFFFF`                     | PASS (AA)                                                    | 4.54 → PASS (AA)                            | PASSED     |
| TC-19   | WCAG Evaluation          | ไม่ผ่านเกณฑ์ (< 4.5)                           | `#FFD166` บน `#FFFCF9`                     | FAIL,`is_compliant = False`                                | 1.41 → FAIL                                 | PASSED     |
| TC-20   | Database Persistence     | สร้างตาราง`palette_history` อัตโนมัติ | DB ไฟล์ใหม่                              | ตารางถูกสร้าง                                   | พบตาราง`palette_history`            | PASSED     |
| TC-21   | Database Persistence     | บันทึกแล้วอ่านกลับ                       | `save_palette(...)` + `get_history()`        | `hex_colors` กลับมาเป็น List เดิม            | ตรงกับจานสีเดิม               | PASSED     |
| TC-22   | Database Persistence     | ประวัติเมื่อฐานข้อมูลว่าง         | DB ใหม่                                      | `[]` ไม่มี error                                      | `[]`                                       | PASSED     |
| TC-23   | Export                   | ส่งออก CSS Variables                                 | จานสี love                                  | ไฟล์`:root { --color-1: ...; }`                        | ได้ไฟล์ตามรูปแบบ             | PASSED     |
| TC-24   | Export                   | ส่งออก JSON                                          | emotion=love + 8 สี                            | JSON มีคีย์`emotion`, `colors`                     | มีคีย์ครบ                           | PASSED     |
| TC-25   | Batch Processing         | ประมวลผล CSV หลายแถว                        | CSV คอลัมน์`text` 2 แถว              | DataFrame 2 แถว คอลัมน์ text/emotion/score/palette | shape (2, 4) ตรงตามคอลัมน์      | PASSED     |

### Sprint 3: Web Dashboard & Deployment (รันด้วย `pytest tests/sprint3 -v`)

| Test ID | หมวดการทดสอบ | รายละเอียดการทดสอบ                   | อินพุต (Input)                       | ผลลัพธ์ที่คาดหวัง (Expected Output)                               | ผลการทดสอบจริง (Actual Output)                        | สถานะ |
| ------- | ------------------------ | ------------------------------------------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ---------- |
| TC-26   | Web Files                | ไฟล์เว็บครบและลิงก์ถูกต้อง   | `web/`                                   | มี index/style/app, ลิงก์เป็น relative path                             | ผ่านทุกเงื่อนไข (4 เทส)                           | PASSED     |
| TC-27   | Web Files                | id ที่ JS เรียกใช้มีใน HTML ครบ      | `app.js` vs `index.html`               | ไม่มี id ที่หายไป                                                     | ไม่มี id ขาด                                                | PASSED     |
| TC-28   | Sprint 2 Parity          | จานสีในเว็บตรงกับ Python              | 6 อารมณ์ × 8 สี                   | ค่าเหมือนกันทุกสี, unknown → neutral                             | ตรงกันทั้งหมด                                          | PASSED     |
| TC-29   | Sprint 2 Parity          | WCAG ในเว็บตรงกับ Python                   | ทุกคู่สีของทุกจานสี     | ratio และสถานะเท่ากับ`palette_engine.py`                          | ตรงกันทุกคู่                                            | PASSED     |
| TC-30   | UI Bilingual Switch      | พจนานุกรม TH/EN ครบและตรงกัน      | `I18N` + `data-i18n` ใน HTML         | คีย์ th = en, ทุกคีย์ใน HTML มีคำแปล                           | ตรงกัน 100% (7 เทส รวม Advisory)                        | PASSED     |
| TC-31   | Text Analyzer            | จับคำสำคัญอังกฤษ/ไทย                | "I am so happy", "ฉันกลัวมาก"    | joy, fear                                                                          | joy, fear                                                           | PASSED     |
| TC-32   | Text Analyzer            | ข้อความว่างหรือไม่มีคำสำคัญ | `""`, `null`, "table chair"            | neutral, score 0.5                                                                 | `{'label': 'neutral', 'score': 0.5}`                              | PASSED     |
| TC-33   | Image Extractor          | สกัดสีจากพิกเซลสังเคราะห์     | พิกเซลแดง 60 / น้ำเงิน 10  | ได้ 8 สี HEX ถูกรูปแบบ แดงมาก่อน                            | `#FF0000` ลำดับแรก, มี `#0000FF`                      | PASSED     |
| TC-34   | Image Extractor          | พิกเซลโปร่งใส / รูปสีเดียว      | alpha = 0 / สีเดียว 40 พิกเซล | โปร่งใสถูกข้าม, รูปสีเดียวยังได้ครบ 8 ช่อง    | โปร่งใสทั้งหมด →`[]`, สีเดียว → 8 ช่อง | PASSED     |
| TC-35   | Export Parity            | CSS/JSON จากเว็บตรงกับ`ReportGenerator` | จานสี joy / fear                      | ข้อความไฟล์เหมือนกันทุกตัวอักษร                     | ตรงกัน                                                        | PASSED     |
| TC-36   | CI/CD Workflow           | Workflow deploy ครบขั้นตอน                   | `deploy-web.yml`                         | มี configure/upload/deploy-pages, publish`web/`, test ต้องผ่านก่อน | ครบทุกเงื่อนไข                                        | PASSED     |

## 🔬 รายละเอียดเคสการทดสอบเชิงลึก (Detailed Test Case Specs)

### 🔹 TC-01 & TC-02: Emotion Client Data Structure Checking

- **การทดสอบ:** `EmotionClient.get_emotion()` ต้องรองรับทั้งผลลัพธ์แบบ `[[...]]` (เมื่อ `return_all_scores=True`) และ `[{...}]`
- **ข้อควรระวัง:** ทดสอบด้วย classifier จำลอง (mock) ไม่ได้โหลดโมเดล Hugging Face จริง เพราะต้องดาวน์โหลดโมเดล จึงควรทดสอบ Integration กับโมเดลจริงอีกครั้งบนเครื่องที่ออนไลน์

### 🔹 TC-15 – TC-18: WCAG 2.1 Contrast Evaluation

- **เกณฑ์:** AAA ≥ 7.0, AA ≥ 4.5, ต่ำกว่านั้น FAIL
- **ค่าอ้างอิง:** ขาว-ดำ = 21.0 (สูงสุด), `#767676` บนขาว = 4.54 (ค่าสีเทาที่เข้มที่สุดซึ่งยังผ่าน AA บนพื้นขาว)

### 🔹 TC-28 – TC-29, TC-35: Sprint 2 ↔ Sprint 3 Parity

- **การทดสอบ:** รัน `web/app.js` ด้วย Node.js แล้วเทียบกับ Python โดยตรง จึงมั่นใจได้ว่าจานสี WCAG และไฟล์ Export ของเว็บให้ผลเหมือน Sprint 2
- **เงื่อนไข:** ต้องมี Node.js (ไม่มีจะถูกข้ามอัตโนมัติ) และเทส Export ต้องมี `pandas`
