# CHANGELOG — Smart Art & Palette Sentiment Analyzer

รายการบันทึกการเปลี่ยนแปลงและการอัปเดตเวอร์ชันของโครงการ **Smart Art & Palette** ตามวงจรการพัฒนาแบบ Agile / Scrum (Sprint 1 ถึง Final Sprint)

---

## [v2.1.0] - 2026-10-13 (Final Sprint — Web UX & Data Quality)

### Added
* หน้าเว็บมินิมอลใหม่: แถบจานสี 8 สีคลิกคัดลอกได้, ปุ่มคัดลอก/ดาวน์โหลดแยกกลุ่ม, ข้อความแจ้งเตือนแบบ toast, คีย์ลัด Ctrl/Cmd+Enter, รองรับมือถือ
* เว็บแสดง **ผลด่วน** จาก keyword ทันที แล้วอัปเดตเป็นผล AI อัตโนมัติเมื่อโมเดลโหลดเสร็จ พร้อมแสดงความคืบหน้าการดาวน์โหลดโมเดล
* ประวัติบนเว็บสูงสุด 200 รายการ: แสดงทีละ 10, ลบทีละรายการ, ลบรายการเก่าสุดอัตโนมัติเมื่อพื้นที่เบราว์เซอร์เต็ม
* กันบันทึกซ้ำ: ข้อความเดิม (ไม่สนตัวพิมพ์/ช่องว่าง) หรือรูปเดิม จะอัปเดตรายการเดิม ทั้ง CLI (`DataStore.find_by_text`) และเว็บ; เว็บรวมรายการซ้ำที่มีอยู่เดิมให้อัตโนมัติ

### Fixed
* ประวัติของรูปภาพแสดงเป็นข้อความ `data:image/...base64` → แสดงเป็นรูปย่อ + ชื่อไฟล์
* สกัดสีจากรูปดูแค่ 8 พิกเซลบนเส้นกลางภาพ → วิเคราะห์ทั้งภาพแล้วเลือกสีเด่นที่ไม่ซ้ำกัน
* การเดาอารมณ์จากรูปตอบ JOY เกือบทุกรูป → ใช้กฎจากเฉดสี/ความสด/ความสว่างครบ 6 อารมณ์
* ข้อความในประวัติไม่ถูก escape (เสี่ยง XSS)
* หน้าเว็บค้าง "Loading AI..." ระหว่างโหลดโมเดลครั้งแรก

---

## [v2.0.0] - 2026-10-13 (Final Sprint — DevOps, CI/CD & Hardening)

### Added (ฟีเจอร์ใหม่)
* Business Logic Layer `src/analysis_service.py`: CRUD ครบ + Search / Filter (อารมณ์, ช่วงความมั่นใจ, ช่วงวันที่) / Sort (หลายคีย์) + สถิติ
* เมนู CLI 12 รายการ (วิเคราะห์, ดู, รายละเอียด+WCAG, แก้ไข, ลบ, ค้นหา, กรอง, เรียง, ส่งออก, batch, insight)
* `src/models.py` (dataclass) และ `src/exceptions.py` (custom exceptions)
* `KeywordEmotionClient` + `FallbackEmotionClient` — ใช้งานได้แม้ไม่มีโมเดล AI / ไม่มีเน็ต (Python และเว็บ)
* AI Insight Report สรุปประวัติอัตโนมัติ, คำแนะนำดีไซน์ครบ 6 อารมณ์
* `.github/workflows/ci.yml` — flake8 + pytest + coverage ≥ 80% + smoke test บน Python 3.10–3.12
* 120 automated tests, `scripts/benchmark.py`, `docs/USER_GUIDE.md`, `docs/API.md`, `docs/BENCHMARK.md`

