# 🎨 Smart Art & Palette Sentiment Analyzer — ระบบวิเคราะห์อารมณ์จากข้อความและสร้างจานสีอัจฉริยะ

**รายวิชา:** CP352301 การเขียนโปรแกรมสคริปต์ (1/2569)
**หัวข้อ:** Smart Art & Palette Sentiment Analyzer (ระบบวิเคราะห์อารมณ์จากข้อความและสร้างจานสีอัจฉริยะ)
**อาจารย์ผู้สอน:** ผศ.บุญทรัพย์ ไวคำ

---

## 📁 รายงานแต่ละ Sprint (Sprint Deliverables)

| Sprint | หัวข้อ | ผลงานสำคัญที่ส่งมอบ | เอกสารสรุป |
| :--- | :--- | :--- | :--- |
| 📦 Sprint 1 | Core System & OOP CLI | Emotion Classifier, Palette Engine, Visualizer, CLI Loop, Unit Test เบื้องต้น | [📄SPRINT1](./Sprint1/README.md) |
| 📦 Sprint 2 | Persistence, Report & AI Advisory | SQLite (ออกแบบ schema Supabase ไว้ต่อยอด), Export JSON/CSS, Batch CSV, AI Advisory, WCAG Checker | [📄SPRINT2](./Sprint2/README.md) |
| 📦 Sprint 3 | Web Dashboard & Deployment | Glassmorphism UI, Bilingual TH/EN, Image Mood Input, GitHub Actions CI/CD | [📄SPRINT3](./Sprint3/README.md) |
| 📦 Final | DevOps, CI/CD & Hardening | CRUD + Search/Filter/Sort, Service Layer, Fallback AI, เว็บมินิมอล + ประวัติ 200 รายการ, 125 tests, CI lint/test, Benchmark | [📄PLAN](./PLAN.md) · [📄CHANGELOG](./CHANGELOG.md) |

---

## 👥 รายชื่อสมาชิกในกลุ่มและบทบาทหน้าที่ (Team Members)

1. **ปฏิภาณ นามสีลี (ท็อป)**
   - **รหัสนักศึกษา:** 683380425-3 | **Email:** patiphan.na@kkumail.com
2. **กฤษฎา สายวัน (กาย)**
   - **รหัสนักศึกษา:** 683380646-7 | **Email:** kitsada.sai@kkumail.com
3. **ภีรภัทร ด่านภูมิพัฒนา (ภีม)**
   - **รหัสนักศึกษา:** 683380436-8 | **Email:** peeraphat.da@kkumail.com
4. **ปฏิพัฒน์ หอทอง (ปลั๊ก)**
   - **รหัสนักศึกษา:** 683380424-5 | **Email:** patipat.ho@kkumail.com

### 🔄 สมาชิกในทีมและการหมุนเวียนบทบาท (Role Rotation Matrix)

Sprint 1–3 หมุนเวียน 3 บทบาท (Planner / Architect, Coder / Dev, Debugger / QA) ครบทุกคน ส่วน Final Sprint ตามคู่มือรายวิชาเปลี่ยนเป็นการทำงานตามความเชี่ยวชาญเฉพาะบุคคล:

| สมาชิก | ชื่อเล่น | Sprint 1 : OOP & SQLite | Sprint 2 : AI & Report | Sprint 3 : Web & Deployment | Final Sprint (ความเชี่ยวชาญ) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| นายกฤษฎา สายวัน | กาย | Planner | Coder | Debugger | Core Logic Lead — OOP, Service Layer, SQLite |
| นายปฏิภาณ นามสีลี | ท็อป | Coder | Planner | Coder | AI & Web Lead — โมเดล NLP, หน้าเว็บ, TH/EN |
| นายปฏิพัฒน์ หอทอง | ปลั๊ก | Coder | Debugger | Coder | DevOps Lead — GitHub Actions CI/CD, Deploy |
| นายภีรภัทร ด่านภูมิพัฒนา | ภีม | Debugger | Coder | Planner | QA & Testing Lead — pytest, Edge cases, WCAG |

---

## 📝 การประเมินกลุ่ม & การประเมินรายบุคคล (Self-Assessment Report)

### Group Self-Assessment (0–10)

