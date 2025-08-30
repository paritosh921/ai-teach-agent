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

        # Introduction to Atomic Stability
        intro_title = Text("Introduction to Atomic Stability", font_size=36)
        noble_gases = Text("Noble Gases: He, Ne, Ar, Kr, Xe, Rn", font_size=32)
        octet_rule = Text("Octet Rule: 8 electrons in valence shell", font_size=32)
        self.play(Write(intro_title))
        self.wait(1)
        self.play(Write(noble_gases))
        self.wait(1)
        self.play(Write(octet_rule))
        self.wait(2)
        self.play(FadeOut(intro_title), FadeOut(noble_gases), FadeOut(octet_rule))

        # Understanding the Duet Rule
        duet_title = Text("Understanding the Duet Rule", font_size=36)
        hydrogen = Text("Hydrogen: 1 electron", font_size=32)
        helium = Text("Helium: 2 electrons", font_size=32)
        self.play(Write(duet_title))
        self.wait(1)
        self.play(Write(hydrogen))
        self.wait(1)
        self.play(Write(helium))
        self.wait(2)
        self.play(FadeOut(duet_title), FadeOut(hydrogen), FadeOut(helium))

        # Ionic Bonding Explained
        ionic_title = Text("Ionic Bonding Explained", font_size=36)
        sodium = Text("Sodium (Na): Loses 1 electron", font_size=32)
        chlorine = Text("Chlorine (Cl): Gains 1 electron", font_size=32)
        self.play(Write(ionic_title))
        self.wait(1)
        self.play(Write(sodium))
        self.wait(1)
        self.play(Write(chlorine))
        self.wait(2)
        self.play(FadeOut(ionic_title), FadeOut(sodium), FadeOut(chlorine))

        # Visualizing Ionic Compounds
        lattice_title = Text("Visualizing Ionic Compounds", font_size=36)
        lattice_structure = Text("NaCl Lattice Structure", font_size=32)
        self.play(Write(lattice_title))
        self.wait(1)
        self.play(Write(lattice_structure))
        self.wait(2)
        self.play(FadeOut(lattice_title), FadeOut(lattice_structure))

        # Covalent Bonding and Lewis Structures
        covalent_title = Text("Covalent Bonding and Lewis Structures", font_size=36)
        h2 = Text("H₂: Single Bond", font_size=32)
        o2 = Text("O₂: Double Bond", font_size=32)
        n2 = Text("N₂: Triple Bond", font_size=32)
        self.play(Write(covalent_title))
        self.wait(1)
        self.play(Write(h2))
        self.wait(1)
        self.play(Write(o2))
        self.wait(1)
        self.play(Write(n2))
        self.wait(2)
        self.play(FadeOut(covalent_title), FadeOut(h2), FadeOut(o2), FadeOut(n2))

        # Exploring Double and Triple Bonds
        bonds_title = Text("Exploring Double and Triple Bonds", font_size=36)
        double_bond = Text("Double Bond: O₂", font_size=32)
        triple_bond = Text("Triple Bond: N₂", font_size=32)
        self.play(Write(bonds_title))
        self.wait(1)
        self.play(Write(double_bond))
        self.wait(1)
        self.play(Write(triple_bond))
        self.wait(2)
        self.play(FadeOut(bonds_title), FadeOut(double_bond), FadeOut(triple_bond))

        # Lewis Structures in Complex Molecules
        complex_title = Text("Lewis Structures in Complex Molecules", font_size=36)
        nh3 = Text("NH₃: Ammonia", font_size=32)
        ch4 = Text("CH₄: Methane", font_size=32)
        self.play(Write(complex_title))
        self.wait(1)
        self.play(Write(nh3))
        self.wait(1)
        self.play(Write(ch4))
        self.wait(2)
        self.play(FadeOut(complex_title), FadeOut(nh3), FadeOut(ch4))

        # Applications of Lewis Structures
        applications_title = Text("Applications of Lewis Structures", font_size=36)
        molecular_shapes = Text("Molecular Shapes: Linear, Bent, Tetrahedral", font_size=32)
        self.play(Write(applications_title))
        self.wait(1)
        self.play(Write(molecular_shapes))
        self.wait(2)
        self.play(FadeOut(applications_title), FadeOut(molecular_shapes))

        # Limitations of the Kössel–Lewis Approach
        limitations_title = Text("Limitations of the Kössel–Lewis Approach", font_size=36)
        limitations_list = Text("Limitations: Incomplete for complex molecules", font_size=32)
        self.play(Write(limitations_title))
        self.wait(1)
        self.play(Write(limitations_list))
        self.wait(2)
        self.play(FadeOut(limitations_title), FadeOut(limitations_list))

        # Summary and Conclusion
        summary_title = Text("Summary and Conclusion", font_size=36)
        key_concepts = Text("Key Concepts: Octet Rule, Ionic & Covalent Bonds", font_size=32)
        self.play(Write(summary_title))
        self.wait(1)
        self.play(Write(key_concepts))
        self.wait(2)
        self.play(FadeOut(summary_title), FadeOut(key_concepts))

        # Interactive Q&A Session
        qa_title = Text("Interactive Q&A Session", font_size=36)
        question = Text("Q: What is the octet rule?", font_size=32)
        self.play(Write(qa_title))
        self.wait(1)
        self.play(Write(question))
        self.wait(2)
        self.play(FadeOut(qa_title), FadeOut(question))