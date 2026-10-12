# Benchmark Results

สร้างโดย `python scripts/benchmark.py`

| ข้อมูล (แถว) | Insert ทั้งหมด | Insert/แถว | โหลดทั้งหมด | Get by id | Search | Filter | Sort | Multi-key sort |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 124 ms | 1.24 ms | 0.7 ms | 0.11 ms | 0.06 ms | 0.02 ms | 0.01 ms | 0.02 ms |
| 1,000 | 1128 ms | 1.13 ms | 3.1 ms | 0.07 ms | 0.49 ms | 0.10 ms | 0.10 ms | 0.24 ms |
| 10,000 | 12960 ms | 1.30 ms | 39.5 ms | 0.07 ms | 5.23 ms | 1.05 ms | 1.74 ms | 3.21 ms |

Keyword analyser (โหมดออฟไลน์): ~59,760 ข้อความ/วินาที

เครื่องที่วัด: Python 3.13.16 บน Linux x86_64 — ค่าที่รายงานคือเวลาดีที่สุดจาก 5 รอบ (ยกเว้น Insert ที่วัดรอบเดียว; insert แต่ละแถว commit ลงดิสก์ทันที)
