# Sprint 1: Core System Foundation & OOP CLI Architecture
**ส่งงาน:** สัปดาห์ที่ 12 (15-16/9/2569) | กำหนดส่ง: 18/9/2569

## 🎯 เป้าหมาย Sprint 1
สร้างโครงสร้าง OOP CLI Application สำหรับวิเคราะห์อารมณ์จากข้อความภาษาอังกฤษ (Hugging Face DistilBERT) แล้วแมปเป็นจานสีจิตวิทยา 8 สี พร้อมแสดงผลแบบ Visual Swatches และรองรับโหมด `--batch`

## ✅ Deliverables ที่ส่งมอบ

### 1. OOP Class Architecture
| คลาส | ไฟล์ | หน้าที่ |
|---|---|---|
| `EmotionClient` | `src/emotion_client.py` | ครอบ DistilBERT Pipeline พร้อม Defensive Fallback |
| `PaletteEngine` | `src/palette_engine.py` | แมป 6 อารมณ์ → จานสี 8 สี + คำนวณ WCAG 2.1 Contrast |
| `PaletteVisualizer` | `src/visualizer.py` | วาด Visual Swatches ด้วย Matplotlib |
| `CLIApp` | `src/cli_app.py` | Interactive CLI Loop + Input Validation + Batch |

### 2. CLI Interface
- รับข้อความภาษาอังกฤษแบบ Interactive (`quit` / `exit` เพื่อออก)
- Input Validation: ปฏิเสธข้อความว่าง, รองรับ Ctrl+C อย่างสุภาพ
- แสดงอารมณ์ + Confidence + รหัสสี HEX และวาด Swatch

### 3. Emotion → Palette Mapping
`joy`, `sadness`, `anger`, `fear`, `love`, `neutral` (อารมณ์ที่ไม่รู้จัก เช่น `surprise` → `neutral`)

### 4. Defensive Fallback
ถ้าโหลดโมเดลไม่ได้ / ไม่มี `transformers` / วิเคราะห์ล้มเหลว ระบบสลับไปใช้ Rule-Based Mock อัตโนมัติ (`fallback: True`) — โปรแกรมไม่พัง

### 5. Batch Mode
```bash
python main.py --batch input.csv --output result.csv   # CSV ต้องมีคอลัมน์ text
```

### 6. Unit Tests (8/8 Passed)
`tests/test_emotion_client.py` — ครอบคลุม Nested List Parsing, Empty Input, Fallback (error / ไม่มีโมเดล), Palette Mapping, WCAG Contrast, Batch CSV

```bash
pip install -r requirements.txt
pytest tests/ -v
python main.py
```

## 👥 บทบาทสมาชิก Sprint 1
| สมาชิก | บทบาท | งานที่ทำ |
|---|---|---|
| กาย | Planner | วางสถาปัตยกรรม OOP และแผนงาน |
| ท็อป | Coder 1 | `EmotionClient` (Hugging Face Pipeline) |
| ปลั๊ก | Coder 2 | `PaletteVisualizer`, `CLIApp`, Batch Mode |
| ภีม | Debugger | Nested-List Fix, Input Validation, Fallback, Unit Tests |

## 📝 Changelog — Sprint 1
### [v0.1.0] - Core System Foundation & OOP CLI Architecture
**Added**
- โครงสร้าง `src/`, `tests/`, `data/`
- `EmotionClient` พร้อม Defensive Fallback และรองรับผลลัพธ์ pipeline หลายรูปแบบ
- `PaletteEngine` จานสี 8 สี × 6 อารมณ์ + WCAG 2.1 Contrast Evaluation
- `PaletteVisualizer` (Matplotlib) พร้อมตัวเลือก `save_path`
- `CLIApp` + `main.py` พร้อมโหมด `--batch`
- Unit Tests อัตโนมัติ `tests/test_emotion_client.py`

## 📂 ไฟล์ที่เกี่ยวข้อง
```
Sprint1/
├── src/
│   ├── cli_app.py          ← Interactive CLI + Batch
│   ├── emotion_client.py   ← HF Pipeline + Defensive Fallback
│   └── palette_engine.py   ← Emotion→Palette + WCAG
├── test/
│   └── test_emotion_client.py   ← 8 tests
├── main.py                 ← Entry Point (--batch)
└── README.md
```
