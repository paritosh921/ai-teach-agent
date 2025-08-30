from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class HistoricalDevelopmentOfBondingTheories(Scene):
    def construct(self):
        # Introduction to Early Bonding Theories
        self.introduction_to_early_bonding_theories()
        self.wait(1)

        # Dalton's Atomic Theory
        self.daltons_atomic_theory()
        self.wait(1)

        # Faraday's Electrical Insights
        self.faradays_electrical_insights()
        self.wait(1)

        # Rutherford's Nuclear Model
        self.rutherfords_nuclear_model()
        self.wait(1)

        # Bohr's Electron Shells
        self.bohrs_electron_shells()
        self.wait(1)

        # Kössel's Ionic Bonding
        self.kossels_ionic_bonding()
        self.wait(1)

        # Lewis's Covalent Bonding
        self.lewiss_covalent_bonding()
        self.wait(1)

        # Octet Rule and Stability
        self.octet_rule_and_stability()
        self.wait(1)

        # Applications of Bonding Theories
        self.applications_of_bonding_theories()
        self.wait(1)

        # Predicting Molecular Shapes
        self.predicting_molecular_shapes()
        self.wait(1)

        # Lewis Structures in Synthesis
        self.lewis_structures_in_synthesis()
        self.wait(1)

        # Summary and Conclusion
        self.summary_and_conclusion()
        self.wait(1)

    def introduction_to_early_bonding_theories(self):
        timeline = NumberLine(x_range=[1800, 1920, 10], length=10, include_numbers=True)
        dalton = Text("Dalton", font_size=36).next_to(timeline.n2p(1803), UP)
        rutherford = Text("Rutherford", font_size=36).next_to(timeline.n2p(1911), UP)
        bohr = Text("Bohr", font_size=36).next_to(timeline.n2p(1913), UP)

        self.play(Create(timeline))
        self.play(Write(dalton))
        self.play(Transform(dalton, rutherford))
        self.play(Transform(dalton, bohr))
        self.play(FadeOut(dalton))

    def daltons_atomic_theory(self):
        sphere = Circle(radius=1, fill_opacity=1, color=BLUE)
        label = Text("Dalton's Model", font_size=36).next_to(sphere, DOWN)

        self.play(FadeIn(sphere))
        self.play(Write(label))
        self.play(Indicate(sphere, scale_factor=1.2))
        self.play(FadeOut(sphere), FadeOut(label))

    def faradays_electrical_insights(self):
        apparatus = VGroup(
            Rectangle(width=4, height=2, color=WHITE),
            Line(LEFT, RIGHT, color=YELLOW).shift(UP * 0.5),
            Line(LEFT, RIGHT, color=YELLOW).shift(DOWN * 0.5)
        )
        label = Text("Faraday's Insights", font_size=36).next_to(apparatus, DOWN)

        self.play(Create(apparatus))
        self.play(Write(label))
        self.play(Indicate(apparatus, scale_factor=1.1))
        self.play(FadeOut(apparatus), FadeOut(label))

    def rutherfords_nuclear_model(self):
        gold_foil = Square(side_length=2, color=GOLD)
        alpha_particles = VGroup(*[Dot(color=RED).shift(LEFT * i) for i in range(3)])
        nucleus = Dot(color=YELLOW).move_to(gold_foil.get_center())

        self.play(Create(gold_foil))
        self.play(FadeIn(alpha_particles))
        self.play(Transform(alpha_particles, nucleus))
        self.play(Indicate(nucleus, scale_factor=1.2))
        self.play(FadeOut(gold_foil), FadeOut(alpha_particles), FadeOut(nucleus))

    def bohrs_electron_shells(self):
        nucleus = Dot(color=YELLOW)
        orbits = VGroup(
            Circle(radius=1.5, color=WHITE),
            Circle(radius=2.5, color=WHITE)
        )
        electrons = VGroup(
            Dot(color=BLUE).move_to(orbits[0].point_at_angle(PI / 4)),
            Dot(color=BLUE).move_to(orbits[1].point_at_angle(PI / 3))
        )

        self.play(FadeIn(nucleus))
        self.play(Create(orbits))
        self.play(FadeIn(electrons))
        self.play(Rotate(electrons, angle=PI, about_point=nucleus.get_center()))
        self.play(FadeOut(nucleus), FadeOut(orbits), FadeOut(electrons))

    def kossels_ionic_bonding(self):
        sodium = Text("Na", font_size=36, color=BLUE).shift(LEFT * 2)
        chlorine = Text("Cl", font_size=36, color=GREEN).shift(RIGHT * 2)
        electron = Dot(color=YELLOW).next_to(sodium, RIGHT)

        self.play(Write(sodium), Write(chlorine))
        self.play(FadeIn(electron))
        self.play(Transform(electron, chlorine))
        self.play(Indicate(chlorine, scale_factor=1.2))
        self.play(FadeOut(sodium), FadeOut(chlorine), FadeOut(electron))

    def lewiss_covalent_bonding(self):
        oxygen = Text("O", font_size=36, color=RED)
        hydrogens = VGroup(
            Text("H", font_size=36, color=BLUE).next_to(oxygen, LEFT),
            Text("H", font_size=36, color=BLUE).next_to(oxygen, RIGHT)
        )
        shared_electrons = VGroup(
            Line(hydrogens[0].get_right(), oxygen.get_left(), color=YELLOW),
            Line(hydrogens[1].get_left(), oxygen.get_right(), color=YELLOW)
        )

        self.play(Write(oxygen), Write(hydrogens))
        self.play(Create(shared_electrons))
        self.play(Indicate(shared_electrons, scale_factor=1.1))
        self.play(FadeOut(oxygen), FadeOut(hydrogens), FadeOut(shared_electrons))

    def octet_rule_and_stability(self):
        neon = Text("Ne", font_size=36, color=ORANGE)
        sodium_ion = Text("Na⁺", font_size=36, color=BLUE).next_to(neon, LEFT, buff=1)
        chloride_ion = Text("Cl⁻", font_size=36, color=GREEN).next_to(neon, RIGHT, buff=1)

        self.play(Write(neon))
        self.play(Write(sodium_ion), Write(chloride_ion))
        self.play(Indicate(neon, scale_factor=1.1))
        self.play(FadeOut(neon), FadeOut(sodium_ion), FadeOut(chloride_ion))

    def applications_of_bonding_theories(self):
        co2 = Text("CO₂", font_size=36, color=WHITE)
        nh3 = Text("NH₃", font_size=36, color=WHITE).next_to(co2, DOWN, buff=1)

        self.play(Write(co2))
        self.play(Transform(co2, nh3))
        self.play(Indicate(nh3, scale_factor=1.1))
        self.play(FadeOut(co2), FadeOut(nh3))

    def predicting_molecular_shapes(self):
        linear = Text("Linear", font_size=36, color=WHITE)
        bent = Text("Bent", font_size=36, color=WHITE).next_to(linear, DOWN, buff=1)
        tetrahedral = Text("Tetrahedral", font_size=36, color=WHITE).next_to(bent, DOWN, buff=1)

        self.play(Write(linear))
        self.play(Transform(linear, bent))
        self.play(Transform(linear, tetrahedral))
        self.play(FadeOut(linear))

    def lewis_structures_in_synthesis(self):
        reactants = Text("Reactants", font_size=36, color=WHITE)
        product = Text("Product", font_size=36, color=WHITE).next_to(reactants, DOWN, buff=1)

        self.play(Write(reactants))
        self.play(Transform(reactants, product))
        self.play(Indicate(product, scale_factor=1.1))
        self.play(FadeOut(reactants))

    def summary_and_conclusion(self):
        timeline_recap = NumberLine(x_range=[1800, 1920, 10], length=10, include_numbers=True)
        key_concepts = Text("Key Concepts", font_size=36, color=WHITE).next_to(timeline_recap, DOWN, buff=1)

        self.play(Create(timeline_recap))
        self.play(Write(key_concepts))
        self.play(Indicate(key_concepts, scale_factor=1.1))
        self.play(FadeOut(timeline_recap), FadeOut(key_concepts))