from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class IntroductionToChemicalBonding(Scene):
    def construct(self):
        # Title
        title = Text("Introduction to Chemical Bonding", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Timeline of Key Historical Developments
        timeline = VGroup(
            Text("1897: Discovery of Electron", font_size=32),
            Text("1911: Rutherford's Nuclear Model", font_size=32),
            Text("1913: Bohr's Model", font_size=32),
            Text("1916: Kössell–Lewis Approach", font_size=32)
        ).arrange(DOWN, buff=0.5).to_edge(LEFT, buff=1)

        timeline_line = Line(timeline.get_top(), timeline.get_bottom(), color=BLUE)
        self.play(Create(timeline_line))
        for event in timeline:
            self.play(FadeIn(event, shift=RIGHT))
            self.wait(1)
        self.wait(2)
        self.play(FadeOut(timeline), FadeOut(timeline_line))

        # Bohr and Rutherford Models
        rutherford_model = VGroup(
            Circle(radius=1, color=WHITE),
            Dot(color=YELLOW).move_to(ORIGIN),
            Text("Nucleus", font_size=32).next_to(ORIGIN, DOWN)
        ).to_edge(LEFT, buff=1)

        bohr_model = VGroup(
            Circle(radius=1, color=WHITE),
            Circle(radius=1.5, color=WHITE),
            Dot(color=YELLOW).move_to(ORIGIN),
            Dot(color=RED).move_to([1.5, 0, 0]),
            Text("Electron", font_size=32).next_to([1.5, 0, 0], RIGHT),
            Text("Nucleus", font_size=32).next_to(ORIGIN, DOWN)
        ).to_edge(RIGHT, buff=1)

        self.play(Create(rutherford_model))
        self.wait(1)
        self.play(Transform(rutherford_model, bohr_model))
        self.wait(2)
        self.play(FadeOut(rutherford_model))

        # Ionic Bonding: Electron Transfer
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT * 2)
        electron = Dot(color=RED).move_to(sodium.get_center())
        arrow = Arrow(sodium.get_center(), chlorine.get_center(), buff=0.5)

        self.play(Create(sodium), Create(chlorine), Create(electron))
        self.wait(1)
        self.play(MoveAlongPath(electron, arrow), Create(arrow))
        self.wait(1)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron), FadeOut(arrow))

        # Covalent Bonding: Shared Electron Pairs
        oxygen = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        hydrogen1 = Circle(radius=0.3, color=GREEN).shift(RIGHT * 1.5 + UP * 0.5)
        hydrogen2 = Circle(radius=0.3, color=GREEN).shift(RIGHT * 1.5 + DOWN * 0.5)
        shared_electrons = VGroup(
            Dot(color=RED).move_to(oxygen.get_center() + RIGHT * 0.5),
            Dot(color=RED).move_to(hydrogen1.get_center() + LEFT * 0.3),
            Dot(color=RED).move_to(hydrogen2.get_center() + LEFT * 0.3)
        )

        self.play(Create(oxygen), Create(hydrogen1), Create(hydrogen2))
        self.wait(1)
        self.play(Create(shared_electrons))
        self.wait(2)
        self.play(FadeOut(oxygen), FadeOut(hydrogen1), FadeOut(hydrogen2), FadeOut(shared_electrons))

        # Octet Rule and Stability
        noble_gas = VGroup(
            Circle(radius=0.5, color=YELLOW),
            *[Dot(color=RED).move_to([0.5 * np.cos(theta), 0.5 * np.sin(theta), 0]) for theta in np.linspace(0, 2 * PI, 8, endpoint=False)]
        ).to_edge(LEFT, buff=1)

        other_element = VGroup(
            Circle(radius=0.5, color=BLUE),
            *[Dot(color=RED).move_to([0.5 * np.cos(theta), 0.5 * np.sin(theta), 0]) for theta in np.linspace(0, 2 * PI, 5, endpoint=False)]
        ).to_edge(RIGHT, buff=1)

        self.play(Create(noble_gas))
        self.wait(1)
        self.play(Transform(noble_gas, other_element))
        self.wait(2)
        self.play(FadeOut(noble_gas))

        # Conclusion and Summary
        summary = VGroup(
            Text("Summary", font_size=40),
            Text("1. Kössell–Lewis Approach", font_size=32),
            Text("2. Ionic and Covalent Bonds", font_size=32),
            Text("3. Octet Rule", font_size=32),
            Text("4. Lewis Dot Structures", font_size=32)
        ).arrange(DOWN, buff=0.5)

        self.play(Write(summary[0]))
        self.wait(1)
        for point in summary[1:]:
            self.play(FadeIn(point, shift=RIGHT))
            self.wait(1)
        self.wait(2)
        self.play(FadeOut(summary))