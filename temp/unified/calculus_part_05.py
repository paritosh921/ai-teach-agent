
from manim import *
import json
import sys
from pathlib import Path

# Ensure repo root is importable for src.* modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.structured_renderer import render_video

BLUEPRINT = json.loads('{"title": "Antiderivatives and the Fundamental Theorem of Calculus", "slides": [{"title": "Antiderivatives and the Fundamental Theorem of Calculus", "bullets": ["Understand the concept of antiderivatives and their role in calculus.", "Explore the Fundamental Theorem of Calculus and its implications.", "Learn to apply the power rule in reverse to find antiderivatives."], "formulas": ["F(x) = x^(n+1)/(n+1) + C"]}, {"title": "Antiderivative", "bullets": ["Antiderivative", "A function F(x) is an antiderivative of f(x) if F\'(x) = f(x)."], "formulas": ["F(x) = x^(n+1)/(n+1) + C"]}, {"title": "Fundamental Theorem of Calculus", "bullets": ["Fundamental Theorem of Calculus", "The theorem that links the concept of differentiating a function with integrating a function."], "formulas": ["F(x) = x^(n+1)/(n+1) + C"]}, {"title": "Finding Antiderivatives Using the Power Rule", "bullets": ["Given f(x) = x^n, the antiderivative F(x) is x^(n+1)/(n+1) + C, where C is the constant of integration.", "For example, if f(x) = x^2, then F(x) = x^3/3 + C."], "formulas": []}, {"title": "Antiderivatives", "bullets": ["Antiderivatives are the reverse process of differentiation.", "If differentiating a function gives us a derivative, finding an antiderivative involves determining the original function from its derivative."], "formulas": []}, {"title": "Fundamental Theorem of Calculus", "bullets": ["This theorem states that if F is an antiderivative of f on an interval [a, b], then the integral of f from a to b is F(b) - F(a).", "This connects the concept of area under a curve with antiderivatives."], "formulas": []}], "meta": {"audience": "undergraduate", "estimated_duration": 10, "difficulty": "intermediate"}}')

class Video(Scene):
    def construct(self):
        render_video(self, BLUEPRINT)
