from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class KosselLewisLegacy(Scene):
    def construct(self):
        # Title
        title = Text("Conclusion: The Legacy of the Kössel–Lewis Approach", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Introduction to Kössel–Lewis Approach
        intro_title = Text("Introduction to Kössel–Lewis Approach", font_size=36)
        timeline = VGroup(
            Text("1900s", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("Kössel: Ionic Bonds", font_size=32),
            Arrow(LEFT, RIGHT),
            Text("Lewis: Covalent Bonds", font_size=32)
        ).arrange(RIGHT, buff=0.5)
        self.play(FadeIn(intro_title, shift=UP))
        self.play(Create(timeline))
        self.wait(2)
        self.play(FadeOut(intro_title, timeline))

        # Noble Gas Configurations
        noble_title = Text("Noble Gas Configurations", font_size=36)
        periodic_table = Table(
            [["He", "Ne", "Ar", "Kr", "Xe", "Rn"]],
            row_labels=[Text("Noble Gases", font_size=32)],
            include_outer_lines=True
        )
        self.play(FadeIn(noble_title, shift=UP))
        self.play(Create(periodic_table))
        self.wait(1)
        self.play(periodic_table.get_entries((1, 1)).animate.set_color(YELLOW))
        self.wait(2)
        self.play(FadeOut(noble_title, periodic_table))

        # Ionic Bonding Explained
        ionic_title = Text("Ionic Bonding Explained", font_size=36)
        sodium = Circle().set_fill(BLUE, opacity=0.5).scale(0.5)
        chlorine = Circle().set_fill(GREEN, opacity=0.5).scale(0.5)
        electron = Dot(color=RED).next_to(sodium, RIGHT, buff=0.1)
        arrow = Arrow(sodium.get_right(), chlorine.get_left(), buff=0.1)
        self.play(FadeIn(ionic_title, shift=UP))
        self.play(FadeIn(sodium, chlorine, electron))
        self.play(Create(arrow))
        self.wait(1)
        self.play(Transform(electron, electron.copy().next_to(chlorine, LEFT, buff=0.1)))
        self.wait(2)
        self.play(FadeOut(ionic_title, sodium, chlorine, electron, arrow))

        # Covalent Bonding Explained
        covalent_title = Text("Covalent Bonding Explained", font_size=36)
        oxygen = Circle().set_fill(ORANGE, opacity=0.5).scale(0.5)
        hydrogen1 = Circle().set_fill(WHITE, opacity=0.5).scale(0.3).next_to(oxygen, LEFT, buff=0.1)
        hydrogen2 = Circle().set_fill(WHITE, opacity=0.5).scale(0.3).next_to(oxygen, RIGHT, buff=0.1)
        bond1 = Line(hydrogen1.get_center(), oxygen.get_center())
        bond2 = Line(hydrogen2.get_center(), oxygen.get_center())
        self.play(FadeIn(covalent_title, shift=UP))
        self.play(FadeIn(oxygen, hydrogen1, hydrogen2))
        self.play(Create(bond1), Create(bond2))
        self.wait(2)
        self.play(FadeOut(covalent_title, oxygen, hydrogen1, hydrogen2, bond1, bond2))

        # Limitations and Legacy
        legacy_title = Text("Limitations and Legacy", font_size=36)
        limitations = VGroup(
            Text("Exceptions to Octet Rule:", font_size=32),
            Text("- Expanded octets", font_size=32),
            Text("- Incomplete octets", font_size=32),
            Text("- Odd-electron molecules", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)
        self.play(FadeIn(legacy_title, shift=UP))
        self.play(Write(limitations))
        self.wait(2)
        self.play(FadeOut(legacy_title, limitations))

        # Summary and Reflection
        summary_title = Text("Summary and Reflection", font_size=36)
        summary_points = VGroup(
            Text("Kössel–Lewis Approach Impact:", font_size=32),
            Text("- Foundation for modern bonding theories", font_size=32),
            Text("- Simplified understanding of chemical stability", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)
        self.play(FadeIn(summary_title, shift=UP))
        self.play(Write(summary_points))
        self.wait(2)
        self.play(FadeOut(summary_title, summary_points))

        # End Scene
        self.wait(1)