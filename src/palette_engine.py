"""
PaletteEngine Module
Handles emotion-to-color mapping, relative luminance calculations,
and WCAG 2.1 contrast ratio evaluations for accessibility compliance.
"""

import math
import re
from typing import Any, Dict, List, Tuple

from src.exceptions import InvalidInputError

HEX_PATTERN = re.compile(r"^#?[0-9a-fA-F]{6}$")


class PaletteEngine:
    """
    Core engine responsible for generating dynamic palettes (8 colors)
    and calculating WCAG 2.1 accessibility scores.
    """

    # 8-colour palettes per emotion. Must stay identical to web/app.js
    # (emotionRules) — tests/test_web.py checks this.
    EMOTION_PALETTES: Dict[str, List[str]] = {
        "joy": [
            "#FFD700", "#FF8C00", "#FF69B4", "#00BFFF",
            "#32CD32", "#FFE4B5", "#FFF8DC", "#2C3E50"
        ],
        "sadness": [
            "#1C2541", "#3A506B", "#5BC0BE", "#6C757D",
            "#ADB5BD", "#D9E2EC", "#F0F4F8", "#0F172A"
        ],
        "anger": [
            "#D00000", "#9D0208", "#E85D04", "#FAA307",
            "#370617", "#FFCCD5", "#FFF0F3", "#2B2D42"
        ],
        "fear": [
            "#2B1E3A", "#4A3E3D", "#2C3539", "#5C5470",
            "#B8C0C2", "#8D99AE", "#EDF2F4", "#111827"
        ],
        "love": [
            "#FF758F", "#FF4D6D", "#C9184A", "#FFB3C1",
            "#FFF0F3", "#800F2F", "#FFCCD5", "#590D22"
        ],
        "surprise": [
            "#7209B7", "#3F37C9", "#4CC9F0", "#F72585",
            "#4895EF", "#E0AAFF", "#F7F0F5", "#10002B"
        ],
        "neutral": [
            "#2B2D42", "#8D99AE", "#EDF2F4", "#F8F9FA",
            "#6C757D", "#343A40", "#E9ECEF", "#ADB5BD"
        ]
    }

    @classmethod
    def get_palette(cls, emotion: str) -> List[str]:
        """
        Retrieves an 8-color HEX palette array based on the given emotion.
        Defaults to 'neutral' if emotion is unknown or unmapped.
        """
        normalized_emotion = emotion.lower().strip() if emotion else "neutral"
        palette = cls.EMOTION_PALETTES.get(
            normalized_emotion, cls.EMOTION_PALETTES["neutral"]
        )
        return list(palette)  # copy so callers cannot mutate the table

    @staticmethod
    def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
        """
        Converts a HEX color string (e.g., '#FFD166') to an RGB tuple (255, 209, 102).
        """
        if not isinstance(hex_code, str) or not HEX_PATTERN.match(hex_code):
            raise InvalidInputError(f"Invalid HEX color format: {hex_code}")
        clean_hex = hex_code.lstrip("#")
        return tuple(int(clean_hex[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def calculate_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """
        Calculates Relative Luminance according to WCAG 2.1 specs.
        L = 0.2126 * R + 0.7152 * G + 0.0722 * B
        """
        normalized = []
        for val in rgb:
            s_rgb = val / 255.0
            if s_rgb <= 0.03928:
                c = s_rgb / 12.92
            else:
                c = math.pow((s_rgb + 0.055) / 1.055, 2.4)
            normalized.append(c)

        r, g, b = normalized
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @classmethod
    def calculate_contrast_ratio(cls, hex1: str, hex2: str) -> float:
        """
        Calculates WCAG 2.1 contrast ratio between two HEX colors.
        Formula: (L1 + 0.05) / (L2 + 0.05) where L1 > L2
        Returns a ratio rounded to 2 decimal places (e.g., 4.51).
        """
        rgb1 = cls.hex_to_rgb(hex1)
        rgb2 = cls.hex_to_rgb(hex2)

        l1 = cls.calculate_relative_luminance(rgb1)
        l2 = cls.calculate_relative_luminance(rgb2)

        lighter = max(l1, l2)
        darker = min(l1, l2)

        ratio = (lighter + 0.05) / (darker + 0.05)
        return round(ratio, 2)

    @classmethod
    def evaluate_wcag_compliance(cls, fg_hex: str, bg_hex: str) -> Dict[str, Any]:
        """
        Evaluates readability compliance based on WCAG 2.1 standards.
        - AAA Level: Ratio >= 7.0
        - AA Level: Ratio >= 4.5
        - Fail: Ratio < 4.5
        """
        ratio = cls.calculate_contrast_ratio(fg_hex, bg_hex)

        if ratio >= 7.0:
            status = "PASS (AAA)"
            is_compliant = True
        elif ratio >= 4.5:
            status = "PASS (AA)"
            is_compliant = True
        else:
            status = "FAIL"
            is_compliant = False

        return {
            "foreground": fg_hex,
            "background": bg_hex,
            "contrast_ratio": ratio,
            "status": status,
            "is_compliant": is_compliant
        }

    @classmethod
    def best_text_pair(cls, palette: List[str]) -> Dict[str, Any]:
        """Return the foreground/background pair with the highest contrast."""
        best = None
        for i, fg in enumerate(palette):
            for bg in palette[i + 1:]:
                result = cls.evaluate_wcag_compliance(fg, bg)
                if best is None or result["contrast_ratio"] > best["contrast_ratio"]:
                    best = result
        if best is None:
            raise InvalidInputError("palette ต้องมีอย่างน้อย 2 สี")
        return best


# --- Quick Self-Test / Verification ---
if __name__ == "__main__":
    engine = PaletteEngine()
    joy_palette = engine.get_palette("joy")
    print(f"Generated 8-Color Joy Palette: {joy_palette}")

    # WCAG Test
    text_color = joy_palette[5]  # #073B4C (Dark text)
    bg_color = joy_palette[1]    # #FFFCF9 (Light bg)
    evaluation = engine.evaluate_wcag_compliance(text_color, bg_color)
    print(f"WCAG Evaluation: {evaluation}")
