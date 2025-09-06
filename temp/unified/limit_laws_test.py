
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Limits and Continuity", "slides": [{"title": "Limits and Continuity", "bullets": ["Understand the epsilon-delta definition", "Interpret one-sided limits", "Identify discontinuities"], "formulas": ["\\\\lim_{x \\\\to a} f(x) = L"]}, {"title": "Limit", "bullets": ["Limit", "Approach of a function value as x approaches a point."], "formulas": ["\\\\lim_{x \\\\to a} f(x) = L"]}, {"title": "Example 1", "bullets": ["Compute limit of (x^2-1)/(x-1) as x->1"], "formulas": []}, {"title": "Intuition", "bullets": ["Limits capture approaching behavior, not necessarily equality."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 2, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
