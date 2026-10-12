"""Design advisory: theme name, font pairing and usage ideas per emotion,
plus an automatic insight report over the saved history (Automation Agent).
"""

from collections import Counter
from typing import Dict, Iterable

from src.models import AnalysisRecord


class AIAdvisory:
    """Rule-based design advisor."""

    ADVISORY_RULES: Dict[str, Dict[str, str]] = {
        "joy": {
            "theme": "Vibrant Sunburst",
            "font": "Poppins / Montserrat (Sans-Serif ตัวหนา สดใส)",
            "usage": "E-Commerce, เว็บไซต์งานเทศกาล, Branding อาหารและเครื่องดื่ม",
        },
        "sadness": {
            "theme": "Melancholic Mist",
            "font": "Lora / Merriweather (Serif คลาสสิก ละมุนตา)",
            "usage": "แอปทำสมาธิ, บล็อกบทความ, Portfolio ส่วนตัว",
        },
        "anger": {
            "theme": "Fiery Passion",
            "font": "Oswald / Bebas Neue (Display Font ตัวหนา ทรงพลัง)",
            "usage": "แบนเนอร์สินค้ากีฬา, Gaming Dashboard, แคมเปญพลังสูง",
        },
        "fear": {
            "theme": "Mystic Shadow",
            "font": "Cinzel / Inter (Serif ลึกลับ + Sans อ่านง่าย)",
            "usage": "แพลตฟอร์ม Cybersecurity, คอนเทนต์สยองขวัญ, เครื่องมือความปลอดภัย",
        },
        "love": {
            "theme": "Romantic Bloom",
            "font": "Playfair Display / Lato (Serif หรูหรา)",
            "usage": "เว็บไซต์งานแต่งงาน, Lifestyle App, แพลตฟอร์มความสัมพันธ์",
        },
        "surprise": {
            "theme": "Electric Wonder",
            "font": "Space Grotesk / Plus Jakarta Sans (Geometric ทันสมัย)",
            "usage": "แอปบันเทิง, แบนเนอร์โปรโมชัน, Interactive Art",
        },
    }

    DEFAULT_ADVICE = {
        "theme": "Modern Neutral",
        "font": "Inter / Roboto (Clean Sans-Serif)",
        "usage": "แอปพลิเคชันทั่วไปและ Dashboard",
    }

    @classmethod
    def get_advice(cls, emotion: str) -> Dict[str, str]:
        key = (emotion or "").lower().strip()
        return dict(cls.ADVISORY_RULES.get(key, cls.DEFAULT_ADVICE))

    @classmethod
    def generate_insight_report(cls, records: Iterable[AnalysisRecord]) -> str:
        """Automatic analysis of the history (Automation Agent feature)."""
        records = list(records)
        if not records:
            return "ยังไม่มีประวัติการวิเคราะห์ — ลองวิเคราะห์ข้อความก่อน"
        counts = Counter(r.emotion for r in records)
        top_emotion, top_count = counts.most_common(1)[0]
        avg_conf = sum(r.confidence for r in records) / len(records)
        low_conf = [r for r in records if r.confidence < 0.5]
        advice = cls.get_advice(top_emotion)

        lines = [
            f"📊 วิเคราะห์ทั้งหมด {len(records)} รายการ",
            "สัดส่วนอารมณ์: " + ", ".join(
                f"{emo} {cnt} ({cnt / len(records):.0%})"
                for emo, cnt in counts.most_common()
            ),
            f"อารมณ์เด่น: {top_emotion.upper()} ({top_count} ครั้ง)",
            f"ความมั่นใจเฉลี่ย: {avg_conf:.1%}",
            f"แนะนำธีมหลักของโปรเจกต์: {advice['theme']} — ฟอนต์ {advice['font']}",
        ]
        if low_conf:
            lines.append(
                f"⚠️ มี {len(low_conf)} รายการที่ความมั่นใจต่ำกว่า 50% "
                "ควรเขียนข้อความให้ชัดเจนขึ้นหรือตรวจสอบด้วยตนเอง"
            )
        return "\n".join(lines)
