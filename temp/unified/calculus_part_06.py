from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class BasicIntegrationTechniques(Scene):
    def construct(self):
        # Introduction to Integration
        self.introduction_to_integration()
        self.wait(2)

        # Antiderivatives and Constants
        self.antiderivatives_and_constants()
        self.wait(2)

        # Fundamental Theorem of Calculus
        self.fundamental_theorem_of_calculus()
        self.wait(2)

        # Basic Integration Formulas
        self.basic_integration_formulas()
        self.wait(2)

        # Worked Examples
        self.worked_examples()
        self.wait(2)

        # Example 1: Power Rule
        self.example_power_rule()
        self.wait(2)

        # Example 2: Exponential Function
        self.example_exponential_function()
        self.wait(2)

        # Example 3: Trigonometric Function
        self.example_trigonometric_function()
        self.wait(2)

        # Integration in Physics
        self.integration_in_physics()
        self.wait(2)

        # Integration in Economics
        self.integration_in_economics()
        self.wait(2)

        # Advanced Techniques: Substitution
        self.advanced_techniques_substitution()
        self.wait(2)

        # Advanced Techniques: Integration by Parts
        self.advanced_techniques_integration_by_parts()
        self.wait(2)

    def introduction_to_integration(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 5], axis_config={"include_numbers": True})
        curve = axes.plot(lambda x: 0.5 * x**2, x_range=[0, 3], color=BLUE)
        area = axes.get_area(curve, x_range=[0, 3], color=BLUE, opacity=0.5)
        self.play(Create(axes), Create(curve))
        self.play(FadeIn(area))

    def antiderivatives_and_constants(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 5], axis_config={"include_numbers": True})
        func_graph = axes.plot(lambda x: 2 * x, x_range=[0, 3], color=GREEN)
        antiderivative_graph = axes.plot(lambda x: x**2, x_range=[0, 3], color=RED)
        self.play(Create(axes), Create(func_graph))
        self.play(Transform(func_graph, antiderivative_graph))

    def fundamental_theorem_of_calculus(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 5], axis_config={"include_numbers": True})
        curve = axes.plot(lambda x: 0.5 * x**2, x_range=[0, 3], color=BLUE)
        area = axes.get_area(curve, x_range=[0, 3], color=BLUE, opacity=0.5)
        bounds = VGroup(
            axes.get_vertical_line(axes.c2p(0, 0), color=YELLOW),
            axes.get_vertical_line(axes.c2p(3, 0), color=YELLOW)
        )
        self.play(Create(axes), Create(curve))
        self.play(FadeIn(area))
        self.play(Create(bounds))

    def basic_integration_formulas(self):
        formulas = VGroup(
            MathTex(r"\int x^n \, dx = \frac{x^{n+1}}{n+1} + C", font_size=36),
            MathTex(r"\int e^x \, dx = e^x + C", font_size=36),
            MathTex(r"\int \sin x \, dx = -\cos x + C", font_size=36)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).to_edge(LEFT)
        examples = VGroup(
            MathTex(r"\int x^2 \, dx = \frac{x^3}{3} + C", font_size=36),
            MathTex(r"\int e^x \, dx = e^x + C", font_size=36),
            MathTex(r"\int \sin x \, dx = -\cos x + C", font_size=36)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).to_edge(RIGHT)
        self.play(Write(formulas))
        self.play(Write(examples))

    def worked_examples(self):
        equation = MathTex(r"\int (3x^2 + 2x + 1) \, dx", font_size=36).to_edge(UP)
        solution_steps = VGroup(
            MathTex(r"= \int 3x^2 \, dx + \int 2x \, dx + \int 1 \, dx", font_size=36),
            MathTex(r"= x^3 + x^2 + x + C", font_size=36)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(equation, DOWN, buff=0.5)
        self.play(Write(equation))
        self.play(Write(solution_steps))

    def example_power_rule(self):
        integral = MathTex(r"\int x^2 \, dx", font_size=36).to_edge(UP)
        transformation = MathTex(r"= \frac{x^3}{3} + C", font_size=36).next_to(integral, DOWN, buff=0.5)
        self.play(Write(integral))
        self.play(Transform(integral, transformation))

    def example_exponential_function(self):
        integral = MathTex(r"\int e^x \, dx", font_size=36).to_edge(UP)
        transformation = MathTex(r"= e^x + C", font_size=36).next_to(integral, DOWN, buff=0.5)
        self.play(Write(integral))
        self.play(Transform(integral, transformation))

    def example_trigonometric_function(self):
        integral = MathTex(r"\int \sin x \, dx", font_size=36).to_edge(UP)
        transformation = MathTex(r"= -\cos x + C", font_size=36).next_to(integral, DOWN, buff=0.5)
        self.play(Write(integral))
        self.play(Transform(integral, transformation))

    def integration_in_physics(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 5], axis_config={"include_numbers": True})
        velocity_graph = axes.plot(lambda x: 2 * x, x_range=[0, 3], color=GREEN)
        displacement_area = axes.get_area(velocity_graph, x_range=[0, 3], color=GREEN, opacity=0.5)
        self.play(Create(axes), Create(velocity_graph))
        self.play(FadeIn(displacement_area))

    def integration_in_economics(self):
        axes = Axes(x_range=[0, 5], y_range=[0, 5], axis_config={"include_numbers": True})
        supply_curve = axes.plot(lambda x: 0.5 * x + 1, x_range=[0, 3], color=RED)
        demand_curve = axes.plot(lambda x: -0.5 * x + 4, x_range=[0, 3], color=BLUE)
        consumer_surplus = axes.get_area(demand_curve, x_range=[0, 1.5], color=BLUE, opacity=0.5)
        producer_surplus = axes.get_area(supply_curve, x_range=[0, 1.5], color=RED, opacity=0.5)
        self.play(Create(axes), Create(supply_curve), Create(demand_curve))
        self.play(FadeIn(consumer_surplus), FadeIn(producer_surplus))

    def advanced_techniques_substitution(self):
        integral = MathTex(r"\int 2x \sqrt{x^2 + 1} \, dx", font_size=36).to_edge(UP)
        substitution = MathTex(r"u = x^2 + 1", font_size=36).next_to(integral, DOWN, buff=0.5)
        solution = MathTex(r"= \int \sqrt{u} \, du", font_size=36).next_to(substitution, DOWN, buff=0.5)
        self.play(Write(integral))
        self.play(Write(substitution))
        self.play(Write(solution))

    def advanced_techniques_integration_by_parts(self):
        integral = MathTex(r"\int x e^x \, dx", font_size=36).to_edge(UP)
        formula = MathTex(r"= uv - \int v \, du", font_size=36).next_to(integral, DOWN, buff=0.5)
        solution = MathTex(r"= x e^x - \int e^x \, dx", font_size=36).next_to(formula, DOWN, buff=0.5)
        self.play(Write(integral))
        self.play(Write(formula))
        self.play(Write(solution))