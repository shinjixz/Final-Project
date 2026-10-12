# LEARNINGLOG — Smart Art & Palette Sentiment Analyzer

เอกสารสรุปองค์ความรู้ ทักษะทางเทคนิค (Technical Skills) และบทเรียนการแก้ปัญหาที่สมาชิกในทีมได้รับจากการพัฒนาโครงการ **Smart Art & Palette** ตลอด Sprint 1–3 และ Final Sprint

---

## 1. Core Technical Learnings (ทักษะทางเทคนิคที่ได้รับ)

### Machine Learning & NLP Engine
* **Hugging Face Transformers:** เรียนรู้การโหลดและใช้งาน Pre-trained Model (`bhadresh-savani/distilbert-base-uncased-emotion`) สำหรับวิเคราะห์ Emotion จากข้อความภาษาอังกฤษ
* **Client-Side AI Execution:** เรียนรู้การแปลง/ย้ายขั้นตอน Inferencing มารันบน Client-Side ผ่าน WebAssembly / ONNX Runtime บนเบราว์เซอร์ ช่วยลดภาระ Backend และรองรับการทำ Static Hosting บน GitHub Pages ฟรี

### Color Science & Accessibility Standards
* **WCAG 2.1 Contrast Calculation:** เรียนรู้การคำนวณอัตราส่วนความต่างสี (Relative Luminance & Contrast Ratio) ตามมาตรฐานสากล เพื่อวัดผล accessibility แสดงสถานะ PASS (AAA/AA) หรือ FAIL
* **Dynamic Palette Mapping:** การแปลง Emotion Label เป็นจานสี Hex 8 สี (เริ่มที่ 5 สีใน Sprint 1 แล้วขยายเป็น 8 สีให้ครอบคลุมพื้นหลัง ตัวอักษร และเส้นขอบ)

### Database & Data Pipelines
* **SQLite Persistence:** การออกแบบ Schema และการจัดการฐานข้อมูล Local SQLite (`data/palette_history.db`) ด้วย `sqlite3` ใน Python
* **Batch Processing & Exporters:** การประมวลผลไฟล์ CSV (Sprint 2 ใช้ `pandas` ภายหลังเปลี่ยนเป็นโมดูล `csv` มาตรฐานเพื่อลด dependency) และส่งออกเป็นไฟล์ `.json` และ `.css` (CSS Variables)

### Modern Frontend & CI/CD
* **Responsive UI & i18n:** การเขียน HTML5/CSS3 แบบ Responsive พร้อมระบบสลับภาษา (TH/EN) ด้วย Vanilla JavaScript (Sprint 3 เป็น Glassmorphism, Final Sprint ปรับเป็น UI มินิมอล)
* **Automated CI/CD Workflows:** `ci.yml` รัน flake8 + pytest บน Python 3.10–3.12 ทุก push/PR และ `deploy-web.yml` deploy เว็บลง GitHub Pages เฉพาะเมื่อเทสต์ผ่าน

---

## 2. Key Challenges & Solutions (ปัญหาที่พบและวิธีแก้ไข)

| ปัญหาที่พบ (Challenge) | สาเหตุ (Root Cause) | แนวทางการแก้ไข (Solution) |
| :--- | :--- | :--- |
| **TypeError จาก Nested List** | ผลลัพธ์จาก Hugging Face Pipeline บางกรณีซ้อน List มาไม่แน่นอน (`[[{...}]]`) | เพิ่มระบบ **Defensive Fallback Unwrapping** เช็กประเภทข้อมูลด้วย `isinstance` ก่อนดึงค่า |
| **Model Loading Lags** | การดึงโมเดล AI ผ่านเครือข่ายใช้เวลานาน หรือเสี่ยงเน็ตหลุด | Strategy pattern + `FallbackEmotionClient` ใช้ keyword analyser เมื่อโมเดลใช้ไม่ได้; บนเว็บแสดงผลด่วนก่อนแล้วอัปเดตเป็นผล AI อัตโนมัติ |
| **Performance Drag on Mobile** | การสกัดสีจากรูปภาพขนาดใหญ่บนมือถือทำให้เบราว์เซอร์หน่วง | เพิ่มกระบวนการ Client-Side Canvas Image Resizing ย่อภาพก่อนประมวลผลสกัดสี |
| **Role Confusion in Reports** | บทบาทสมาชิกสลับกันจนทำให้ระบบตรวจสอบรายงาน Failure | จัดทำตารางหมวนเวียนบทบาท (Agile Rotation) ให้ชัดเจนและสอดคล้องกันทุก Sprint |

