from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ContributionsOfWalterKossel(Scene):
    def construct(self):
        # Introduction to Atomic Models
        dalton_model = Circle(radius=1, color=BLUE)
        dalton_label = Text("Dalton's Model", font_size=36).next_to(dalton_model, DOWN)
        self.play(Create(dalton_model), Write(dalton_label))
        self.wait(2)

        # Transition to Rutherford's Model
        rutherford_nucleus = Dot(color=RED)
        rutherford_electrons = VGroup(*[Dot(color=YELLOW).shift(1.5 * RIGHT).rotate(angle, about_point=rutherford_nucleus.get_center()) for angle in [0, PI/2, PI, 3*PI/2]])
        rutherford_model = VGroup(rutherford_nucleus, rutherford_electrons)
        rutherford_label = Text("Rutherford's Model", font_size=36).next_to(rutherford_model, DOWN)
        self.play(Transform(dalton_model, rutherford_model), Transform(dalton_label, rutherford_label))
        self.wait(2)

        # Bohr's Model Introduction
        bohr_nucleus = Dot(color=RED)
        bohr_shells = VGroup(*[Circle(radius=r, color=GREEN).move_to(bohr_nucleus) for r in [1.5, 2.5]])
        bohr_electrons = VGroup(*[Dot(color=YELLOW).shift(1.5 * RIGHT).rotate(angle, about_point=bohr_nucleus.get_center()) for angle in [0, PI]])
        bohr_model = VGroup(bohr_nucleus, bohr_shells, bohr_electrons)
        bohr_label = Text("Bohr's Model", font_size=36).next_to(bohr_model, DOWN)
        self.play(Transform(rutherford_model, bohr_model), Transform(rutherford_label, bohr_label))
        self.wait(2)

        # Historical Context of Atomic Models
        self.play(FadeOut(bohr_model, bohr_label))
        self.wait(1)

        # Introduction to Kössel's Theory
        kossel_atom = Circle(radius=1, color=BLUE)
        kossel_electron = Dot(color=YELLOW).shift(1.2 * RIGHT)
        kossel_arrow = Arrow(kossel_electron.get_center(), kossel_electron.get_center() + RIGHT, buff=0)
        kossel_diagram = VGroup(kossel_atom, kossel_electron, kossel_arrow)
        kossel_label = Text("Kössel's Theory", font_size=36).next_to(kossel_diagram, DOWN)
        self.play(Create(kossel_diagram), Write(kossel_label))
        self.wait(2)

        # Kössel's Theory of Ionic Bonding
        sodium = Circle(radius=0.5, color=BLUE).shift(LEFT)
        chlorine = Circle(radius=0.5, color=GREEN).shift(RIGHT)
        electron_transfer = Arrow(sodium.get_center(), chlorine.get_center(), buff=0)
        self.play(Create(sodium), Create(chlorine), Create(electron_transfer))
        self.wait(2)

        # Example: Sodium Chloride Formation
        na_plus = Text("Na+", font_size=36).move_to(sodium)
        cl_minus = Text("Cl-", font_size=36).move_to(chlorine)
        lattice = VGroup(na_plus, cl_minus)
        self.play(Transform(sodium, na_plus), Transform(chlorine, cl_minus))
        self.wait(2)

        # Electrovalency Explained
        electrovalency_label = Text("Electrovalency", font_size=36).next_to(lattice, UP)
        self.play(Write(electrovalency_label))
        self.wait(2)

        # Predicting Ionic Compounds
        self.play(FadeOut(lattice, electrovalency_label))
        self.wait(1)

        # Material Science Applications
        material_structure = VGroup(*[Dot(color=BLUE).shift(i * RIGHT + j * UP) for i in range(-2, 3) for j in range(-2, 3)])
        self.play(Create(material_structure))
        self.wait(2)

        # Review and Summary
        summary_points = VGroup(
            Text("Kössel's Contributions:", font_size=36),
            Text("- Ionic Bonding", font_size=32),
            Text("- Electrovalency", font_size=32),
            Text("- Predicting Ionic Compounds", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).to_edge(LEFT)
        self.play(Write(summary_points))
        self.wait(2)

        # Conclusion and Reflection
        reflection_text = Text("Ionic bonding is fundamental to chemistry.", font_size=36).to_edge(DOWN)
        self.play(Write(reflection_text))
        self.wait(2)