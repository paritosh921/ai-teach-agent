"""
Adaptive renderer for slide-based lessons with varied, readable layouts.

Renders slides with adaptive sizing, auto-wrapping, and pagination.
Supported slide types:
- title: {"type":"title","text": str}
- bullets: {"type":"bullets","title": str, "items": [str]}
- two_column: {"type":"two_column","left_title": str, "left": str, "right_title": str, "right": str}
- equation: {"type":"equation","title": str, "lines": [latex_str]}
- plot: {"type":"plot","title": str, "expr": py_expr, "x_range":[min,max,step], "y_range":[min,max,step]}
- bar: {"type":"bar","title": str, "labels":[str], "values":[number]}
- figure: {"type":"figure","title": str, "caption": str}

The generator injects a JSON list into [{"type": "title", "text": "Understanding Free Fall: A Special Case of Motion"}, {"type": "bullets", "title": "Objectives", "items": ["Understand free fall as motion with constant acceleration.", "Derive key equations for free-falling objects.", "Visualize velocity and distance relationships in free fall."]}, {"type": "two_column", "left_title": "Free Fall", "left": "Motion under gravitational acceleration only.", "right_title": "Gravitational Acceleration", "right": "Acceleration due to Earth's gravity, approx. -9.8 m/s²."}, {"type": "equation", "title": "Key Equations", "lines": ["t = \\sqrt{\\frac{2h}{g}}", "v = \\sqrt{2gh}"]}, {"type": "plot", "title": "Velocity vs. Time", "expr": "v = -9.8*t", "x_range": [0, 10, 0.1], "y_range": [-100, 0, 10]}, {"type": "plot", "title": "Distance vs. Time", "expr": "d = 0.5*-9.8*t**2", "x_range": [0, 10, 0.1], "y_range": [0, 500, 50]}, {"type": "bar", "title": "Gravitational Acceleration on Different Planets", "labels": ["Earth", "Moon", "Mars"], "values": [9.8, 1.6, 3.7]}, {"type": "figure", "title": "Free Fall Illustration", "caption": "An object in free fall experiences constant acceleration due to gravity."}, {"type": "bullets", "title": "Summary", "items": ["Free fall illustrates motion under constant gravity.", "Velocity and distance show linear and quadratic time relationships."]}] at build time.
"""

from manim import *
import numpy as np
import re

# ---------- layout primitives ----------
SAFE_MARGIN = 0.6


def safe_rect(scene, margin=SAFE_MARGIN):
    # Use config frame size for CE 0.18 compatibility
    w = config.frame_width - 2 * margin
    h = config.frame_height - 2 * margin
    r = Rectangle(width=max(0.1, w), height=max(0.1, h)).set_stroke(width=0).set_opacity(0)
    r.move_to(ORIGIN)
    return r


def autowrap_to_width(text, max_w, font_size=36, line_buff=0.18, align=LEFT):
    words = (text or "").split()
    if not words:
        return Text("", font_size=font_size)
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if Text(cand, font_size=font_size).width <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) == 1:
        return Text(lines[0], font_size=font_size)
    vg = VGroup(*[Text(l, font_size=font_size) for l in lines]).arrange(DOWN, aligned_edge=align, buff=0.16)
    return vg


def group_fits(group: Mobject, region: Mobject, pad=0.15):
    return (group.width <= region.width - 2 * pad) and (group.height <= region.height - 2 * pad)


def scale_to_fit(group: Mobject, region: Mobject, pad=0.15):
    max_w = max(0.1, region.width - 2 * pad)
    max_h = max(0.1, region.height - 2 * pad)
    if group.width > max_w:
        group.scale_to_fit_width(max_w)
    if group.height > max_h:
        group.scale_to_fit_height(max_h)


def center_in(group: Mobject, region: Mobject):
    group.move_to(region.get_center())
    return group


