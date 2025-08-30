from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class IonicBondingKosselPerspective(Scene):
    def construct(self):
        # Introduction to Ionic Bonding
        self.introduction_to_ionic_bonding()
        self.wait(2)

        # Sodium Chloride Example
        self.sodium_chloride_example()
        self.wait(2)

        # Properties of Ionic Compounds
        self.properties_of_ionic_compounds()
        self.wait(2)

        # Electron Transfer Mechanism
        self.electron_transfer_mechanism()
        self.wait(2)

        # Energy Considerations
        self.energy_considerations()
        self.wait(2)

        # Lattice Energy
        self.lattice_energy()
        self.wait(2)

        # Real-World Applications
        self.real_world_applications()
        self.wait(2)

        # Comparison with Covalent Bonds
        self.comparison_with_covalent_bonds()
        self.wait(2)

        # Visualizing Ionic Compounds
        self.visualizing_ionic_compounds()
        self.wait(2)

        # Conductivity in Ionic Compounds
        self.conductivity_in_ionic_compounds()
        self.wait(2)

        # Solubility of Ionic Compounds
        self.solubility_of_ionic_compounds()
        self.wait(2)

        # Review and Summary
        self.review_and_summary()
        self.wait(2)

    def introduction_to_ionic_bonding(self):
        title = Text("Introduction to Ionic Bonding").to_edge(UP)
        atom1 = Circle(radius=0.5, color=BLUE).shift(LEFT)
        atom2 = Circle(radius=0.5, color=RED).shift(RIGHT)
        electron = Dot(color=YELLOW).move_to(atom1.get_center())
        arrow = Arrow(atom1.get_center(), atom2.get_center(), buff=0.5, color=YELLOW)

        self.play(Write(title))
        self.play(Create(atom1), Create(atom2), FadeIn(electron))
        self.play(Transform(electron, electron.copy().move_to(atom2.get_center())), Create(arrow))
        self.play(FadeOut(arrow), electron.animate.set_color(RED), atom1.animate.set_color(GREEN), atom2.animate.set_color(ORANGE))
        self.play(FadeOut(electron))

    def sodium_chloride_example(self):
        title = Text("Sodium Chloride Example").to_edge(UP)
        na = Circle(radius=0.5, color=BLUE).shift(LEFT)
        cl = Circle(radius=0.5, color=RED).shift(RIGHT)
        electron = Dot(color=YELLOW).move_to(na.get_center())
        arrow = Arrow(na.get_center(), cl.get_center(), buff=0.5, color=YELLOW)

        self.play(Write(title))
        self.play(Create(na), Create(cl), FadeIn(electron))
        self.play(Transform(electron, electron.copy().move_to(cl.get_center())), Create(arrow))
        self.play(FadeOut(arrow), electron.animate.set_color(RED), na.animate.set_color(GREEN), cl.animate.set_color(ORANGE))
        self.play(FadeOut(electron))

        lattice = VGroup(*[Square(side_length=0.5, color=WHITE) for _ in range(9)]).arrange_in_grid(rows=3, buff=0.1)
        self.play(Transform(VGroup(na, cl), lattice))

    def properties_of_ionic_compounds(self):
        title = Text("Properties of Ionic Compounds").to_edge(UP)
        thermometer = SVGMobject("thermometer.svg").scale(0.5).shift(LEFT * 3)
        circuit = SVGMobject("circuit.svg").scale(0.5)
        water = SVGMobject("water.svg").scale(0.5).shift(RIGHT * 3)

        self.play(Write(title))
        self.play(FadeIn(thermometer), FadeIn(circuit), FadeIn(water))
        self.play(thermometer.animate.shift(UP), circuit.animate.shift(UP), water.animate.shift(UP))

    def electron_transfer_mechanism(self):
        title = Text("Electron Transfer Mechanism").to_edge(UP)
        na = Circle(radius=0.5, color=BLUE).shift(LEFT)
        cl = Circle(radius=0.5, color=RED).shift(RIGHT)
        electron = Dot(color=YELLOW).move_to(na.get_center())
        arrow = Arrow(na.get_center(), cl.get_center(), buff=0.5, color=YELLOW)

        self.play(Write(title))
        self.play(Create(na), Create(cl), FadeIn(electron))
        self.play(Transform(electron, electron.copy().move_to(cl.get_center())), Create(arrow))
        self.play(FadeOut(arrow), electron.animate.set_color(RED), na.animate.set_color(GREEN), cl.animate.set_color(ORANGE))
        self.play(FadeOut(electron))

    def energy_considerations(self):
        title = Text("Energy Considerations").to_edge(UP)
        energy_levels = VGroup(
            Line(LEFT, RIGHT, color=BLUE).shift(UP),
            Line(LEFT, RIGHT, color=RED).shift(DOWN)
        )
        arrow = Arrow(energy_levels[0].get_center(), energy_levels[1].get_center(), buff=0.1, color=YELLOW)

        self.play(Write(title))
        self.play(Create(energy_levels))
        self.play(Create(arrow))
        self.play(FadeOut(arrow))

    def lattice_energy(self):
        title = Text("Lattice Energy").to_edge(UP)
        lattice = VGroup(*[Square(side_length=0.5, color=WHITE) for _ in range(9)]).arrange_in_grid(rows=3, buff=0.1)
        energy_arrow = Arrow(UP, DOWN, buff=0.1, color=YELLOW).next_to(lattice, RIGHT)

        self.play(Write(title))
        self.play(Create(lattice))
        self.play(Create(energy_arrow))
        self.play(FadeOut(energy_arrow))

    def real_world_applications(self):
        title = Text("Real-World Applications").to_edge(UP)
        factory = SVGMobject("factory.svg").scale(0.5).shift(LEFT * 3)
        products = SVGMobject("products.svg").scale(0.5).shift(RIGHT * 3)

        self.play(Write(title))
        self.play(FadeIn(factory), FadeIn(products))
        self.play(factory.animate.shift(UP), products.animate.shift(UP))

    def comparison_with_covalent_bonds(self):
        title = Text("Comparison with Covalent Bonds").to_edge(UP)
        ionic_bond = VGroup(Circle(radius=0.5, color=BLUE), Circle(radius=0.5, color=RED)).arrange(RIGHT, buff=0.5)
        covalent_bond = VGroup(Circle(radius=0.5, color=GREEN), Circle(radius=0.5, color=GREEN)).arrange(RIGHT, buff=0.5)
        comparison_chart = VGroup(ionic_bond, covalent_bond).arrange(DOWN, buff=1)

        self.play(Write(title))
        self.play(Create(comparison_chart))

    def visualizing_ionic_compounds(self):
        title = Text("Visualizing Ionic Compounds").to_edge(UP)
        lattice = VGroup(*[Cube(side_length=0.5, color=WHITE) for _ in range(9)]).arrange_in_grid(rows=3, buff=0.1)

        self.play(Write(title))
        self.play(Create(lattice))
        self.play(Rotate(lattice, angle=PI / 4))

    def conductivity_in_ionic_compounds(self):
        title = Text("Conductivity in Ionic Compounds").to_edge(UP)
        ions = VGroup(*[Dot(color=BLUE) for _ in range(5)]).arrange(RIGHT, buff=0.5)
        electric_field = Arrow(LEFT, RIGHT, buff=0.1, color=YELLOW).next_to(ions, UP)

        self.play(Write(title))
        self.play(Create(ions))
        self.play(Create(electric_field))
        self.play(ions.animate.shift(RIGHT * 2))

    def solubility_of_ionic_compounds(self):
        title = Text("Solubility of Ionic Compounds").to_edge(UP)
        water_molecules = VGroup(*[Dot(color=BLUE) for _ in range(5)]).arrange(RIGHT, buff=0.5)
        ions = VGroup(*[Dot(color=RED) for _ in range(5)]).arrange(RIGHT, buff=0.5).shift(DOWN)

        self.play(Write(title))
        self.play(Create(water_molecules), Create(ions))
        self.play(ions.animate.shift(UP))

    def review_and_summary(self):
        title = Text("Review and Summary").to_edge(UP)
        summary_points = VGroup(
            Text("1. Ionic bonds form through electron transfer."),
            Text("2. Ionic compounds have high melting points."),
            Text("3. They conduct electricity when dissolved.")
        ).arrange(DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(summary_points, shift=UP))