from manim import *
import numpy as np

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
    return best


def build_bullets(scene, title, items, min_font=30):
    t_reg = make_panel(scene, (2, 0), (3, 11))
    b_reg = make_panel(scene, (4, 0), (11, 11))
    # Title
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))

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


def build_equation(scene, title, latex_lines):
    t_reg = make_panel(scene, (2, 0), (3, 11))
    e_reg = make_panel(scene, (4, 0), (10, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    rows = VGroup(*[MathTex(s).scale(1.0) for s in (latex_lines or [])]).arrange(DOWN, buff=0.6)
    scale_to_fit(rows, e_reg, pad=0.15)
    center_in(rows, e_reg)
    for r in rows:
        scene.play(Write(r))
        scene.wait(0.3)


def build_plot(scene, title, expr, x_range=(-5, 5, 1), y_range=(-3, 3, 1)):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    p_reg = make_panel(scene, (3, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    axes = Axes(x_range=x_range, y_range=y_range, axis_config={"include_numbers": True})
    scale_to_fit(axes, p_reg, pad=0.2)
    center_in(axes, p_reg)
    scene.play(Create(axes))
    allowed = {k: getattr(np, k) for k in [
        "sin", "cos", "tan", "exp", "log", "sqrt", "abs", "arctan", "arcsin", "arccos"
    ]}
    def f(x):
        return eval(expr, {"__builtins__": {}}, dict(allowed, x=x))
    graph = axes.plot(lambda x: f(x), x_range=(x_range[0], x_range[1]))
    scene.play(Create(graph))
    scene.wait(0.6)


def build_bar(scene, title, labels, values):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    c_reg = make_panel(scene, (3, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    chart = BarChart(values=values, bar_names=labels, y_range=[0, max(values) * 1.2, max(1, int(max(values) // 5))])
    scale_to_fit(chart, c_reg, pad=0.2)
    center_in(chart, c_reg)
    scene.play(Create(chart))
    scene.wait(0.6)


def build_figure(scene, title, caption=""):
    t_reg = make_panel(scene, (1, 0), (2, 11))
    f_reg = make_panel(scene, (3, 0), (9, 11))
    c_reg = make_panel(scene, (10, 0), (11, 11))
    t = autowrap_to_width(title, max_w=t_reg.width * 0.98, font_size=46)
    scale_to_fit(t, t_reg, pad=0.05)
    center_in(t, t_reg)
    scene.play(Write(t))
    plane = NumberPlane(x_range=[-4, 4, 1], y_range=[-3, 3, 1])
    vec = Arrow(start=plane.c2p(0, 0), end=plane.c2p(2, 1), buff=0)
    grp = VGroup(plane, vec)
    scale_to_fit(grp, f_reg, pad=0.2)
    center_in(grp, f_reg)
    scene.play(Create(grp))
    if caption:
        cap = autowrap_to_width(caption, max_w=c_reg.width * 0.98, font_size=32, align=LEFT)
        scale_to_fit(cap, c_reg, pad=0.05)
        center_in(cap, c_reg)
        scene.play(FadeIn(cap, shift=UP))
    scene.wait(0.6)


# ---------- SCENE ----------
class Lesson(Scene):
    def construct(self):
        slides = [{"type": "title", "text": "Introduction to Motion: Position, Velocity, and Acceleration"}, {"type": "bullets", "title": "Objectives", "items": ["Define and differentiate between position, velocity, and acceleration.", "Understand and calculate average and instantaneous velocity.", "Visualize motion through graphs and diagrams."]}, {"type": "two_column", "left_title": "Position", "left": "The location of an object relative to a reference point, which can be positive or negative.", "right_title": "Velocity", "right": "The rate of change of position with respect to time, indicating how fast an object moves and in which direction."}, {"type": "two_column", "left_title": "Acceleration", "left": "The rate of change of velocity with respect to time, showing how quickly an object speeds up or slows down.", "right_title": "Key Concept", "right": "Understanding acceleration helps in predicting motion."}, {"type": "equation", "title": "Average Velocity Formula", "lines": ["v_{avg} = \\frac{\\Delta x}{\\Delta t}"]}, {"type": "equation", "title": "Instantaneous Velocity Formula", "lines": ["v_{inst} = \\frac{dx}{dt}"]}, {"type": "plot", "title": "Velocity vs. Time Graph", "expr": "v = 3*t + 2", "x_range": [0, 10, 0.1], "y_range": [0, 40, 1]}, {"type": "bar", "title": "Comparison of Concepts", "labels": ["Position", "Velocity", "Acceleration"], "values": [1, 2, 3]}, {"type": "figure", "title": "Motion Diagram", "caption": "A diagram illustrating the motion of an object over time."}, {"type": "bullets", "title": "Summary", "items": ["Position, velocity, and acceleration are foundational concepts in physics.", "Understanding these concepts helps analyze and predict motion."]}]  # list[dict] injected by generator

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