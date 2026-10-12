"""Static checks for the web dashboard + Python/JS fallback parity."""
import json
import os
import re
import shutil
import subprocess

import pytest

from src.emotion_client import KeywordEmotionClient

WEB = os.path.join(os.path.dirname(__file__), "..", "web")
APP_JS = open(os.path.join(WEB, "app.js"), encoding="utf-8").read()
NODE = shutil.which("node")

SAMPLES = [
    "I am so extremely happy and excited about this new project!",
    "The weather today is so gloomy and I feel lonely.",
    "I cannot believe how furious I am with their bad customer service.",
    "I'm scared and anxious about the dark",
    "I love you darling",
    "Wow what an unexpected surprise",
    "The table is made of wood",
]


def test_no_fake_confidence_or_dead_backend():
    assert "Math.random" not in APP_JS
    assert "99.5%" not in APP_JS and "95.0%" not in APP_JS
    assert "localhost" not in APP_JS


def test_ai_library_is_loaded_lazily():
    # A top-level CDN import would break the whole page when the CDN is down.
    assert not re.search(r"^import .*cdn\.jsdelivr", APP_JS, re.MULTILINE)
    assert "await import(TRANSFORMERS_CDN)" in APP_JS


def test_index_loads_app_module():
    html = open(os.path.join(WEB, "index.html"), encoding="utf-8").read()
    assert 'type="module" src="app.js"' in html


@pytest.mark.skipif(NODE is None, reason="Node.js not installed")
def test_js_and_python_keyword_fallback_agree(tmp_path):
    module = tmp_path / "kf.mjs"
    shutil.copy(os.path.join(WEB, "keyword_fallback.js"), module)
    script = (f"import('{module.as_posix()}').then(m => console.log(JSON.stringify("
              f"{json.dumps(SAMPLES)}.map(t => m.keywordEmotion(t)))))")
    js_results = json.loads(subprocess.check_output([NODE, "-e", script], text=True))
    python = KeywordEmotionClient()
    for text, js in zip(SAMPLES, js_results):
        py = python.get_emotion(text)
        expected_label = None if py.label == "neutral" else py.label
        assert js["label"] == expected_label, text
        assert round(js["score"], 4) == py.score, text


def test_python_and_web_palettes_are_identical():
    from src.palette_engine import PaletteEngine
    start = APP_JS.index("const emotionRules")
    block = APP_JS[start:APP_JS.index("\n};", start)]
    web = {
        m.group(1).lower(): re.findall(r"#[0-9A-Fa-f]{6}", m.group(2))
        for m in re.finditer(r"(\w+): \{\s*palette: \[(.*?)\]", block, re.S)
    }
    assert len(web) == 6
    for emotion, colors in web.items():
        assert PaletteEngine.get_palette(emotion) == colors, emotion
