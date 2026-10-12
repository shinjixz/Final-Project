"""Presentation helper: draw palette swatches.

* ``render_text`` — coloured blocks in the terminal (no dependencies)
* ``plot_palette`` — matplotlib image, saved to a PNG file (works without a
  display, e.g. on CI or over SSH)
"""

from typing import List, Optional

from src.palette_engine import PaletteEngine


class PaletteVisualizer:
    """Render palettes for the CLI."""

    @staticmethod
    def render_text(colors: List[str]) -> str:
        blocks = []
        for color in colors:
            r, g, b = PaletteEngine.hex_to_rgb(color)
            blocks.append(f"\033[48;2;{r};{g};{b}m    \033[0m {color}")
        return "  ".join(blocks)

    @staticmethod
    def plot_palette(emotion: str, colors: List[str], score: float,
                     output_path: str = "data/palette_preview.png") -> Optional[str]:
        """Save a swatch image. Returns the path, or None if matplotlib is missing."""
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            return None

        fig, ax = plt.subplots(figsize=(max(len(colors), 1), 2))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")
        for i, color in enumerate(colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
            ax.text(i + 0.5, -0.2, color, ha="center", va="top",
                    fontsize=8, color="white", fontweight="bold")
        ax.set_xlim(0, len(colors))
        ax.set_ylim(-0.5, 1)
        ax.axis("off")
        ax.set_title(f"Emotion: {emotion.upper()} (Confidence: {score * 100:.1f}%)",
                     color="white", fontsize=12, pad=10)
        fig.tight_layout()
        fig.savefig(output_path, facecolor=fig.get_facecolor())
        plt.close(fig)
        return output_path
