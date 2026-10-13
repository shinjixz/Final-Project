# Final Term Project Pitch

## 1. ชื่อโครงการ (Project Title)
**Smart Art & Palette** — Dynamic Emotion-Based Palette Generator & AI Design Advisory  
*(ระบบเจเนอเรตจานสีอัจฉริยะตามอารมณ์พร้อม AI แนะนำการออกแบบ)*

---

## 2. ที่มาและความสำคัญของปัญหา (Problem Statement)
นักออกแบบและนักพัฒนาระบบมักประสบปัญหาในการเลือกชุดสีที่สามารถถ่ายทอด "อารมณ์" หรือ "มู้ดแอนด์โทน" ของงาน UI/UX และสื่อทัศนศิลป์ได้อย่างถูกต้อง การเลือกสีด้วยตนเองใช้เวลานาน ขาดการตรวจสอบมาตรฐานความต่างสี (Contrast) ที่เป็นระบบ และไม่มีเครื่องมือช่วยแนะนำการจับคู่ฟอนต์หรือธีมการออกแบบที่สอดคล้องกับเนื้อหาข้อความโดยอัตโนมัติ

---

## 3. ทางออกของปัญหา (Proposed Solution)
แอปพลิเคชันประมวลผลภาษาธรรมชาติ (NLP) อัจฉริยะที่สกัดอารมณ์จากข้อความของผู้ใช้ แล้วสร้างเป็นจานสี 8 สีที่เข้ากัน ระบบสามารถตรวจสอบอัตราส่วนความต่างสีตามมาตรฐาน WCAG 2.1, ให้คำแนะนำด้านการออกแบบด้วย AI (แนะนำฟอนต์และธีม), บันทึกประวัติลง SQLite, รองรับการประมวลผลไฟล์ CSV ปริมาณมาก (Batch Processing) และมาพร้อมหน้าเว็บที่ใช้งานได้ทันทีบนเบราว์เซอร์ พร้อมฟังก์ชันสกัดสีจากรูปภาพ

---

## 4. ขอบเขตเทคโนโลยี (Domain)
ประมวลผลภาษาธรรมชาติ (NLP) / ปัญญาประดิษฐ์และการวิเคราะห์ข้อมูล / เครื่องมือสำหรับนักออกแบบและนักพัฒนา / เว็บแอปพลิเคชัน

---

## 5. API และโมเดล ML ที่ใช้ (API(s) / ML Models to Use)
* **ชื่อโมเดล:** Hugging Face Transformers (`bhadresh-savani/distilbert-base-uncased-emotion`)
  * **ลิงก์เอกสาร:** https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion
  * **ประเภทข้อมูล:** การวิเคราะห์อารมณ์จากข้อความ 6 อารมณ์ (Joy, Sadness, Anger, Fear, Love, Surprise) ใช้ในโปรแกรม Python
* **โมเดลบนเว็บ:** `Xenova/distilbert-base-uncased-mnli` (zero-shot classification) ผ่าน Transformers.js / ONNX Runtime รันบนเบราว์เซอร์ของผู้ใช้
  * **ลิงก์เอกสาร:** https://huggingface.co/docs/transformers.js
* **โหมดสำรอง:** Keyword analyser (ไม่ต้องใช้โมเดล) ใช้เมื่อโมเดลโหลดไม่ได้ ทั้งฝั่ง Python และเว็บ

---

## 6. แผนการจัดเก็บข้อมูล (Data Persistence Plan)
* **ฐานข้อมูลในเครื่อง:** SQLite (`data/palette_history.db`)
* **ข้อมูลที่จัดเก็บ:** ข้อความอินพุต, อารมณ์ที่วิเคราะห์ได้, ค่าความเชื่อมั่น (Confidence Score), ชุดสี HEX 8 สี และเวลาที่ประมวลผล
* **ฝั่งเว็บ:** localStorage ของเบราว์เซอร์ สูงสุด 200 รายการ (กันข้อมูลซ้ำ)
* **การรองรับระบบคลาวด์ (แผนต่อยอด ยังไม่ได้ implement):** ออกแบบ Schema ไว้สำหรับย้ายขึ้น PostgreSQL / Supabase

---

## 7. สถาปัตยกรรมเชิงวัตถุ (Framework Style)
* **สถาปัตยกรรม OOP และการแบ่งมอดูล:**
  * `AnalysisService` (Business Logic: CRUD, ค้นหา, กรอง, เรียงลำดับ, สถิติ)
  * `EmotionAnalyzer` → `TransformerEmotionClient` / `KeywordEmotionClient` / `FallbackEmotionClient` (Strategy pattern)
  * `PaletteEngine` (การแมปปิ้งสีและการคำนวณความต่างสี WCAG 2.1)
  * `DataStore` (Repository ของฐานข้อมูล SQLite: CRUD + กู้คืนไฟล์เสีย)
  * `ReportGenerator` (ตัวประมวลผลไฟล์ CSV และส่งออกเป็น JSON/CSS)
  * `AIAdvisory` (แนะนำฟอนต์และธีม + Insight Report อัตโนมัติ)
  * `CLIApp` (เมนู CLI 12 รายการ) และ custom exceptions ใน `exceptions.py`

