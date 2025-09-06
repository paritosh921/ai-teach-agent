"""
Layout utilities for deterministic, overlap-safe placement.

Provides a safe drawing area, fitting helpers, and paragraph-style text
wrapping using Manim measurements.
"""

from manim import *
import numpy as np

SAFE_MARGIN = 0.6


def safe_rect(scene: Scene, margin: float = SAFE_MARGIN) -> Mobject:
    w = config.frame_width - 2 * margin
    h = config.frame_height - 2 * margin
    r = Rectangle(width=max(0.1, w), height=max(0.1, h)).set_opacity(0).set_stroke(width=0)
    r.move_to(ORIGIN)
    return r


def scale_to_fit(m: Mobject, max_w: float, max_h: float) -> None:
    if getattr(m, "width", None) and m.width > max_w:
        m.scale_to_fit_width(max_w)
    if getattr(m, "height", None) and m.height > max_h:
        m.scale_to_fit_height(max_h)


def clamp_to(m: Mobject, rect: Mobject, pad: float = 0.0) -> None:
    left = rect.get_left()[0] + pad
    right = rect.get_right()[0] - pad
    bottom = rect.get_bottom()[1] + pad
    top = rect.get_top()[1] - pad
    cx, cy, _ = m.get_center()
    cx = float(np.clip(cx, left, right))
    cy = float(np.clip(cy, bottom, top))
    m.move_to(np.array([cx, cy, 0.0]))


def fit_and_place(m: Mobject, region: Mobject, pad: float = 0.2) -> Mobject:
    max_w = region.width - 2 * pad
    max_h = region.height - 2 * pad
    scale_to_fit(m, max_w, max_h)
    m.move_to(region.get_center())
    clamp_to(m, region, pad=pad)
    return m


def autowrap_text(txt: str, max_w: float, font_size: int = 36, line_buff: float = 0.18, align=LEFT) -> Mobject:
    words = (txt or "").split()
    if not words:
        return Text("", font_size=font_size)
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if not cur or Text(cand, font_size=font_size).width <= max_w:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) <= 1:
        return Text(" ".join(lines), font_size=font_size)
    vg = VGroup(*[Text(l, font_size=font_size) for l in lines]).arrange(
        DOWN, aligned_edge=align, buff=line_buff
    )
    return vg
