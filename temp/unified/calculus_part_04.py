
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Applications of Derivatives", "slides": [{"title": "Applications of Derivatives", "bullets": ["Understand the basic rules of differentiation.", "Comprehend the geometric interpretation of derivatives.", "Explore real-world applications of derivatives.", "Recognize higher-order derivatives and their significance."], "formulas": ["f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]"]}, {"title": "Derivative", "bullets": ["Derivative", "The derivative represents the instantaneous rate of change of a function with respect to one of its variables."], "formulas": ["f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]"]}, {"title": "Power Rule", "bullets": ["Power Rule", "The derivative of x^n is nx^(n-1)."], "formulas": ["f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]"]}, {"title": "Constant Rule", "bullets": ["Constant Rule", "The derivative of a constant is zero."], "formulas": ["f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]"]}, {"title": "Constant Multiple Rule", "bullets": ["Constant Multiple Rule", "The derivative of a constant times a function is the constant times the derivative of the function."], "formulas": ["f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]"]}, {"title": "Example 1: Derivative of x^2", "bullets": ["Using the power rule, d/dx(x^2) = 2x.", "This can be derived from first principles by calculating the limit as h approaches zero of [(x+h)^2 - x^2]/h."], "formulas": []}, {"title": "Example 2: Derivative of a Constant", "bullets": ["For a constant c, d/dx(c) = 0.", "This is because the slope of a horizontal line is zero."], "formulas": []}, {"title": "Derivative from First Principles", "bullets": ["The derivative is defined as the limit of the average rate of change as the interval approaches zero.", "This is expressed as f\'(x) = lim(h→0) [(f(x+h) - f(x))/h]."], "formulas": []}, {"title": "Geometric Interpretation", "bullets": ["Geometrically, the derivative at a point is the slope of the tangent line to the curve at that point.", "This provides a visual understanding of how the function is changing at that specific location."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
