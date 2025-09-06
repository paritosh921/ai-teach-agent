"""
Renderer template for block IR.

This file is used as a template: the generator replaces the blocks = [{"type": "title", "text": "Block IR Demo"}, {"type": "two_column", "left": "Goal one; Goal two", "right": "Summary text"}, {"type": "formula", "latex": "a^2+b^2=c^2", "row_start": 2, "row_end": 3}] marker
with a JSON list of block dicts and writes a temp Scene file to compile.
"""

from manim import *
from src.components import PanelGrid, Title, TwoColumn, FormulaBlock


class Lesson(Scene):
    def construct(self):
        grid = PanelGrid(self, rows=8, cols=12, margin=0.6)

        # Filled in by generator (JSON -> Python list of dicts)
        blocks = [{"type": "title", "text": "Block IR Demo"}, {"type": "two_column", "left": "Goal one; Goal two", "right": "Summary text"}, {"type": "formula", "latex": "a^2+b^2=c^2", "row_start": 2, "row_end": 3}]

        # Basic fade-in progression
        for b in blocks:
            t = b.get("type")
            if t == "title":
                obj = Title.build(self, grid, b.get("text", ""))
                self.play(FadeIn(obj, shift=DOWN * 0.2))
            elif t == "two_column":
                l, r = TwoColumn.build(self, grid, b.get("left", ""), b.get("right", ""))
                self.play(FadeIn(VGroup(l, r), lag_ratio=0.1))
            elif t == "formula":
                obj = FormulaBlock.build(self, grid, b.get("latex", ""), b.get("row_start", 2), b.get("row_end", 3))
                self.play(FadeIn(obj))
            self.wait(0.4)

        self.wait(1.0)

