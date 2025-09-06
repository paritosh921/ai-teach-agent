from manim import *
import json
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from src.structured_renderer import render_video
BLUEPRINT = json.loads('''{
  "slides": [
    {
      "title": "Slide One",
      "bullets": [
        "First bullet point to wrap and display properly inside the left column.",
        "Second bullet, a bit longer, to verify wrapping works and stays within safe margins."
      ],
      "formulas": [
        "a^2 + b^2 = c^2"
      ]
    },
    {
      "title": "Slide Two",
      "bullets": [
        "Key idea: smooth layout without overlaps.",
        "Right column shows formula."
      ],
      "formulas": [
        "\\\\int_a^b f(x) dx = F(b)-F(a)"
      ]
    }
  ],
  "title": "Test Structured Renderer",
  "meta": {
    "audience": "undergraduate",
    "estimated_duration": 2
  }
}''')
class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
