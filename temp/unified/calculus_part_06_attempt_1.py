from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class BasicIntegrationTechniques(Scene):
    def construct(self):
        # Title
        title = Text("Basic Integration Techniques", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

        # Introduction to Antiderivatives
        self.introduction_to_antiderivatives()

        # Understanding Derivatives and Antiderivatives
        self.understanding_derivatives_and_antiderivatives()

        # Fundamental Theorem of Calculus
        self.fundamental_theorem_of_calculus()

        # Visualizing Definite Integrals
        self.visualizing_definite_integrals()

        # Basic Integration Formulas
        self.basic_integration_formulas()

        # Example 1: Integrating a Power Function
        self.example_integrating_power_function()

        # Example 2: Integrating an Exponential Function
        self.example_integrating_exponential_function()

        # Application in Physics: Work Done by a Force
        self.application_in_physics()

        # Application in Economics: Consumer Surplus
        self.application_in_economics()

        # Integration by Substitution
        self.integration_by_substitution()

        # Integration by Parts
        self.integration_by_parts()

        # Summary and Conclusion
        self.summary_and_conclusion()

    def introduction_to_antiderivatives(self):
        axes = Axes(x_range=[-1, 3], y_range=[-1, 5], axis_config={"include_numbers": True})
        graph_2x = axes.plot(lambda x: 2*x, color=BLUE, x_range=[-1, 3])
        graph_x2 = axes.plot(lambda x: x**2, color=GREEN, x_range=[-1, 3])

        self.play(Create(axes), Create(graph_2x))
        self.wait(1)
        self.play(Create(graph_x2))
        self.wait(1)

        label_2x = MathTex("y=2x", color=BLUE).next_to(graph_2x, UP)
        label_x2 = MathTex("y=x^2", color=GREEN).next_to(graph_x2, DOWN)

        self.play(Write(label_2x), Write(label_x2))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph_2x), FadeOut(graph_x2), FadeOut(label_2x), FadeOut(label_x2))

    def understanding_derivatives_and_antiderivatives(self):
        axes = Axes(x_range=[-1, 3], y_range=[-1, 5], axis_config={"include_numbers": True})
        graph_x2 = axes.plot(lambda x: x**2, color=GREEN, x_range=[-1, 3])
        tangent_line = axes.get_tangent_line(1, graph_x2, length=4, color=YELLOW)
        dot = Dot(axes.c2p(1, 1**2), color=RED)

        self.play(Create(axes), Create(graph_x2))
        self.wait(1)
        self.play(Create(tangent_line), Create(dot))
        self.wait(1)

        slope_label = MathTex("f'(x)=2x", color=YELLOW).next_to(tangent_line, RIGHT)
        self.play(Write(slope_label))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph_x2), FadeOut(tangent_line), FadeOut(dot), FadeOut(slope_label))

    def fundamental_theorem_of_calculus(self):
        axes = Axes(x_range=[0, 4], y_range=[0, 4], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=GREEN, x_range=[0, 4])
        area = axes.get_area(graph, x_range=[1, 3], color=BLUE, opacity=0.5)

        self.play(Create(axes), Create(graph))
        self.wait(1)
        self.play(Create(area))
        self.wait(1)

        a_label = MathTex("a").next_to(axes.c2p(1, 0), DOWN)
        b_label = MathTex("b").next_to(axes.c2p(3, 0), DOWN)
        self.play(Write(a_label), Write(b_label))
        self.wait(1)

        ftc_label = MathTex("F(b) - F(a)", color=YELLOW).next_to(area, UP)
        self.play(Write(ftc_label))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(area), FadeOut(a_label), FadeOut(b_label), FadeOut(ftc_label))

    def visualizing_definite_integrals(self):
        number_line = NumberLine(x_range=[0, 4], include_numbers=True)
        axes = Axes(x_range=[0, 4], y_range=[0, 4], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=GREEN, x_range=[0, 4])
        area = axes.get_area(graph, x_range=[1, 3], color=BLUE, opacity=0.5)

        self.play(Create(number_line))
        self.wait(1)
        self.play(Create(axes), Create(graph))
        self.wait(1)
        self.play(Create(area))
        self.wait(2)
        self.play(FadeOut(number_line), FadeOut(axes), FadeOut(graph), FadeOut(area))

    def basic_integration_formulas(self):
        formulas = VGroup(
            MathTex(r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C", font_size=36),
            MathTex(r"\int e^x \, dx = e^x + C", font_size=36),
            MathTex(r"\int \sin x \, dx = -\cos x + C", font_size=36),
            MathTex(r"\int \cos x \, dx = \sin x + C", font_size=36)
        ).arrange(DOWN, buff=0.5)

        self.play(Write(formulas[0]))
        self.wait(1)
        self.play(Write(formulas[1]))
        self.wait(1)
        self.play(Write(formulas[2]))
        self.wait(1)
        self.play(Write(formulas[3]))
        self.wait(2)
        self.play(FadeOut(formulas))

    def example_integrating_power_function(self):
        example = MathTex(r"\int x^3 \, dx", font_size=36)
        result = MathTex(r"= \frac{x^4}{4} + C", font_size=36).next_to(example, RIGHT)

        self.play(Write(example))
        self.wait(1)
        self.play(Write(result))
        self.wait(2)
        self.play(FadeOut(example), FadeOut(result))

    def example_integrating_exponential_function(self):
        example = MathTex(r"\int e^x \, dx", font_size=36)
        result = MathTex(r"= e^x + C", font_size=36).next_to(example, RIGHT)

        self.play(Write(example))
        self.wait(1)
        self.play(Write(result))
        self.wait(2)
        self.play(FadeOut(example), FadeOut(result))

    def application_in_physics(self):
        axes = Axes(x_range=[0, 4], y_range=[0, 4], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: 2*x, color=GREEN, x_range=[0, 4])
        area = axes.get_area(graph, x_range=[1, 3], color=BLUE, opacity=0.5)

        self.play(Create(axes), Create(graph))
        self.wait(1)
        self.play(Create(area))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(graph), FadeOut(area))

    def application_in_economics(self):
        axes = Axes(x_range=[0, 4], y_range=[0, 4], axis_config={"include_numbers": True})
        demand_curve = axes.plot(lambda x: 4 - x, color=GREEN, x_range=[0, 4])
        area = axes.get_area(demand_curve, x_range=[1, 3], color=BLUE, opacity=0.5)

        self.play(Create(axes), Create(demand_curve))
        self.wait(1)
        self.play(Create(area))
        self.wait(2)
        self.play(FadeOut(axes), FadeOut(demand_curve), FadeOut(area))

    def integration_by_substitution(self):
        example = MathTex(r"\int 2x \cdot e^{x^2} \, dx", font_size=36)
        substitution = MathTex(r"u = x^2 \Rightarrow du = 2x \, dx", font_size=36).next_to(example, DOWN)
        result = MathTex(r"= \int e^u \, du = e^{x^2} + C", font_size=36).next_to(substitution, DOWN)

        self.play(Write(example))
        self.wait(1)
        self.play(Write(substitution))
        self.wait(1)
        self.play(Write(result))
        self.wait(2)
        self.play(FadeOut(example), FadeOut(substitution), FadeOut(result))

    def integration_by_parts(self):
        example = MathTex(r"\int x \cdot e^x \, dx", font_size=36)
        formula = MathTex(r"= uv - \int v \, du", font_size=36).next_to(example, DOWN)
        result = MathTex(r"= x \cdot e^x - \int e^x \, dx = x \cdot e^x - e^x + C", font_size=36).next_to(formula, DOWN)

        self.play(Write(example))
        self.wait(1)
        self.play(Write(formula))
        self.wait(1)
        self.play(Write(result))
        self.wait(2)
        self.play(FadeOut(example), FadeOut(formula), FadeOut(result))

    def summary_and_conclusion(self):
        summary = VGroup(
            Text("Key Concepts:", font_size=36),
            Text("- Antiderivatives", font_size=32),
            Text("- Fundamental Theorem of Calculus", font_size=32),
            Text("- Basic Integration Formulas", font_size=32),
            Text("- Integration Techniques", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)

        self.play(Write(summary[0]))
        self.wait(1)
        self.play(Write(summary[1]))
        self.wait(1)
        self.play(Write(summary[2]))
        self.wait(1)
        self.play(Write(summary[3]))
        self.wait(1)
        self.play(Write(summary[4]))
        self.wait(2)
        self.play(FadeOut(summary))