| หัวข้อ | น้ำหนัก | คะแนนกลุ่ม (0-10) | เหตุผล |
| :--- | :---: | :---: | :--- |
| บรรลุวัตถุประสงค์กลุ่ม | 30% | 9.0 | พัฒนาฟีเจอร์ครบตามแผนทั้ง 3 Sprints ได้แก่ Emotion Classifier, Color Psychology Mapping, CLI, SQLite, Export JSON/CSS, Batch CSV, AI Advisory, WCAG Checker และ Web Dashboard 2 ภาษา (TH/EN) พร้อม Deploy บน GitHub Pages |
| ความสอดคล้องของเนื้อหาและมาตรฐานของงาน | 30% | 9.5 | ออกแบบโมดูลเชิงวัตถุ (OOP) แยกหน้าที่ชัดเจนตามหลัก Separation of Concerns (`EmotionClient`, `PaletteEngine`, `PaletteVisualizer`, `DataStore`, `ReportGenerator`, `AIAdvisory`, `CLIApp`) มี Defensive Fallback และ Input Validation |
| ปริมาณ คุณภาพ และธรรมาภิบาลของงาน | 30% | 9.0 | มีชุดทดสอบอัตโนมัติด้วย `pytest` (125 test cases, coverage ~92%), เอกสารรายงานประจำ Sprint และ CI/CD (Lint + Test + Deploy) ด้วย GitHub Actions |
| ภาพรวมงานกลุ่มทั้งหมด | 10% | 9.5 | ทำงานเสร็จตามกำหนดทุก Sprint ร่วมมือกันตามบทบาท และมีการหมุนเวียนบทบาท (Role Rotation Matrix) ครบทั้ง 3 หน้าที่ทุกคน |
| **รวม (ถ่วงน้ำหนัก)** | **100%** | **≈ 9.20 / 10** | ผลงานเสร็จสมบูรณ์ครบทั้ง Core Engine, Persistence, AI Advisory และ Web Deployment |

### Individual Self-Assessment (0–10)

#### 📊 ตารางสรุปคะแนนประเมินตนเองรายบุคคลแยกตาม Sprint (Sprint-by-Sprint Summary)

| ชื่อ - สกุล | Sprint 1 (OOP & CLI) | Sprint 2 (AI, Report & Cloud) | Sprint 3 (Web & DevOps) | คะแนนเฉลี่ยรวม |
| :--- | :---: | :---: | :---: | :---: |
| **นายปฏิภาณ นามสีลี (ท็อป)**<br>• Sprint 1: Coder<br>• Sprint 2: Planner<br>• Sprint 3: Coder | 9.5 / 10 | 9.5 / 10 | 9.5 / 10 | **9.50 / 10** |
| **นายกฤษฎา สายวัน (กาย)**<br>• Sprint 1: Planner<br>• Sprint 2: Coder<br>• Sprint 3: Debugger | 9.5 / 10 | 9.0 / 10 | 9.5 / 10 | **9.33 / 10** |
| **นายภีรภัทร ด่านภูมิพัฒนา (ภีม)**<br>• Sprint 1: Debugger<br>• Sprint 2: Coder<br>• Sprint 3: Planner | 9.0 / 10 | 9.5 / 10 | 9.5 / 10 | **9.33 / 10** |
| **นายปฏิพัฒน์ หอทอง (ปลั๊ก)**<br>• Sprint 1: Coder<br>• Sprint 2: Debugger<br>• Sprint 3: Coder | 9.5 / 10 | 9.5 / 10 | 9.0 / 10 | **9.33 / 10** |

#### 📝 รายละเอียดคะแนนประเมินตนเองรายบุคคลแยกตามแต่ละ Sprint

##### 📦 Sprint 1: Core System Foundation & OOP CLI Architecture

| สมาชิก | บทบาทใน Sprint 1 | ด้านความรับผิดชอบ | ด้านการมีส่วนร่วม | ด้านการสื่อสาร | รวม Sprint 1 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| ปฏิภาณ นามสีลี (ท็อป) | Coder | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| กฤษฎา สายวัน (กาย) | Planner | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| ภีรภัทร ด่านภูมิพัฒนา (ภีม) | Debugger | 9.0 | 9.0 | 9.0 | 9.0 / 10 |
| ปฏิพัฒน์ หอทอง (ปลั๊ก) | Coder | 9.5 | 9.5 | 9.5 | 9.5 / 10 |

