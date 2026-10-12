import pytest

from src.exceptions import InvalidInputError
from src.models import EMOTIONS
from src.palette_engine import PaletteEngine


@pytest.mark.parametrize("emotion", EMOTIONS)
def test_every_emotion_has_8_valid_colors(emotion):
    palette = PaletteEngine.get_palette(emotion)
    assert len(palette) == 8
    for color in palette:
        PaletteEngine.hex_to_rgb(color)


@pytest.mark.parametrize("emotion", ["unknown", "", None, "  JOY  "])
def test_unknown_or_messy_emotion(emotion):
    palette = PaletteEngine.get_palette(emotion)
    assert len(palette) == 8
    if emotion == "  JOY  ":
        assert palette == PaletteEngine.get_palette("joy")
    else:
        assert palette == PaletteEngine.get_palette("neutral")


def test_get_palette_returns_copy():
    PaletteEngine.get_palette("joy").append("#000000")
    assert len(PaletteEngine.get_palette("joy")) == 8


def test_hex_to_rgb():
    assert PaletteEngine.hex_to_rgb("#FFD166") == (255, 209, 102)
    assert PaletteEngine.hex_to_rgb("ffd166") == (255, 209, 102)


@pytest.mark.parametrize("bad", ["#FFF", "#GGGGGG", "", None, "#1234567"])
def test_hex_to_rgb_invalid(bad):
    with pytest.raises(InvalidInputError):
        PaletteEngine.hex_to_rgb(bad)


def test_black_white_contrast_is_21():
    assert PaletteEngine.calculate_contrast_ratio("#000000", "#FFFFFF") == 21.0
    assert PaletteEngine.calculate_contrast_ratio("#FFFFFF", "#000000") == 21.0


@pytest.mark.parametrize("fg,bg,status", [
    ("#000000", "#FFFFFF", "PASS (AAA)"),
    ("#767676", "#FFFFFF", "PASS (AA)"),
    ("#AAAAAA", "#FFFFFF", "FAIL"),
])
def test_wcag_levels(fg, bg, status):
    assert PaletteEngine.evaluate_wcag_compliance(fg, bg)["status"] == status


def test_best_text_pair_picks_highest_contrast():
    pair = PaletteEngine.best_text_pair(["#777777", "#000000", "#FFFFFF"])
    assert pair["contrast_ratio"] == 21.0


def test_best_text_pair_needs_two_colors():
    with pytest.raises(InvalidInputError):
        PaletteEngine.best_text_pair(["#000000"])
