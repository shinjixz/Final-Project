"""
Module: ai_advisory.py
Role: Planner (ท็อป)
Description: คำแนะนำแนวคิดดีไซน์ + Font Pairings + การนำไปใช้งานตามอารมณ์ (Rule-Based)
"""


class AIAdvisory:
    ADVISORY_RULES = {
        "joy": {
            "theme": "Vibrant Sunburst",
            "concept": "ใช้สีสดและพื้นที่โล่งกว้าง เน้นความเคลื่อนไหวและความมีชีวิตชีวา มุมโค้งมน",
            "font_pairing": {"heading": "Poppins (Bold)", "body": "Nunito"},
            "usage": "เหมาะกับแอป E-Commerce, เว็บไซต์งานเทศกาล หรือ Branding อาหารและเครื่องดื่ม",
        },
        "sadness": {
            "theme": "Melancholic Rain",
            "concept": "โทนเย็นหม่น ไล่ระดับนุ่ม เว้นระยะห่างมาก ให้ความรู้สึกสงบและครุ่นคิด",
            "font_pairing": {"heading": "Merriweather", "body": "Lora"},
            "usage": "เหมาะกับแอปพลิเคชันเพื่อการทำสมาธิ (Meditation App) หรือบล็อกเขียนบทความ",
        },
        "anger": {
            "theme": "High-Contrast Impact",
            "concept": "คอนทราสต์สูง เส้นคม มุมเหลี่ยม จัดวางแบบชิดและตัวอักษรขนาดใหญ่เพื่อสร้างแรงปะทะ",
            "font_pairing": {"heading": "Bebas Neue", "body": "Oswald"},
            "usage": "เหมาะกับแบนเนอร์สินค้ากีฬา หรือสื่อประชาสัมพันธ์การออกกำลังกาย",
        },
        "fear": {
            "theme": "Midnight Suspense",
            "concept": "พื้นหลังมืดลึกคู่สีม่วงสว่างเป็นจุดเน้น ใช้เงาและการไล่เฉดเพื่อสร้างความลึกลับ",
            "font_pairing": {"heading": "Cinzel", "body": "Raleway"},
            "usage": "เหมาะกับโปสเตอร์หนัง/เกมสยองขวัญ หรือหน้า Landing งานอีเวนต์ฮาโลวีน",
        },
        "love": {
            "theme": "Soft Blush Romance",
            "concept": "สีพีชและชมพูอ่อนนุ่ม ใช้รูปทรงอ่อนโยนและลวดลายละเอียดเพื่อความอบอุ่น",
            "font_pairing": {"heading": "Playfair Display", "body": "Lato"},
            "usage": "เหมาะกับการ์ดเชิญงานแต่งงาน แบรนด์ความงาม หรือแอปหาคู่",
        },
        "neutral": {
            "theme": "Modern Neutral",
            "concept": "สีเรียบ จัดวางสะอาด เน้นความอ่านง่ายและลำดับชั้นข้อมูลที่ชัดเจน",
            "font_pairing": {"heading": "Inter (Semi-Bold)", "body": "Roboto"},
            "usage": "เหมาะสำหรับแอปพลิเคชันทั่วไปและ Dashboard",
        },
    }

    @classmethod
    def get_advice(cls, emotion: str) -> dict:
        """คืนคำแนะนำ (ถ้าไม่รู้จักอารมณ์ -> neutral) — คืนสำเนา แก้ไขภายนอกไม่กระทบกฎต้นฉบับ"""
        key = emotion.lower().strip() if isinstance(emotion, str) else "neutral"
        rule = cls.ADVISORY_RULES.get(key, cls.ADVISORY_RULES["neutral"])
        return {**rule, "font_pairing": dict(rule["font_pairing"])}

    @classmethod
    def format_advice(cls, emotion: str) -> str:
        a = cls.get_advice(emotion)
        fp = a["font_pairing"]
        return (f"🎨 ธีม: {a['theme']}\n"
                f"💡 แนวคิด: {a['concept']}\n"
                f"🔤 ฟอนต์: หัวข้อ {fp['heading']} + เนื้อหา {fp['body']}\n"
                f"📌 การใช้งาน: {a['usage']}")