##### 📦 Sprint 2: Persistence, Report & AI Advisory

| สมาชิก | บทบาทใน Sprint 2 | ด้านความรับผิดชอบ | ด้านการมีส่วนร่วม | ด้านการสื่อสาร | รวม Sprint 2 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| ปฏิภาณ นามสีลี (ท็อป) | Planner | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| กฤษฎา สายวัน (กาย) | Coder | 9.0 | 9.0 | 9.0 | 9.0 / 10 |
| ภีรภัทร ด่านภูมิพัฒนา (ภีม) | Coder | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| ปฏิพัฒน์ หอทอง (ปลั๊ก) | Debugger | 9.5 | 9.5 | 9.5 | 9.5 / 10 |

##### 📦 Sprint 3: Web Dashboard & Deployment

| สมาชิก | บทบาทใน Sprint 3 | ด้านความรับผิดชอบ | ด้านการมีส่วนร่วม | ด้านการสื่อสาร | รวม Sprint 3 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| ปฏิภาณ นามสีลี (ท็อป) | Coder | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| กฤษฎา สายวัน (กาย) | Debugger | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| ภีรภัทร ด่านภูมิพัฒนา (ภีม) | Planner | 9.5 | 9.5 | 9.5 | 9.5 / 10 |
| ปฏิพัฒน์ หอทอง (ปลั๊ก) | Coder | 9.0 | 9.0 | 9.0 | 9.0 / 10 |

---

## ✨ ฟีเจอร์ของระบบ (Features)

### 🧠 วิเคราะห์อารมณ์และจานสี (Business Logic)
- **Emotion Analyzer — Strategy Pattern** (`src/emotion_client.py`)
  - `TransformerEmotionClient` ใช้โมเดล Hugging Face DistilBERT จำแนก 6 อารมณ์ (joy, sadness, anger, fear, love, surprise)
  - `KeywordEmotionClient` โหมดออฟไลน์แบบ keyword ใช้ได้โดยไม่ต้องติดตั้ง ML library
  - `FallbackEmotionClient` ถ้าโมเดลโหลดไม่ได้หรือพัง จะสลับไปโหมด keyword อัตโนมัติ และบอกผู้ใช้ตรง ๆ (ไม่แสดงค่าความมั่นใจปลอม)
- **Palette Engine** (`src/palette_engine.py`) จานสี 8 สีต่ออารมณ์ (ตรงกับหน้าเว็บ 100% มีเทสต์ยืนยัน) + คำนวณ WCAG 2.1 Contrast Ratio + หา “คู่สีที่อ่านง่ายที่สุด”
- **AI Design Advisory + Insight Report** (`src/ai_advisory.py`) แนะนำธีม ฟอนต์ การใช้งาน และสรุปสถิติประวัติอัตโนมัติ (Automation Agent)

### 💾 ข้อมูลและอัลกอริทึม
- **CRUD ครบ** ผ่าน `AnalysisService` → `DataStore` (SQLite): สร้าง / อ่าน / แก้ไขข้อความแล้ววิเคราะห์ใหม่ / ลบ / ล้างทั้งหมด — ข้อความเดิม (ไม่สนตัวพิมพ์และช่องว่าง) จะอัปเดตรายการเดิมแทนการบันทึกซ้ำ
- **Search** ค้นหาจากข้อความ อารมณ์ หรือรหัสสี (ไม่สนตัวพิมพ์เล็ก-ใหญ่)
- **Filter** ตามอารมณ์ ช่วงความมั่นใจ และช่วงวันที่ (ตรวจค่าผิดพลาดทุกกรณี)
- **Sort** ได้ 5 ฟิลด์ + เรียงหลายคีย์ (Stable sort)
- **Export** จานสีเป็น `.json` / `.css` และ **Batch CSV** (แถวที่ผิดพลาดถูกบันทึกไว้ ไม่ทำให้ทั้งไฟล์ล้ม)

