from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class KosselLewisApproach(Scene):
    def construct(self):
        # Title
        title = Text("Core Postulates of the Kössel–Lewis Approach", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Introduction to Noble Gas Configurations
        self.intro_noble_gas_configurations()

        # Understanding the Octet Rule
        self.understanding_octet_rule()

        # The Duet Rule
        self.the_duet_rule()

        # Ionic Bonding
        self.ionic_bonding()

        # Formation of NaCl
        self.formation_of_nacl()

        # Covalent Bonding
        self.covalent_bonding()

        # Formation of H2O
        self.formation_of_h2o()

        # Lewis Dot Symbols
        self.lewis_dot_symbols()

        # Visualizing Electron Shells
        self.visualizing_electron_shells()

        # Comparing Ionic and Covalent Bonds
        self.comparing_ionic_and_covalent_bonds()

        # Applications in Chemical Reactions
        self.applications_in_chemical_reactions()

        # Applications in Material Science
        self.applications_in_material_science()

    def intro_noble_gas_configurations(self):
        noble_gases = VGroup(
            Circle(radius=1, color=BLUE).shift(LEFT * 3),
            Circle(radius=1, color=BLUE).shift(RIGHT * 3)
        )
        dots = VGroup(
            *[Dot(point=pos, color=YELLOW) for pos in [LEFT * 3 + UP, LEFT * 3 + DOWN, RIGHT * 3 + UP, RIGHT * 3 + DOWN]]
        )
        self.play(Create(noble_gases), FadeIn(dots))
        self.wait(1)
        self.play(dots.animate.shift(UP * 0.5), noble_gases.animate.set_color(GREEN))
        self.wait(1)
        self.play(FadeOut(noble_gases), FadeOut(dots))

    def understanding_octet_rule(self):
        number_line = NumberLine(x_range=[0, 9, 1], length=8, include_numbers=True)
        self.play(Create(number_line))
        dots = VGroup(*[Dot(number_line.n2p(i), color=YELLOW) for i in range(1, 9)])
        self.play(FadeIn(dots))
        self.wait(1)
        self.play(dots[7].animate.set_color(RED))
        self.wait(1)
        self.play(FadeOut(number_line), FadeOut(dots))

    def the_duet_rule(self):
        hydrogen = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        helium = Circle(radius=0.5, color=BLUE).shift(RIGHT * 2)
        dots = VGroup(
            Dot(hydrogen.get_center() + UP * 0.5, color=YELLOW),
            Dot(helium.get_center() + UP * 0.5, color=YELLOW)
        )
        self.play(Create(hydrogen), Create(helium), FadeIn(dots))
        self.wait(1)
        self.play(dots.animate.shift(DOWN * 0.5), hydrogen.animate.set_color(GREEN), helium.animate.set_color(GREEN))
        self.wait(1)
        self.play(FadeOut(hydrogen), FadeOut(helium), FadeOut(dots))

    def ionic_bonding(self):
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 3)
        chlorine = Circle(radius=0.5, color=BLUE).shift(RIGHT * 3)
        electron = Dot(sodium.get_center() + UP * 0.5, color=YELLOW)
        arrow = Arrow(start=sodium.get_center(), end=chlorine.get_center(), buff=0.5)
        self.play(Create(sodium), Create(chlorine), FadeIn(electron))
        self.wait(1)
        self.play(Create(arrow), electron.animate.move_to(chlorine.get_center() + UP * 0.5))
        self.wait(1)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron), FadeOut(arrow))

    def formation_of_nacl(self):
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 3)
        chlorine = Circle(radius=0.5, color=BLUE).shift(RIGHT * 3)
        electron = Dot(sodium.get_center() + UP * 0.5, color=YELLOW)
        arrow = Arrow(start=sodium.get_center(), end=chlorine.get_center(), buff=0.5)
        self.play(Create(sodium), Create(chlorine), FadeIn(electron))
        self.wait(1)
        self.play(Create(arrow), electron.animate.move_to(chlorine.get_center() + UP * 0.5))
        self.wait(1)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron), FadeOut(arrow))

    def covalent_bonding(self):
        oxygen = Circle(radius=0.5, color=BLUE)
        hydrogen1 = Circle(radius=0.3, color=BLUE).shift(LEFT * 2)
        hydrogen2 = Circle(radius=0.3, color=BLUE).shift(RIGHT * 2)
        shared_electrons = VGroup(
            Dot(oxygen.get_center() + LEFT * 0.5, color=YELLOW),
            Dot(oxygen.get_center() + RIGHT * 0.5, color=YELLOW)
        )
        self.play(Create(oxygen), Create(hydrogen1), Create(hydrogen2), FadeIn(shared_electrons))
        self.wait(1)
        self.play(shared_electrons.animate.shift(UP * 0.5), oxygen.animate.set_color(GREEN))
        self.wait(1)
        self.play(FadeOut(oxygen), FadeOut(hydrogen1), FadeOut(hydrogen2), FadeOut(shared_electrons))

    def formation_of_h2o(self):
        oxygen = Circle(radius=0.5, color=BLUE)
        hydrogen1 = Circle(radius=0.3, color=BLUE).shift(LEFT * 2)
        hydrogen2 = Circle(radius=0.3, color=BLUE).shift(RIGHT * 2)
        shared_electrons = VGroup(
            Dot(oxygen.get_center() + LEFT * 0.5, color=YELLOW),
            Dot(oxygen.get_center() + RIGHT * 0.5, color=YELLOW)
        )
        self.play(Create(oxygen), Create(hydrogen1), Create(hydrogen2), FadeIn(shared_electrons))
        self.wait(1)
        self.play(shared_electrons.animate.shift(UP * 0.5), oxygen.animate.set_color(GREEN))
        self.wait(1)
        self.play(FadeOut(oxygen), FadeOut(hydrogen1), FadeOut(hydrogen2), FadeOut(shared_electrons))

    def lewis_dot_symbols(self):
        elements = VGroup(
            Text("H", font_size=32).shift(LEFT * 3),
            Text("O", font_size=32),
            Text("Cl", font_size=32).shift(RIGHT * 3)
        )
        dots = VGroup(
            Dot(elements[0].get_center() + UP * 0.5, color=YELLOW),
            Dot(elements[1].get_center() + UP * 0.5, color=YELLOW),
            Dot(elements[2].get_center() + UP * 0.5, color=YELLOW)
        )
        self.play(Write(elements), FadeIn(dots))
        self.wait(1)
        self.play(dots.animate.shift(DOWN * 0.5))
        self.wait(1)
        self.play(FadeOut(elements), FadeOut(dots))

    def visualizing_electron_shells(self):
        nucleus = Dot(color=RED)
        shells = VGroup(
            Circle(radius=1, color=BLUE),
            Circle(radius=2, color=BLUE)
        )
        electrons = VGroup(
            Dot(shells[0].point_at_angle(PI / 4), color=YELLOW),
            Dot(shells[1].point_at_angle(PI / 2), color=YELLOW)
        )
        self.play(FadeIn(nucleus), Create(shells), FadeIn(electrons))
        self.wait(1)
        self.play(electrons.animate.shift(UP * 0.5))
        self.wait(1)
        self.play(FadeOut(nucleus), FadeOut(shells), FadeOut(electrons))

    def comparing_ionic_and_covalent_bonds(self):
        table = Table(
            [["Ionic", "Covalent"],
             ["Transfer", "Sharing"],
             ["NaCl", "H2O"]],
            col_labels=[Text("Bond Type"), Text("Characteristic")],
            include_outer_lines=True
        )
        self.play(Create(table))
        self.wait(1)
        self.play(table.get_entries((2, 1)).animate.set_color(RED))
        self.wait(1)
        self.play(FadeOut(table))

    def applications_in_chemical_reactions(self):
        reactants = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 3),
            Circle(radius=0.5, color=BLUE).shift(LEFT)
        )
        products = VGroup(
            Circle(radius=0.5, color=GREEN).shift(RIGHT),
            Circle(radius=0.5, color=GREEN).shift(RIGHT * 3)
        )
        arrow = Arrow(start=reactants.get_center(), end=products.get_center(), buff=0.5)
        self.play(Create(reactants), Create(arrow), Create(products))
        self.wait(1)
        self.play(reactants.animate.shift(RIGHT * 2), products.animate.shift(LEFT * 2))
        self.wait(1)
        self.play(FadeOut(reactants), FadeOut(products), FadeOut(arrow))

    def applications_in_material_science(self):
        lattice = VGroup(
            *[Line(LEFT, RIGHT, color=BLUE).shift(UP * i) for i in range(-2, 3)],
            *[Line(DOWN, UP, color=BLUE).shift(RIGHT * i) for i in range(-2, 3)]
        )
        bonds = VGroup(
            *[Dot(point, color=YELLOW) for point in lattice.get_all_points()]
        )
        self.play(Create(lattice), FadeIn(bonds))
        self.wait(1)
        self.play(bonds.animate.shift(UP * 0.5))
        self.wait(1)
        self.play(FadeOut(lattice), FadeOut(bonds))