def clamp_inside_scene(scene: Scene, m: Mobject, pad: float = 0.02) -> None:
    """Ensure m is fully inside the safe area by scaling (if needed) and shifting.

    This is a last-resort guard against any residual drift from animations or rounding.
    """
    safe = safe_rect(scene)
    # Scale to not exceed safe rect
    max_w = max(0.1, safe.width - 2 * pad)
    max_h = max(0.1, safe.height - 2 * pad)
    if m.width > max_w or m.height > max_h:
        m.scale(min(max_w / max(m.width, 1e-6), max_h / max(m.height, 1e-6)))
    # Shift into bounds
    left_bound = safe.get_left()[0] + pad
    right_bound = safe.get_right()[0] - pad
    bottom_bound = safe.get_bottom()[1] + pad
    top_bound = safe.get_top()[1] - pad
    dx = 0.0
    dy = 0.0
    left = m.get_left()[0]
    right = m.get_right()[0]
    bottom = m.get_bottom()[1]
    top = m.get_top()[1]
    if left < left_bound and right <= right_bound:
        dx = left_bound - left
    elif right > right_bound and left >= left_bound:
        dx = right_bound - right
    # If both out, width > safe; we already scaled, so recompute and clamp center
    left = m.get_left()[0]; right = m.get_right()[0]
    if left < left_bound:
        dx = max(dx, left_bound - left)
    if right > right_bound:
        dx = min(dx, right_bound - right)
    if bottom < bottom_bound and top <= top_bound:
        dy = bottom_bound - bottom
    elif top > top_bound and bottom >= bottom_bound:
        dy = top_bound - top
    bottom = m.get_bottom()[1]; top = m.get_top()[1]
    if bottom < bottom_bound:
        dy = max(dy, bottom_bound - bottom)
    if top > top_bound:
        dy = min(dy, top_bound - top)
    if abs(dx) > 1e-6 or abs(dy) > 1e-6:
        m.shift(np.array([dx, dy, 0.0]))


def make_panel(scene, tl, br, rows=12, cols=12):
    # tl, br in grid coords (0..rows-1, 0..cols-1), inclusive
    root = safe_rect(scene)
    cw = root.width / cols
    ch = root.height / rows
    top_left = root.get_corner(UL)
    left = top_left[0] + (tl[1]) * cw
    right = top_left[0] + (br[1] + 1) * cw
    top = top_left[1] - (tl[0]) * ch
    bottom = top_left[1] - (br[0] + 1) * ch
    rect = Rectangle(width=right - left, height=top - bottom).set_stroke(width=0).set_opacity(0)
    rect.move_to([(left + right) / 2, (top + bottom) / 2, 0])
    return rect


# ---------- adaptive builders ----------
def build_title(scene, text):
    region = make_panel(scene, (0, 0), (1, 11), rows=12, cols=12)
    # Grow-to-fit search
    f_hi, f_lo = 72, 36
    best = Text("", font_size=f_lo)
    while f_hi - f_lo > 1:
        mid = (f_hi + f_lo) // 2
        cand = autowrap_to_width(text, max_w=region.width * 0.96, font_size=mid, align=LEFT)
        if group_fits(cand, region, pad=0.02):
            best = cand
            f_lo = mid
        else:
            f_hi = mid
    scale_to_fit(best, region, pad=0.02)
    center_in(best, region)
    scene.play(FadeIn(best, shift=UP))
    clamp_inside_scene(scene, best)
    return best