### 🛡️ ความทนทานต่อข้อผิดพลาด (Error Resilience)
| สถานการณ์ | ระบบทำอะไร |
|---|---|
| ไม่มีโฟลเดอร์ `data/` หรือไฟล์ DB | สร้างใหม่อัตโนมัติ |
| ไฟล์ DB เสียหาย | ย้ายไฟล์เสียเป็น `*.corrupt-<เวลา>` แล้วสร้าง DB ใหม่ แจ้งผู้ใช้ตอนเปิดโปรแกรม |
| โมเดล AI โหลดไม่ได้ / ไม่มีเน็ต | ใช้ keyword analyser แทน (CLI และเว็บ) |
| ข้อความว่าง / ยาวเกิน / id ไม่ใช่ตัวเลข / id ไม่มีอยู่ | แสดง ⚠️ ข้อความเตือน โปรแกรมทำงานต่อ |
| ไฟล์ CSV หาย / ไม่มีคอลัมน์ `text` / ไฟล์ binary | แสดงข้อความเตือน |
| Ctrl+C / EOF | ปิดโปรแกรมอย่างสุภาพ |
| บนเว็บ: CDN ล่ม, ไฟล์ไม่ใช่รูป, รูปเกิน 10 MB, รูปเสีย, localStorage เต็ม | แจ้งเตือนในหน้าเว็บ หน้าเว็บยังใช้งานได้ |

### 🌐 Web Dashboard (`web/`)
- UI มินิมอล คอลัมน์เดียว รองรับมือถือ, สลับภาษา TH/EN, สกัดสีเด่นจากรูปภาพ, Export ASE / JSON / Figma tokens / HEX / RGB / HSL / Tailwind / CSS Vars, คลิกสีเพื่อคัดลอก
- AI ทำงานบนเบราว์เซอร์ผู้ใช้ (Transformers.js) — เริ่มโหลดโมเดลทันทีที่เปิดหน้า แสดง **ผลด่วน** จาก `web/keyword_fallback.js` ก่อน แล้วอัปเดตเป็นผล AI อัตโนมัติเมื่อโหลดเสร็จ ถ้า CDN ล่มก็ยังใช้งานได้
- ประวัติในเบราว์เซอร์สูงสุด 200 รายการ (แสดงทีละ 10, ลบทีละรายการ, รูปย่อของภาพ) ข้อความ/รูปเดิมที่วิเคราะห์ซ้ำจะอัปเดตรายการเดิม ไม่บันทึกซ้ำ ถ้าพื้นที่เต็มจะลบรายการเก่าสุดให้อัตโนมัติ

---

## 🏗️ สถาปัตยกรรม (3-Layer Architecture)

```text
Presentation   : cli_app.py (เมนู CLI), visualizer.py, web/
      │  เรียกเฉพาะ AnalysisService
Business Logic : analysis_service.py (CRUD + search/filter/sort/stats)
                 emotion_client.py, palette_engine.py, ai_advisory.py,
                 report_generator.py, models.py, exceptions.py
      │
Data Access    : data_store.py (SQLite repository)
```
Class Diagram และ Design Patterns ดูได้ที่ [PLAN.md](./PLAN.md) · สเปกโมดูล/API ดูที่ [docs/API.md](./docs/API.md)

---

## 🗂️ โครงสร้างไดเรกทอรี

```text
Final-Project/
├── .github/workflows/
│   ├── ci.yml                 # Lint (flake8) + pytest + coverage บน Python 3.10–3.12
│   └── deploy-web.yml         # ทดสอบผ่านก่อน แล้วค่อย Deploy web/ ขึ้น GitHub Pages
├── src/
│   ├── models.py              # Domain models (AnalysisRecord, EmotionResult)
│   ├── exceptions.py          # Custom exceptions
│   ├── emotion_client.py      # Analyzer strategies + fallback
│   ├── palette_engine.py      # Palettes + WCAG
│   ├── ai_advisory.py         # Design advice + insight report
│   ├── analysis_service.py    # Business logic (CRUD, search, filter, sort)
│   ├── data_store.py          # SQLite repository
│   ├── report_generator.py    # JSON/CSS export + batch CSV
│   ├── visualizer.py          # Terminal swatches / PNG
│   └── cli_app.py             # เมนู CLI
├── web/                       # index.html, style.css, app.js, keyword_fallback.js
├── tests/                     # 125 unit/integration tests
├── scripts/benchmark.py       # วัดความเร็ว
├── docs/                      # USER_GUIDE.md, API.md, BENCHMARK.md
├── data/sample_batch.csv
├── Sprint1/ Sprint2/ Sprint3/ # งานส่งรายสัปดาห์ (เก็บไว้เป็นประวัติ)
├── main.py
├── requirements.txt / requirements-ml.txt / requirements-dev.txt
└── PLAN.md, TEST_CASE.md, CHANGELOG.md, LEARNINGLOG.md, PROJECTPITCH.md
```

