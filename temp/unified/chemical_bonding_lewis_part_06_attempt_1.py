from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class IonicBondsKosselPerspective(Scene):
    def construct(self):
        # Introduction to Ionic Bonds
        title = Text("Ionic Bonds: Kössel's Perspective", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Sodium and Chlorine Atoms
        Na_atom = Circle(radius=1, color=BLUE).shift(LEFT * 3)
        Cl_atom = Circle(radius=1, color=GREEN).shift(RIGHT * 3)
        Na_label = Text("Na", font_size=36).next_to(Na_atom, DOWN)
        Cl_label = Text("Cl", font_size=36).next_to(Cl_atom, DOWN)
        electron = Dot(color=YELLOW).move_to(Na_atom.get_center() + RIGHT * 0.5)
        electron_arrow = Arrow(Na_atom.get_center() + RIGHT * 0.5, Cl_atom.get_center() + LEFT * 0.5, buff=0.1, color=YELLOW)

        self.play(Create(Na_atom), Create(Cl_atom), Write(Na_label), Write(Cl_label))
        self.play(FadeIn(electron))
        self.play(GrowArrow(electron_arrow))
        self.wait(1)

        # Transform atoms into ions
        Na_ion = Circle(radius=1, color=BLUE).shift(LEFT * 3)
        Cl_ion = Circle(radius=1, color=GREEN).shift(RIGHT * 3)
        Na_charge = Text("Na⁺", font_size=36).move_to(Na_ion.get_center())
        Cl_charge = Text("Cl⁻", font_size=36).move_to(Cl_ion.get_center())

        self.play(Transform(Na_atom, Na_ion), Transform(Cl_atom, Cl_ion), FadeOut(electron), FadeOut(electron_arrow))
        self.play(Transform(Na_label, Na_charge), Transform(Cl_label, Cl_charge))
        self.wait(1)

        # Electron Configuration of Sodium
        Na_Bohr_model = VGroup(
            Circle(radius=1, color=BLUE),
            Dot(color=YELLOW).shift(RIGHT * 0.5)
        ).move_to(ORIGIN)
        Na_Bohr_label = Text("Na", font_size=36).next_to(Na_Bohr_model, DOWN)

        self.play(FadeOut(Na_atom), FadeOut(Cl_atom), FadeOut(Na_label), FadeOut(Cl_label))
        self.play(Create(Na_Bohr_model), Write(Na_Bohr_label))
        self.wait(1)

        # Highlight the outermost electron
        self.play(Indicate(Na_Bohr_model[1]))
        self.wait(1)

        # Electron Configuration of Chlorine
        Cl_Bohr_model = VGroup(
            Circle(radius=1, color=GREEN),
            Dot(color=YELLOW).shift(LEFT * 0.5)
        ).move_to(ORIGIN)
        Cl_Bohr_label = Text("Cl", font_size=36).next_to(Cl_Bohr_model, DOWN)

        self.play(Transform(Na_Bohr_model, Cl_Bohr_model), Transform(Na_Bohr_label, Cl_Bohr_label))
        self.wait(1)

        # Highlight the outermost electron shell
        self.play(Indicate(Cl_Bohr_model[1]))
        self.wait(1)

        # Electron Transfer Process
        self.play(FadeOut(Na_Bohr_model), FadeOut(Na_Bohr_label))
        self.play(FadeIn(Na_atom), FadeIn(Cl_atom), FadeIn(Na_label), FadeIn(Cl_label))
        self.play(FadeIn(electron), GrowArrow(electron_arrow))
        self.wait(1)

        # Show charge formation on ions
        self.play(Transform(Na_atom, Na_ion), Transform(Cl_atom, Cl_ion), FadeOut(electron), FadeOut(electron_arrow))
        self.play(Transform(Na_label, Na_charge), Transform(Cl_label, Cl_charge))
        self.wait(1)

        # Formation of NaCl
        NaCl_molecule = VGroup(Na_ion, Cl_ion).arrange(RIGHT, buff=0.5)
        self.play(Transform(VGroup(Na_ion, Cl_ion), NaCl_molecule))
        self.wait(1)

        # Properties of Ionic Compounds
        NaCl_lattice = VGroup(*[Square(side_length=0.5, color=WHITE) for _ in range(16)]).arrange_in_grid(4, 4, buff=0.1)
        self.play(Transform(NaCl_molecule, NaCl_lattice))
        self.wait(1)

        # Rotate lattice to show structure
        self.play(Rotate(NaCl_lattice, angle=PI/4))
        self.wait(1)

        # Conductivity of Ionic Compounds
        solution = Rectangle(width=6, height=3, color=BLUE).shift(DOWN * 2)
        ions = VGroup(*[Dot(color=YELLOW) for _ in range(8)]).arrange_in_grid(2, 4, buff=0.5).move_to(solution.get_center())
        electric_current = Arrow(LEFT, RIGHT, buff=0.1, color=RED).next_to(solution, UP)

        self.play(FadeOut(NaCl_lattice), FadeIn(solution), FadeIn(ions))
        self.play(GrowArrow(electric_current))
        self.wait(1)

        # Animate ions moving in solution
        self.play(ions.animate.shift(RIGHT * 2), run_time=2)
        self.wait(1)

        # Melting and Boiling Points
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 1000, 100], axis_config={"include_numbers": True}).shift(UP * 2)
        melting_point_graph = axes.plot(lambda x: 100 * x, x_range=[0, 10], color=YELLOW)
        self.play(Create(axes), Create(melting_point_graph))
        self.wait(1)

        # Highlight differences
        self.play(Indicate(melting_point_graph))
        self.wait(1)

        # Crystalline Lattice Structure
        lattice = VGroup(*[Cube(side_length=0.5, fill_opacity=0.5) for _ in range(8)]).arrange_in_grid(2, 4, buff=0.1)
        self.play(Transform(melting_point_graph, lattice))
        self.wait(1)

        # Rotate lattice to show depth
        self.play(Rotate(lattice, angle=PI/4))
        self.wait(1)

        # Industrial Applications
        applications = VGroup(
            Text("Applications:", font_size=36),
            Text("1. Salt Production", font_size=32),
            Text("2. Electrolysis", font_size=32),
            Text("3. Ceramics", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).shift(DOWN * 2)

        self.play(FadeOut(lattice), Write(applications))
        self.wait(1)

        # Summary of Ionic Bonds
        summary_text = VGroup(
            Text("Summary:", font_size=36),
            Text("- Ionic bonds form through electron transfer.", font_size=32),
            Text("- High melting and boiling points.", font_size=32),
            Text("- Conduct electricity when molten or dissolved.", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).shift(DOWN * 2)

        self.play(FadeOut(applications), Write(summary_text))
        self.wait(1)

        # Conclusion and Review
        review_text = VGroup(
            Text("Review:", font_size=36),
            Text("Ionic bonds are crucial in chemistry.", font_size=32),
            Text("Understanding their properties is key.", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).shift(DOWN * 2)

        self.play(FadeOut(summary_text), Write(review_text))
        self.wait(1)

        self.play(FadeOut(review_text), FadeOut(title))
        self.wait(1)