"""
Renderer template for block IR.

This file is used as a template: the generator replaces the blocks = [{"type": "title", "text": "Kinetic and Potential Energy"}, {"type": "two_column", "left": "Kinetic energy is the energy of motion.", "right": "KE = ½mv²"}, {"type": "two_column", "left": "Potential energy is stored energy due to position.", "right": "PE = mgh"}, {"type": "two_column", "left": "Work-Energy Theorem relates work to energy change.", "right": "W_net = ΔKE"}, {"type": "two_column", "left": "Summary", "right": "Kinetic and potential energy help us understand motion and forces."}, {"type": "formula", "latex": "KE = \\frac{1}{2}mv^2", "row_start": 1, "row_end": 2}, {"type": "formula", "latex": "W_{net} = \\Delta KE", "row_start": 3, "row_end": 4}, {"type": "formula", "latex": "PE = mgh", "row_start": 5, "row_end": 6}] marker
with a JSON list of block dicts and writes a temp Scene file to compile.
"""

from manim import *
from src.components import PanelGrid, Title, TwoColumn, FormulaBlock, BulletList, CaptionUnder


class Lesson(Scene):
    def construct(self):
        grid = PanelGrid(self, rows=8, cols=12, margin=0.6)

        # Filled in by generator (JSON -> Python list of dicts)
        blocks = [{"type": "title", "text": "Kinetic and Potential Energy"}, {"type": "two_column", "left": "Kinetic energy is the energy of motion.", "right": "KE = ½mv²"}, {"type": "two_column", "left": "Potential energy is stored energy due to position.", "right": "PE = mgh"}, {"type": "two_column", "left": "Work-Energy Theorem relates work to energy change.", "right": "W_net = ΔKE"}, {"type": "two_column", "left": "Summary", "right": "Kinetic and potential energy help us understand motion and forces."}, {"type": "formula", "latex": "KE = \\frac{1}{2}mv^2", "row_start": 1, "row_end": 2}, {"type": "formula", "latex": "W_{net} = \\Delta KE", "row_start": 3, "row_end": 4}, {"type": "formula", "latex": "PE = mgh", "row_start": 5, "row_end": 6}]

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
            elif t == "bullet_list":
                obj = BulletList.build(self, grid, b.get("bullets", []), b.get("side", "full"), b.get("row_start", 2), b.get("row_end", None), b.get("font_size", 34))
                self.play(FadeIn(obj))
            elif t == "caption":
                obj = CaptionUnder.build(self, grid, b.get("text", ""))
                self.play(FadeIn(obj))
            self.wait(0.4)

        self.wait(1.0)