---

## 8. บทบาทและความรับผิดชอบ (Roles & Responsibilities)
* **ผู้ดูแลระบบและสถาปนิก (Planner / System Architect):** Sprint 1 กาย / Sprint 2 ท็อป / Sprint 3 ภีม — ดูแลการตั้งค่า Repo, ออกแบบ Schema ฐานข้อมูล, กำหนดสเปก i18n และตั้งค่า GitHub Actions CI/CD
* **นักพัฒนาหลัก (Core Developers):** Sprint 1 ท็อป, ปลั๊ก / Sprint 2 กาย, ภีม / Sprint 3 ท็อป, ปลั๊ก — พัฒนาระบบเชื่อมต่อ NLP DistilBERT, ตัวแสดงผล Matplotlib, ระบบ SQLite, ตัวส่งออก Batch และ Web UI
* **ผู้ทดสอบและควบคุมคุณภาพ (Automated Tester & QA Debugger):** Sprint 1 ภีม / Sprint 2 ปลั๊ก / Sprint 3 กาย — เขียน Unit Test (`pytest`), จัดการดักจับ Exception ป้องกันแอป Crash, ตรวจสอบการคำนวณ WCAG และทดสอบการทำงานข้ามเบราว์เซอร์
* **Final Sprint (ทำงานตามความเชี่ยวชาญ):** กาย — Core Logic Lead / ท็อป — AI & Web Lead / ปลั๊ก — DevOps Lead / ภีม — QA & Testing Lead

---

## 9. ฟีเจอร์หลักขั้นต้น (Features - MVP)
* วิเคราะห์อารมณ์จากข้อความด้วยโมเดล NLP DistilBERT
* เจเนอเรตจานสี 5 สี (HEX/RGB) ตามอารมณ์ที่วิเคราะห์ได้ (ขยายเป็น 8 สีใน Sprint 2)
* แสดงผลแถบสี Swatches บน Terminal ด้วย Matplotlib
* อินเทอร์เฟซ CLI แบบโต้ตอบ พร้อมระบบทำความสะอาดข้อความและการจัดการ Exception เบื้องต้น

---

## 10. ฟีเจอร์เพิ่มเติมที่ทำสำเร็จ (Stretch Features - Completed)
* **ระบบตรวจความต่างสี WCAG 2.1:** คำนวณความต่างของสีข้อความและพื้นหลังพร้อมแสดงสถานะ PASS (AAA/AA) หรือ FAIL
* **AI ให้คำแนะนำการออกแบบ:** แนะนำชื่อธีม การจับคู่ฟอนต์ (Font Pairings) และเทคนิคการนำไปใช้ในงาน UI/UX
* **การประมวลผล Batch & ส่งออกไฟล์:** อ่านไฟล์ CSV หลายบรรทัดและส่งออกเป็นไฟล์ `.json` และ `.css` (CSS Variables)
* **การบันทึกข้อมูลด้วย SQLite:** จัดเก็บประวัติการใช้งานลงในฐานข้อมูล SQLite Local DB
* **Web Dashboard & สกัดสีจากรูป:** หน้าเว็บมินิมอลรันบน GitHub Pages สกัดสีเด่นจากรูปภาพได้ รองรับ 2 ภาษา (ไทย/อังกฤษ) แสดงผลทันทีแม้โมเดลยังโหลดไม่เสร็จ และเก็บประวัติได้ 200 รายการ
* **CRUD + ค้นหา / กรอง / เรียงลำดับ:** ผ่านเมนู CLI พร้อมกันบันทึกข้อความซ้ำ
* **ระบบ CI/CD อัตโนมัติ:** `ci.yml` (flake8 + pytest บน Python 3.10–3.12) และ `deploy-web.yml` (deploy เฉพาะเมื่อเทสต์ผ่าน)

---

## 11. รายการตรวจสอบการประเมิน (Evaluation Checklist)
* โมเดล NLP และตัววิเคราะห์อารมณ์ทำงานได้ถูกต้อง พร้อมระบบ Fallback สำรอง
* ข้อมูลถูกบันทึกลงฐานข้อมูล SQLite Local DB (`data/palette_history.db`)
* โค้ดเป็นไปตามมาตรฐาน PEP 8 และหลักการเขียนโปรแกรมเชิงวัตถุ (OOP)
* ผ่านการทดสอบอัตโนมัติ 125 tests (`pytest`, coverage ~92%) ครอบคลุม NLP, ฐานข้อมูล, CLI, การส่งออกไฟล์ และเว็บ
* CI/CD รัน lint + test อัตโนมัติผ่าน GitHub Actions และ Deploy ลง GitHub Pages สำเร็จ
* เอกสารครบถ้วน (`README.md`, `PLAN.md`, `CHANGELOG.md`, `LEARNINGLOG.md`, `TEST_CASE.md`, `docs/USER_GUIDE.md`, `docs/API.md`, `docs/BENCHMARK.md`, รายงาน Sprint 1–3)
* บันทึกบทบาทและการหมุนเวียนงานของสมาชิกชัดเจน
