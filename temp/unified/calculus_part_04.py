from manim import *
import random, numpy as np
random.seed(42); np.random.seed(42)

class ApplicationsOfDerivatives(Scene):
    def construct(self):
        # Introduction to Derivatives
        self.introduction_to_derivatives()
        self.wait(2)

        # Understanding Slope
        self.understanding_slope()
        self.wait(2)

        # Limit Definition of Derivatives
        self.limit_definition_of_derivatives()
        self.wait(2)

        # Power Rule Derivation
        self.power_rule_derivation()
        self.wait(2)

        # Constant Rule Explanation
        self.constant_rule_explanation()
        self.wait(2)

        # Example: Derivative of x^2
        self.example_derivative_of_x_squared()
        self.wait(2)

        # Example: Derivative of a Constant
        self.example_derivative_of_constant()
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

        # Conclusion and Summary
        self.conclusion_and_summary()
        self.wait(2)

    def introduction_to_derivatives(self):
        # Draw a curve with a tangent line at a point
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        curve = axes.plot(lambda x: x**2, color=BLUE)
        tangent_line = axes.get_tangent_line(1, curve, length=4, color=YELLOW)
        point = Dot(axes.c2p(1, 1**2), color=RED)

        self.play(Create(axes), Create(curve))
        self.play(Create(tangent_line), FadeIn(point))
        self.wait()

    def understanding_slope(self):
        # Illustrate a simple linear function and its slope
        line = Line(LEFT, RIGHT, color=GREEN).shift(UP)
        slope_arrow = Arrow(start=line.get_start(), end=line.get_end(), buff=0, color=ORANGE)
        slope_label = MathTex("m=1", font_size=36).next_to(slope_arrow, UP)

        self.play(Create(line))
        self.play(Create(slope_arrow), Write(slope_label))
        self.wait()

    def limit_definition_of_derivatives(self):
        # Show a curve with secant lines approaching a tangent
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        curve = axes.plot(lambda x: x**2, color=BLUE)
        secant_line1 = axes.get_secant_slope_group(1, curve, dx=1, secant_line_color=GREEN)
        secant_line2 = axes.get_secant_slope_group(1, curve, dx=0.5, secant_line_color=GREEN)
        tangent_line = axes.get_tangent_line(1, curve, length=4, color=YELLOW)

        self.play(Create(axes), Create(curve))
        self.play(Create(secant_line1))
        self.play(Transform(secant_line1, secant_line2))
        self.play(Transform(secant_line1, tangent_line))
        self.wait()

    def power_rule_derivation(self):
        # Use a polynomial function to demonstrate the Power Rule
        equation = MathTex(r"\frac{d}{dx}x^n = nx^{n-1}", font_size=36).to_edge(UP)
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        polynomial = axes.plot(lambda x: x**3, color=BLUE)
        derivative = axes.plot(lambda x: 3*x**2, color=RED)

        self.play(Write(equation))
        self.play(Create(axes), Create(polynomial))
        self.play(Transform(polynomial, derivative))
        self.wait()

    def constant_rule_explanation(self):
        # Illustrate a constant function and its flat slope
        axes = Axes(x_range=[-3, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        constant_line = axes.plot(lambda x: 2, color=BLUE)
        slope_label = MathTex("m=0", font_size=36).next_to(constant_line, RIGHT)

        self.play(Create(axes), Create(constant_line))
        self.play(Write(slope_label))
        self.wait()

    def example_derivative_of_x_squared(self):
        # Show the function x^2 and its derivative 2x
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        function = axes.plot(lambda x: x**2, color=BLUE)
        derivative = axes.plot(lambda x: 2*x, color=RED)
        tangent_line = axes.get_tangent_line(1, function, length=4, color=YELLOW)

        self.play(Create(axes), Create(function))
        self.play(Transform(function, derivative))
        self.play(Create(tangent_line))
        self.wait()

    def example_derivative_of_constant(self):
        # Illustrate a constant function and its zero derivative
        axes = Axes(x_range=[-3, 3], y_range=[-1, 3], axis_config={"include_numbers": True})
        constant_line = axes.plot(lambda x: 2, color=BLUE)
        zero_slope_label = MathTex("m=0", font_size=36).next_to(constant_line, RIGHT)

        self.play(Create(axes), Create(constant_line))
        self.play(Write(zero_slope_label))
        self.wait()

    def higher_order_derivatives(self):
        # Show graphs of a function, its first, and second derivatives
        axes = Axes(x_range=[-3, 3], y_range=[-1, 9], axis_config={"include_numbers": True})
        function = axes.plot(lambda x: x**3, color=BLUE)
        first_derivative = axes.plot(lambda x: 3*x**2, color=RED)
        second_derivative = axes.plot(lambda x: 6*x, color=GREEN)

        self.play(Create(axes), Create(function))
        self.play(Transform(function, first_derivative))
        self.play(Transform(function, second_derivative))
        self.wait()

    def applications_in_physics(self):
        # Use motion graphs to show velocity and acceleration
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        position_graph = axes.plot(lambda x: x**2, color=BLUE)
        velocity_graph = axes.plot(lambda x: 2*x, color=RED)
        acceleration_graph = axes.plot(lambda x: 2, color=GREEN)

        self.play(Create(axes), Create(position_graph))
        self.play(Transform(position_graph, velocity_graph))
        self.play(Transform(position_graph, acceleration_graph))
        self.wait()

    def applications_in_economics(self):
        # Show profit and cost functions with marginal analysis
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        cost_function = axes.plot(lambda x: x**2 + 2, color=BLUE)
        profit_function = axes.plot(lambda x: -x**2 + 4*x + 5, color=RED)

        self.play(Create(axes), Create(cost_function))
        self.play(Create(profit_function))
        self.wait()

    def applications_in_biology(self):
        # Use population growth graphs to show rate changes
        axes = Axes(x_range=[0, 5], y_range=[0, 25], axis_config={"include_numbers": True})
        population_growth = axes.plot(lambda x: x**2, color=BLUE)
        growth_rate = axes.plot(lambda x: 2*x, color=RED)

        self.play(Create(axes), Create(population_growth))
        self.play(Transform(population_growth, growth_rate))
        self.wait()

    def conclusion_and_summary(self):
        # Review key concepts with a summary slide
        summary_text = Text("Summary of Derivatives", font_size=48).to_edge(UP)
        bullet_points = BulletedList(
            "Derivatives as rates of change",
            "Limit definition of derivatives",
            "Basic derivative rules",
            "Applications in various fields",
            font_size=36
        )

        self.play(Write(summary_text))
        self.play(FadeIn(bullet_points))
        self.wait()