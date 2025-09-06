from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ApplicationsOfDerivatives(Scene):
    def construct(self):
        # Introduction to Derivatives
        self.introduction_to_derivatives()
        self.wait(2)

        # Limit Definition of Derivative
        self.limit_definition_of_derivative()
        self.wait(2)

        # Power Rule Derivation
        self.power_rule_derivation()
        self.wait(2)

        # Constant and Sum Rules
        self.constant_and_sum_rules()
        self.wait(2)

        # Geometric Interpretation
        self.geometric_interpretation()
        self.wait(2)

        # Example: Derivative of x^3
        self.example_derivative_of_x_cubed()
        self.wait(2)

        # Higher-order Derivatives
        self.higher_order_derivatives()
        self.wait(2)

        # Applications in Physics
        self.applications_in_physics()
        self.wait(2)

        # Applications in Economics
        self.applications_in_economics()
        self.wait(2)

        # Applications in Biology
        self.applications_in_biology()
        self.wait(2)

        # Example: Velocity and Acceleration
        self.example_velocity_and_acceleration()
        self.wait(2)

        # Summary and Conclusion
        self.summary_and_conclusion()
        self.wait(2)

    def introduction_to_derivatives(self):
        title = Text("Introduction to Derivatives", font_size=48).to_edge(UP)
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=BLUE)
        tangent_line = axes.get_tangent_line(1, graph, color=YELLOW)
        self.play(Write(title), Create(axes), Create(graph))
        self.play(Create(tangent_line))
        self.wait(1)

    def limit_definition_of_derivative(self):
        title = Text("Limit Definition of Derivative", font_size=48).to_edge(UP)
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=BLUE)
        secant_line = always_redraw(lambda: axes.get_secant_slope_group(
            1, graph, dx=0.5, secant_line_color=GREEN, secant_line_length=4
        ))
        tangent_line = axes.get_tangent_line(1, graph, color=YELLOW)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(graph))
        self.play(Create(secant_line))
        self.play(Transform(secant_line, tangent_line))
        self.wait(1)

    def power_rule_derivation(self):
        title = Text("Power Rule Derivation", font_size=48).to_edge(UP)
        eq1 = MathTex(r"f(x) = x^n", font_size=36).shift(UP)
        eq2 = MathTex(r"f'(x) = \lim_{h \to 0} \frac{(x+h)^n - x^n}{h}", font_size=36)
        eq3 = MathTex(r"= nx^{n-1}", font_size=36).shift(DOWN)
        self.play(Transform(self.mobjects[0], title), Write(eq1))
        self.play(Write(eq2))
        self.play(Transform(eq2, eq3))
        self.wait(1)

    def constant_and_sum_rules(self):
        title = Text("Constant and Sum Rules", font_size=48).to_edge(UP)
        eq1 = MathTex(r"\frac{d}{dx}(c) = 0", font_size=36).shift(UP)
        eq2 = MathTex(r"\frac{d}{dx}(f(x) + g(x)) = f'(x) + g'(x)", font_size=36)
        self.play(Transform(self.mobjects[0], title), Write(eq1))
        self.play(Write(eq2))
        self.wait(1)

    def geometric_interpretation(self):
        title = Text("Geometric Interpretation", font_size=48).to_edge(UP)
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**2, color=BLUE)
        tangent_lines = VGroup(
            *[axes.get_tangent_line(x, graph, color=YELLOW) for x in np.linspace(-2, 2, 5)]
        )
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(graph))
        self.play(Create(tangent_lines))
        self.wait(1)

    def example_derivative_of_x_cubed(self):
        title = Text("Example: Derivative of x^3", font_size=48).to_edge(UP)
        axes = Axes(x_range=[-3, 3], y_range=[-10, 10], axis_config={"include_numbers": True})
        graph = axes.plot(lambda x: x**3, color=BLUE)
        derivative_graph = axes.plot(lambda x: 3*x**2, color=GREEN)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(graph))
        self.play(Transform(graph, derivative_graph))
        self.wait(1)

    def higher_order_derivatives(self):
        title = Text("Higher-order Derivatives", font_size=48).to_edge(UP)
        eq1 = MathTex(r"f(x) = x^3", font_size=36).shift(UP)
        eq2 = MathTex(r"f'(x) = 3x^2", font_size=36)
        eq3 = MathTex(r"f''(x) = 6x", font_size=36).shift(DOWN)
        self.play(Transform(self.mobjects[0], title), Write(eq1))
        self.play(Write(eq2))
        self.play(Write(eq3))
        self.wait(1)

    def applications_in_physics(self):
        title = Text("Applications in Physics", font_size=48).to_edge(UP)
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        position_graph = axes.plot(lambda t: t**2, color=BLUE)
        velocity_graph = axes.plot(lambda t: 2*t, color=GREEN)
        acceleration_graph = axes.plot(lambda t: 2, color=RED)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(position_graph))
        self.play(Transform(position_graph, velocity_graph))
        self.play(Transform(position_graph, acceleration_graph))
        self.wait(1)

    def applications_in_economics(self):
        title = Text("Applications in Economics", font_size=48).to_edge(UP)
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        cost_graph = axes.plot(lambda x: x**2, color=BLUE)
        profit_graph = axes.plot(lambda x: -x**2 + 5*x, color=GREEN)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(cost_graph))
        self.play(Transform(cost_graph, profit_graph))
        self.wait(1)

    def applications_in_biology(self):
        title = Text("Applications in Biology", font_size=48).to_edge(UP)
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        growth_curve = axes.plot(lambda t: 5/(1 + np.exp(-t)), color=BLUE)
        tangent_line = axes.get_tangent_line(2, growth_curve, color=YELLOW)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(growth_curve))
        self.play(Create(tangent_line))
        self.wait(1)

    def example_velocity_and_acceleration(self):
        title = Text("Example: Velocity and Acceleration", font_size=48).to_edge(UP)
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        position_graph = axes.plot(lambda t: t**2, color=BLUE)
        velocity_graph = axes.plot(lambda t: 2*t, color=GREEN)
        acceleration_graph = axes.plot(lambda t: 2, color=RED)
        self.play(Transform(self.mobjects[0], title), Create(axes), Create(position_graph))
        self.play(Transform(position_graph, velocity_graph))
        self.play(Transform(position_graph, acceleration_graph))
        self.wait(1)

    def summary_and_conclusion(self):
        title = Text("Summary and Conclusion", font_size=48).to_edge(UP)
        summary = VGroup(
            Text("Key Points:", font_size=36).shift(UP*2),
            Text("- Derivatives as rates of change", font_size=32),
            Text("- Power, Constant, and Sum Rules", font_size=32),
            Text("- Applications in various fields", font_size=32)
        ).arrange(DOWN, aligned_edge=LEFT)
        self.play(Transform(self.mobjects[0], title), FadeIn(summary))
        self.wait(1)