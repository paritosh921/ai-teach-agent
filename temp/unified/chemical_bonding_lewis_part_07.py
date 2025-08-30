from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class CovalentBonding(Scene):
    def construct(self):
        # Introduction to Covalent Bonding
        self.intro_covalent_bonding()
        self.wait(2)

        # Understanding Electron Sharing
        self.understanding_electron_sharing()
        self.wait(2)

        # Types of Covalent Bonds
        self.types_of_covalent_bonds()
        self.wait(2)

        # Single Covalent Bonds
        self.single_covalent_bonds()
        self.wait(2)

        # Double Covalent Bonds
        self.double_covalent_bonds()
        self.wait(2)

        # Triple Covalent Bonds
        self.triple_covalent_bonds()
        self.wait(2)

        # Properties of Covalent Compounds
        self.properties_of_covalent_compounds()
        self.wait(2)

        # Melting and Boiling Points
        self.melting_and_boiling_points()
        self.wait(2)

        # Network Solids
        self.network_solids()
        self.wait(2)

        # Lewis Structures in Organic Chemistry
        self.lewis_structures_in_organic_chemistry()
        self.wait(2)

        # Review of Key Concepts
        self.review_of_key_concepts()
        self.wait(2)

        # Conclusion and Applications
        self.conclusion_and_applications()
        self.wait(2)

    def intro_covalent_bonding(self):
        title = Text("Introduction to Covalent Bonding", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Hydrogen atoms and electron sharing
        hydrogen1 = Dot(color=BLUE).shift(LEFT)
        hydrogen2 = Dot(color=BLUE).shift(RIGHT)
        electron1 = Dot(color=YELLOW).next_to(hydrogen1, RIGHT, buff=0.1)
        electron2 = Dot(color=YELLOW).next_to(hydrogen2, LEFT, buff=0.1)

        self.play(FadeIn(hydrogen1, hydrogen2, electron1, electron2))
        self.play(hydrogen1.animate.shift(RIGHT * 0.5), hydrogen2.animate.shift(LEFT * 0.5))
        self.play(electron1.animate.move_to(electron2.get_center()), FadeOut(electron2))
        bond = Line(hydrogen1.get_center(), hydrogen2.get_center(), color=WHITE)
        self.play(Create(bond))
        self.wait(1)
        self.play(FadeOut(hydrogen1, hydrogen2, electron1, bond))

    def understanding_electron_sharing(self):
        number_line = NumberLine(x_range=[-3, 3, 1], length=6, include_numbers=True)
        electron1 = Dot(color=YELLOW).move_to(number_line.n2p(-1))
        electron2 = Dot(color=YELLOW).move_to(number_line.n2p(1))

        self.play(Create(number_line), FadeIn(electron1, electron2))
        self.play(electron1.animate.move_to(number_line.n2p(0)), electron2.animate.move_to(number_line.n2p(0)))
        self.play(Indicate(electron1, color=GREEN))
        self.wait(1)
        self.play(FadeOut(number_line, electron1, electron2))

    def types_of_covalent_bonds(self):
        h2_structure = MathTex("H-H", font_size=48)
        o2_structure = MathTex("O=O", font_size=48)
        n2_structure = MathTex("N\\equiv N", font_size=48)

        self.play(Write(h2_structure))
        self.wait(1)
        self.play(Transform(h2_structure, o2_structure))
        self.wait(1)
        self.play(Transform(h2_structure, n2_structure))
        self.wait(1)
        self.play(FadeOut(h2_structure))

    def single_covalent_bonds(self):
        single_bond = MathTex("H-H", font_size=48)
        strength_indicator = Text("Strength: Weak", font_size=32).next_to(single_bond, DOWN)

        self.play(Write(single_bond))
        self.play(Write(strength_indicator))
        self.wait(1)
        self.play(FadeOut(single_bond, strength_indicator))

    def double_covalent_bonds(self):
        double_bond = MathTex("O=O", font_size=48)
        comparison_chart = Text("Double Bond vs Single Bond", font_size=32).next_to(double_bond, DOWN)

        self.play(Write(double_bond))
        self.play(Write(comparison_chart))
        self.wait(1)
        self.play(FadeOut(double_bond, comparison_chart))

    def triple_covalent_bonds(self):
        triple_bond = MathTex("N\\equiv N", font_size=48)
        implication_notes = Text("Triple Bond: Strongest", font_size=32).next_to(triple_bond, DOWN)

        self.play(Write(triple_bond))
        self.play(Write(implication_notes))
        self.wait(1)
        self.play(FadeOut(triple_bond, implication_notes))

    def properties_of_covalent_compounds(self):
        molecule_examples = VGroup(
            Text("H₂O", font_size=32),
            Text("CO₂", font_size=32),
            Text("CH₄", font_size=32)
        ).arrange(RIGHT, buff=1)
        network_solid_example = Text("Diamond", font_size=32).next_to(molecule_examples, DOWN, buff=1)

        self.play(FadeIn(molecule_examples))
        self.play(FadeIn(network_solid_example))
        self.wait(1)
        self.play(FadeOut(molecule_examples, network_solid_example))

    def melting_and_boiling_points(self):
        axes = Axes(x_range=[0, 5, 1], y_range=[0, 100, 20], axis_config={"include_numbers": True})
        melting_points = VGroup(
            Dot(axes.c2p(1, 10), color=RED),
            Dot(axes.c2p(2, 20), color=RED),
            Dot(axes.c2p(3, 30), color=RED)
        )
        boiling_points = VGroup(
            Dot(axes.c2p(1, 50), color=BLUE),
            Dot(axes.c2p(2, 60), color=BLUE),
            Dot(axes.c2p(3, 70), color=BLUE)
        )

        self.play(Create(axes))
        self.play(FadeIn(melting_points, boiling_points))
        self.play(Indicate(melting_points, color=GREEN))
        self.wait(1)
        self.play(FadeOut(axes, melting_points, boiling_points))

    def network_solids(self):
        diamond_structure = Text("Diamond Structure", font_size=32)
        high_melting_point_indicator = Text("High Melting Point", font_size=32).next_to(diamond_structure, DOWN)

        self.play(Write(diamond_structure))
        self.play(Write(high_melting_point_indicator))
        self.wait(1)
        self.play(FadeOut(diamond_structure, high_melting_point_indicator))

    def lewis_structures_in_organic_chemistry(self):
        organic_molecule = Text("CH₄", font_size=48)
        lewis_structure_organic = MathTex("H-\\overset{\\cdot\\cdot}{C}-H", font_size=48).next_to(organic_molecule, DOWN)

        self.play(Write(organic_molecule))
        self.play(Write(lewis_structure_organic))
        self.wait(1)
        self.play(FadeOut(organic_molecule, lewis_structure_organic))

    def review_of_key_concepts(self):
        summary_chart = Text("Summary of Covalent Bonds", font_size=32)
        key_concepts_list = VGroup(
            Text("Single Bond", font_size=32),
            Text("Double Bond", font_size=32),
            Text("Triple Bond", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)

        self.play(Write(summary_chart))
        self.play(FadeIn(key_concepts_list))
        self.wait(1)
        self.play(FadeOut(summary_chart, key_concepts_list))

    def conclusion_and_applications(self):
        applications_diagram = Text("Applications in Chemistry", font_size=32)
        future_implications = Text("Future Implications", font_size=32).next_to(applications_diagram, DOWN)

        self.play(Write(applications_diagram))
        self.play(Write(future_implications))
        self.wait(1)
        self.play(FadeOut(applications_diagram, future_implications))