---

## 2.1 Final Sprint Learnings (สิ่งที่ได้เรียนรู้ใน Final Sprint)

| ปัญหาที่พบ | สาเหตุ | สิ่งที่เรียนรู้ / วิธีแก้ |
| :--- | :--- | :--- |
| โปรแกรมและเทสต์ทั้งหมดรันไม่ได้ | import โฟลเดอร์ `Sprint4` ที่ไม่มีอยู่ และไม่มีใครรันเทสต์ก่อน push | ต้องมี CI รันเทสต์ทุก push — ปัญหาแบบนี้จะถูกจับได้ทันที |
| CLI เรียกเมธอดที่ไม่มีอยู่ใน DataStore | UI เรียกฐานข้อมูลตรง ๆ และไม่มี interface กลาง | แยก Business Logic Layer (`AnalysisService`) ให้ UI เรียกที่เดียว |
| ค่าความมั่นใจปลอมบนเว็บ | ใช้ค่าสุ่ม/ค่าตายตัวเมื่อ AI ล่ม | ผลลัพธ์ต้องซื่อตรง แจ้งผู้ใช้ว่าใช้โหมดสำรองแทนการแต่งตัวเลข |
| เทสต์ช้าและต้องใช้เน็ต | โหลดโมเดลจริงในเทสต์ | ใช้ Fake analyzer ผ่าน Strategy pattern ทำให้เทสต์ 125 ตัวรันในไม่ถึง 2 วินาที |
| ประวัติซ้ำและรูปไม่แสดง | ไม่ตรวจข้อมูลซ้ำ และเก็บรูปเต็มเป็นข้อความ | กำหนด key สำหรับเทียบข้อมูลซ้ำ และเก็บรูปย่อแทนรูปเต็ม |

---

## 3. Agile/Scrum & Soft Skills Reflection

* **Cross-Functional Collaboration:** ได้ทดลองหมุนเวียนบทบาท (Planner, Coder, Debugger/QA) ทำให้เข้าใจมุมมองของทั้งคนวางแผน คนเขียนโค้ด และคนทดสอบระบบ
* **Defensive Programming Mindset:** ได้เรียนรู้ว่าการเขียนโค้ดให้ "ใช้งานได้" ไม่เพียงพอ แต่ต้องเขียนโค้ดให้ "ล้มเหลวอย่างปลอดภัย" (Fail Safely) เมื่อเจอ Edge Cases หรือปัญหาจาก External APIs
* **Documentation First:** เอกสารที่สมบูรณ์ (`README`, `CHANGELOG`, `SPRINT Reports`) ช่วยลดเวลาในการสื่อสารในทีมและทำให้งานส่งมอบได้ราบรื่น

---

## Member Key Takeaways (สรุปสิ่งที่ได้เรียนรู้รายบุคคล)

* **นายกฤษฎา สายวัน (กาย):** ได้พัฒนาทักษะด้าน System Architecture การวางโครงสร้าง OOP Class และการทำ SQLite Integration
* **นายปฏิภาณ นามสีลี (ท็อป):** ได้เรียนรู้การนำโมเดล NLP มาประยุกต์ใช้งานจริง การทำ UI/UX Glassmorphism และระบบสลับภาษา (i18n)
* **นายปฏิพัฒน์ หอทอง (ปลั๊ก):** ได้ทักษะการตั้งค่า CI/CD Pipeline ด้วย GitHub Actions และการเขียน JavaScript Core เพื่อสกัดสีจากรูปภาพ
* **นายภีรภัทร ด่านภูมิพัฒนา (ภีม):** ได้เรียนรู้การเขียน Automated Testing ด้วย `pytest`, การตรวจสอบมาตรฐาน WCAG 2.1 และการสร้าง AI Design Advisory Engine
