
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Basic Derivative Rules", "slides": [{"title": "Basic Derivative Rules", "bullets": ["Understand the concept of the derivative as an instantaneous rate of change.", "Visualize the derivative as the slope of the tangent line on a graph.", "Learn to compute derivatives using first principles.", "Apply derivative rules to solve problems."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Derivative", "bullets": ["Derivative", "The derivative of a function at a point is the slope of the tangent line to the graph of the function at that point."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Limit", "bullets": ["Limit", "A fundamental concept in calculus used to define derivatives, representing the value that a function approaches as the input approaches some value."], "formulas": ["f\'(x) = lim(h→0) [f(x+h) - f(x)]/h"]}, {"title": "Derivative of f(x) = x²", "bullets": ["Using the limit definition, f\'(x) = lim(h→0) [(x+h)² - x²]/h = 2x.", "This shows the slope of y = x² at any point x is 2x."], "formulas": []}, {"title": "Derivative of f(x) = x³", "bullets": ["Compute using first principles: f\'(x) = lim(h→0) [(x+h)³ - x³]/h = 3x²."], "formulas": []}, {"title": "Geometrical Meaning", "bullets": ["The derivative can be visualized as the slope of the tangent line to the curve at a point.", "This contrasts with the average rate of change, which is the slope of a secant line through two points."], "formulas": []}, {"title": "Misconceptions", "bullets": ["A common misconception is confusing the average rate of change with the instantaneous rate of change.", "The former is over an interval, while the latter is at a single point."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
