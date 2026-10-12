# 🧩 Module / API Specification

ทุกโมดูลอยู่ในแพ็กเกจ `src`. ข้อผิดพลาดที่คาดได้ทั้งหมดเป็นลูกของ `AppError`

## Layer overview

| Layer | Module | ความรับผิดชอบ |
| :--- | :--- | :--- |
| Presentation | `cli_app.py` | เมนู, อ่านอินพุต, แสดงผล, จับ `AppError` |
| Presentation | `visualizer.py` | แสดงจานสีในเทอร์มินัล / บันทึก PNG |
| Business Logic | `analysis_service.py` | Use case ทั้งหมด: CRUD, search, filter, sort, stats |
| Business Logic | `emotion_client.py` | วิเคราะห์อารมณ์ (Strategy) |
| Business Logic | `palette_engine.py` | จานสี + WCAG |
| Business Logic | `ai_advisory.py` | คำแนะนำดีไซน์ + insight report |
| Business Logic | `report_generator.py` | Export JSON/CSS, Batch CSV |
| Business Logic | `models.py`, `exceptions.py` | Domain models, exceptions |
| Data Access | `data_store.py` | SQLite repository |

---

## `src.models`

```python
EMOTIONS = ("joy", "sadness", "anger", "fear", "love", "surprise")
ALL_LABELS = EMOTIONS + ("neutral",)

@dataclass EmotionResult(label: str, score: float, source: str = "model")   # source: "model" | "keyword"
@dataclass AnalysisRecord(input_text, emotion, confidence, hex_colors, id=None, created_at=<now ISO>)
    .palette_size -> int
    .to_dict() -> dict
```

## `src.exceptions`

| Exception | เกิดเมื่อ |
| :--- | :--- |
| `AppError` | คลาสแม่ |
| `InvalidInputError` | ข้อความว่าง/ยาวเกิน, id ไม่ใช่ตัวเลข, อารมณ์/ฟิลด์ไม่รู้จัก, ช่วงค่าไม่ถูกต้อง, รหัสสีผิด |
| `RecordNotFoundError(record_id)` | ไม่พบ id |
| `StorageError` | อ่าน/เขียน DB หรือไฟล์ไม่ได้ |
| `AnalysisError` | โมเดลโหลดไม่ได้หรือวิเคราะห์ไม่สำเร็จ |

## `src.emotion_client`

| API | คำอธิบาย |
| :--- | :--- |
| `validate_text(text) -> str` | strip และตรวจ (ไม่ว่าง, ≤ 1000 ตัวอักษร) |
| `EmotionAnalyzer.get_emotion(text) -> EmotionResult` | interface (abstract) |
| `TransformerEmotionClient(model_name=DEFAULT_MODEL, classifier=None)` | DistilBERT; รับ `classifier` ปลอมได้สำหรับเทสต์ |
| `KeywordEmotionClient()` | keyword lexicon; ไม่เจอคำใดเลย → `neutral`, score 0.0 |
| `FallbackEmotionClient(primary, fallback=None)` | ใช้ primary ถ้า `AnalysisError` ใช้ fallback; เก็บสาเหตุใน `.last_error` |
| `create_emotion_client(offline=False)` | factory เลือก analyzer ที่ใช้ได้ |

Keyword score = `(คำที่ตรงอารมณ์ชนะ / คำที่ตรงทั้งหมด) × n/(n+1)` — คำเดียวได้สูงสุด 50% จึงไม่อ้างความมั่นใจเกินจริง

## `src.palette_engine.PaletteEngine` (class methods)

| API | คืนค่า |
| :--- | :--- |
| `get_palette(emotion)` | list 8 สี (สำเนา); อารมณ์ไม่รู้จัก → `neutral` |
| `hex_to_rgb(hex)` | `(r, g, b)` หรือ `InvalidInputError` |
| `calculate_relative_luminance(rgb)` | float ตาม WCAG 2.1 |
| `calculate_contrast_ratio(a, b)` | float 1–21 |
| `evaluate_wcag_compliance(fg, bg)` | `{foreground, background, contrast_ratio, status, is_compliant}` — AAA ≥ 7, AA ≥ 4.5 |
| `best_text_pair(palette)` | ผลของคู่สีที่ contrast สูงสุด |