---

## 💻 การติดตั้งและใช้งาน

ต้องใช้ **Python 3.10+** · คู่มือละเอียดอยู่ที่ [docs/USER_GUIDE.md](./docs/USER_GUIDE.md)

```bash
# 1) ติดตั้ง (แบบเบา — ใช้ได้ทันที)
pip install -r requirements.txt
# 1b) ถ้าต้องการโมเดล AI จริง (ดาวน์โหลดหลายร้อย MB)
pip install -r requirements-ml.txt

# 2) โหมดเมนู CLI
python main.py              # ใช้โมเดล AI ถ้ามี ไม่มีจะใช้ keyword อัตโนมัติ
python main.py --offline    # บังคับโหมด keyword (เดโมไม่ต้องใช้เน็ต)

# 3) โหมด Batch
python main.py --batch data/sample_batch.csv --output exports/batch_output.csv

# 4) หน้าเว็บในเครื่อง (สำรองเวลาเว็บออนไลน์ล่ม)
cd web && python -m http.server 8000   # เปิด http://localhost:8000

# 5) ทดสอบ + lint + วัดความเร็ว
pip install -r requirements-dev.txt
flake8 && pytest --cov=src
python scripts/benchmark.py
```

🌐 เว็บออนไลน์: https://shinjixz.github.io/Final-Project/

---

## ⚙️ CI/CD

- `ci.yml` — ทุก push / pull request: `flake8` (PEP8) → `pytest` + coverage ขั้นต่ำ 80% → smoke test โหมด batch → `node --check` ไฟล์ JS ทดสอบบน Python 3.10, 3.11, 3.12
- `deploy-web.yml` — push เข้า `main`: รันเทสต์ก่อน ถ้าผ่านจึง deploy `web/` ขึ้น GitHub Pages

---

## 📈 ประสิทธิภาพและความสามารถรองรับผู้ใช้

ผลวัดจริงจาก `scripts/benchmark.py` (รายละเอียดใน [docs/BENCHMARK.md](./docs/BENCHMARK.md)): กับข้อมูล **10,000 แถว** ค้นหา ~5 ms, กรอง ~1 ms, เรียงลำดับ ~2 ms, เรียงหลายคีย์ ~3 ms

**เว็บ:** เป็น static site และโมเดล AI รันบนเครื่องผู้ใช้แต่ละคน ฝั่งเซิร์ฟเวอร์จึงไม่ต้องประมวลผล จำนวนผู้ใช้ถูกจำกัดโดยโควตาของ GitHub Pages (soft limit แบนด์วิดท์ ~100 GB/เดือน) ไม่ใช่โค้ดของเรา หน้าเว็บทั้งหมด ~58 KB จึงรองรับได้ราว 1.7 ล้านครั้งเข้าชม/เดือน (คำนวณจากโควตา ยังไม่ได้ทำ load test) ไฟล์โมเดลโหลดจาก CDN ของ Hugging Face จึงไม่กินโควตานี้ และเบราว์เซอร์เก็บโมเดลไว้หลังโหลดครั้งแรก

**CLI:** ออกแบบให้ใช้คนเดียวต่อเครื่อง (SQLite ไฟล์เดียว) — ถ้าจะให้หลายคนใช้ร่วมกันต้องย้ายไป PostgreSQL + API (ดูแผนต่อยอดใน PLAN.md)

---

## 🔭 ข้อจำกัดและแผนพัฒนาต่อ
- รองรับเฉพาะข้อความภาษาอังกฤษ → แผน: ใช้โมเดลภาษาไทย เช่น WangchanBERTa
- ข้อมูล CLI กับเว็บแยกกัน (SQLite vs localStorage) → แผน: REST API + PostgreSQL/Supabase กลาง
- Image mood ใช้กฎจากโทนสี ไม่ใช่โมเดล AI → แผน: ใช้โมเดล vision
- เพิ่ม Service Worker ให้เว็บใช้งานออฟไลน์ได้ และ deploy สำรองอีกที่ (Netlify / Cloudflare Pages)
