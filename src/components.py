"""
Small, safe component set for deterministic layout.

Each component places content within a PanelGrid region using fit/clip helpers,
ensuring nothing goes off-frame and no overlaps occur.
"""

from manim import *
from .layout import safe_rect, fit_and_place, autowrap_text


class PanelGrid:
    """12-col grid; returns rectangle regions inside the safe area."""

    def __init__(self, scene: Scene, rows: int = 8, cols: int = 12, margin: float = 0.6, vpad: float = 0.25, hpad: float = 0.25):
        self.scene = scene
        self.root = safe_rect(scene, margin=margin)
        self.rows, self.cols = rows, cols
        self.vpad, self.hpad = vpad, hpad
        self._cells = self._build_cells()

    def _build_cells(self):
        cells = []
        W = self.root.width
        H = self.root.height
        cw = W / self.cols
        ch = H / self.rows
        top_left = self.root.get_corner(UL)
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                x = top_left[0] + (c + 0.5) * cw
                y = top_left[1] - (r + 0.5) * ch
                cell = (
                    Rectangle(width=cw - self.hpad, height=ch - self.vpad)
                    .set_opacity(0)
                    .set_stroke(width=0)
                )
                cell.move_to([x, y, 0])
                row.append(cell)
            cells.append(row)
        return cells

    def region(self, r0: int, c0: int, r1: int, c1: int) -> Mobject:
        """Inclusive cell indices. (r0,c0) top-left; (r1,c1) bottom-right."""
        group = VGroup()
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                group.add(self._cells[r][c])
        rect = (
            Rectangle(width=group.width, height=group.height)
            .move_to(group.get_center())
            .set_opacity(0)
            .set_stroke(width=0)
        )
        return rect


class Title:
    @staticmethod
    def build(scene: Scene, grid: PanelGrid, text: str) -> Mobject:
        reg = grid.region(0, 0, 0, grid.cols - 1)  # top row full width
        t = autowrap_text(text or "", max_w=reg.width, font_size=48, align=LEFT)
        t = fit_and_place(t, reg, pad=0.05)
        scene.add(t)
        return t


class TwoColumn:
    @staticmethod
    def build(scene: Scene, grid: PanelGrid, left_text: str, right_text: str) -> tuple[Mobject, Mobject]:
        top_row = 1
        regL = grid.region(top_row, 0, grid.rows - 1, grid.cols // 2 - 1)
        regR = grid.region(top_row, grid.cols // 2, grid.rows - 1, grid.cols - 1)
        left = autowrap_text(left_text or "", max_w=regL.width, font_size=36, align=LEFT)
        right = autowrap_text(right_text or "", max_w=regR.width, font_size=36, align=LEFT)
        fit_and_place(left, regL, pad=0.1)
        fit_and_place(right, regR, pad=0.1)
        scene.add(left)
        scene.add(right)
        return left, right


class FormulaBlock:
    @staticmethod
    def build(scene: Scene, grid: PanelGrid, latex: str, row_start: int = 2, row_end: int = 3) -> Mobject:
        row_start = max(1, row_start)
        row_end = max(row_start, row_end)
        reg = grid.region(row_start, 1, row_end, grid.cols - 2)
        try:
            m = MathTex(latex or "")
        except Exception:
            m = Text(latex or "", font_size=36)
        fit_and_place(m, reg, pad=0.2)
        scene.add(m)
        return m


class BulletList:
    @staticmethod
    def build(scene: Scene, grid: PanelGrid, bullets: list[str], side: str = "full", row_start: int = 2, row_end: int = None, font_size: int = 34) -> Mobject:
        if row_end is None:
            row_end = grid.rows - 1
        side = (side or "full").lower()
        if side == "left":
            reg = grid.region(row_start, 0, row_end, grid.cols // 2 - 1)
        elif side == "right":
            reg = grid.region(row_start, grid.cols // 2, row_end, grid.cols - 1)
        else:
            reg = grid.region(row_start, 0, row_end, grid.cols - 1)
        items = []
        max_w = reg.width * 0.95
        for b in (bullets or [])[:10]:
            text = str(b).strip()
            if not text:
                continue
            line = autowrap_text(f"- {text}", max_w=max_w, font_size=font_size)
            items.append(line)
        if not items:
            g = VGroup()
        else:
            g = VGroup(*items).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        fit_and_place(g, reg, pad=0.12)
        scene.add(g)
        return g


class CaptionUnder:
    @staticmethod
    def build(scene: Scene, grid: PanelGrid, text: str) -> Mobject:
        # Bottom band full width
        reg = grid.region(grid.rows - 1, 0, grid.rows - 1, grid.cols - 1)
        t = autowrap_text(text or "", max_w=reg.width, font_size=28, align=LEFT)
        fit_and_place(t, reg, pad=0.05)
        scene.add(t)
        return t
