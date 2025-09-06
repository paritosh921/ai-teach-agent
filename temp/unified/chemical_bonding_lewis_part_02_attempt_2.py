from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class HistoricalContextOfChemicalBonding(Scene):
    def construct(self):
        # Introduction to Historical Context
        timeline = NumberLine(x_range=[1800, 1920, 10], length=10, include_numbers=True)
        self.play(Create(timeline))
        self.wait(1)

        # Highlight key figures and discoveries
        key_figures = VGroup(
            Text("Dalton", font_size=32).next_to(timeline.n2p(1808), UP),
            Text("Faraday", font_size=32).next_to(timeline.n2p(1832), UP),
            Text("Rutherford", font_size=32).next_to(timeline.n2p(1911), UP),
            Text("Bohr", font_size=32).next_to(timeline.n2p(1913), UP)
        )
        self.play(FadeIn(key_figures))
        self.wait(1)

        # Dalton's Atomic Theory
        dalton_sphere = Sphere(radius=0.5).set_fill(BLUE, opacity=0.5)
        dalton_text = Text("Indivisible Atoms", font_size=32).next_to(dalton_sphere, DOWN)
        self.play(FadeIn(dalton_sphere), Write(dalton_text))
        self.wait(1)

        # Faraday's Electrostatic Concepts
        positive_charge = Dot(color=RED).shift(LEFT)
        negative_charge = Dot(color=BLUE).shift(RIGHT)
        attraction_arrow = Arrow(positive_charge, negative_charge, buff=0.1)
        self.play(FadeIn(positive_charge, negative_charge), Create(attraction_arrow))
        self.wait(1)

        # Rutherford's Nuclear Model
        nucleus = Dot(color=YELLOW)
        electron_orbits = VGroup(
            Circle(radius=1).shift(LEFT),
            Circle(radius=1.5).shift(RIGHT)
        )
        self.play(FadeIn(nucleus), Create(electron_orbits))
        self.wait(1)

        # Bohr's Atomic Model
        bohr_orbits = VGroup(
            Circle(radius=1.2).shift(LEFT),
            Circle(radius=1.8).shift(RIGHT)
        )
        electrons = VGroup(
            Dot(color=WHITE).move_to(bohr_orbits[0].point_from_proportion(0.25)),
            Dot(color=WHITE).move_to(bohr_orbits[1].point_from_proportion(0.75))
        )
        self.play(Transform(electron_orbits, bohr_orbits), FadeIn(electrons))
        self.wait(1)

        # Kössel's Ionic Bonding
        sodium_atom = Text("Na", font_size=32).shift(LEFT * 2)
        chlorine_atom = Text("Cl", font_size=32).shift(RIGHT * 2)
        electron_transfer = Arrow(sodium_atom, chlorine_atom, buff=0.1)
        self.play(FadeIn(sodium_atom, chlorine_atom), Create(electron_transfer))
        self.wait(1)

        # Lewis's Covalent Bonding
        oxygen_atom = Text("O", font_size=32)
        hydrogen_atoms = VGroup(
            Text("H", font_size=32).next_to(oxygen_atom, LEFT),
            Text("H", font_size=32).next_to(oxygen_atom, RIGHT)
        )
        electron_pairs = VGroup(
            Dot(color=WHITE).move_to(oxygen_atom.get_center() + LEFT * 0.5),
            Dot(color=WHITE).move_to(oxygen_atom.get_center() + RIGHT * 0.5)
        )
        self.play(FadeIn(oxygen_atom, hydrogen_atoms), FadeIn(electron_pairs))
        self.wait(1)

        # Octet Rule and Stability
        atom_models = VGroup(
            Circle(radius=0.5).shift(LEFT),
            Circle(radius=0.5).shift(RIGHT)
        )
        electron_shells = VGroup(
            Dot(color=WHITE).move_to(atom_models[0].get_center() + UP * 0.3),
            Dot(color=WHITE).move_to(atom_models[1].get_center() + DOWN * 0.3)
        )
        self.play(FadeIn(atom_models), FadeIn(electron_shells))
        self.wait(1)

        # Example: Sodium Chloride Formation
        na_atom = Text("Na", font_size=32).shift(LEFT * 2)
        cl_atom = Text("Cl", font_size=32).shift(RIGHT * 2)
        electron_transfer_na_cl = Arrow(na_atom, cl_atom, buff=0.1)
        self.play(FadeIn(na_atom, cl_atom), Create(electron_transfer_na_cl))
        self.wait(1)

        # Example: Water Molecule Structure
        oxygen = Text("O", font_size=32)
        hydrogens = VGroup(
            Text("H", font_size=32).next_to(oxygen, LEFT),
            Text("H", font_size=32).next_to(oxygen, RIGHT)
        )
        shared_electrons = VGroup(
            Dot(color=WHITE).move_to(oxygen.get_center() + LEFT * 0.5),
            Dot(color=WHITE).move_to(oxygen.get_center() + RIGHT * 0.5)
        )
        self.play(FadeIn(oxygen, hydrogens), FadeIn(shared_electrons))
        self.wait(1)

        # Predicting Molecular Structures
        co2_molecule = VGroup(
            Text("C", font_size=32),
            Text("O", font_size=32).next_to(ORIGIN, LEFT),
            Text("O", font_size=32).next_to(ORIGIN, RIGHT)
        )
        nh3_molecule = VGroup(
            Text("N", font_size=32),
            Text("H", font_size=32).next_to(ORIGIN, UP),
            Text("H", font_size=32).next_to(ORIGIN, LEFT),
            Text("H", font_size=32).next_to(ORIGIN, RIGHT)
        )
        self.play(FadeIn(co2_molecule, nh3_molecule))
        self.wait(1)

        # Applications and Limitations
        comparison_table = Table(
            [["Ionic", "Covalent"],
             ["Transfer of electrons", "Sharing of electrons"],
             ["High melting point", "Low melting point"]],
            col_labels=[Text("Bond Type", font_size=32), Text("Properties", font_size=32)],
            include_outer_lines=True
        )
        self.play(FadeIn(comparison_table))
        self.wait(1)

        # Summary and Modern Implications
        modern_timeline = NumberLine(x_range=[1920, 2020, 20], length=10, include_numbers=True)
        quantum_models = VGroup(
            Text("Quantum Chemistry", font_size=32).next_to(modern_timeline.n2p(2000), UP)
        )
        self.play(Create(modern_timeline), FadeIn(quantum_models))
        self.wait(1)