### Fixed (แก้ไข)
* `main.py` และเทสต์ import `Sprint4.src` ที่ไม่มีอยู่ → โปรแกรมและเทสต์รันไม่ได้
* `src/__init__.py` มีโค้ด EmotionClient ซ้ำ (import transformers ทุกครั้ง)
* CLI เรียก `save_analysis()` ที่ไม่มีอยู่ใน `DataStore`
* DataStore พังเมื่อไม่มีโฟลเดอร์ `data/` หรือไฟล์ DB เสีย; connection ไม่ถูกปิด
* เว็บ: ความมั่นใจจากรูปเป็นค่าสุ่ม, เมื่อ AI ล่มแสดง `SADNESS 99.5%` ตายตัว, import CDN บรรทัดแรกทำให้ทั้งหน้าพัง, เรียก `localhost:3000` ที่ไม่มีอยู่, ไม่ตรวจชนิด/ขนาดไฟล์รูป
* จานสี Python ไม่ตรงกับเว็บ และขาดอารมณ์ `surprise`
* `index.html` ที่ root อ้าง `style.css` ที่ไม่มี → เปลี่ยนเป็นหน้า redirect ไป `web/`

### Changed
* `deploy-web.yml` deploy เฉพาะเมื่อ lint + test ผ่าน
* แยก dependencies: `requirements.txt` (เบา), `requirements-ml.txt` (AI), `requirements-dev.txt` (ทดสอบ)
* เลิก track `data/palette_history.db` (เพิ่ม `.gitignore`)
* เอกสารระบุตรง ๆ ว่า Supabase เป็นแผนต่อยอด ยังไม่ได้ implement

---

## [v1.0.0] - 2026-09-25 (Sprint 3 Release — Final Submission)

### Added (ฟีเจอร์ใหม่)
* **Web Application Dashboard:** หน้าเว็บแดชบอร์ดประมวลผลเรียลไทม์ ตกแต่งในสไตล์ Modern Glassmorphism Responsive UI (`web/index.html`, `style.css`, `app.js`)
* **Client-Side AI & Palette Engine:** รองรับการประมวลผลสกัดอารมณ์และคำนวณจานสีบนเบราว์เซอร์ 100% ผ่าน WebAssembly / ONNX Runtime
* **Bilingual Support (i18n):** ระบบสลับภาษาบนหน้าเว็บ 2 ภาษา (ภาษาไทย / English) แบบ Instant Toggle
* **Image Palette Extractor:** ฟังก์ชันอัปโหลดรูปภาพเพื่อสกัดโทนสีหลัก (Color Extraction from Images) นำมาเปรียบเทียบกับจานสีอารมณ์
* **Automated CI/CD Workflow:** ไฟล์สคริปต์ `.github/workflows/deploy-web.yml` สั่งการ Build และ Deploy ไปยัง GitHub Pages อัตโนมัติเมื่อ Push ขึ้นกิ่ง `main`

### Fixed & Improved (แก้ไขและปรับปรุง)
* ปรับปรุงประสิทธิภาพ Image Extractor บนอุปกรณ์เคลื่อนที่ ด้วยการย่อขนาดภาพด้วย Client-Side Canvas ก่อนสกัดสี
* ปรับแต่ง UI ให้รองรับ Cross-Browser Compatibility (Chrome, Edge, Safari, Firefox) และ Mobile Responsive
* สรุปและจัดทำเอกสารส่งมอบโครงการสมบูรณ์ (`README.md`, `CHANGELOG.md`, `LEARNINGLOG.md`, และรายงาน `SPRINT1.md` - `SPRINT3.md`)

---

## [v0.2.0] - 2026-09-18 (Sprint 2 Release — Persistence & Advisory)

