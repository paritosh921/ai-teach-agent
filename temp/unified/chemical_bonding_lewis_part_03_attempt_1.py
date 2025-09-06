from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ContributionsOfWalterKossel(Scene):
    def construct(self):
        # Title
        title = Text("Contributions of Walter Kössel", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Historical Context
        self.show_historical_context()

        # Kössel's Ionic Bonding
        self.show_kossel_ionic_bonding()

        # Worked Example: NaCl Formation
        self.show_nacl_formation()

        # Electrovalency Concept
        self.show_electrovalency_concept()

        # Comparing Ionic and Covalent Bonds
        self.compare_ionic_covalent_bonds()

        # Applications in Chemical Reactions
        self.show_chemical_reactions()

        # Visualizing Ion Formation
        self.visualize_ion_formation()

        # Periodic Trends in Ionic Bonding
        self.show_periodic_trends()

        # Real-World Example: Table Salt
        self.show_table_salt_example()

        # Advanced Concepts: Lattice Energy
        self.show_lattice_energy()

        # Review and Summary
        self.review_summary()

        # Interactive Q&A
        self.interactive_qa()

    def show_historical_context(self):
        # Dalton's Model
        dalton = Sphere(radius=0.5, color=BLUE).shift(LEFT * 3)
        dalton_label = Text("Dalton's Model", font_size=32).next_to(dalton, DOWN)
        self.play(Create(dalton), Write(dalton_label))
        self.wait(1)

        # Rutherford's Model
        rutherford = VGroup(
            Circle(radius=0.5, color=YELLOW),
            Dot(color=RED).move_to(LEFT * 0.5),
            Dot(color=RED).move_to(RIGHT * 0.5)
        ).shift(ORIGIN)
        rutherford_label = Text("Rutherford's Model", font_size=32).next_to(rutherford, DOWN)
        self.play(Transform(dalton, rutherford), Transform(dalton_label, rutherford_label))
        self.wait(1)

        # Bohr's Model
        bohr = VGroup(
            Circle(radius=0.5, color=YELLOW),
            Dot(color=RED).move_to(LEFT * 0.5),
            Dot(color=RED).move_to(RIGHT * 0.5),
            Circle(radius=1, color=GREEN, stroke_opacity=0.5)
        ).shift(RIGHT * 3)
        bohr_label = Text("Bohr's Model", font_size=32).next_to(bohr, DOWN)
        self.play(Transform(rutherford, bohr), Transform(rutherford_label, bohr_label))
        self.wait(2)
        self.play(FadeOut(rutherford), FadeOut(rutherford_label))

    def show_kossel_ionic_bonding(self):
        # Sodium and Chlorine atoms
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT * 2)
        electron = Dot(color=YELLOW).move_to(sodium.get_center())
        arrow = Arrow(sodium.get_center(), chlorine.get_center(), buff=0.5, color=WHITE)

        self.play(Create(sodium), Create(chlorine), Create(electron))
        self.wait(1)
        self.play(Create(arrow), MoveAlongPath(electron, arrow))
        self.wait(1)

        # Ions
        sodium_ion = Text("Na⁺", font_size=32).move_to(sodium.get_center())
        chlorine_ion = Text("Cl⁻", font_size=32).move_to(chlorine.get_center())
        self.play(Transform(sodium, sodium_ion), Transform(chlorine, chlorine_ion))
        self.wait(2)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron), FadeOut(arrow))

    def show_nacl_formation(self):
        # Step-by-step NaCl formation
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT * 2)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT * 2)
        electron = Dot(color=YELLOW).move_to(sodium.get_center())
        arrow = Arrow(sodium.get_center(), chlorine.get_center(), buff=0.5, color=WHITE)

        self.play(Create(sodium), Create(chlorine), Create(electron))
        self.wait(1)
        self.play(Create(arrow), MoveAlongPath(electron, arrow))
        self.wait(1)

        # Ions
        sodium_ion = Text("Na⁺", font_size=32).move_to(sodium.get_center())
        chlorine_ion = Text("Cl⁻", font_size=32).move_to(chlorine.get_center())
        self.play(Transform(sodium, sodium_ion), Transform(chlorine, chlorine_ion))
        self.wait(2)
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron), FadeOut(arrow))

    def show_electrovalency_concept(self):
        # Periodic Table with Electrovalency
        table = NumberPlane(x_range=[0, 10, 1], y_range=[0, 10, 1], background_line_style={"stroke_opacity": 0.3})
        alkali_metals = VGroup(*[Square(side_length=1, color=RED).move_to(table.c2p(i, 0)) for i in range(1, 3)])
        halogens = VGroup(*[Square(side_length=1, color=BLUE).move_to(table.c2p(i, 0)) for i in range(7, 9)])

        self.play(Create(table))
        self.play(Create(alkali_metals), Create(halogens))
        self.wait(2)
        self.play(FadeOut(table), FadeOut(alkali_metals), FadeOut(halogens))

    def compare_ionic_covalent_bonds(self):
        # Ionic vs Covalent Bonds
        ionic_bond = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Circle(radius=0.5, color=GREEN).shift(RIGHT * 2),
            Arrow(LEFT * 1.5, RIGHT * 1.5, buff=0.5, color=WHITE)
        )
        covalent_bond = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Circle(radius=0.5, color=GREEN).shift(RIGHT * 2),
            Line(LEFT * 1.5, RIGHT * 1.5, color=WHITE)
        ).shift(DOWN * 2)

        self.play(Create(ionic_bond))
        self.wait(1)
        self.play(Transform(ionic_bond, covalent_bond))
        self.wait(2)
        self.play(FadeOut(ionic_bond))

    def show_chemical_reactions(self):
        # Simple Reaction with Ionic Compounds
        reactants = Text("Na + Cl₂", font_size=32).shift(LEFT * 2)
        products = Text("2 NaCl", font_size=32).shift(RIGHT * 2)
        arrow = Arrow(LEFT * 1.5, RIGHT * 1.5, buff=0.5, color=WHITE)

        self.play(Write(reactants), Create(arrow))
        self.wait(1)
        self.play(Transform(reactants, products))
        self.wait(2)
        self.play(FadeOut(reactants), FadeOut(arrow))

    def visualize_ion_formation(self):
        # Electron loss and gain
        metals = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Dot(color=YELLOW).move_to(LEFT * 2)
        )
        non_metals = VGroup(
            Circle(radius=0.5, color=GREEN).shift(RIGHT * 2),
            Dot(color=YELLOW).move_to(RIGHT * 2)
        )

        self.play(Create(metals), Create(non_metals))
        self.wait(1)
        self.play(metals[1].animate.move_to(non_metals[0].get_center()))
        self.wait(2)
        self.play(FadeOut(metals), FadeOut(non_metals))

    def show_periodic_trends(self):
        # Graph showing periodic trends
        graph = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], axis_config={"include_numbers": True})
        atomic_size = graph.plot(lambda x: 10 - x, color=RED)
        ionization_energy = graph.plot(lambda x: x, color=BLUE)

        self.play(Create(graph), Create(atomic_size), Create(ionization_energy))
        self.wait(2)
        self.play(FadeOut(graph), FadeOut(atomic_size), FadeOut(ionization_energy))

    def show_table_salt_example(self):
        # NaCl Crystal Structure
        lattice = VGroup(*[Square(side_length=0.5, color=WHITE).move_to([i, j, 0]) for i in range(-2, 3) for j in range(-2, 3)])
        self.play(Create(lattice))
        self.wait(2)
        self.play(Rotate(lattice, angle=PI/4))
        self.wait(2)
        self.play(FadeOut(lattice))

    def show_lattice_energy(self):
        # Energy Diagram
        energy_diagram = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], axis_config={"include_numbers": True})
        energy_curve = energy_diagram.plot(lambda x: -x**2 + 10, color=GREEN)

        self.play(Create(energy_diagram), Create(energy_curve))
        self.wait(2)
        self.play(FadeOut(energy_diagram), FadeOut(energy_curve))

    def review_summary(self):
        # Summary Slide
        summary = VGroup(
            Text("Summary", font_size=40).to_edge(UP),
            Text("1. Kössel's Ionic Bonding Theory", font_size=32).shift(UP * 1),
            Text("2. Ionic vs Covalent Bonds", font_size=32),
            Text("3. Applications in Chemistry", font_size=32).shift(DOWN * 1)
        )
        self.play(Write(summary))
        self.wait(2)
        self.play(FadeOut(summary))

    def interactive_qa(self):
        # Interactive Q&A
        question = Text("What is ionic bonding?", font_size=32).to_edge(UP)
        answer_options = VGroup(
            Text("A. Sharing of electrons", font_size=32).shift(UP * 1),
            Text("B. Transfer of electrons", font_size=32),
            Text("C. Metallic bonding", font_size=32).shift(DOWN * 1)
        )
        correct_answer = SurroundingRectangle(answer_options[1], color=GREEN)

        self.play(Write(question), Write(answer_options))
        self.wait(1)
        self.play(Create(correct_answer))
        self.wait(2)
        self.play(FadeOut(question), FadeOut(answer_options), FadeOut(correct_answer))