from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class KosselLewisApproach(Scene):
    def construct(self):
        # Introduction to Kössel–Lewis Approach
        title = Text("Kössel–Lewis Approach", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Periodic Table with Valence Electrons
        periodic_table = NumberPlane(x_range=[0, 10, 1], y_range=[0, 10, 1], background_line_style={"stroke_opacity": 0.5})
        electron_clouds = VGroup(
            Dot(point=periodic_table.c2p(1, 1), color=YELLOW),
            Dot(point=periodic_table.c2p(2, 1), color=YELLOW),
            Dot(point=periodic_table.c2p(3, 1), color=YELLOW),
        )
        self.play(Create(periodic_table), FadeIn(electron_clouds))
        self.wait(1)

        # Highlight Valence Electrons
        self.play(electron_clouds.animate.set_color(RED))
        self.wait(1)

        # Understanding Ionic Bonds
        na = Dot(color=BLUE).shift(LEFT * 2)
        cl = Dot(color=GREEN).shift(RIGHT * 2)
        arrow = Arrow(na.get_center(), cl.get_center(), buff=0.1)
        self.play(FadeIn(na), FadeIn(cl), GrowArrow(arrow))
        self.wait(1)

        # Animate Electron Transfer
        electron = Dot(color=YELLOW).move_to(na.get_center())
        self.play(electron.animate.move_to(cl.get_center()))
        self.wait(1)

        # Understanding Covalent Bonds
        h1 = Dot(color=BLUE).shift(LEFT * 2)
        o = Dot(color=GREEN)
        h2 = Dot(color=BLUE).shift(RIGHT * 2)
        line1 = Line(h1.get_center(), o.get_center())
        line2 = Line(o.get_center(), h2.get_center())
        self.play(FadeIn(h1), FadeIn(o), FadeIn(h2), Create(line1), Create(line2))
        self.wait(1)

        # Lewis Structures and the Octet Rule
        co2_structure = VGroup(
            Text("CO₂", font_size=32),
            Dot().shift(LEFT * 1.5),
            Dot().shift(RIGHT * 1.5),
            Dot().shift(UP * 0.5),
            Dot().shift(DOWN * 0.5)
        ).arrange(RIGHT, buff=0.5)
        self.play(Write(co2_structure))
        self.wait(1)

        # Strengths of the Kössel–Lewis Approach
        strengths_table = Table(
            [["Ionic Compounds", "Covalent Compounds"],
             ["NaCl", "H₂O"]],
            col_labels=[Text("Type"), Text("Example")],
            include_outer_lines=True
        ).scale(0.5).to_edge(DOWN)
        self.play(Create(strengths_table))
        self.wait(1)

        # Weaknesses of the Kössel–Lewis Approach
        resonance_example = VGroup(
            Text("Resonance", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("Transition Metals", font_size=32)
        ).arrange(RIGHT, buff=0.5).to_edge(UP)
        self.play(Write(resonance_example))
        self.wait(1)

        # Applications in Modern Chemistry
        timeline = VGroup(
            Text("Kössel–Lewis", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("VSEPR", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("VBT", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("MOT", font_size=32)
        ).arrange(RIGHT, buff=0.5).to_edge(DOWN)
        self.play(Write(timeline))
        self.wait(1)

        # Conclusion
        conclusion = Text("Enduring Significance", font_size=36).to_edge(UP)
        self.play(Write(conclusion))
        self.wait(1)

        # Review and Reflection
        questions = VGroup(
            Text("Reflect on Kössel–Lewis:", font_size=32),
            Text("1. What are its strengths?", font_size=28),
            Text("2. What are its limitations?", font_size=28),
            Text("3. How does it impact modern chemistry?", font_size=28)
        ).arrange(DOWN, buff=0.3).to_edge(DOWN)
        self.play(FadeIn(questions))
        self.wait(2)

        # End Scene
        self.play(FadeOut(VGroup(title, periodic_table, electron_clouds, na, cl, arrow, electron, h1, o, h2, line1, line2, co2_structure, strengths_table, resonance_example, timeline, conclusion, questions)))
        self.wait(1)