def build_bullets(scene, title, items, min_font=30):
    t_reg = make_panel(scene, (2, 0), (3, 11))
    b_reg = make_panel(scene, (4, 0), (11, 11))
    # Title
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    clamp_inside_scene(scene, t)

    # Bullets with pagination if needed
    pages = []
    f = 36
    # Try to fit all; if fails, reduce font
    while True:
        cur = VGroup()
        for it in items:
            para = autowrap_to_width(it, max_w=b_reg.width * 0.92, font_size=f, align=LEFT)
            row = VGroup(Text("•", font_size=f), para).arrange(RIGHT, buff=0.35, aligned_edge=UP)
            cur.add(row)
        cur.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        if group_fits(cur, b_reg, pad=0.05) or f <= min_font:
            break
        f -= 2
    if not group_fits(cur, b_reg, pad=0.05):
        # paginate by splitting items
        half = max(1, len(items) // 2)
        pages.append(items[:half])
        pages.append(items[half:])
    else:
        pages.append(items)

    for idx, page in enumerate(pages):
        g = VGroup()
        for it in page:
            para = autowrap_to_width(it, max_w=b_reg.width * 0.92, font_size=f, align=LEFT)
            row = VGroup(Text("•", font_size=f), para).arrange(RIGHT, buff=0.35, aligned_edge=UP)
            g.add(row)
        g.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        scale_to_fit(g, b_reg, pad=0.05)
        g.move_to(b_reg.get_left() + RIGHT * 0.1)
        scene.play(FadeIn(g, shift=RIGHT))
        clamp_inside_scene(scene, g)
        scene.wait(0.6)
        if idx < len(pages) - 1:
            scene.play(FadeOut(g))


def build_two_col(scene, left_title, left_text, right_title, right_text):
    l_reg = make_panel(scene, (2, 0), (11, 5))
    r_reg = make_panel(scene, (2, 6), (11, 11))
    lt = autowrap_to_width(left_title, max_w=l_reg.width * 0.95, font_size=42)
    rt = autowrap_to_width(right_title, max_w=r_reg.width * 0.95, font_size=42)
    lx = autowrap_to_width(left_text, max_w=l_reg.width * 0.95, font_size=34, align=LEFT)
    rx = autowrap_to_width(right_text, max_w=r_reg.width * 0.95, font_size=34, align=LEFT)
    l = VGroup(lt, lx).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    r = VGroup(rt, rx).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    scale_to_fit(l, l_reg, pad=0.05)
    center_in(l, l_reg)
    scale_to_fit(r, r_reg, pad=0.05)
    center_in(r, r_reg)
    scene.play(FadeIn(l, shift=LEFT), FadeIn(r, shift=RIGHT))
    clamp_inside_scene(scene, l)
    clamp_inside_scene(scene, r)


def build_equation(scene, title, latex_lines):
    t_reg = make_panel(scene, (2, 0), (3, 11))
    e_reg = make_panel(scene, (4, 0), (10, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    clamp_inside_scene(scene, t)
    objs = []
    for s in (latex_lines or []):
        try:
            objs.append(MathTex(s).scale(1.0))
        except Exception:
            objs.append(Text(s, font_size=36))
    rows = VGroup(*objs).arrange(DOWN, buff=0.6)
    scale_to_fit(rows, e_reg, pad=0.15)
    center_in(rows, e_reg)
    for r in rows:
        scene.play(Write(r))
        clamp_inside_scene(scene, r)
        scene.wait(0.3)


def build_plot(scene, title, expr, x_range=(-5, 5, 1), y_range=(-3, 3, 1)):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    p_reg = make_panel(scene, (3, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    clamp_inside_scene(scene, t)
    axes = Axes(x_range=x_range, y_range=y_range, axis_config={"include_numbers": True})
    scale_to_fit(axes, p_reg, pad=0.2)
    center_in(axes, p_reg)
    scene.play(Create(axes))
    clamp_inside_scene(scene, axes)
    allowed = {k: getattr(np, k) for k in [
        "sin", "cos", "tan", "exp", "log", "sqrt", "abs", "arctan", "arcsin", "arccos"
    ]}
    # Support constants, symbols, and numpy namespace
    allowed.update({
        "pi": np.pi, "e": np.e, "np": np,
        # default physical constants/symbols used in expressions
        "g": 9.8,  # gravity magnitude
        "a": 1.0,  # default acceleration
        "v0": 0.0, "k": 1.0, "b": 1.0, "m": 1.0, "c": 1.0
    })

    def normalize_expr(s: str) -> str:
        s = str(s or "").strip()
        # Take RHS of assignment if present
        if "=" in s:
            s = s.split("=")[-1]
        # caret power to python power
        s = s.replace("^", "**")
        # pi constant
        s = re.sub(r"\bpi\b", "np.pi", s)
        # unify variable name to x
        s = re.sub(r"\bt\b", "x", s)
        return s

    expr = normalize_expr(expr)
    def f(x):
        try:
            return eval(expr, {"__builtins__": {}}, dict(allowed, x=x))
        except Exception:
            # Fallback to a simple sine if expression is invalid
            return np.sin(x)
    graph = axes.plot(lambda x: f(x), x_range=(x_range[0], x_range[1]))
    grp = VGroup(axes, graph)
    scene.play(Create(graph))
    clamp_inside_scene(scene, grp)
    scene.wait(0.6)


def build_bar(scene, title, labels, values):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    c_reg = make_panel(scene, (3, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    clamp_inside_scene(scene, t)
    chart = BarChart(values=values, bar_names=labels, y_range=[0, max(values) * 1.2, max(1, int(max(values) // 5))])
    scale_to_fit(chart, c_reg, pad=0.2)
    center_in(chart, c_reg)
    scene.play(Create(chart))
    clamp_inside_scene(scene, chart)
    scene.wait(0.6)


def build_figure(scene, title, caption=""):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    f_reg = make_panel(scene, (3, 0), (9, 11))
    c_reg = make_panel(scene, (10, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    clamp_inside_scene(scene, t)
    plane = NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1])
    vec = Arrow(start=plane.c2p(0, 0), end=plane.c2p(2, 1), buff=0)
    grp = VGroup(plane, vec)
    scale_to_fit(grp, f_reg, pad=0.2)
    center_in(grp, f_reg)
    scene.play(Create(grp))
    clamp_inside_scene(scene, grp)
    if caption:
        cap = autowrap_to_width(caption, max_w=c_reg.width * 0.98, font_size=32, align=LEFT)
        scale_to_fit(cap, c_reg, pad=0.05)
        center_in(cap, c_reg)
        scene.play(FadeIn(cap, shift=UP))
        clamp_inside_scene(scene, cap)
    scene.wait(0.6)


# ---------- SCENE ----------
class Lesson(Scene):
    def construct(self):
        slides = [{"type": "title", "text": "Understanding Free Fall: A Special Case of Motion"}, {"type": "bullets", "title": "Objectives", "items": ["Understand free fall as motion with constant acceleration.", "Derive key equations for free-falling objects.", "Visualize velocity and distance relationships in free fall."]}, {"type": "two_column", "left_title": "Free Fall", "left": "Motion under gravitational acceleration only.", "right_title": "Gravitational Acceleration", "right": "Acceleration due to Earth's gravity, approx. -9.8 m/s²."}, {"type": "equation", "title": "Key Equations", "lines": ["t = \\sqrt{\\frac{2h}{g}}", "v = \\sqrt{2gh}"]}, {"type": "plot", "title": "Velocity vs. Time", "expr": "v = -9.8*t", "x_range": [0, 10, 0.1], "y_range": [-100, 0, 10]}, {"type": "plot", "title": "Distance vs. Time", "expr": "d = 0.5*-9.8*t**2", "x_range": [0, 10, 0.1], "y_range": [0, 500, 50]}, {"type": "bar", "title": "Gravitational Acceleration on Different Planets", "labels": ["Earth", "Moon", "Mars"], "values": [9.8, 1.6, 3.7]}, {"type": "figure", "title": "Free Fall Illustration", "caption": "An object in free fall experiences constant acceleration due to gravity."}, {"type": "bullets", "title": "Summary", "items": ["Free fall illustrates motion under constant gravity.", "Velocity and distance show linear and quadratic time relationships."]}]  # list[dict] injected by generator

        # Title slide if present
        if slides and slides[0].get("type") == "title":
            build_title(self, slides[0].get("text", ""))
            self.wait(0.6)
            slides = slides[1:]

        # Content slides
        for s in slides:
            t = s.get("type")
            if t == "bullets":
                build_bullets(self, s.get("title", ""), s.get("items", []))
            elif t == "two_column":
                build_two_col(
                    self,
                    s.get("left_title", ""),
                    s.get("left", ""),
                    s.get("right_title", ""),
                    s.get("right", ""),
                )
            elif t == "equation":
                build_equation(self, s.get("title", "Derivation"), s.get("lines", []))
            elif t == "plot":
                build_plot(
                    self,
                    s.get("title", "Plot"),
                    s.get("expr", "np.sin(x)"),
                    tuple(s.get("x_range", [-5, 5, 1])),
                    tuple(s.get("y_range", [-3, 3, 1])),
                )
            elif t == "bar":
                build_bar(self, s.get("title", "Chart"), s.get("labels", []), s.get("values", []))
            elif t == "figure":
                build_figure(self, s.get("title", "Figure"), s.get("caption", ""))
            else:
                # fallback bullet slide
                build_bullets(self, s.get("title", ""), s.get("items", []))
            self.wait(0.4)
            # clear for next slide
            self.play(*[FadeOut(m) for m in list(self.mobjects)])
            self.wait(0.2)
