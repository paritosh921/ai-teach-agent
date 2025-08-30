from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class LewisDotStructures(Scene):
    def construct(self):
        # Introduction to Valence Electrons
        self.intro_valence_electrons()
        self.wait(2)

        # Understanding the Octet Rule
        self.intro_octet_rule()
        self.wait(2)

        # Drawing H₂O Lewis Structure
        self.draw_h2o_structure()
        self.wait(2)

        # CO₂ Structure and Geometry
        self.draw_co2_structure()
        self.wait(2)

        # NH₃ Structure and Lone Pair Effects
        self.draw_nh3_structure()
        self.wait(2)

        # Common Misconceptions
        self.common_misconceptions()
        self.wait(2)

        # Predicting Molecular Geometry
        self.predict_molecular_geometry()
        self.wait(2)

        # Chemical Reactivity
        self.chemical_reactivity()
        self.wait(2)

        # Application: Water Molecule
        self.application_water()
        self.wait(2)

        # Application: Carbon Dioxide
        self.application_co2()
        self.wait(2)

        # Application: Ammonia
        self.application_ammonia()
        self.wait(2)

        # Conclusion and Summary
        self.conclusion_summary()
        self.wait(2)

    def intro_valence_electrons(self):
        title = Text("Valence Electrons").to_edge(UP)
        periodic_table = Rectangle(width=6, height=4).shift(DOWN)
        electron_dots = VGroup(*[Dot() for _ in range(8)]).arrange_in_grid(rows=2, buff=0.5).next_to(periodic_table, RIGHT)
        
        self.play(Write(title))
        self.play(Create(periodic_table))
        self.play(FadeIn(electron_dots))

    def intro_octet_rule(self):
        title = Text("Octet Rule").to_edge(UP)
        atom = Circle(radius=1).shift(LEFT)
        electron_dots = VGroup(*[Dot() for _ in range(8)]).arrange_in_grid(rows=2, buff=0.3).next_to(atom, RIGHT)
        bonds = VGroup(Line(atom.get_right(), electron_dots[0].get_left()), Line(atom.get_right(), electron_dots[1].get_left()))

        self.play(Transform(title, Text("Understanding the Octet Rule").to_edge(UP)))
        self.play(Create(atom))
        self.play(FadeIn(electron_dots))
        self.play(Create(bonds))

    def draw_h2o_structure(self):
        title = Text("H₂O Lewis Structure").to_edge(UP)
        oxygen = Tex("O", font_size=64).shift(LEFT)
        hydrogens = VGroup(Tex("H", font_size=64).next_to(oxygen, LEFT, buff=1), Tex("H", font_size=64).next_to(oxygen, RIGHT, buff=1))
        lone_pairs = VGroup(*[Dot() for _ in range(4)]).arrange_in_grid(rows=2, buff=0.3).next_to(oxygen, UP, buff=0.5)
        bonds = VGroup(Line(oxygen.get_left(), hydrogens[0].get_right()), Line(oxygen.get_right(), hydrogens[1].get_left()))

        self.play(Transform(title, Text("Drawing H₂O Lewis Structure").to_edge(UP)))
        self.play(Write(oxygen), Write(hydrogens))
        self.play(Create(bonds))
        self.play(FadeIn(lone_pairs))

    def draw_co2_structure(self):
        title = Text("CO₂ Structure and Geometry").to_edge(UP)
        carbon = Tex("C", font_size=64)
        oxygens = VGroup(Tex("O", font_size=64).next_to(carbon, LEFT, buff=1), Tex("O", font_size=64).next_to(carbon, RIGHT, buff=1))
        double_bonds = VGroup(Line(carbon.get_left(), oxygens[0].get_right()), Line(carbon.get_right(), oxygens[1].get_left()))

        self.play(Transform(title, Text("CO₂ Structure and Geometry").to_edge(UP)))
        self.play(Write(carbon), Write(oxygens))
        self.play(Create(double_bonds))

    def draw_nh3_structure(self):
        title = Text("NH₃ Structure and Lone Pair Effects").to_edge(UP)
        nitrogen = Tex("N", font_size=64)
        hydrogens = VGroup(Tex("H", font_size=64).next_to(nitrogen, UP, buff=1), Tex("H", font_size=64).next_to(nitrogen, LEFT, buff=1), Tex("H", font_size=64).next_to(nitrogen, RIGHT, buff=1))
        lone_pair = Dot().next_to(nitrogen, DOWN, buff=0.5)
        bonds = VGroup(Line(nitrogen.get_top(), hydrogens[0].get_bottom()), Line(nitrogen.get_left(), hydrogens[1].get_right()), Line(nitrogen.get_right(), hydrogens[2].get_left()))

        self.play(Transform(title, Text("NH₃ Structure and Lone Pair Effects").to_edge(UP)))
        self.play(Write(nitrogen), Write(hydrogens))
        self.play(Create(bonds))
        self.play(FadeIn(lone_pair))

    def common_misconceptions(self):
        title = Text("Common Misconceptions").to_edge(UP)
        incorrect_structure = Tex("H - O - H", font_size=64).shift(LEFT)
        correct_structure = Tex("H : O : H", font_size=64).shift(RIGHT)
        arrow = Arrow(incorrect_structure.get_right(), correct_structure.get_left())

        self.play(Transform(title, Text("Common Misconceptions").to_edge(UP)))
        self.play(Write(incorrect_structure))
        self.play(Create(arrow))
        self.play(Transform(incorrect_structure, correct_structure))

    def predict_molecular_geometry(self):
        title = Text("Predicting Molecular Geometry").to_edge(UP)
        molecule = Tex("H₂O", font_size=64)
        geometry = Tex("Bent Shape", font_size=48).next_to(molecule, DOWN, buff=1)
        arrow = Arrow(molecule.get_bottom(), geometry.get_top())

        self.play(Transform(title, Text("Predicting Molecular Geometry").to_edge(UP)))
        self.play(Write(molecule))
        self.play(Create(arrow))
        self.play(Write(geometry))

    def chemical_reactivity(self):
        title = Text("Chemical Reactivity").to_edge(UP)
        molecule = Tex("NH₃", font_size=64)
        reactive_sites = VGroup(Dot().next_to(molecule, UP, buff=0.5), Dot().next_to(molecule, DOWN, buff=0.5))
        arrow = Arrow(molecule.get_bottom(), reactive_sites[1].get_top())

        self.play(Transform(title, Text("Chemical Reactivity").to_edge(UP)))
        self.play(Write(molecule))
        self.play(Create(arrow))
        self.play(FadeIn(reactive_sites))

    def application_water(self):
        title = Text("Application: Water Molecule").to_edge(UP)
        water_molecule = Tex("H₂O", font_size=64)
        hydrogen_bonds = VGroup(Line(water_molecule.get_left(), water_molecule.get_right()), Line(water_molecule.get_top(), water_molecule.get_bottom()))

        self.play(Transform(title, Text("Application: Water Molecule").to_edge(UP)))
        self.play(Write(water_molecule))
        self.play(Create(hydrogen_bonds))

    def application_co2(self):
        title = Text("Application: Carbon Dioxide").to_edge(UP)
        co2_molecule = Tex("CO₂", font_size=64)
        greenhouse_effect = Tex("Greenhouse Effect", font_size=48).next_to(co2_molecule, DOWN, buff=1)
        arrow = Arrow(co2_molecule.get_bottom(), greenhouse_effect.get_top())

        self.play(Transform(title, Text("Application: Carbon Dioxide").to_edge(UP)))
        self.play(Write(co2_molecule))
        self.play(Create(arrow))
        self.play(Write(greenhouse_effect))

    def application_ammonia(self):
        title = Text("Application: Ammonia").to_edge(UP)
        ammonia_molecule = Tex("NH₃", font_size=64)
        fertilizer = Tex("Fertilizer", font_size=48).next_to(ammonia_molecule, DOWN, buff=1)
        arrow = Arrow(ammonia_molecule.get_bottom(), fertilizer.get_top())

        self.play(Transform(title, Text("Application: Ammonia").to_edge(UP)))
        self.play(Write(ammonia_molecule))
        self.play(Create(arrow))
        self.play(Write(fertilizer))

    def conclusion_summary(self):
        title = Text("Conclusion and Summary").to_edge(UP)
        summary = Tex("Lewis Dot Structures: Key Points", font_size=48).shift(DOWN)
        key_points = VGroup(
            Tex("1. Visualize valence electrons", font_size=32),
            Tex("2. Apply the octet rule", font_size=32),
            Tex("3. Predict molecular geometry", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(summary, DOWN, buff=0.5)

        self.play(Transform(title, Text("Conclusion and Summary").to_edge(UP)))
        self.play(Write(summary))
        self.play(FadeIn(key_points))