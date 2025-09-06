
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Understanding Limits", "slides": [{"title": "Understanding Limits", "bullets": ["Understand the intuitive concept of limits.", "Learn how to apply limit laws to evaluate limits.", "Recognize common misconceptions about limits."], "formulas": ["lim(x→a) [f(x) + g(x)] = lim(x→a) f(x) + lim(x→a) g(x)"]}, {"title": "Limit", "bullets": ["Limit", "The value that a function approaches as the input approaches a particular point."], "formulas": ["lim(x→a) [f(x) + g(x)] = lim(x→a) f(x) + lim(x→a) g(x)"]}, {"title": "Epsilon-Delta Definition", "bullets": ["Epsilon-Delta Definition", "A formal definition of limits using arbitrary closeness."], "formulas": ["lim(x→a) [f(x) + g(x)] = lim(x→a) f(x) + lim(x→a) g(x)"]}, {"title": "Example 1: Basic Limit Evaluation", "bullets": ["Evaluate lim(x→3) (2x + 1).", "As x approaches 3, the function approaches 7."], "formulas": []}, {"title": "Example 2: Using Limit Laws", "bullets": ["Evaluate lim(x→2) (x² + 3x).", "Break it down using the sum rule: lim(x→2) x² + lim(x→2) 3x = 4 + 6 = 10."], "formulas": []}, {"title": "Intuitive Understanding of Limits", "bullets": ["Imagine driving towards a stop sign.", "The limit is akin to the speed you approach as you near the sign, even if you never actually stop."], "formulas": []}, {"title": "Limit Laws", "bullets": ["These laws allow us to break down complex limits into simpler parts, much like solving a puzzle by assembling smaller pieces."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
