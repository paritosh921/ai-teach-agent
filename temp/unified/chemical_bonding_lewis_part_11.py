from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class KosselLewisApproach(Scene):
    def construct(self):
        # Introduction to Kössel–Lewis Approach
        title = Text("Applications of the Kössel–Lewis Approach", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Display a periodic table highlighting Na, Cl, Mg, and O
        periodic_table = PeriodicTable()  # Corrected from ElementTable to PeriodicTable
        self.play(Create(periodic_table))
        self.wait(1)

        # Highlight Na and Cl, then show electron transfer
        na = periodic_table.get_element("Na")
        cl = periodic_table.get_element("Cl")
        self.play(na.animate.set_color(YELLOW), cl.animate.set_color(YELLOW))
        self.wait(1)

        # Transition to Mg and O, illustrating ionic bonding
        mg = periodic_table.get_element("Mg")
        o = periodic_table.get_element("O")
        self.play(na.animate.set_color(WHITE), cl.animate.set_color(WHITE))
        self.play(mg.animate.set_color(YELLOW), o.animate.set_color(YELLOW))
        self.wait(1)

        # Understanding Ionic Bonds
        self.play(FadeOut(periodic_table))
        na_dot = Dot(color=BLUE).shift(LEFT)
        cl_dot = Dot(color=RED).shift(RIGHT)
        arrow = Arrow(na_dot, cl_dot, buff=0.1)
        self.play(Create(na_dot), Create(cl_dot), Create(arrow))
        self.wait(1)

        # Animate Na losing an electron, Cl gaining it
        electron = Dot(color=WHITE).move_to(na_dot)
        self.play(Transform(electron, cl_dot))
        self.wait(1)

        # Show resulting Na⁺ and Cl⁻ ions
        na_ion = Text("Na⁺", font_size=32).next_to(na_dot, DOWN)
        cl_ion = Text("Cl⁻", font_size=32).next_to(cl_dot, DOWN)
        self.play(Write(na_ion), Write(cl_ion))
        self.wait(2)

        # Lattice Structure of Ionic Compounds
        self.play(FadeOut(na_dot, cl_dot, arrow, electron, na_ion, cl_ion))
        lattice = VGroup(*[Cube() for _ in range(8)]).arrange_in_grid(2, 4, buff=0.5)
        self.play(Create(lattice))
        self.wait(1)

        # Rotate the lattice to show 3D structure
        self.play(Rotate(lattice, angle=PI/4, axis=UP))
        self.wait(2)

        # Predicting Structures with Lewis
        self.play(FadeOut(lattice))
        co2 = MathTex("O=C=O", font_size=32).shift(UP * 2)
        h2o = MathTex("H-O-H", font_size=32)
        nh3 = MathTex("\\text{H}_3\\text{N}", font_size=32).shift(DOWN * 2)
        self.play(Write(co2))
        self.wait(1)
        self.play(Write(h2o))
        self.wait(1)
        self.play(Write(nh3))
        self.wait(2)

        # Covalent Bonding Explained
        self.play(FadeOut(co2, h2o, nh3))
        h2o_structure = VGroup(
            Dot(color=BLUE).shift(LEFT),
            Dot(color=RED),
            Dot(color=BLUE).shift(RIGHT)
        )
        self.play(Create(h2o_structure))
        self.wait(1)

        # Animate electron pairs forming covalent bonds
        shared_electrons = VGroup(
            Dot(color=WHITE).move_to(h2o_structure[0]),
            Dot(color=WHITE).move_to(h2o_structure[2])
        )
        self.play(Transform(shared_electrons[0], h2o_structure[1]), 
                  Transform(shared_electrons[1], h2o_structure[1]))
        self.wait(2)

        # Bond Order and Molecular Properties
        self.play(FadeOut(h2o_structure, shared_electrons))
        n2 = MathTex("N\\equiv N", font_size=32).shift(LEFT * 2)
        o2 = MathTex("O=O", font_size=32).shift(RIGHT * 2)
        self.play(Write(n2), Write(o2))
        self.wait(1)

        # Show triple bond in N₂, indicate strength
        self.play(n2.animate.set_color(GREEN))
        self.wait(1)

        # Show double bond in O₂, indicate relative weakness
        self.play(o2.animate.set_color(RED))
        self.wait(2)

        # Visualizing Bond Order
        self.play(FadeOut(n2, o2))
        bond_scale = NumberLine(x_range=[1, 3, 1], length=6, include_numbers=True)
        self.play(Create(bond_scale))
        self.wait(1)

        # Animate bond length changes with bond order
        bond_indicator = Arrow(start=bond_scale.n2p(1), end=bond_scale.n2p(3), buff=0)
        self.play(Create(bond_indicator))
        self.wait(2)

        # Polyatomic Ions and Modern Theories
        self.play(FadeOut(bond_scale, bond_indicator))
        nh4 = MathTex("\\text{NH}_4^+", font_size=32).shift(UP)
        so4 = MathTex("\\text{SO}_4^{2-}", font_size=32).shift(DOWN)
        self.play(Write(nh4))
        self.wait(1)
        self.play(Write(so4))
        self.wait(2)

        # Application in Chemical Engineering
        self.play(FadeOut(nh4, so4))
        materials = Text("Materials: NaCl, MgO, etc.", font_size=32)
        self.play(Write(materials))
        self.wait(2)

        # Application in Pharmaceuticals
        self.play(FadeOut(materials))
        drug_interaction = Text("Drug-Receptor Interaction", font_size=32)
        self.play(Write(drug_interaction))
        self.wait(2)

        # Summary and Conclusion
        self.play(FadeOut(drug_interaction))
        summary = VGroup(
            Text("Kössel–Lewis Approach", font_size=32),
            Text("Ionic and Covalent Bonds", font_size=32),
            Text("Bond Order", font_size=32),
            Text("Modern Bonding Theories", font_size=32)
        ).arrange(DOWN, buff=0.5)
        self.play(Write(summary))
        self.wait(2)

        # Interactive Q&A
        self.play(FadeOut(summary))
        question = Text("What is the bond order of N₂?", font_size=32)
        self.play(Write(question))
        self.wait(2)
        answer = Text("Answer: 3 (Triple Bond)", font_size=32).next_to(question, DOWN)
        self.play(Write(answer))
        self.wait(2)