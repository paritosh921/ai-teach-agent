
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "The Derivative as a Limit", "slides": [{"title": "The Derivative as a Limit", "bullets": ["Understand the definition of a derivative as a limit.", "Visualize the concept of instantaneous rate of change.", "Apply the derivative formula to simple functions."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Derivative", "bullets": ["Derivative", "The derivative of a function at a point measures the rate at which the function\'s value changes as its input changes."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Limit", "bullets": ["Limit", "A limit describes the value that a function approaches as the input approaches some value."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Derivative of a Linear Function", "bullets": ["Consider f(x) = 3x + 2.", "The derivative, f\'(x), is the constant 3, representing the slope of the line."], "formulas": []}, {"title": "Derivative of a Quadratic Function", "bullets": ["For f(x) = x^2, the derivative f\'(x) = 2x.", "This represents the slope of the tangent line at any point x."], "formulas": []}, {"title": "The Derivative as a Limit", "bullets": ["The derivative of a function f(x) at a point x is defined as the limit of the difference quotient as the change in x approaches zero.", "This captures the idea of an instantaneous rate of change."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
