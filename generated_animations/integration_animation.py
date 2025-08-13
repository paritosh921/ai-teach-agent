from manim import *

class IntegrationScene(Scene):
    def construct(self):
        # Create a text title and put it on screen
        title = Text("Integration", color=BLUE)
        title.scale(1.5)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Create and display the integral formula
        formula = Tex(r"\int_a^b f(x) \, dx")
        self.play(Write(formula))
        self.wait(1)

        # Explanation of the integral formula
        explanation = Text("The integral from a to b of f(x) with respect to x", color=GREEN)
        explanation.next_to(formula, DOWN)
        self.play(Write(explanation))
        self.wait(1)

        # Create and display a graph of a function
        graph = FunctionGraph(lambda x: 0.2 * (x - 2) * (x + 1) * (x + 2), color=YELLOW)
        self.play(ShowCreation(graph))
        self.wait(1)

        # Highlight the area under the graph between x=-1 and x=2
        area = AreaUnderCurve(
            graph,
            x_range=[-1, 2],
            color=RED,
            fill_opacity=0.5,
            dx_scaling=100,  # Increase this for better accuracy
        )
        self.play(ShowCreation(area))
        self.wait(1)

        # Animate the integral calculation
        integral = Tex(r"\int_{-1}^{2} f(x) \, dx = ", r"\approx 1.5")
        integral.next_to(area, DOWN)
        self.play(Write(integral))
        self.wait(2)

        # Fade out all objects
        self.play(FadeOut(area), FadeOut(integral), FadeOut(graph), FadeOut(formula), FadeOut(explanation))