### Added (ฟีเจอร์ใหม่)
* **Local SQLite DataStore:** บันทึกประวัติข้อความ, อารมณ์, ค่า confidence และจานสี Hex Code ลงใน `data/palette_history.db`
* **Batch File Processing:** ระบบอ่านและประมวลผลไฟล์ข้อความ CSV ปริมาณมากพร้อมกันในคำสั่งเดียว (`main.py --batch`)
* **Multi-Format Exporter:** สกัดผลลัพธ์จานสีส่งออกเป็นไฟล์ `.json` และไฟล์ `.css` (CSS Variables) สำหรับนักพัฒนา UI/UX
* **AI Design Advisory Engine:** ระบบแนะนำชื่อธีมการออกแบบ, การจับคู่ฟอนต์ (Font Pairings) และแนวทางการนำไปใช้งาน (`src/ai_advisory.py`)
* **WCAG 2.1 Color Contrast Checker:** คำนวณอัตราส่วนความต่างสีพร้อมแสดงสถานะ PASS (AAA) / PASS (AA) / FAIL ตามมาตรฐานสากล

### Fixed & Improved (แก้ไขและปรับปรุง)
* วางแผนการเชื่อมต่อ Cloud Database (Supabase PostgreSQL) — *หมายเหตุ: ตรวจสอบใน Final Sprint พบว่ายังไม่ได้ implement ดู v2.0.0*
* เพิ่มชุดทดสอบอัตโนมัติ `tests/test_sprint2.py` สำหรับตรวจสอบการทำงานของ Database และการคำนวณ WCAG

---

## [v0.1.0] - 2026-09-11 (Sprint 1 Release — Core OOP CLI Foundation)

### Added (ฟีเจอร์ใหม่)
* **NLP Emotion Analysis Engine:** เชื่อมต่อ Hugging Face Transformers ใช้โมเดล `bhadresh-savani/distilbert-base-uncased-emotion` ในการวิเคราะห์ข้อความภาษาอังกฤษและไทย
* **Dynamic Palette Generator:** แมปปิ้งโทนสีหลัก 5 สีตามหมวดหมู่อารมณ์ (Joy, Sadness, Anger, Fear, Love, Neutral)
* **Matplotlib Palette Renderer:** เรนเดอร์ภาพแถบสี Swatch ในโทน Dark Theme (`src/visualizer.py`)
* **Interactive CLI Interface:** หน้าจอรับคำสั่งแบบโต้ตอบเรียลไทม์ผ่าน Terminal (`python main.py --cli`)
* **Automated Unit Tests:** ชุดทดสอบ `tests/test_emotion_client.py` ตรวจสอบความถูกต้องของการคืนค่าจากโมเดล AI

### Security & Defensive Programming
* **Defensive Fallback Unwrapping:** ระบบดักจับและตรวจสอบ Data Structure จาก AI ป้องกันปัญหากรอบข้อมูลซ้อน List (`TypeError`) และคืนค่าสี Neutral สำรองเมื่อเครือข่ายขัดข้อง
* จัดทำโครงสร้างโปรเจกต์แบบ Object-Oriented Programming (OOP) และ Modular Separation (`src/`, `tests/`, `data/`)

---

## รายชื่อผู้พัฒนาและการหมุนเวียนบทบาท (Development Team & Role Rotation)

| Sprint | Planner | Coder | Debugger / QA |
| :---: | :--- | :--- | :--- |
| **Sprint 1** | นายกฤษฎา สายวัน (กาย) | นายปฏิภาณ นามสีลี (ท็อป)<br>นายปฏิพัฒน์ หอทอง (ปลั๊ก) | นายภีรภัทร ด่านภูมิพัฒนา (ภีม) |
| **Sprint 2** | นายปฏิภาณ นามสีลี (ท็อป) | นายกฤษฎา สายวัน (กาย)<br>นายภีรภัทร ด่านภูมิพัฒนา (ภีม) | นายปฏิพัฒน์ หอทอง (ปลั๊ก) |
| **Sprint 3** | นายภีรภัทร ด่านภูมิพัฒนา (ภีม) | นายปฏิภาณ นามสีลี (ท็อป)<br>นายปฏิพัฒน์ หอทอง (ปลั๊ก) | นายกฤษฎา สายวัน (กาย) |

**Final Sprint (ทำงานตามความเชี่ยวชาญ):** กาย — Core Logic Lead, ท็อป — AI & Web Lead, ปลั๊ก — DevOps Lead, ภีม — QA & Testing Lead
