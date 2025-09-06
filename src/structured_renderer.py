"""
Structured Manim renderer with auto-layout to avoid overlaps/out-of-frame.

This module renders a simple, deterministic slide deck from a blueprint dict:

Blueprint schema (minimal):
{
  "title": str,
  "slides": [
    {"title": str, "bullets": [str, ...], "formulas": [str, ...]}
  ],
  "meta": {"audience": str, "estimated_duration": int}
}

The renderer ensures content stays inside a safe area, wraps long lines,
and scales groups to fit the frame without relying on LLM edits.
"""

from typing import Dict, Any, List, Tuple
from manim import *


SAFE_MARGIN = 0.5  # frame units
TITLE_SIZE = 54
BULLET_SIZE = 36
MIN_BULLET_SIZE = 26
FORMULA_SCALE = 0.9


def _wrap_into_lines(text: str, max_width: float, font_size: int) -> List[str]:
    """Split text into lines so each line fits max_width when rendered.

    Uses Text width measurement for accurate wrapping.
    """
    words = text.strip().split()
    if not words:
        return []
    lines: List[str] = []
    cur: List[str] = []
    for w in words:
        trial = (" ".join(cur + [w])).strip()
        if not trial:
            cur.append(w)
            continue
        m = Text(trial, font_size=font_size)
        if m.width <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
                cur = [w]
            else:
                # Single very long word; accept it and let scaling handle later
                lines.append(w)
                cur = []
    if cur:
        lines.append(" ".join(cur))
    return lines


def _build_bullets(bullets: List[str], col_width: float, base_size: int) -> VGroup:
    """Create a VGroup of bullet lines wrapped to fit col_width.

    Returns a VGroup where each Mobject is a line (with "- " prefix for first
    line of each bullet, and indent for wrapped continuation lines).
    """
    items: List[Mobject] = []
    for bullet in bullets:
        bullet = bullet.strip()
        if not bullet:
            continue
        wrapped = _wrap_into_lines(bullet, col_width, base_size)
        for i, line in enumerate(wrapped):
            prefix = "- " if i == 0 else "  "
            t = Text(prefix + line, font_size=base_size)
            items.append(t)
    if not items:
        return VGroup()
    group = VGroup(*items)
    group.arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    return group


def _build_formula_group(formulas: List[str], max_width: float) -> VGroup:
    """Create a VGroup of MathTex formulas scaled to fit width.

    Limits to at most 2 formulas for clarity.
    """
    if not formulas:
        return VGroup()
    objs: List[Mobject] = []
    for f in formulas[:2]:
        try:
            m = MathTex(f)
        except Exception:
            # fallback: plain text
            m = Text(f, font_size=BULLET_SIZE)
        m.scale_to_fit_width(max_width * FORMULA_SCALE)
        objs.append(m)
    vg = VGroup(*objs).arrange(DOWN, center=False, aligned_edge=LEFT, buff=0.3)
    return vg


def _safe_area() -> Tuple[float, float, float, float]:
    """Return left, right, top, bottom bounds of the safe drawable area."""
    w = config.frame_width
    h = config.frame_height
    left = -w / 2 + SAFE_MARGIN
    right = w / 2 - SAFE_MARGIN
    top = h / 2 - SAFE_MARGIN
    bottom = -h / 2 + SAFE_MARGIN
    return left, right, top, bottom


def _fit_columns(left_group: VGroup, right_group: VGroup, avail_height: float) -> None:
    """Scale columns uniformly if their max height exceeds available height."""
    max_h = max(left_group.height if len(left_group) else 0, right_group.height if len(right_group) else 0)
    if max_h > 1e-6 and max_h > avail_height:
        scale = avail_height / max_h
        left_group.scale(scale)
        right_group.scale(scale)


def _place_slide(scene: Scene, title_text: Mobject, left_group: VGroup, right_group: VGroup) -> None:
    left, right, top, bottom = _safe_area()
    # Title at top center
    title_text.to_edge(UP)
    title_text.shift(DOWN * 0.3)
    # Available height below title
    avail_height = (top - title_text.get_bottom()[1]) - (SAFE_MARGIN * 0.5) - (abs(bottom))
    if avail_height <= 0:
        avail_height = (config.frame_height - title_text.height) - 1.0
    # Two columns
    col_gap = 0.5
    col_width = (right - left - col_gap) / 2
    # Constrain left/right widths
    if len(left_group):
        left_group.scale_to_fit_width(min(col_width, max(1.0, col_width)))
    if len(right_group):
        right_group.scale_to_fit_width(min(col_width, max(1.0, col_width)))
    # Fit to height if needed
    _fit_columns(left_group, right_group, avail_height)
    # Position columns
    if len(left_group):
        left_group.to_edge(LEFT)
        left_group.shift(RIGHT * (SAFE_MARGIN))
        # Align top under title
        delta = title_text.get_bottom()[1] - left_group.get_top()[1] - 0.4
        left_group.shift(DOWN * delta)
    if len(right_group):
        right_group.to_edge(RIGHT)
        right_group.shift(LEFT * (SAFE_MARGIN))
        delta = title_text.get_bottom()[1] - right_group.get_top()[1] - 0.4
        right_group.shift(DOWN * delta)


def render_video(scene: Scene, blueprint: Dict[str, Any]) -> None:
    """Render a full video from a simple blueprint dict."""
    title = blueprint.get("title", "Lesson")
    slides = blueprint.get("slides", []) or [{"title": title, "bullets": [], "formulas": []}]

    for i, slide in enumerate(slides, start=1):
        slide_title = slide.get("title") or title
        bullets = [b for b in slide.get("bullets", []) if isinstance(b, str) and b.strip()]
        formulas = [f for f in slide.get("formulas", []) if isinstance(f, str) and f.strip()]

        # Build title
        t = Text(slide_title, font_size=TITLE_SIZE, weight=BOLD)
        # Compute safe col width for wrapping bullets
        left, right, top, bottom = _safe_area()
        col_gap = 0.5
        col_width = (right - left - col_gap) / 2
        # Adjust bullet font dynamically so content is readable
        bullet_size = BULLET_SIZE
        bullets_group = _build_bullets(bullets, col_width, bullet_size)
        # If too tall, try reducing size down to MIN_BULLET_SIZE
        max_iter = 3
        while bullets_group.height > (config.frame_height * 0.65) and bullet_size > MIN_BULLET_SIZE and max_iter > 0:
            bullet_size = max(MIN_BULLET_SIZE, bullet_size - 4)
            bullets_group = _build_bullets(bullets, col_width, bullet_size)
            max_iter -= 1

        formulas_group = _build_formula_group(formulas, col_width)

        _place_slide(scene, t, bullets_group, formulas_group)

        anims: List[Animation] = []
        anims.append(FadeIn(t, shift=DOWN * 0.2, lag_ratio=0.2))
        if len(bullets_group):
            anims.append(FadeIn(bullets_group, lag_ratio=0.1))
        if len(formulas_group):
            anims.append(FadeIn(formulas_group, lag_ratio=0.1))
        scene.play(*anims)
        scene.wait(1.2)

        if i < len(slides):
            # Transition to next slide
            scene.play(FadeOut(VGroup(t, bullets_group, formulas_group)))
            scene.wait(0.2)

