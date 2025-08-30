from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ModernEvaluationOfKosselLewis(Scene):
    def construct(self):
        # Introduction to Kössel–Lewis Approach
        self.introduction_to_kossel_lewis()
        self.wait(2)

        # Core Principles of Kössel–Lewis
        self.core_principles_of_kossel_lewis()
        self.wait(2)

        # Worked Example: Water Molecule
        self.worked_example_water_molecule()
        self.wait(2)

        # Worked Example: Sodium Chloride Formation
        self.worked_example_sodium_chloride()
        self.wait(2)

        # Octet Rule in Detail
        self.octet_rule_in_detail()
        self.wait(2)

        # Lewis Structures: Basics
        self.lewis_structures_basics()
        self.wait(2)

        # Lewis Structures: Complex Molecules
        self.lewis_structures_complex_molecules()
        self.wait(2)

        # Limitations of Kössel–Lewis
        self.limitations_of_kossel_lewis()
        self.wait(2)

        # Extensions to Modern Theories
        self.extensions_to_modern_theories()
        self.wait(2)

        # Applications in Chemical Education
        self.applications_in_chemical_education()
        self.wait(2)

        # Applications in Molecular Design
        self.applications_in_molecular_design()
        self.wait(2)

        # Conclusion and Summary
        self.conclusion_and_summary()
        self.wait(2)

    def introduction_to_kossel_lewis(self):
        title = Text("Introduction to Kössel–Lewis Approach", font_size=36).to_edge(UP)
        timeline = Line(LEFT, RIGHT).scale(3)
        dot1 = Dot(timeline.get_start())
        dot2 = Dot(timeline.get_end())
        label1 = Text("Early 20th Century", font_size=32).next_to(dot1, DOWN)
        label2 = Text("Kössel–Lewis", font_size=32).next_to(dot2, DOWN)
        self.play(FadeIn(title), Create(timeline), FadeIn(dot1, dot2), Write(label1), Write(label2))

    def core_principles_of_kossel_lewis(self):
        title = Text("Core Principles of Kössel–Lewis", font_size=36).to_edge(UP)
        octet_rule = Text("Octet Rule", font_size=32).shift(UP)
        electron_pairs = Text("Electron Pairs", font_size=32).shift(DOWN)
        self.play(Transform(title, title.copy()), FadeIn(octet_rule, electron_pairs))

    def worked_example_water_molecule(self):
        title = Text("Worked Example: Water Molecule", font_size=36).to_edge(UP)
        h_atom = Circle(radius=0.5, color=BLUE).shift(LEFT)
        o_atom = Circle(radius=0.7, color=RED)
        h2_atom = Circle(radius=0.5, color=BLUE).shift(RIGHT)
        arrow1 = Arrow(h_atom.get_right(), o_atom.get_left(), buff=0.1)
        arrow2 = Arrow(h2_atom.get_left(), o_atom.get_right(), buff=0.1)
        self.play(Transform(title, title.copy()), FadeIn(h_atom, o_atom, h2_atom), Create(arrow1), Create(arrow2))

    def worked_example_sodium_chloride(self):
        title = Text("Worked Example: Sodium Chloride Formation", font_size=36).to_edge(UP)
        na_atom = Circle(radius=0.5, color=YELLOW).shift(LEFT)
        cl_atom = Circle(radius=0.7, color=GREEN).shift(RIGHT)
        electron_transfer = Arrow(na_atom.get_right(), cl_atom.get_left(), buff=0.1)
        self.play(Transform(title, title.copy()), FadeIn(na_atom, cl_atom), Create(electron_transfer))

    def octet_rule_in_detail(self):
        title = Text("Octet Rule in Detail", font_size=36).to_edge(UP)
        atoms = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Circle(radius=0.5, color=RED),
            Circle(radius=0.5, color=GREEN).shift(RIGHT * 2)
        )
        self.play(Transform(title, title.copy()), FadeIn(atoms))

    def lewis_structures_basics(self):
        title = Text("Lewis Structures: Basics", font_size=36).to_edge(UP)
        h2_structure = Text("H₂: H-H", font_size=32).shift(UP)
        o2_structure = Text("O₂: O=O", font_size=32).shift(DOWN)
        self.play(Transform(title, title.copy()), Write(h2_structure), Write(o2_structure))

    def lewis_structures_complex_molecules(self):
        title = Text("Lewis Structures: Complex Molecules", font_size=36).to_edge(UP)
        ch4_structure = Text("CH₄: H-C-H", font_size=32).shift(UP)
        nh3_structure = Text("NH₃: H-N-H", font_size=32).shift(DOWN)
        self.play(Transform(title, title.copy()), Write(ch4_structure), Write(nh3_structure))

    def limitations_of_kossel_lewis(self):
        title = Text("Limitations of Kössel–Lewis", font_size=36).to_edge(UP)
        limitations = Text("Doesn't explain all bonding scenarios", font_size=32)
        self.play(Transform(title, title.copy()), FadeIn(limitations))

    def extensions_to_modern_theories(self):
        title = Text("Extensions to Modern Theories", font_size=36).to_edge(UP)
        vbt = Text("Valence Bond Theory", font_size=32).shift(UP)
        mot = Text("Molecular Orbital Theory", font_size=32).shift(DOWN)
        self.play(Transform(title, title.copy()), FadeIn(vbt, mot))

    def applications_in_chemical_education(self):
        title = Text("Applications in Chemical Education", font_size=36).to_edge(UP)
        applications = Text("Teaching basic chemistry concepts", font_size=32)
        self.play(Transform(title, title.copy()), Write(applications))

    def applications_in_molecular_design(self):
        title = Text("Applications in Molecular Design", font_size=36).to_edge(UP)
        design = Text("Design of molecules for pharmaceuticals", font_size=32)
        self.play(Transform(title, title.copy()), Write(design))

    def conclusion_and_summary(self):
        title = Text("Conclusion and Summary", font_size=36).to_edge(UP)
        summary = Text("Impact and enduring relevance of Kössel–Lewis", font_size=32)
        self.play(Transform(title, title.copy()), Write(summary))