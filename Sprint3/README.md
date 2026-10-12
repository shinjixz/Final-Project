# Sprint 3: Web Dashboard & Deployment (Completed)

นำเสนอ: สัปดาห์ที่ 14 (29-30/9/2569) | กำหนดส่ง: 2/10/2569

## 🎯 เป้าหมาย Sprint 3

ต่อยอดจาก Sprint 2 (PaletteEngine 8 สี + WCAG 2.1 + Export) ไปเป็น Web Dashboard แบบ Responsive Glassmorphic UI พร้อมระบบสลับภาษา TH/EN, ตัวสกัดสีจากรูปภาพ และ Deploy ขึ้น GitHub Pages อัตโนมัติ

## 🔗 ความต่อเนื่องจาก Sprint 2

| สิ่งที่ Sprint 2 สร้างไว้                      | สิ่งที่ Sprint 3 นำไปใช้ต่อ                                                                                |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `PaletteEngine.EMOTION_PALETTES` (6 อารมณ์ × 8 สี) | พอร์ตเป็น`PALETTES` ใน `web/app.js` ค่าเหมือนกันทุกสี                                       |
| `calculate_contrast_ratio` / `evaluate_wcag_compliance`   | พอร์ตเป็น`contrastRatio` / `evaluateWcag` ผลลัพธ์ตรงกันทุกคู่สี (ทดสอบกับ Python) |
| `ReportGenerator.export_to_css` / `export_to_json`        | ปุ่ม Download CSS / JSON ใช้รูปแบบไฟล์เดียวกัน                                                     |
| `AIAdvisory` (joy, sadness, anger)                          | คงธีมเดิม และเพิ่ม fear, love, neutral ให้ครบ 6 อารมณ์                                         |

## ✅ Deliverables ที่ส่งมอบ

### 1. Frontend (`web/`)

| ไฟล์           | หน้าที่                                                                                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `web/index.html` | โครงหน้า: วิเคราะห์จากข้อความ, จากรูปภาพ, จานสี, คำแนะนำ, ตรวจ WCAG                                       |
| `web/style.css`  | Glassmorphic UI (`backdrop-filter`) สีพื้นหลังเปลี่ยนตามจานสีที่สร้าง, Responsive, รองรับ `prefers-reduced-motion` |
| `web/app.js`     | Logic ทั้งหมด แยกส่วน Pure logic ออกจาก DOM เพื่อให้ทดสอบด้วย Node ได้                                                |

### 2. Bilingual Toggle (TH/EN)

- ปุ่มสลับภาษามุมขวาบน จำค่าที่เลือกไว้ใน `localStorage` (ถ้าเบราว์เซอร์ปิดการเก็บข้อมูล จะใช้ภาษาไทยเป็นค่าเริ่มต้น)
- ข้อความทุกจุดใช้ `data-i18n` + พจนานุกรม `I18N` (th/en คีย์ตรงกัน 100%)
- ตัววิเคราะห์ข้อความรับได้ทั้งคำอังกฤษและคำไทย

### 3. Image Color Extractor

- ลากรูปมาวางหรือเลือกไฟล์ ย่อรูปบน `<canvas>` แล้วสกัด 8 สีเด่น (quantize 4 บิต/ช่อง + คัดสีที่ห่างกันพอ)
- ประมวลผลในเบราว์เซอร์ทั้งหมด **ไม่มีการอัปโหลดรูป**
- ผลลัพธ์เข้าสู่ส่วน Export และตรวจ WCAG เหมือนจานสีจากข้อความ

### 4. CI/CD (`.github/workflows/deploy-web.yml`)

- Trigger: push ไป `main` ที่แตะ `web/**` หรือรันเองผ่าน `workflow_dispatch`
- Job `test` รัน `pytest tests/sprint3` ก่อน ถ้าไม่ผ่านจะไม่ Deploy
- Job `deploy` อัปโหลดโฟลเดอร์ `web/` ไปยัง GitHub Pages
- ต้องเปิดครั้งแรกที่ **Settings → Pages → Source: GitHub Actions**

### 5. Unit Tests (31 tests)

`tests/sprint3/test_web.py` — รัน `pytest tests/sprint3 -v`

| กลุ่มเทส    | จำนวน | ตรวจอะไร                                                                          |
| ------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| TestWebFiles        | 4          | ไฟล์ครบ, ลิงก์ asset ถูก, id ใน JS มีใน HTML, path เป็น relative |
| TestWorkflow        | 3          | ขั้นตอน Pages ครบ, publish`web/`, เทสต้องผ่านก่อน deploy       |
| TestSprint2Parity   | 6          | จานสีและ WCAG ตรงกับ`palette_engine.py` (ทุกคู่สี)                |
| TestAdvisoryAndI18n | 7          | Advisory ตรง Sprint 1, th/en คีย์ครบและตรงกัน                          |
| TestAnalyzer        | 4          | คำสำคัญอังกฤษ/ไทย, ข้อความว่าง → neutral                      |
| TestImageExtractor  | 5          | ครบ 8 สี, สีเด่นมาก่อน, พิกเซลโปร่งใสถูกข้าม         |
| TestExportParity    | 2          | CSS/JSON ตรงกับ`ReportGenerator`                                                  |

เทสที่รัน JavaScript ต้องมี Node.js (ไม่มีจะถูกข้ามอัตโนมัติ) และเทส Export ต้องมี `pandas`

ผลรันล่าสุดในสภาพแวดล้อมพัฒนา: **31 passed**


## 👥 บทบาทสมาชิก Sprint 3

> ปรับชื่อให้ตรงกับทีมจริงก่อนส่ง

| สมาชิก | บทบาท | งานที่ทำ                                                                                           |
| ------------ | ---------- | ---------------------------------------------------------------------------------------------------------- |
| ปลั๊ก   | Planner    | ออกแบบโครงหน้าเว็บ, กำหนดคำแปล TH/EN, วางขั้นตอน CI/CD               |
| กาย       | Coder      | เขียน Image Extractor                                                                                 |
| ภีม       | Coder      | เขียน`index.html`, `style.css`, `app.js`                                                        |
| ท็อป     | Debugger   | เขียน`tests/sprint3`, ตรวจ Input Validation และกรณีรูปเสีย/ไฟล์ผิดชนิด |

## 📝 Changelog — Sprint 3

### [v0.3.0] - Sprint 3: Web Dashboard & Deployment

**Added**

- `web/index.html`, `web/style.css`, `web/app.js` (Responsive Glassmorphic UI)
- Bilingual toggle TH/EN
- Image Color Extractor (Canvas, 8 สี)
- Advisory เพิ่ม fear, love, neutral
- `.github/workflows/deploy-web.yml` (test → deploy ไป GitHub Pages)
- `tests/sprint3/test_web.py` (31 tests)

**Changed**

- แยกโค้ด `src/` ตาม Sprint: `sprint1/`, `sprint2/`, `sprint3/`

## 📂 ไฟล์ที่เกี่ยวข้อง

```
Sprint3/
├── src/
│   ├── app.js          ← Web Logic (JavaScript)
│   ├── index.html      ← Web UI (โครงหน้าเว็บ)
│   └── style.css       ← Styling (CSS)
├── test/
│   └── test_web.py     ← Web Tests
└── README.md
```
