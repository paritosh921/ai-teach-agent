from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ComparativeViewIonicVsCovalentBonds(Scene):
    def construct(self):
        # Introduction to Bonding
        title_intro = Text("Introduction to Bonding").to_edge(UP)
        self.play(Write(title_intro))
        
        atoms = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT),
            Circle(radius=0.5, color=RED).shift(RIGHT)
        )
        electrons = VGroup(
            Dot(color=YELLOW).move_to(atoms[0].get_center() + 0.5 * UP),
            Dot(color=YELLOW).move_to(atoms[1].get_center() + 0.5 * DOWN)
        )
        self.play(Create(atoms), FadeIn(electrons))
        self.wait(1)
        
        # Atomic Structure Basics
        self.play(FadeOut(atoms), FadeOut(electrons), FadeOut(title_intro))
        title_atomic_structure = Text("Atomic Structure Basics").to_edge(UP)
        self.play(Write(title_atomic_structure))
        
        nucleus = Dot(color=GREEN).shift(LEFT * 3)
        electron_shells = VGroup(
            Circle(radius=1, color=WHITE).move_to(nucleus.get_center()),
            Circle(radius=1.5, color=WHITE).move_to(nucleus.get_center())
        )
        valence_electrons = VGroup(
            Dot(color=YELLOW).move_to(electron_shells[1].point_at_angle(PI / 4)),
            Dot(color=YELLOW).move_to(electron_shells[1].point_at_angle(3 * PI / 4))
        )
        self.play(Create(nucleus), Create(electron_shells), FadeIn(valence_electrons))
        self.wait(1)
        
        # Mechanism of Ionic Bonds
        self.play(FadeOut(nucleus), FadeOut(electron_shells), FadeOut(valence_electrons), FadeOut(title_atomic_structure))
        title_ionic_bonds = Text("Mechanism of Ionic Bonds").to_edge(UP)
        self.play(Write(title_ionic_bonds))
        
        na_atom = Circle(radius=0.5, color=BLUE).shift(LEFT * 3)
        cl_atom = Circle(radius=0.5, color=RED).shift(RIGHT * 3)
        electron = Dot(color=YELLOW).move_to(na_atom.get_center() + 0.5 * UP)
        self.play(Create(na_atom), Create(cl_atom), FadeIn(electron))
        
        self.play(electron.animate.move_to(cl_atom.get_center() + 0.5 * UP))
        na_plus = Tex("Na$^+$", color=BLUE).move_to(na_atom.get_center())
        cl_minus = Tex("Cl$^-$", color=RED).move_to(cl_atom.get_center())
        self.play(Transform(na_atom, na_plus), Transform(cl_atom, cl_minus))
        self.wait(1)
        
        # Electrostatic Attraction
        self.play(FadeOut(na_atom), FadeOut(cl_atom), FadeOut(electron), FadeOut(title_ionic_bonds))
        title_electrostatic = Text("Electrostatic Attraction").to_edge(UP)
        self.play(Write(title_electrostatic))
        
        na_plus = Tex("Na$^+$", color=BLUE).shift(LEFT * 2)
        cl_minus = Tex("Cl$^-$", color=RED).shift(RIGHT * 2)
        force_vector = Arrow(na_plus.get_center(), cl_minus.get_center(), buff=0.1, color=GREEN)
        self.play(FadeIn(na_plus), FadeIn(cl_minus), GrowArrow(force_vector))
        self.wait(1)
        
        # Mechanism of Covalent Bonds
        self.play(FadeOut(na_plus), FadeOut(cl_minus), FadeOut(force_vector), FadeOut(title_electrostatic))
        title_covalent_bonds = Text("Mechanism of Covalent Bonds").to_edge(UP)
        self.play(Write(title_covalent_bonds))
        
        h_atoms = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 2),
            Circle(radius=0.5, color=BLUE).shift(RIGHT * 2)
        )
        o_atom = Circle(radius=0.5, color=RED)
        shared_electrons = VGroup(
            Dot(color=YELLOW).move_to(o_atom.get_center() + 0.5 * UP),
            Dot(color=YELLOW).move_to(o_atom.get_center() + 0.5 * DOWN)
        )
        self.play(Create(h_atoms), Create(o_atom), FadeIn(shared_electrons))
        self.wait(1)
        
        # Molecular Shapes
        self.play(FadeOut(h_atoms), FadeOut(o_atom), FadeOut(shared_electrons), FadeOut(title_covalent_bonds))
        title_molecular_shapes = Text("Molecular Shapes").to_edge(UP)
        self.play(Write(title_molecular_shapes))
        
        linear_molecule = VGroup(
            Dot(color=BLUE).shift(LEFT),
            Dot(color=RED),
            Dot(color=BLUE).shift(RIGHT)
        ).arrange(RIGHT, buff=0.5)
        bent_molecule = VGroup(
            Dot(color=BLUE).shift(LEFT),
            Dot(color=RED),
            Dot(color=BLUE).shift(UP)
        ).arrange(RIGHT, buff=0.5)
        tetrahedral_molecule = VGroup(
            Dot(color=BLUE).shift(LEFT),
            Dot(color=RED),
            Dot(color=BLUE).shift(RIGHT),
            Dot(color=BLUE).shift(UP)
        ).arrange(RIGHT, buff=0.5)
        
        self.play(Create(linear_molecule))
        self.wait(1)
        self.play(Transform(linear_molecule, bent_molecule))
        self.wait(1)
        self.play(Transform(linear_molecule, tetrahedral_molecule))
        self.wait(1)
        
        # Properties and Examples
        self.play(FadeOut(linear_molecule), FadeOut(title_molecular_shapes))
        title_properties_examples = Text("Properties and Examples").to_edge(UP)
        self.play(Write(title_properties_examples))
        
        lattice = VGroup(
            Square(side_length=0.5, color=BLUE).shift(LEFT),
            Square(side_length=0.5, color=RED).shift(RIGHT)
        ).arrange(RIGHT, buff=0.1)
        molecule = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT),
            Circle(radius=0.5, color=RED).shift(RIGHT)
        ).arrange(RIGHT, buff=0.5)
        
        self.play(Create(lattice))
        self.wait(1)
        self.play(Transform(lattice, molecule))
        self.wait(1)
        
        # Conductivity and Bond Strength
        self.play(FadeOut(lattice), FadeOut(title_properties_examples))
        title_conductivity_strength = Text("Conductivity and Bond Strength").to_edge(UP)
        self.play(Write(title_conductivity_strength))
        
        ions_in_solution = VGroup(
            Dot(color=BLUE).shift(LEFT),
            Dot(color=RED).shift(RIGHT)
        ).arrange(RIGHT, buff=0.5)
        covalent_bond = Line(LEFT, RIGHT, color=YELLOW)
        
        self.play(Create(ions_in_solution))
        self.wait(1)
        self.play(Transform(ions_in_solution, covalent_bond))
        self.wait(1)
        
        # Real-world Applications
        self.play(FadeOut(ions_in_solution), FadeOut(title_conductivity_strength))
        title_real_world = Text("Real-world Applications").to_edge(UP)
        self.play(Write(title_real_world))
        
        materials = VGroup(
            Text("Salt").shift(LEFT * 3),
            Text("Water"),
            Text("Polymer").shift(RIGHT * 3)
        )
        self.play(FadeIn(materials))
        self.wait(1)
        
        # Conclusion and Applications
        self.play(FadeOut(materials), FadeOut(title_real_world))
        title_conclusion = Text("Conclusion and Applications").to_edge(UP)
        self.play(Write(title_conclusion))
        
        materials_with_labels = VGroup(
            Text("Salt (Ionic)", font_size=32).shift(LEFT * 3),
            Text("Water (Covalent)", font_size=32),
            Text("Polymer (Covalent)", font_size=32).shift(RIGHT * 3)
        )
        self.play(FadeIn(materials_with_labels))
        self.wait(1)
        
        # Review and Summary
        self.play(FadeOut(materials_with_labels), FadeOut(title_conclusion))
        title_review_summary = Text("Review and Summary").to_edge(UP)
        self.play(Write(title_review_summary))
        
        key_terms = VGroup(
            Text("Ionic Bond").shift(LEFT * 3),
            Text("Covalent Bond")
        )
        definitions = VGroup(
            Text("Electron transfer").shift(LEFT * 3),
            Text("Electron sharing")
        )
        self.play(FadeIn(key_terms), FadeIn(definitions))
        self.wait(1)
        
        # Closing Remarks
        self.play(FadeOut(key_terms), FadeOut(definitions), FadeOut(title_review_summary))
        title_closing_remarks = Text("Closing Remarks").to_edge(UP)
        self.play(Write(title_closing_remarks))
        
        # Assuming the images are available in the working directory
        collage = VGroup(
            ImageMobject("ionic_compound.png").shift(LEFT * 3),
            ImageMobject("covalent_compound.png").shift(RIGHT * 3)
        )
        self.play(FadeIn(collage))
        self.wait(1)
        self.play(FadeOut(collage), FadeOut(title_closing_remarks))
        self.wait(1)