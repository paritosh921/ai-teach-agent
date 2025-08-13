from manim import *

class ChemicalBonding(Scene):
    def construct(self):
        self.introduction()
        self.atomic_structure()
        self.ionic_bonding()
        self.covalent_bonding()
        self.metallic_bonding()
        self.mathematical_elements()
        self.visual_metaphors()
        self.conclusion()

    def introduction(self):
        title = Text("The Incredible World of Chemical Bonding")
        hook = Text("What makes water, a diamond, or a lump of sodium chloride? It's all about the bonds!")
        learning_objectives = BulletedList(
            "Understand what chemical bonding is and its importance.",
            "Learn the different types of chemical bonding."
        )
        self.play(Write(title), run_time=2)
        self.play(FadeIn(hook), run_time=2)
        self.play(Write(learning_objectives), run_time=2)
        self.wait(2)

    def atomic_structure(self):
        title = Text("Atomic Structure and the Octet Rule")
        diagram = Circle()  # Placeholder for actual diagram
        narration = Text("Atoms are made up of electrons, protons, and neutrons. The Octet Rule is a chemical rule of thumb that reflects the theory that main-group elements tend to bond in such a way that each atom has eight electrons in its valence shell, giving it the same electronic configuration as a noble gas.")
        self.play(Write(title), run_time=2)
        self.play(FadeIn(diagram), run_time=2)
        self.play(Write(narration), run_time=2)
        self.wait(2)

    def ionic_bonding(self):
        title = Text("Ionic Bonding")
        diagram = Circle()  # Placeholder for actual diagram
        narration = Text("Ionic bonding occurs between metals and non-metals. Here, one atom gives up one or more electrons to another atom. So, one atom becomes positively charged, and the other atom becomes negatively charged.")
        self.play(Write(title), run_time=2)
        self.play(FadeIn(diagram), run_time=2)
        self.play(Write(narration), run_time=2)
        self.wait(2)

    def covalent_bonding(self):
        title = Text("Covalent Bonding")
        diagram = Circle()  # Placeholder for actual diagram
        narration = Text("Covalent bonding occurs between non-metals. Here, atoms share electrons to achieve a stable electron configuration.")
        self.play(Write(title), run_time=2)
        self.play(FadeIn(diagram), run_time=2)
        self.play(Write(narration), run_time=2)
        self.wait(2)

    def metallic_bonding(self):
        title = Text("Metallic Bonding")
        diagram = Circle()  # Placeholder for actual diagram
        narration = Text("In metallic bonding, positive ions are surrounded by a cloud of rapidly moving dislocated electrons. This is often described as a 'sea of electrons'.")
        self.play(Write(title), run_time=2)
        self.play(FadeIn(diagram), run_time=2)
        self.play(Write(narration), run_time=2)
        self.wait(2)

    def mathematical_elements(self):
        formula = Tex("E = k (Q1 Q2) / r")
        graph = FunctionGraph(lambda x: 1/x, x_range=[0.1, 10], color=BLUE)
        self.play(Write(formula), run_time=2)
        self.play(Create(graph), run_time=2)
        self.wait(2)

    def visual_metaphors(self):
        # Placeholder for actual animations
        self.play(Create(Circle()), run_time=2)
        self.play(Create(Circle()), run_time=2)
        self.play(Create(Circle()), run_time=2)
        self.play(Create(Circle()), run_time=2)

    def conclusion(self):
        summary_points = BulletedList(
            "Chemical bonding is about achieving a stable electron configuration",
            "There are three types of chemical bonding: Ionic, covalent, and metallic"
        )
        key_takeaway = Text("The whole world around us, from the air we breathe to the objects we use, is made up of atoms connected by chemical bonds. Understanding these bonds helps us understand the world at its most fundamental level.")
        self.play(Write(summary_points), run_time=2)
        self.play(Write(key_takeaway), run_time=2)
        self.wait(2)
