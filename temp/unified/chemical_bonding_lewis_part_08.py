from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class OctetRuleScene(Scene):
    def construct(self):
        # Title
        title = Text("The Octet Rule: Central Principle", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Introduction to the Octet Rule
        self.introduction_to_octet_rule()

        # Ionic Bonding Example
        self.ionic_bonding_example()

        # Covalent Bonding Example
        self.covalent_bonding_example()

        # Limitations of the Octet Rule
        self.limitations_of_octet_rule()

        # Lewis Structures Introduction
        self.lewis_structures_introduction()

        # Lewis Structures for Polyatomic Ions
        self.lewis_structures_polyatomic_ions()

        # Expanded Octets
        self.expanded_octets()

        # Incomplete Octets
        self.incomplete_octets()

        # Odd-Electron Species
        self.odd_electron_species()

        # Octet Rule in Chemical Reactions
        self.octet_rule_in_chemical_reactions()

        # Real-World Applications
        self.real_world_applications()

        # Conclusion and Summary
        self.conclusion_and_summary()

    def introduction_to_octet_rule(self):
        noble_gas = Circle(radius=1, color=BLUE)
        electrons = VGroup(*[Dot(point=noble_gas.point_at_angle(angle), color=YELLOW) for angle in np.linspace(0, TAU, 8, endpoint=False)])
        self.play(Create(noble_gas), FadeIn(electrons))
        self.wait(2)
        self.play(FadeOut(noble_gas), FadeOut(electrons))

    def ionic_bonding_example(self):
        sodium = Circle(radius=0.5, color=RED).shift(LEFT)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT)
        arrow = Arrow(sodium.get_right(), chlorine.get_left(), buff=0.1)
        self.play(Create(sodium), Create(chlorine), Create(arrow))
        self.wait(2)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(arrow))

    def covalent_bonding_example(self):
        carbon = Circle(radius=0.5, color=BLUE)
        hydrogens = VGroup(*[Circle(radius=0.3, color=WHITE).shift(1.5 * direction) for direction in [UP, DOWN, LEFT, RIGHT]])
        bonds = VGroup(*[Line(carbon.get_center(), hydrogen.get_center()) for hydrogen in hydrogens])
        self.play(Create(carbon), Create(hydrogens), Create(bonds))
        self.wait(2)
        self.play(FadeOut(carbon), FadeOut(hydrogens), FadeOut(bonds))

    def limitations_of_octet_rule(self):
        sf6 = Text("SF₆", font_size=36).shift(UP)
        no = Text("NO", font_size=36).shift(DOWN)
        self.play(Write(sf6), Write(no))
        self.wait(2)
        self.play(FadeOut(sf6), FadeOut(no))

    def lewis_structures_introduction(self):
        oxygen = Circle(radius=0.5, color=BLUE)
        hydrogens = VGroup(*[Circle(radius=0.3, color=WHITE).shift(1.5 * direction) for direction in [LEFT, RIGHT]])
        bonds = VGroup(*[Line(oxygen.get_center(), hydrogen.get_center()) for hydrogen in hydrogens])
        self.play(Create(oxygen), Create(hydrogens), Create(bonds))
        self.wait(2)
        self.play(FadeOut(oxygen), FadeOut(hydrogens), FadeOut(bonds))

    def lewis_structures_polyatomic_ions(self):
        sulfate = Text("SO₄²⁻", font_size=36)
        self.play(Write(sulfate))
        self.wait(2)
        self.play(FadeOut(sulfate))

    def expanded_octets(self):
        pf5 = Text("PF₅", font_size=36)
        self.play(Write(pf5))
        self.wait(2)
        self.play(FadeOut(pf5))

    def incomplete_octets(self):
        bf3 = Text("BF₃", font_size=36)
        self.play(Write(bf3))
        self.wait(2)
        self.play(FadeOut(bf3))

    def odd_electron_species(self):
        no = Text("NO", font_size=36)
        self.play(Write(no))
        self.wait(2)
        self.play(FadeOut(no))

    def octet_rule_in_chemical_reactions(self):
        reaction = Text("H₂ + Cl₂ → 2HCl", font_size=36)
        self.play(Write(reaction))
        self.wait(2)
        self.play(FadeOut(reaction))

    def real_world_applications(self):
        applications = Text("Plastics, Metals, etc.", font_size=36)
        self.play(Write(applications))
        self.wait(2)
        self.play(FadeOut(applications))

    def conclusion_and_summary(self):
        summary = Text("Octet Rule: Key Points", font_size=36)
        self.play(Write(summary))
        self.wait(2)
        self.play(FadeOut(summary))