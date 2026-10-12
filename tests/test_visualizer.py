import pytest

from src.visualizer import PaletteVisualizer


def test_render_text_contains_every_color():
    out = PaletteVisualizer.render_text(["#000000", "#FFFFFF"])
    assert "#000000" in out and "#FFFFFF" in out and "\033[48;2;0;0;0m" in out


def test_plot_palette_saves_png(tmp_path):
    pytest.importorskip("matplotlib")
    path = PaletteVisualizer.plot_palette("joy", ["#000000", "#FFFFFF"], 0.9,
                                          str(tmp_path / "p.png"))
    assert path and (tmp_path / "p.png").stat().st_size > 0
