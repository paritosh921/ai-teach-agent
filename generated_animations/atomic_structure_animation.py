from manim import *

class AtomicStructure(Scene):
    def construct(self):
        # Introduction
        title = Text("Unveiling the World of Atoms: Understanding Atomic Structure")
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        hook = Text("Ever wondered what makes up everything in the universe? Let's dive into the amazing world of atomic structure!")
        self.play(Write(hook))
        self.wait(2)
        self.play(FadeOut(hook))
        
        # Content Section 1: Introduction to Atoms
        intro_title = Text("Introduction to Atoms")
        self.play(Write(intro_title))
        self.wait(1)
        
        atom_text = Text("Atoms: Building blocks of matter")
        self.play(Write(atom_text))
        self.wait(2)
        self.play(FadeOut(atom_text))
        
        # Content Section 2: Components of an Atom
        components_title = Text("Components of an Atom")
        self.play(Transform(intro_title, components_title))
        self.wait(1)
        
        atom_diagram = Circle() # Simplified representation of an atom
        self.play(FadeIn(atom_diagram))
        self.wait(2)
        self.play(FadeOut(atom_diagram))
        
        # Content Section 3: Arrangement of Electrons
        arrangement_title = Text("Arrangement of Electrons")
        self.play(Transform(intro_title, arrangement_title))
        self.wait(1)
        
        electron_arrangement = Circle() # Simplified representation of electron arrangement
        self.play(Transform(atom_diagram, electron_arrangement))
        self.wait(2)
        self.play(FadeOut(electron_arrangement))
        
        # Content Section 4: Atomic Number and Atomic Mass
        atomic_title = Text("Atomic Number and Atomic Mass")
        self.play(Transform(intro_title, atomic_title))
        self.wait(1)
        
        atomic_text = Text("Atomic Number = Number of Protons; Atomic Mass = Number of Protons + Neutrons")
        self.play(Write(atomic_text))
        self.wait(2)
        self.play(FadeOut(atomic_text))
        
        # Mathematical Elements
        formula = Tex("A = Z + N")
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(formula))
        
        graph = FunctionGraph(lambda x: x**2, x_range=[1, 7])
        self.play(Create(graph))
        self.wait(2)
        self.play(FadeOut(graph))
        
        # Conclusion
        conclusion_title = Text("Conclusion")
        self.play(Transform(intro_title, conclusion_title))
        self.wait(1)
        
        summary_points = BulletedList(
            "Atoms are the building blocks of matter",
            "They consist of protons, neutrons, and electrons",
            "Electrons inhabit energy levels or shells",
            "Atomic number and atomic mass define different atoms"
        )
        self.play(Create(summary_points))
        self.wait(2)
        self.play(FadeOut(summary_points))
        
        takeaway = Text("Atoms, though incredibly small, make up everything we see in the universe. Their structure - protons, neutrons, and electrons in specific arrangements - gives them unique properties.")
        self.play(Write(takeaway))
        self.wait(2)
        self.play(FadeOut(takeaway))