## `src.data_store.DataStore(db_path="data/palette_history.db")`

| API | คำอธิบาย |
| :--- | :--- |
| `add(record) -> AnalysisRecord` | Create (เติม `id`) |
| `get(id) -> AnalysisRecord` | Read / `RecordNotFoundError` |
| `list_all()` / `get_history(limit)` | Read (ใหม่สุดก่อน) |
| `find_by_text(text)` | รายการล่าสุดที่ข้อความตรงกัน (ไม่สนตัวพิมพ์/ช่องว่าง) หรือ `None` |
| `update(record)` | Update ทุกฟิลด์ / `RecordNotFoundError` |
| `delete(id)` / `clear() -> int` / `count()` | Delete |
| `.recovered_from` | path ไฟล์ DB เสียที่ถูกสำรองไว้ (หรือ `None`) |

ทุก query ใช้ parameter `?` (กัน SQL injection), connection ปิดทุกครั้งด้วย `closing()`

## `src.analysis_service.AnalysisService(analyzer, store)`

| API | คำอธิบาย | ความซับซ้อน |
| :--- | :--- | :--- |
| `analyze(text, save=True)` | วิเคราะห์ + จานสี + บันทึก ถ้าข้อความซ้ำจะอัปเดตรายการเดิม (`last_was_duplicate = True`) | – |
| `get(id)` / `list_history(limit=None)` | อ่าน (id รับ string ได้ ตรวจให้) | – |
| `update_text(id, text)` | แก้ข้อความและวิเคราะห์ใหม่ | – |
| `delete(id)` / `clear_history()` | ลบ | – |
| `search(records, keyword)` | หาในข้อความ (substring), อารมณ์ หรือรหัสสี (ตรงทั้งคำ) ไม่สนตัวพิมพ์ | O(n) |
| `filter(records, emotion, min_confidence, max_confidence, date_from, date_to)` | ทุกเงื่อนไขเป็น AND, ค่า None = ไม่กรอง | O(n) |
| `sort(records, by="date", descending=True, then_by=None)` | ฟิลด์: `id, date, confidence, emotion, text` | O(n log n) |
| `statistics()` | `{total, by_emotion, average_confidence}` | O(n) |
| `insight_report()` | สรุปภาษาไทยอัตโนมัติ | O(n) |

## `src.report_generator.ReportGenerator`

| API | คำอธิบาย |
| :--- | :--- |
| `export_to_css(palette, filename)` | `:root { --color-1: …; }` |
| `export_to_json(emotion, palette, filename)` | `{"emotion": …, "colors": […]}` |
| `export_history_json(records, filename)` | ประวัติทั้งหมดเป็น JSON |
| `read_batch_csv(path) -> list[str]` | คอลัมน์ `text` (ข้ามแถวว่าง) |
| `process_batch_csv(path, service, save=True) -> list[dict]` | แถวที่ผิดพลาดใส่ข้อความใน `error` |
| `write_batch_output(rows, filename)` | เขียน CSV ผลลัพธ์ |

## Web (`web/`)

| ไฟล์ | หน้าที่ |
| :--- | :--- |
| `app.js` | UI, โหลด Transformers.js แบบ lazy (`zero-shot-classification`, `Xenova/distilbert-base-uncased-mnli`) แสดงผลด่วนก่อนแล้วอัปเดตเป็นผล AI, export, ประวัติใน `localStorage` สูงสุด 200 รายการ (ลบรายการเก่าอัตโนมัติเมื่อพื้นที่เต็ม) |
| `keyword_fallback.js` | `keywordEmotion(text) -> {label, score}` — ตรงกับ `KeywordEmotionClient` (มีเทสต์ตรวจ) |
