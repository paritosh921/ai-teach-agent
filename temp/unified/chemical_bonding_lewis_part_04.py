from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ContributionsOfGilbertNLewis(Scene):
    def construct(self):
        # Introduction to Covalent Bonding
        self.introduction_to_covalent_bonding()
        self.wait(2)

        # Lewis Dot Structures
        self.lewis_dot_structures()
        self.wait(2)

        # Example: Water Molecule
        self.example_water_molecule()
        self.wait(2)

        # Example: Methane Molecule
        self.example_methane_molecule()
        self.wait(2)

        # Comparing Ionic and Covalent Bonds
        self.comparing_ionic_and_covalent_bonds()
        self.wait(2)

        # Lewis Dot Structure: Ammonia (NH₃)
        self.lewis_dot_structure_ammonia()
        self.wait(2)

        # Lewis Dot Structure: Oxygen Molecule (O₂)
        self.lewis_dot_structure_oxygen()
        self.wait(2)

        # Lewis Dot Structure: Carbon Dioxide (CO₂)
        self.lewis_dot_structure_carbon_dioxide()
        self.wait(2)

        # Lewis Dot Structure: Ethanol (C₂H₅OH)
        self.lewis_dot_structure_ethanol()
        self.wait(2)

        # Lewis Dot Structure: Nitrogen Molecule (N₂)
        self.lewis_dot_structure_nitrogen()
        self.wait(2)

        # Lewis Dot Structure: Sulfur Hexafluoride (SF₆)
        self.lewis_dot_structure_sulfur_hexafluoride()
        self.wait(2)

        # Applications of Covalent Bonding
        self.applications_of_covalent_bonding()
        self.wait(2)

    def introduction_to_covalent_bonding(self):
        title = Text("Introduction to Covalent Bonding", font_size=36).to_edge(UP)
        atom1 = Circle(radius=0.5, color=BLUE).shift(LEFT)
        atom2 = Circle(radius=0.5, color=RED).shift(RIGHT)
        electron1 = Dot(color=YELLOW).move_to(atom1.get_center() + RIGHT * 0.5)
        electron2 = Dot(color=YELLOW).move_to(atom2.get_center() + LEFT * 0.5)

        self.play(Write(title))
        self.play(Create(atom1), Create(atom2), FadeIn(electron1), FadeIn(electron2))
        self.play(electron1.animate.move_to(atom1.get_center() + RIGHT * 0.2),
                  electron2.animate.move_to(atom2.get_center() + LEFT * 0.2))
        self.play(electron1.animate.move_to((atom1.get_center() + atom2.get_center()) / 2),
                  electron2.animate.move_to((atom1.get_center() + atom2.get_center()) / 2))
        self.wait()

    def lewis_dot_structures(self):
        title = Text("Lewis Dot Structures", font_size=36).to_edge(UP)
        atom = Circle(radius=0.5, color=GREEN)
        electrons = VGroup(*[Dot(color=YELLOW).move_to(atom.get_center() + RIGHT * 0.5 * i) for i in range(1, 5)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(atom))
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def example_water_molecule(self):
        title = Text("Example: Water Molecule (H₂O)", font_size=36).to_edge(UP)
        oxygen = Circle(radius=0.5, color=BLUE)
        hydrogen1 = Circle(radius=0.3, color=RED).shift(LEFT * 1.5)
        hydrogen2 = Circle(radius=0.3, color=RED).shift(RIGHT * 1.5)
        electrons = VGroup(*[Dot(color=YELLOW).move_to(oxygen.get_center() + RIGHT * 0.5 * i) for i in range(1, 5)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(oxygen), Create(hydrogen1), Create(hydrogen2))
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def example_methane_molecule(self):
        title = Text("Example: Methane Molecule (CH₄)", font_size=36).to_edge(UP)
        carbon = Circle(radius=0.5, color=GREEN)
        hydrogens = VGroup(*[Circle(radius=0.3, color=RED).shift(DOWN * 1.5).rotate_about_origin(i * PI / 2) for i in range(4)])
        electrons = VGroup(*[Dot(color=YELLOW).move_to(carbon.get_center() + RIGHT * 0.5 * i) for i in range(1, 5)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(carbon), *[Create(hydrogen) for hydrogen in hydrogens])
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def comparing_ionic_and_covalent_bonds(self):
        title = Text("Comparing Ionic and Covalent Bonds", font_size=36).to_edge(UP)
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT * 2)
        electron = Dot(color=YELLOW).move_to(sodium.get_center() + RIGHT * 0.5)

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(sodium), Create(chlorine), FadeIn(electron))
        self.play(electron.animate.move_to(chlorine.get_center() + LEFT * 0.5))
        self.wait()

    def lewis_dot_structure_ammonia(self):
        title = Text("Lewis Dot Structure: Ammonia (NH₃)", font_size=36).to_edge(UP)
        nitrogen = Circle(radius=0.5, color=BLUE)
        hydrogens = VGroup(*[Circle(radius=0.3, color=RED).shift(DOWN * 1.5).rotate_about_origin(i * PI / 3) for i in range(3)])
        electrons = VGroup(*[Dot(color=YELLOW).move_to(nitrogen.get_center() + RIGHT * 0.5 * i) for i in range(1, 3)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(nitrogen), *[Create(hydrogen) for hydrogen in hydrogens])
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def lewis_dot_structure_oxygen(self):
        title = Text("Lewis Dot Structure: Oxygen Molecule (O₂)", font_size=36).to_edge(UP)
        oxygen1 = Circle(radius=0.5, color=BLUE).shift(LEFT)
        oxygen2 = Circle(radius=0.5, color=BLUE).shift(RIGHT)
        electrons = VGroup(*[Dot(color=YELLOW).move_to(oxygen1.get_center() + RIGHT * 0.5 * i) for i in range(1, 3)] +
                           [Dot(color=YELLOW).move_to(oxygen2.get_center() + LEFT * 0.5 * i) for i in range(1, 3)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(oxygen1), Create(oxygen2))
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def lewis_dot_structure_carbon_dioxide(self):
        title = Text("Lewis Dot Structure: Carbon Dioxide (CO₂)", font_size=36).to_edge(UP)
        carbon = Circle(radius=0.5, color=GREEN)
        oxygens = VGroup(*[Circle(radius=0.5, color=BLUE).shift(LEFT * 2), Circle(radius=0.5, color=BLUE).shift(RIGHT * 2)])
        electrons = VGroup(*[Dot(color=YELLOW).move_to(carbon.get_center() + RIGHT * 0.5 * i) for i in range(1, 3)] +
                           [Dot(color=YELLOW).move_to(oxygens[0].get_center() + RIGHT * 0.5 * i) for i in range(1, 3)] +
                           [Dot(color=YELLOW).move_to(oxygens[1].get_center() + LEFT * 0.5 * i) for i in range(1, 3)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(carbon), *[Create(oxygen) for oxygen in oxygens])
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def lewis_dot_structure_ethanol(self):
        title = Text("Lewis Dot Structure: Ethanol (C₂H₅OH)", font_size=36).to_edge(UP)
        carbons = VGroup(*[Circle(radius=0.5, color=GREEN).shift(LEFT * i) for i in range(2)])
        oxygens = Circle(radius=0.5, color=BLUE).shift(RIGHT * 2)
        hydrogens = VGroup(*[Circle(radius=0.3, color=RED).shift(UP * 1.5).rotate_about_origin(i * PI / 3) for i in range(5)])
        electrons = VGroup(*[Dot(color=YELLOW).move_to(carbons[0].get_center() + RIGHT * 0.5 * i) for i in range(1, 3)] +
                           [Dot(color=YELLOW).move_to(carbons[1].get_center() + LEFT * 0.5 * i) for i in range(1, 3)] +
                           [Dot(color=YELLOW).move_to(oxygens.get_center() + LEFT * 0.5 * i) for i in range(1, 3)])

        self.play(Transform(self.mobjects[0], title))
        self.play(*[Create(carbon) for carbon in carbons], Create(oxygens), *[Create(hydrogen) for hydrogen in hydrogens])
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def lewis_dot_structure_nitrogen(self):
        title = Text("Lewis Dot Structure: Nitrogen Molecule (N₂)", font_size=36).to_edge(UP)
        nitrogen1 = Circle(radius=0.5, color=BLUE).shift(LEFT)
        nitrogen2 = Circle(radius=0.5, color=BLUE).shift(RIGHT)
        electrons = VGroup(*[Dot(color=YELLOW).move_to(nitrogen1.get_center() + RIGHT * 0.5 * i) for i in range(1, 4)] +
                           [Dot(color=YELLOW).move_to(nitrogen2.get_center() + LEFT * 0.5 * i) for i in range(1, 4)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(nitrogen1), Create(nitrogen2))
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def lewis_dot_structure_sulfur_hexafluoride(self):
        title = Text("Lewis Dot Structure: Sulfur Hexafluoride (SF₆)", font_size=36).to_edge(UP)
        sulfur = Circle(radius=0.5, color=GREEN)
        fluorines = VGroup(*[Circle(radius=0.3, color=BLUE).shift(DOWN * 1.5).rotate_about_origin(i * PI / 3) for i in range(6)])
        electrons = VGroup(*[Dot(color=YELLOW).move_to(sulfur.get_center() + RIGHT * 0.5 * i) for i in range(1, 7)])

        self.play(Transform(self.mobjects[0], title))
        self.play(Create(sulfur), *[Create(fluorine) for fluorine in fluorines])
        self.play(*[FadeIn(electron) for electron in electrons])
        self.wait()

    def applications_of_covalent_bonding(self):
        title = Text("Applications of Covalent Bonding", font_size=36).to_edge(UP)
        molecules = VGroup(*[Circle(radius=0.5, color=GREEN).shift(LEFT * i) for i in range(3)])
        reactions = VGroup(*[Arrow(molecules[i].get_center(), molecules[i + 1].get_center(), buff=0.1) for i in range(2)])

        self.play(Transform(self.mobjects[0], title))
        self.play(*[Create(molecule) for molecule in molecules])
        self.play(*[Create(reaction) for reaction in reactions])
        self.wait()